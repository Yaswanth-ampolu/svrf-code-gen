import streamlit as st
import os
from dotenv import load_dotenv
import time

from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings, ChatNVIDIA
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.output_parsers import StrOutputParser

# Load environment
load_dotenv()
os.environ['NVIDIA_API_KEY'] = os.getenv("NVIDIA_API_KEY")

# App UI
st.set_page_config(page_title="SVRF Generator", layout="wide")
st.title("📐 Sierra Design Rule → SVRF Code Generator")
st.markdown("""
This tool helps convert semiconductor design rules from PDF manuals into valid SVRF code snippets.

### 🔄 Steps:
1. Ensure design rule PDFs are in the `./designrulepdf` directory.
2. Click **Documents Embedding** to build the knowledge base.
3. Ask your query below — like:  
   - `"Generate SVRF for M0B spacing and width"`
   - `"What are the rules for V0B enclosures?"`

4. Download your generated SVRF code.

---
""")

# Improved Prompt
prompt = ChatPromptTemplate.from_template(
"""
You are an expert in VLSI physical verification.

Your task is to translate semiconductor design rules into **SVRF (Standard Verification Rule Format)** code for use in DRC tools like Calibre.

### Instructions:
- Use SVRF keywords like `LAYER`, `WIDTH`, `SPACING`, `ENCLOSURE`, `AREA`, `RECTANGLE`, `NOTCH`, `EXTENSION`, `EXACT`, etc.
- Each rule must begin with a descriptive comment (e.g., `// M0B minimum spacing`)
- Include one SVRF instruction per line.
- Be concise and syntactically correct.

### Example:
<context>
layer:M0B, dimension:width, min:11, when:vertical
layer:M0B, dimension:spacing, min:10, when:vertical
</context>

### Output:
// M0B minimum vertical width
LAYER M0B ;
WIDTH M0B VERTICAL < 11 ;

// M0B minimum vertical spacing
SPACING M0B M0B VERTICAL < 10 ;

Now generate the corresponding SVRF code for:
<context>
{context}
</context>
"""
)

# Embed Vector Store
def vector_embedding():
    if "vectors" not in st.session_state:
        with st.spinner("Loading and embedding PDF rules..."):
            st.session_state.embeddings = NVIDIAEmbeddings()
            loader = PyPDFDirectoryLoader("./designrulepdf")
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=50)
            final_docs = splitter.split_documents(docs[:30])
            st.session_state.vectors = FAISS.from_documents(final_docs, st.session_state.embeddings)
            st.success("✅ Vector store created and ready.")

# LLM
llm = ChatNVIDIA(model="meta/llama3-70b-instruct")

# Query Input
query = st.text_input("🔍 Enter Your Question or Design Rule Specification:")

# Embedding Trigger
if st.button("📂 Documents Embedding"):
    vector_embedding()

# Run Retrieval and Output
if query:
    if "vectors" not in st.session_state:
        st.warning("Please run the document embedding step first.")
        st.stop()

    # Setup Chain
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = st.session_state.vectors.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    # Query
    with st.spinner("Generating SVRF Code..."):
        start = time.process_time()
        response = retrieval_chain.invoke({'input': query})
        elapsed = time.process_time() - start

    # Format Output
    formatted_output = "\n".join(
        line.strip() for line in response['answer'].splitlines() if line.strip()
    )

    # Show Results
    st.subheader("✅ Generated SVRF Code")
    st.code(formatted_output, language="svrf")
    st.write(f"⏱️ Response Time: {elapsed:.2f} seconds")

    # Download Button
    st.download_button("⬇️ Download SVRF Code", formatted_output, file_name="svrf_output.svrf")

    # Show Source Documents
    with st.expander("📄 Document Similarity Matches"):
        for i, doc in enumerate(response.get("context", [])):
            st.markdown(f"**Match {i+1}:**")
            st.write(doc.page_content)
            st.markdown("---")

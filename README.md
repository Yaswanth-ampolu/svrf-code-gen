

# **SVRF Code Generator for VLSI Design Rules**

## **Purpose**
The `app2.py` script automates the conversion of semiconductor design rules (from PDF manuals) into SVRF (Standard Verification Rule Format) code. It leverages AI to streamline the translation process, reducing manual effort in VLSI design verification.

## **Goal**
- **Input**: PDF documents containing semiconductor design rules.
- **Output**: Valid SVRF code snippets for design verification.
- **Key Features**:
  - Extracts and interprets design rules from PDFs.
  - Generates SVRF code with proper formatting (comments, layer names, dimensions).
  - Provides a user-friendly interface for querying and retrieving results.

## **Process**
1. **Document Loading**:
   - Loads PDFs from `./designrulepdf`.
   - Splits documents into chunks for processing.

2. **Embeddings & Vector Store**:
   - Converts text into embeddings using NVIDIA's AI.
   - Stores embeddings in a FAISS database for efficient retrieval.

3. **SVRF Generation**:
   - Uses a LangChain pipeline to:
     - Retrieve relevant design rules.
     - Translate rules into SVRF code using a predefined prompt and the LLaMA3-70B model.

4. **User Interaction**:
   - Accepts user queries via a text input.
   - Displays generated SVRF code, response time, and document matches.


This documentation avoids deep code explanations and focuses on the high-level workflow. Let me know if you'd like any refinements!

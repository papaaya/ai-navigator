# In-Context Cursor App

This project is an advanced research paper analyzer and code generator powered by Llama 4 (1M context window). It provides:
- **FastAPI backend** for chat, multimodal, paper-to-code, and PDF processing endpoints
- **Gradio frontend** for user-friendly research paper ingestion and chat
- **PDF processing** to extract text and references from arXiv papers
- **Llama 4 integration** for in-depth reasoning, code generation, and scientific Q&A

## Features
- **/chat**: Text and multimodal chat with Llama 4
- **/code_gen**: Generate Python code from research paper content
- **/pdf/process**: Download, extract, and ingest arXiv papers and references
- **/paper/chat**: Chat about a specific paper using its content as context
- **Gradio UI**: User-friendly interface for paper ingestion and chat

## Setup Instructions

### 1. Clone the repository
```sh
git clone git@github.com-personal:papaaya/ai-navigator.git
cd ai-navigator
```

### 2. Create and activate a virtual environment
```sh
python3 -m venv venv-llama4
source venv-llama4/bin/activate
```

### 3. Install dependencies
```sh
pip install -r requirements.txt
```

### 4. Set up your environment variables
Create a `.env` file in the project root:
```
LLAMA_API_KEY=your_llama_api_key_here
```

### 5. Run the FastAPI backend
```sh
python src/main.py
```
- The server will run at `http://localhost:8001`
- Visit `http://localhost:8001/docs` for interactive API docs

### 6. Run the Gradio frontend (optional)
```sh
python src/gradio_frontend.py
```
- The UI will be available at `http://localhost:7860`

## Example Usage

### Ingest an arXiv paper and chat about it
1. Use the Gradio UI or call the `/pdf/process` endpoint with an arXiv URL (e.g. `https://arxiv.org/abs/1706.03762`)
2. Once ingested, use `/paper/chat` to ask questions about the paper

### Generate code from a research paper
- Use the `/code_gen` endpoint with the paper content and (optionally) images

## Project Structure
```
ai-navigator/
  src/
    main.py              # FastAPI backend
    llama_api_caller.py  # Llama 4 API service
    pdf_processor.py     # PDF download and processing
    gradio_frontend.py   # Gradio UI (uses FastAPI backend)
```

## Requirements
- Python 3.9+
- Llama 4 API key (set in `.env`)

## Notes
- All sensitive files (`.env`, `venv-llama4/`, `.vscode/`) are git-ignored
- For best results, use with arXiv papers and ensure your Llama 4 API key is valid

---

**Developed with ❤️ using FastAPI, Gradio, and Llama 4**

---

## Project Submission Details

**PoC Email:**
`aipapaaya@gmail.com`

**Team Member Names and Emails:**
- `papaaya (aipapaaya@gmail.com)`
- `mkaur711@uw.edu`
- `rian.rahman10@gmail.com`

**Github Project Link:**
`https://github.com/papaaya/ai-navigator`

**Technologies Used:**
- Python
- FastAPI
- Llama 4 (Llama-4-Maverick-17B-128E-Instruct-FP8)
- Gradio
- PyPDF2 & PyMuPDF (for PDF processing)
- Uvicorn
- Git & GitHub

**Project Description:**
An advanced research paper analyzer and code generation system. The application leverages the Llama 4 1M+ context window to ingest arXiv papers, extract text and references, and allow users to chat about the content. It also features a "paper-to-code" endpoint that transforms algorithms and descriptions from research papers into high-quality, runnable Python code, complete with dependencies and unit tests. The system is served via a FastAPI backend and includes an optional Gradio frontend for a user-friendly interface.

**Which Llama model did you use?**
`Llama-4-Maverick-17B-128E-Instruct-FP8`

**How satisfied are you with the overall performance of the Llama models?**
Very Satisfied.

**What aspects of the model affected your satisfaction?**
The model's performance was excellent across all tasks. Key aspects include:
1.  **Multimodal Understanding:** The model accurately analyzed and described the content of multiple images, identifying common themes and specific details.
2.  **Advanced Code Generation:** It successfully translated a high-level algorithm from a pseudo-code description into a complete, correct, and well-documented Python implementation, including generating a `requirements.txt` file and a `pytest` test suite.
3.  **Complex Instruction Following:** The model consistently adhered to the complex system prompt, providing structured JSON output and following detailed instructions for code generation, docstrings, and error handling.
4.  **Reference Extraction:** It effectively processed raw text from a PDF to extract and format citations, demonstrating strong reasoning and NLP capabilities.


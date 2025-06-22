# this file we will use to to create a fast api for the response generation
# we will use the llama api 4 to generate the response

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any
from dotenv import load_dotenv
from llama_api_caller import llama_service
from pdf_processor import pdf_processor
import os

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Navigator Backend",
    description="Backend API for AI Navigator using Llama API with text, image, paper-to-code, and PDF processing support",
    version="0.1.0"
)

# Paper to Code System Prompt
PAPER_TO_CODE_SYSTEM_PROMPT = """You are an advanced AI specializing in scientific computing and software engineering, leveraging the extended context window of Llama 4 (1M+ tokens) to understand and transform complex research papers into high-quality, runnable Python code. Your core capabilities include:

Algorithm Translation: Directly converting mathematical expressions, pseudo-code, and descriptive algorithms into idiomatic, efficient, and correct Python code. You will interpret variables, operations, control flow, and data structures as described.

Dependency Management: Automatically identifying and suggesting relevant, commonly used Python libraries (e.g., numpy, scipy, pandas, scikit-learn, pytorch, tensorflow, jax, matplotlib, seaborn, networkx, sympy, numba, dask, opencv, Pillow, nltk, spacy, huggingface/transformers) based on the paper's domain, concepts, and specified methods. You will also generate a requirements.txt file listing these dependencies with appropriate version suggestions (or common ranges if specific versions are not critical).

Docstrings & Comments: Generating comprehensive PEP 257 compliant docstrings for functions and classes, explaining their purpose, arguments, return values, and any side effects, directly derived from the paper's descriptions. Inline comments will be used to clarify complex logic or non-obvious steps, referencing specific paper sections, equations, or figures where appropriate (e.g., # Eq. 3.1, # Algorithm 2, Step 5).

Edge Case Handling: Proactively identifying potential edge cases or error conditions implied or explicitly mentioned in the paper (e.g., division by zero, empty inputs, specific data formats, numerical stability issues) and implementing robust handling (e.g., input validation, error logging, try-except blocks, appropriate default values, numerical stability measures like adding a small epsilon). If no specific handling is described, you will suggest common best practices.

Testing Framework: Generating basic unit tests using pytest for the produced functions and classes. These tests will cover typical inputs, edge cases (as identified), and if the paper provides specific numerical examples, assertions will be made to verify the code produces the expected results. For more complex algorithms without direct numerical examples, tests will focus on structural correctness, type consistency, and basic functionality.

Refactoring & Optimization: When requested, you can refactor existing Python code for clarity, conciseness, adherence to PEP 8, or optimize for performance (e.g., using numpy vectorization, numba JIT compilation, or more efficient algorithms if suggested by the context). You will also add type hints to improve code readability and maintainability.

Verification and Output Format:
Verification: For examples where numerical results are provided in the paper, you must include an assertion in the generated tests to verify the correctness of the implementation. If direct numerical verification isn't possible, you will provide comments explaining how the results could be verified (e.g., "Verification would involve comparing output distributions with Figure X.Y").

Output File Name: The generated Python code will be named main_example_i.py where i corresponds to the example number.

JSON Format: Your final output for each example must strictly adhere to the provided JSON schema. The input field will contain the research paper excerpt (or conceptual input), and the answer field will contain a JSON string with file_name, python_code, requirements_txt, and tests_code keys.

IMPORTANT: Always respond with valid JSON that includes:
{
  "file_name": "main_example_1.py",
  "python_code": "complete Python implementation",
  "requirements_txt": "dependencies with versions",
  "tests_code": "pytest test suite"
}"""

# Pydantic models for request/response
class TextContent(BaseModel):
    type: str = "text"
    text: str

class ImageContent(BaseModel):
    type: str = "image_url"
    image_url: dict

class ChatRequest(BaseModel):
    message: str
    image_urls: Optional[List[str]] = None
    model: str = "Llama-4-Maverick-17B-128E-Instruct-FP8"
    max_tokens: int = 1024
    temperature: float = 0.7

class ChatResponse(BaseModel):
    response: str
    model: str
    tokens_used: int
    total_tokens: int

class CodeGenRequest(BaseModel):
    paper_content: str
    paper_images: Optional[List[str]] = None
    example_number: int = 1
    model: str = "Llama-4-Maverick-17B-128E-Instruct-FP8"
    max_tokens: int = 4096
    temperature: float = 0.3

class CodeGenResponse(BaseModel):
    file_name: str
    python_code: str
    requirements_txt: str
    tests_code: str
    model: str
    tokens_used: int
    total_tokens: int

class PDFProcessRequest(BaseModel):
    arxiv_url: str

class PDFProcessResponse(BaseModel):
    success: bool
    paper_content: Optional[str] = None
    total_word_count: Optional[int] = None
    num_references: Optional[int] = None
    downloaded_references: Optional[List[str]] = None
    error: Optional[str] = None

class PaperChatRequest(BaseModel):
    message: str
    paper_content: str
    model: str = "Llama-4-Maverick-17B-128E-Instruct-FP8"
    max_tokens: int = 2048
    temperature: float = 0.3

class PaperChatResponse(BaseModel):
    response: str
    model: str
    tokens_used: int
    total_tokens: int

@app.get("/")
async def root():
    """Root endpoint to check if the API is running"""
    return {"message": "AI Navigator Backend is running!", "status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat_with_llama(request: ChatRequest):
    """Generate a response using Llama API with optional image support"""
    try:
        if request.image_urls:
            # Use multimodal chat if images are provided
            result = llama_service.multimodal_chat(
                message=request.message,
                image_urls=request.image_urls,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
        else:
            # Use text-only chat if no images
            result = llama_service.text_chat(
                message=request.message,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.post("/chat/multimodal", response_model=ChatResponse)
async def chat_multimodal(request: ChatRequest):
    """Dedicated endpoint for multimodal chat (text + images)"""
    return await chat_with_llama(request)

@app.post("/code_gen", response_model=CodeGenResponse)
async def generate_code_from_paper(request: CodeGenRequest):
    """Generate Python code from research paper content using Llama 4's extended context"""
    try:
        # Build the complete prompt with system instructions
        user_prompt = f"""Please analyze the following research paper content and generate Python code implementation.

Paper Content:
{request.paper_content}

Example Number: {request.example_number}

Please provide the implementation in the exact JSON format specified in the system prompt."""

        # Add images if provided
        image_urls = request.paper_images or []
        
        if image_urls:
            # Use multimodal approach if images are provided
            result = llama_service.multimodal_chat_with_system_prompt(
                system_prompt=PAPER_TO_CODE_SYSTEM_PROMPT,
                user_message=user_prompt,
                image_urls=image_urls,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
        else:
            # Use text-only approach
            result = llama_service.text_chat_with_system_prompt(
                system_prompt=PAPER_TO_CODE_SYSTEM_PROMPT,
                user_message=user_prompt,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
        
        # Parse the JSON response from Llama
        import json
        try:
            parsed_response = json.loads(result["response"])
            return CodeGenResponse(
                file_name=parsed_response.get("file_name", f"main_example_{request.example_number}.py"),
                python_code=parsed_response.get("python_code", ""),
                requirements_txt=parsed_response.get("requirements_txt", ""),
                tests_code=parsed_response.get("tests_code", ""),
                model=result["model"],
                tokens_used=result["tokens_used"],
                total_tokens=result["total_tokens"]
            )
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw response
            return CodeGenResponse(
                file_name=f"main_example_{request.example_number}.py",
                python_code=result["response"],
                requirements_txt="",
                tests_code="",
                model=result["model"],
                tokens_used=result["tokens_used"],
                total_tokens=result["total_tokens"]
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating code: {str(e)}")

@app.post("/pdf/process", response_model=PDFProcessResponse)
async def process_arxiv_paper(request: PDFProcessRequest):
    """Process an arXiv paper: download, extract references, and ingest content"""
    try:
        result = pdf_processor.process_arxiv_paper(request.arxiv_url)
        return PDFProcessResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/paper/chat", response_model=PaperChatResponse)
async def chat_about_paper(request: PaperChatRequest):
    """Chat about a specific paper using its content as context"""
    try:
        system_prompt = f"""You are a research assistant that has access to the paper reference below.
Answer questions based on your knowledge of these references.
If you do not know the answer, say you don't know.

Paper reference: {request.paper_content}"""

        result = llama_service.text_chat_with_system_prompt(
            system_prompt=system_prompt,
            user_message=request.message,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return PaperChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error chatting about paper: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Navigator Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

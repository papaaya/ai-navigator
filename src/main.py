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

QnA_Prompt = """
You are a helpful assistant that can answer questions about the paper with the focus on the code generation.

## LLM's Pre-Code Generation Thought Process: Questions for Paper Analysis

The LLM should aim to build a mental model of the paper's contribution and identify the "codeable units."

### **Phase 1: High-Level Understanding & Scope Definition**

1.  **What is the core problem this paper is trying to solve?** (Abstract, Introduction)
    * *Self-correction:* Is this a novel problem, or a novel solution to an existing problem? How does this impact the expected code?
2.  **What is the main contribution or proposed solution (e.g., a new algorithm, model, framework)?** (Abstract, Introduction, sometimes Conclusion)
    * *Self-correction:* Is the primary contribution conceptual, or is there a tangible method/algorithm that can be implemented?
3.  **What are the prerequisites or foundational concepts necessary to understand this solution?** (Introduction, Related Work, Background sections)
    * *Self-correction:* Are there any external algorithms or data structures assumed to be known that need to be implemented or imported?
4.  **What is the overall architecture or system design if applicable?** (System Architecture, Methodology, Model Architecture sections)
    * *Self-correction:* Is this a monolithic algorithm or a system composed of multiple interacting modules? If modular, which module is the primary focus for code generation?
5.  **What kind of data does this method operate on, and what kind of output does it produce?** (Data, Methodology, sometimes Results sections)
    * *Self-correction:* What are the input/output formats (e.g., tensors, text, images, graphs, specific data structures)? Are there any preprocessing or postprocessing steps mentioned?

### **Phase 2: Identifying Codeable Sections & Prioritization**

6.  **Where are the explicit algorithms or pseudo-code blocks located?** (Methodology, Algorithms, Appendix)
    * *Self-correction:* Are there multiple algorithms? Which one is the most central or requested for implementation?
7.  **Are there mathematical formulas or equations that are critical for the implementation?** (Methodology, Theoretical Analysis, Appendix)
    * *Self-correction:* Do these equations directly translate to code, or do they describe underlying principles that need to be approximated or numerically solved?
8.  **Are there figures (flowcharts, diagrams) that illustrate the algorithm's control flow or data transformations?** (Figures, Methodology)
    * *Self-correction:* Can these diagrams clarify ambiguous pseudo-code or provide a higher-level view of the implementation steps?
9.  **Are there specific data structures described or implied as necessary for efficient implementation?** (Methodology, Implementation Details)
    * *Self-correction:* Are these standard data structures (e.g., hash maps, trees, linked lists) that can be imported, or novel ones that need custom implementation?
10. **Are there any "Implementation Details" or "Experimental Setup" sections that provide concrete values, hyperparameters, or library suggestions?** (Implementation Details, Experimental Setup, Appendix)
    * *Self-correction:* What are typical dimensions, data types, initial values, or configurations? Are there common libraries (e.g., NumPy, PyTorch, SciPy) implied?
11. **Are there any existing open-source code links provided by the authors or mentioned in the paper?** (References, Footnotes, Appendix, GitHub links)
    * *Self-correction:* Is the goal to replicate or to generate *new* code based on the description? If code exists, can it be used as a reference for validation or just for understanding the implementation style?

### **Phase 3: Deep Dive into Algorithm Details (Code Generation Focus)**

12. **For the chosen algorithm/method, what are its precise inputs, their types, and their expected shapes/formats?** (Algorithm Description, Mathematical Notations)
13. **What are the precise outputs, their types, and their expected shapes/formats?** (Algorithm Description, Mathematical Notations)
14. **What are the step-by-step logical operations? Can these be mapped directly to programming constructs (loops, conditionals, function calls)?** (Pseudo-code, Detailed Description)
15. **Are there any specific constants, thresholds, or magic numbers mentioned that need to be hardcoded or passed as parameters?** (Implementation Details, Formulas)
16. **Are there any specific mathematical functions (e.g., `softmax`, `log`, matrix multiplications, convolutions) required? Which libraries typically provide these?** (Formulas, Model Architecture)
17. **What are the identified edge cases or assumptions made by the authors that should be considered for robustness?** (Discussion, Limitations, Experimental Setup)
    * *Self-correction:* How should the code handle invalid inputs, empty sets, or boundary conditions?
18. **Are there any performance considerations mentioned (e.g., "O(N log N)", "parallelizable") that influence the choice of data structures or implementation strategy?** (Complexity Analysis, Discussion)
19. **If there are examples or small test cases provided (e.g., in figures, tables, or a small numerical example), how can these be used to generate unit tests?** (Examples, Results, Appendix)
20. **Is there any discussion on limitations, potential failure modes, or areas for future work that might hint at further code enhancements or unaddressed problems?** (Discussion, Conclusion)

### **Phase 4: Output Structuring & Refinement**

21. **What are the natural classes, functions, or modules that emerge from the algorithm's structure?** (Overall architecture, distinct logical components)
22. **What would be appropriate docstrings and inline comments to explain the code, drawing directly from the paper's descriptions?** (Abstract, Method, Algorithm sections)
23. **What standard Python libraries are explicitly or implicitly required, and how should they be declared (e.g., in `requirements.txt`)?** (Implementation Details, common ML/scientific computing practices)
24. **How can the generated code be formatted for readability and adherence to common Python style guides (e.g., PEP 8)?** (General programming best practices)
"""

# Paper to Code System Prompt
PAPER_TO_CODE_SYSTEM_PROMPT = """You are an advanced AI specializing in scientific computing and software engineering, leveraging the extended context window of Llama 4 (1M+ tokens) to understand and transform complex research papers into high-quality, runnable Python code. Your core capabilities include:

Algorithm Translation: Directly converting mathematical expressions, pseudo-code, and descriptive algorithms into idiomatic, efficient, and correct Python code. You will interpret variables, operations, control flow, and data structures as described.

Dependency Management: Automatically identifying and suggesting relevant, commonly used Python libraries (e.g., numpy, scipy, pandas, scikit-learn, pytorch, tensorflow, jax, matplotlib, seaborn, networkx, sympy, numba, dask, opencv, Pillow, nltk, spacy, huggingface/transformers) based on the paper's domain, concepts, and specified methods. You will also generate a requirements.txt file listing these dependencies with appropriate version suggestions (or common ranges if specific versions are not critical).

Docstrings & Comments: Generating comprehensive PEP 257 compliant docstrings for functions and classes, explaining their purpose, arguments, return values, and any side effects, directly derived from the paper's descriptions. Inline comments will be used to clarify complex logic or non-obvious steps, referencing specific paper sections, equations, or figures where appropriate (e.g., # Eq. 3.1, # Algorithm 2, Step 5).

Edge Case Handling: Proactively identifying potential edge cases or error conditions implied or explicitly mentioned in the paper (e.g., division by zero, empty inputs, specific data formats, numerical stability issues) and implementing robust handling (e.g., input validation, error logging, try-except blocks, appropriate default values, numerical stability measures like adding a small epsilon). If no specific handling is described, you will suggest common best practices.

Testing Framework: Generating basic unit tests using pytest for the produced functions and classes. These tests will cover typical inputs, edge cases (as identified), and if the paper provides specific numerical examples, assertions will be made to verify the code produces the expected results. For more complex algorithms without direct numerical examples, tests will focus on structural correctness, type consistency, and basic functionality.

Verifiable Assertions: Adding simple verifiable assertions for the code to ensure the code is correct.

Refactoring & Optimization: When requested, you can refactor existing Python code for clarity, conciseness, adherence to PEP 8, or optimize for performance (e.g., using numpy vectorization, numba JIT compilation, or more efficient algorithms if suggested by the context). You will also add type hints to improve code readability and maintainability.

VERIFICATION AND OUTPUT FORMAT:
You MUST respond with a valid JSON object that includes ALL of the following fields:

{
  "file_name": "main_example_1.py",
  "python_code": "complete Python implementation with imports, functions, classes, and main execution",
  "requirements_txt": "list of dependencies with versions (minimum 3-5 packages)",
  "tests_code": "complete pytest test suite with 3-5 test cases covering normal usage and edge cases"
}

CRITICAL REQUIREMENTS:
1. The python_code MUST be a complete, runnable Python script
2. The requirements_txt MUST contain at least 3-5 relevant packages with version numbers
3. The tests_code MUST contain at least 3-5 pytest test cases
4. All code must be properly formatted and follow PEP 8 standards
5. Include comprehensive docstrings and comments
6. Handle edge cases and input validation
7. The response MUST be valid JSON - no additional text before or after the JSON object"""

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

class QnARequest(BaseModel):
    arxiv_url: str
    questions: List[str]
    model: str = "Llama-4-Maverick-17B-128E-Instruct-FP8"
    max_tokens: int = 2048
    temperature: float = 0.3

class QnAResponse(BaseModel):
    paper_title: str
    answers: List[Dict[str, str]]  # List of {"question": "...", "answer": "..."}
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
        # Debug: Print the received request
        print(f"DEBUG: Received request with paper_content length: {len(request.paper_content)}")
        print(f"DEBUG: Request fields: {request.model_dump().keys()}")
        
        # Send paper content directly as user message
        user_message = request.paper_content

        # Add images if provided
        image_urls = request.paper_images or []
        
        print(f"DEBUG: About to call Llama API with user_message length: {len(user_message)}")
        
        # Check if content is too large and truncate if necessary
        max_content_length = 500000  # Limit to ~500k characters
        if len(user_message) > max_content_length:
            print(f"DEBUG: Content too large ({len(user_message)} chars), truncating to {max_content_length}")
            user_message = user_message[:max_content_length] + "\n\n[Content truncated due to length limits]"
        
        if image_urls:
            # Use multimodal approach if images are provided
            result = llama_service.multimodal_chat_with_system_prompt(
                system_prompt=PAPER_TO_CODE_SYSTEM_PROMPT,
                user_message=user_message,
                image_urls=image_urls,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
        else:
            # Use system prompt approach for structured output
            result = llama_service.text_chat_with_response_format(
                system_prompt=PAPER_TO_CODE_SYSTEM_PROMPT,
                user_message=user_message,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
        
        print(f"DEBUG: Llama API result: {result}")
        
        # Check if the response is empty
        if not result.get("response", "").strip():
            print("DEBUG: Empty response from Llama API")
            return CodeGenResponse(
                file_name=f"main_example_{request.example_number}.py",
                python_code="# ERROR: The paper content was too large or complex for the model to process.\n# Please try with a shorter paper or a more focused section.",
                requirements_txt="",
                tests_code="",
                model=result["model"],
                tokens_used=result["tokens_used"],
                total_tokens=result["total_tokens"]
            )
        
        # If the response contains MessageTextContentItem wrapper, try to extract clean JSON
        response_text = result["response"]
        if "MessageTextContentItem" in response_text:
            print("DEBUG: Detected MessageTextContentItem wrapper, attempting to extract clean JSON")
            # Try to extract the actual JSON content
            if "text='" in response_text:
                start = response_text.find("text='") + 6
                end = response_text.rfind("')")
                if start > 5 and end > start:
                    response_text = response_text[start:end]
        
        # Try to clean up the response if it's not pure JSON
        if not response_text.strip().startswith('{'):
            # Add a follow-up instruction to get clean JSON
            cleanup_prompt = "Please provide ONLY the JSON object with the required fields (file_name, python_code, requirements_txt, tests_code). Do not include any additional text, explanations, or wrappers. Return only valid JSON."
            
            cleanup_result = llama_service.text_chat_with_system_prompt(
                system_prompt="You are a JSON formatter. Return only valid JSON objects without any additional text or wrappers.",
                user_message=f"Original response: {response_text}\n\n{cleanup_prompt}",
                model=request.model,
                max_tokens=2048,
                temperature=0.1
            )
            
            response_text = cleanup_result["response"]
            print(f"DEBUG: Cleanup result: {response_text[:200]}...")
        
        # Parse the JSON response from Llama
        import json
        try:
            parsed_response = json.loads(response_text)
            
            # Validate that all required fields are present and not empty
            required_fields = ["python_code", "requirements_txt", "tests_code"]
            missing_fields = []
            empty_fields = []
            
            for field in required_fields:
                if field not in parsed_response:
                    missing_fields.append(field)
                elif not parsed_response[field] or parsed_response[field].strip() == "":
                    empty_fields.append(field)
            
            if missing_fields:
                print(f"DEBUG: Missing required fields: {missing_fields}")
                # Return error response
                return CodeGenResponse(
                    file_name=f"main_example_{request.example_number}.py",
                    python_code=f"ERROR: Missing required fields: {missing_fields}",
                    requirements_txt="",
                    tests_code="",
                    model=result["model"],
                    tokens_used=result["tokens_used"],
                    total_tokens=result["total_tokens"]
                )
            
            if empty_fields:
                print(f"DEBUG: Empty required fields: {empty_fields}")
                # Add warnings to the code
                warning_msg = f"# WARNING: The following fields were empty: {empty_fields}\n"
                python_code = warning_msg + parsed_response.get("python_code", "")
            else:
                python_code = parsed_response.get("python_code", "")
            
            return CodeGenResponse(
                file_name=parsed_response.get("file_name", f"main_example_{request.example_number}.py"),
                python_code=python_code,
                requirements_txt=parsed_response.get("requirements_txt", ""),
                tests_code=parsed_response.get("tests_code", ""),
                model=result["model"],
                tokens_used=result["tokens_used"],
                total_tokens=result["total_tokens"]
            )
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw response
            print(f"DEBUG: JSON decode error. Raw response: {response_text[:500]}...")
            return CodeGenResponse(
                file_name=f"main_example_{request.example_number}.py",
                python_code=response_text,
                requirements_txt="",
                tests_code="",
                model=result["model"],
                tokens_used=result["tokens_used"],
                total_tokens=result["total_tokens"]
            )
        
    except Exception as e:
        print(f"DEBUG: Exception in /code_gen: {str(e)}")
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

@app.post("/code_gen/test", response_model=CodeGenResponse)
async def test_code_generation():
    """Test endpoint for code generation with a simple prompt"""
    try:
        # Simple test prompt
        test_prompt = "Create a simple Python function that adds two numbers and returns the result."
        
        print(f"DEBUG: Testing with simple prompt: {test_prompt}")
        
        result = llama_service.text_chat_with_response_format(
            system_prompt=PAPER_TO_CODE_SYSTEM_PROMPT,
            user_message=test_prompt,
            model="Llama-4-Maverick-17B-128E-Instruct-FP8",
            max_tokens=4096,
            temperature=0.3
        )
        
        print(f"DEBUG: Test result: {result}")
        
        # Check if the response is empty
        if not result.get("response", "").strip():
            print("DEBUG: Empty response from Llama API in test")
            return CodeGenResponse(
                file_name="test_example.py",
                python_code="# ERROR: The test prompt was too complex for the model to process.",
                requirements_txt="",
                tests_code="",
                model=result["model"],
                tokens_used=result["tokens_used"],
                total_tokens=result["total_tokens"]
            )
        
        # If the response contains MessageTextContentItem wrapper, try to extract clean JSON
        response_text = result["response"]
        if "MessageTextContentItem" in response_text:
            print("DEBUG: Detected MessageTextContentItem wrapper, attempting to extract clean JSON")
            # Try to extract the actual JSON content
            if "text='" in response_text:
                start = response_text.find("text='") + 6
                end = response_text.rfind("')")
                if start > 5 and end > start:
                    response_text = response_text[start:end]
        
        # Try to clean up the response if it's not pure JSON
        if not response_text.strip().startswith('{'):
            # Add a follow-up instruction to get clean JSON
            cleanup_prompt = "Please provide ONLY the JSON object with the required fields (file_name, python_code, requirements_txt, tests_code). Do not include any additional text, explanations, or wrappers. Return only valid JSON."
            
            cleanup_result = llama_service.text_chat_with_system_prompt(
                system_prompt="You are a JSON formatter. Return only valid JSON objects without any additional text or wrappers.",
                user_message=f"Original response: {response_text}\n\n{cleanup_prompt}",
                model="Llama-4-Maverick-17B-128E-Instruct-FP8",
                max_tokens=2048,
                temperature=0.1
            )
            
            response_text = cleanup_result["response"]
            print(f"DEBUG: Cleanup result: {response_text[:200]}...")
        
        # Parse the JSON response from Llama
        import json
        try:
            parsed_response = json.loads(response_text)
            
            # Validate that all required fields are present and not empty
            required_fields = ["python_code", "requirements_txt", "tests_code"]
            missing_fields = []
            empty_fields = []
            
            for field in required_fields:
                if field not in parsed_response:
                    missing_fields.append(field)
                elif not parsed_response[field] or parsed_response[field].strip() == "":
                    empty_fields.append(field)
            
            if missing_fields:
                print(f"DEBUG: Missing required fields: {missing_fields}")
                # Return error response
                return CodeGenResponse(
                    file_name="test_example.py",
                    python_code=f"ERROR: Missing required fields: {missing_fields}",
                    requirements_txt="",
                    tests_code="",
                    model=result["model"],
                    tokens_used=result["tokens_used"],
                    total_tokens=result["total_tokens"]
                )
            
            if empty_fields:
                print(f"DEBUG: Empty required fields: {empty_fields}")
                # Add warnings to the code
                warning_msg = f"# WARNING: The following fields were empty: {empty_fields}\n"
                python_code = warning_msg + parsed_response.get("python_code", "")
            else:
                python_code = parsed_response.get("python_code", "")
            
            return CodeGenResponse(
                file_name=parsed_response.get("file_name", "test_example.py"),
                python_code=python_code,
                requirements_txt=parsed_response.get("requirements_txt", ""),
                tests_code=parsed_response.get("tests_code", ""),
                model=result["model"],
                tokens_used=result["tokens_used"],
                total_tokens=result["total_tokens"]
            )
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw response
            print(f"DEBUG: JSON decode error. Raw response: {response_text[:500]}...")
            return CodeGenResponse(
                file_name="test_example.py",
                python_code=response_text,
                requirements_txt="",
                tests_code="",
                model=result["model"],
                tokens_used=result["tokens_used"],
                total_tokens=result["total_tokens"]
            )
        
    except Exception as e:
        print(f"DEBUG: Exception in test endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in test: {str(e)}")

@app.post("/qa", response_model=QnAResponse)
async def qa_about_paper(request: QnARequest):
    """Answer questions about a specific paper using its content as context"""
    try:
        # First, process the arXiv paper to get its content
        print(f"DEBUG: Processing arXiv paper: {request.arxiv_url}")
        pdf_result = pdf_processor.process_arxiv_paper(request.arxiv_url)
        
        if not pdf_result["success"]:
            raise HTTPException(status_code=400, detail=f"Failed to process arXiv paper: {pdf_result['error']}")
        
        paper_content = pdf_result["paper_content"]
        print(f"DEBUG: Paper content length: {len(paper_content)}")
        
        # Use the existing QnA_Prompt for comprehensive paper analysis
        system_prompt = QnA_Prompt + f"\n\nPaper content:\n{paper_content}\n\nPlease answer all 25 questions above based on the paper content provided."

        # Process the comprehensive analysis with all 25 questions
        print(f"DEBUG: Processing comprehensive paper analysis with 25 questions")
        
        result = llama_service.text_chat_with_system_prompt(
            system_prompt=system_prompt,
            user_message="Please provide a comprehensive analysis answering all 25 questions about this research paper.",
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Extract paper title using LLM for accurate extraction
        title_extraction_prompt = f"""Extract the title of this research paper. Return ONLY the paper title, nothing else.

Paper content:
{paper_content[:2000]}...

Paper title:"""
        
        title_result = llama_service.text_chat_with_system_prompt(
            system_prompt="You are a research paper title extractor. Extract only the main title of the paper, not license text, author names, or other metadata.",
            user_message=title_extraction_prompt,
            model=request.model,
            max_tokens=100,
            temperature=0.1
        )
        
        paper_title = title_result["response"].strip()
        if not paper_title or len(paper_title) > 200:
            paper_title = "Research Paper"  # Fallback
        
        # Format the response to match the expected structure
        answers = [{
            "question": "Comprehensive Paper Analysis (25 Questions)",
            "answer": result["response"]
        }]
        
        return QnAResponse(
            paper_title=paper_title,
            answers=answers,
            model=request.model,
            tokens_used=result["tokens_used"],
            total_tokens=result["total_tokens"]
        )
        
    except Exception as e:
        print(f"DEBUG: Exception in /qa: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error answering questions: {str(e)}")

@app.post("/qa/test", response_model=QnAResponse)
async def test_qa_functionality():
    """Test endpoint for Q&A functionality with a sample paper"""
    try:
        # Sample arXiv URL (Attention is All You Need paper)
        sample_arxiv_url = "https://arxiv.org/abs/1706.03762"
        
        # Create a test request - questions field is no longer used but kept for compatibility
        test_request = QnARequest(
            arxiv_url=sample_arxiv_url,
            questions=[],  # Not used anymore - will use comprehensive 25-question analysis
            model="Llama-4-Maverick-17B-128E-Instruct-FP8",
            max_tokens=4096,  # Increased for comprehensive analysis
            temperature=0.3
        )
        
        # Call the main Q&A endpoint
        return await qa_about_paper(test_request)
        
    except Exception as e:
        print(f"DEBUG: Exception in /qa/test: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in Q&A test: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Navigator Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

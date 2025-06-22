import base64
import json
import fitz  # PyMuPDF
import pdfplumber
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from llama_api_client import LlamaAPIClient
from dotenv import load_dotenv
import os

# Load env vars and initialize API client
load_dotenv()
LLM_API_KEY = os.getenv("LLAMA_API_KEY")
client = LlamaAPIClient(api_key=LLM_API_KEY)

# --- FastAPI App Setup ---
app = FastAPI(
    title="LlamaLens API",
    version="2.0.0",
    description="Advanced research paper analysis with LLaMA 4, featuring section extraction and code generation.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---

class ProcessingConfig(BaseModel):
    outputFormat: str
    mode: str

class DocumentRequest(BaseModel):
    filename: str
    content: str = Field(..., description="Base64 encoded content of the uploaded file.")
    config: ProcessingConfig

class ProcessingResponse(BaseModel):
    summary: Optional[str] = Field(None, description="Overall summary of the paper's contribution and findings.")
    sections: Optional[Dict[str, str]] = Field(None, description="Extracted sections like 'abstract', 'methodology', and 'results'.")
    generatedCode: Optional[str] = Field(None, description="Python code generated based on the paper's methodology.")
    tablesAnalysis: Optional[str] = Field(None, description="The AI's analysis of data tables found in the document.")

# --- Helper Functions ---

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extracts text content from PDF bytes using PyMuPDF."""
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            return "".join(page.get_text() for page in doc)
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        raise HTTPException(status_code=400, detail="Failed to parse the provided PDF file.")

def extract_tables_as_text(pdf_bytes: bytes) -> str:
    """Extracts all tables from a PDF and formats them as markdown strings."""
    all_tables_text = ""
    try:
        with pdfplumber.open(pdf_bytes) as pdf:
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if not tables:
                    continue
                
                all_tables_text += f"--- Page {i+1} Tables ---\n\n"
                for j, table in enumerate(tables):
                    if not table: continue
                    # Convert table to markdown format
                    header = " | ".join(str(cell) for cell in table[0])
                    separator = " | ".join(["---"] * len(table[0]))
                    body = "\n".join([" | ".join(str(cell) for cell in row) for row in table[1:]])
                    
                    markdown_table = f"**Table {j+1}**\n{header}\n{separator}\n{body}\n\n"
                    all_tables_text += markdown_table
    except Exception as e:
        print(f"Warning: Could not extract tables from PDF: {e}")
        return "" # Return empty string on failure, not a critical error
    return all_tables_text

def generate_analysis_prompt(document_text: str, tables_text: str) -> str:
    """Creates a prompt for a multi-stage analysis of a research paper."""
    json_schema = {
        "summary": "A concise summary of the paper's main contributions, methodology, and key results.",
        "sections": {
            "abstract": "The full, extracted abstract of the paper.",
            "methodology": "A detailed explanation of the methodology, algorithm, or core techniques described.",
            "results": "A summary of the key findings, experimental results, or evaluation metrics."
        },
        "generatedCode": "A functional Python code implementation based on the 'methodology' section. The code should be complete and runnable if possible.",
        "tablesAnalysis": "If tables were found, provide a detailed analysis and interpretation of the data presented in them. If no tables were found, this should be null."
    }

    prompt_sections = [
        "Analyze the following research paper. Your task is to perform a comprehensive analysis and structure your output as a valid JSON object.",
        "**Document Text:**",
        "---",
        document_text[:10000], # Keep text context reasonable
        "---"
    ]

    if tables_text:
        prompt_sections.extend([
            "**Extracted Tables:**",
            "---",
            tables_text[:4000], # Keep table context reasonable
            "---"
        ])
        
    prompt_sections.extend([
        "**Instructions:**",
        "1.  **Summarize:** Create a concise summary of the paper's main contributions and findings.",
        "2.  **Extract Sections:** Identify and extract the content for the 'abstract', 'methodology', and 'results' sections. If a section is not clearly present, provide the most relevant information.",
        "3.  **Analyze Tables:** If table data is provided above, analyze it and summarize its significance.",
        "4.  **Generate Code:** Based on the extracted methodology, write a functional Python code snippet.",
        "\n**Output Format:**",
        "You MUST output a single, valid JSON object that conforms exactly to the following schema. Do not include any explanatory text, markdown formatting, or notes outside of the JSON structure.",
        "\n**CRITICAL:** All string values within the JSON, especially in `generatedCode`, MUST be properly escaped. For example, backslashes (\\\\) and double quotes (\") must be escaped (e.g., \"my string with a \\\\ backslash and a \\\" quote.\").",
        "\n**JSON Schema:**",
        json.dumps(json_schema, indent=2)
    ])

    return "\n".join(prompt_sections)

# --- API Routes ---

@app.post("/process-document", response_model=ProcessingResponse)
async def process_document(request: DocumentRequest):
    try:
        # 1. Decode and extract content from the uploaded file
        pdf_bytes = base64.b64decode(request.content)
        document_text = extract_text_from_pdf_bytes(pdf_bytes)
        tables_text = extract_tables_as_text(pdf_bytes)
        
        # 2. Generate the detailed analysis prompt
        prompt = generate_analysis_prompt(document_text, tables_text)

        # 3. Call the LLaMA 4 API
        response = client.chat.completions.create(
            model="Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=4096,
            temperature=0.3,
        )

        # 4. Parse the structured JSON response from the model
        raw_content = response.completion_message.content.text
        
        try:
            # Aggressively clean and extract the JSON object from the model's response.
            # This handles cases where the model wraps the JSON in markdown or adds extra text.
            json_str = raw_content.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:-3].strip()
            
            # Find the start and end of the main JSON object
            start_index = json_str.find('{')
            end_index = json_str.rfind('}')
            
            if start_index != -1 and end_index != -1 and end_index > start_index:
                json_str = json_str[start_index : end_index + 1]
            
            parsed_data = json.loads(json_str)
            
            # 5. Return the structured response
            return ProcessingResponse(
                summary=parsed_data.get("summary"),
                sections=parsed_data.get("sections"),
                generatedCode=parsed_data.get("generatedCode"),
                tablesAnalysis=parsed_data.get("tablesAnalysis"),
            )
            
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing model response: {e}\nRaw content: {raw_content}")
            # Return the raw content for debugging on the frontend instead of a 500 error.
            return ProcessingResponse(
                summary=f"Error: Failed to parse JSON response from AI. Raw output below:\n\n{raw_content}"
            )

    except HTTPException as e:
        raise e  # Re-raise known HTTP exceptions
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during document processing.")

@app.get("/health")
async def health_check():
    return {"status": "ok", "model": "LlamaLens v2.0"}

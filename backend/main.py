import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from llama_api_client import LlamaAPIClient
from dotenv import load_dotenv
import os

# Load env vars
load_dotenv()
LLM_API_KEY = os.getenv("LLAMA_API_KEY")

# Init LLaMA API Client
client = LlamaAPIClient(api_key=LLM_API_KEY)

# FastAPI app
app = FastAPI(
    title="LLaMA 4 Analyzer API",
    version="1.0.0",
    description="Backend for document analysis with LLaMA 4"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request/Response Models ---

class SectionResult(BaseModel):
    title: str
    content: str
    reasoning: str

class ProcessingConfig(BaseModel):
    outputFormat: str
    mode: str

class DocumentRequest(BaseModel):
    filename: str
    content: Optional[str] = None
    config: ProcessingConfig

class ProcessingResponse(BaseModel):
    summary: Optional[str] = None
    generatedCode: Optional[str] = None
    sections: Optional[List[SectionResult]] = None

# --- Routes ---

def generate_prompt(request: DocumentRequest) -> str:
    """Generates a detailed prompt asking for a structured JSON response."""
    
    json_schema = {
        "summary": "string (one-paragraph summary of the document, only for STATIC mode)",
        "sections": [{
            "title": "string (logical title for this section)",
            "content": "string (a summary of this section's content)",
            "reasoning": "string (AI reasoning for why this section is important)"
        }],
        "generatedCode": f"string (a relevant, functional code snippet in {request.config.outputFormat.upper()} based on the document's content)"
    }

    if request.config.mode == "static":
        del json_schema["sections"]
        task = "Provide a one-paragraph summary and generate relevant starter code."
    else: # live mode
        del json_schema["summary"]
        task = "Split the document into logical sections with content summaries and reasoning, and also generate relevant starter code."

    return f"""
Analyze the document titled "{request.filename}". Your task is: {task}

You MUST output a valid JSON object. Do not include any text, notes, or formatting outside of the JSON object.
The JSON object must conform to this structure:
{json.dumps(json_schema, indent=2)}
"""

@app.post("/process-document", response_model=ProcessingResponse)
async def process_document(request: DocumentRequest):
    try:
        prompt = generate_prompt(request)

        response = client.chat.completions.create(
            model="Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=2048,
            temperature=0.4,
        )

        # Correctly access the text content from the response object
        raw_content = response.completion_message.content.text
        
        # Clean and parse the JSON response from the model
        try:
            # Remove potential markdown code block fences
            if raw_content.strip().startswith("```json"):
                raw_content = raw_content.strip()[7:-3]
            
            parsed_data = json.loads(raw_content)
            
            # Create Pydantic models from the parsed data
            sections_data = parsed_data.get("sections")
            sections = [SectionResult(**s) for s in sections_data] if sections_data else None

            return ProcessingResponse(
                summary=parsed_data.get("summary"),
                generatedCode=parsed_data.get("generatedCode"),
                sections=sections
            )
            
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing model response: {e}")
            print(f"Raw model response received: {raw_content}")
            raise HTTPException(status_code=500, detail="Failed to parse the structured response from the AI model.")

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "ok", "model": "LLaMA 4"}

# this file we will use to to create a fast api for the response generation
# we will use the llama api 4 to generate the response

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llama_api_client import LlamaAPIClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Navigator Backend",
    description="Backend API for AI Navigator using Llama API",
    version="0.1.0"
)

# Initialize Llama API client
client = LlamaAPIClient()

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    model: str = "Llama-4-Maverick-17B-128E-Instruct-FP8"
    max_tokens: int = 1024
    temperature: float = 0.7

class ChatResponse(BaseModel):
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
    """Generate a response using Llama API"""
    try:
        # Make API call to Llama
        response = client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": "user", "content": request.message}
            ],
            max_completion_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        
        # Extract response data - simplified approach
        content = str(response.completion_message.content)
        
        # Get token metrics
        total_tokens = 0
        completion_tokens = 0
        if hasattr(response, 'metrics') and response.metrics:
            for metric in response.metrics:
                if metric.metric == "num_total_tokens":
                    total_tokens = int(metric.value)
                elif metric.metric == "num_completion_tokens":
                    completion_tokens = int(metric.value)
        
        return ChatResponse(
            response=content,
            model=request.model,
            tokens_used=completion_tokens,
            total_tokens=total_tokens
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Navigator Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

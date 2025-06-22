from llama_api_client import LlamaAPIClient
from dotenv import load_dotenv
import os
from typing import List, Optional, Dict, Any

# Load environment variables from .env file
load_dotenv()

class LlamaAPIService:
    def __init__(self):
        self.client = LlamaAPIClient()
        self.default_model = "Llama-4-Maverick-17B-128E-Instruct-FP8"
        self.default_max_tokens = 1024
        self.default_temperature = 0.7
    
    def text_chat(self, message: str, model: Optional[str] = None, 
                  max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> Dict[str, Any]:
        """Generate text response using Llama API"""
        model = model or self.default_model
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature or self.default_temperature
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": message}
            ],
            max_completion_tokens=max_tokens,
            temperature=temperature,
        )
        
        return self._extract_response_data(response, model)
    
    def text_chat_with_system_prompt(self, system_prompt: str, user_message: str, 
                                   model: Optional[str] = None, max_tokens: Optional[int] = None, 
                                   temperature: Optional[float] = None) -> Dict[str, Any]:
        """Generate text response using Llama API with custom system prompt"""
        model = model or self.default_model
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature or self.default_temperature
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_completion_tokens=max_tokens,
            temperature=temperature
        )
        
        return self._extract_response_data(response, model)
    
    def text_chat_with_response_format(self, system_prompt: str, user_message: str, 
                                     model: Optional[str] = None, max_tokens: Optional[int] = None, 
                                     temperature: Optional[float] = None) -> Dict[str, Any]:
        """Generate text response using Llama API with structured output via system prompt"""
        model = model or self.default_model
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature or self.default_temperature
        
        # Combine system prompt with user message
        combined_prompt = f"{system_prompt}\n\nUser Request: {user_message}"
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": combined_prompt}
            ],
            max_completion_tokens=max_tokens,
            temperature=temperature,
        )
        
        return self._extract_response_data(response, model)
    
    def multimodal_chat(self, message: str, image_urls: List[str], 
                       model: Optional[str] = None, max_tokens: Optional[int] = None, 
                       temperature: Optional[float] = None) -> Dict[str, Any]:
        """Generate multimodal response using Llama API with images"""
        model = model or self.default_model
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature or self.default_temperature
        
        # Build content array
        content = [
            {
                "type": "text",
                "text": message,
            }
        ]
        
        # Add image URLs
        for image_url in image_urls:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                },
            })
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": content
                },
            ],
            max_completion_tokens=max_tokens,
            temperature=temperature,
        )
        
        return self._extract_response_data(response, model)
    
    def multimodal_chat_with_system_prompt(self, system_prompt: str, user_message: str, 
                                         image_urls: List[str], model: Optional[str] = None, 
                                         max_tokens: Optional[int] = None, 
                                         temperature: Optional[float] = None) -> Dict[str, Any]:
        """Generate multimodal response using Llama API with custom system prompt and images"""
        model = model or self.default_model
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature or self.default_temperature
        
        # Build content array
        content = [
            {
                "type": "text",
                "text": user_message,
            }
        ]
        
        # Add image URLs
        for image_url in image_urls:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                },
            })
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": content
                },
            ],
            max_completion_tokens=max_tokens,
            temperature=temperature,
        )
        
        return self._extract_response_data(response, model)
    
    def _extract_response_data(self, response, model: str) -> Dict[str, Any]:
        """Extract response data and metrics from Llama API response"""
        # Extract response content - handle different response formats
        if hasattr(response.completion_message, 'content'):
            if isinstance(response.completion_message.content, str):
                content = response.completion_message.content
            elif hasattr(response.completion_message.content, 'text'):
                content = response.completion_message.content.text
            else:
                content = str(response.completion_message.content)
        else:
            content = str(response.completion_message)
        
        # Get token metrics
        total_tokens = 0
        completion_tokens = 0
        if hasattr(response, 'metrics') and response.metrics:
            for metric in response.metrics:
                if metric.metric == "num_total_tokens":
                    total_tokens = int(metric.value)
                elif metric.metric == "num_completion_tokens":
                    completion_tokens = int(metric.value)
        
        return {
            "response": content,
            "model": model,
            "tokens_used": completion_tokens,
            "total_tokens": total_tokens
        }

# Create a global instance for easy import
llama_service = LlamaAPIService()

# Convenience functions for backward compatibility
def text_chat(message: str, **kwargs) -> Dict[str, Any]:
    """Convenience function for text chat"""
    return llama_service.text_chat(message, **kwargs)

def multimodal_chat(message: str, image_urls: List[str], **kwargs) -> Dict[str, Any]:
    """Convenience function for multimodal chat"""
    return llama_service.multimodal_chat(message, image_urls, **kwargs)

def text_chat_with_system_prompt(system_prompt: str, user_message: str, **kwargs) -> Dict[str, Any]:
    """Convenience function for text chat with system prompt"""
    return llama_service.text_chat_with_system_prompt(system_prompt, user_message, **kwargs)

def text_chat_with_response_format(system_prompt: str, user_message: str, **kwargs) -> Dict[str, Any]:
    """Convenience function for text chat with response_format parameter"""
    return llama_service.text_chat_with_response_format(system_prompt, user_message, **kwargs)

def multimodal_chat_with_system_prompt(system_prompt: str, user_message: str, image_urls: List[str], **kwargs) -> Dict[str, Any]:
    """Convenience function for multimodal chat with system prompt"""
    return llama_service.multimodal_chat_with_system_prompt(system_prompt, user_message, image_urls, **kwargs)

# Test functions for standalone testing
def test_text_chat(message="Hello, how are you?"):
    """Test text-only chat"""
    print("=== Testing Text-only Chat ===")
    result = text_chat(message)
    print("Text Response:", result["response"])
    print()

def test_multimodal_chat(message: str, image_urls: List[str]):
    """Test multimodal chat with images"""
    print("=== Testing Multimodal Chat with Images ===")
    result = multimodal_chat(message, image_urls)
    print("Multimodal Response:", result["response"])

def test_paper_to_code(paper_content: str, example_number: int = 1):
    """Test paper to code generation"""
    print("=== Testing Paper to Code Generation ===")
    
    # Import the system prompt from main.py
    from main import PAPER_TO_CODE_SYSTEM_PROMPT
    
    user_prompt = f"""Please analyze the following research paper content and generate Python code implementation.

Paper Content:
{paper_content}

Example Number: {example_number}

Please provide the implementation in the exact JSON format specified in the system prompt."""

    result = text_chat_with_system_prompt(
        system_prompt=PAPER_TO_CODE_SYSTEM_PROMPT,
        user_message=user_prompt,
        max_tokens=4096,
        temperature=0.3
    )
    print("Code Generation Response:", result["response"])

if __name__ == "__main__":
    # Test text-only chat
    test_text_chat()
    
    # Test multimodal chat with sample images
    sample_image_urls = [
        "https://upload.wikimedia.org/wikipedia/commons/2/2e/Lama_glama_Laguna_Colorada_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/1/12/Llamas%2C_Laguna_Milluni_y_Nevado_Huayna_Potos%C3%AD_%28La_Paz_-_Bolivia%29.jpg"
    ]
    
    test_multimodal_chat(
        message="What do these two images have in common?",
        image_urls=sample_image_urls
    )
    
    # Test paper to code with a simple example
    sample_paper_content = """
    Algorithm 1: Simple Linear Regression
    
    Input: Training data (X, y) where X is a matrix of features and y is the target vector
    Output: Coefficients w and bias b
    
    1. Initialize w = 0, b = 0
    2. For each iteration:
       a. Compute predictions: y_pred = X * w + b
       b. Compute gradients: dw = (2/n) * X^T * (y_pred - y), db = (2/n) * sum(y_pred - y)
       c. Update parameters: w = w - learning_rate * dw, b = b - learning_rate * db
    3. Return w, b
    """
    
    test_paper_to_code(sample_paper_content, 1)
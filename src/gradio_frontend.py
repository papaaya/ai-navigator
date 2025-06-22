import os
import requests
import json
import time
import gradio as gr
from typing import List, Dict, Any

# FastAPI backend URL
FASTAPI_URL = "http://localhost:8001"

class GradioFrontend:
    def __init__(self):
        self.paper_content = {"text": ""}
        self.backend_url = FASTAPI_URL
    
    def process_arxiv_paper(self, arxiv_url: str, progress=gr.Progress()) -> str:
        """Process arXiv paper using FastAPI backend"""
        try:
            progress(0.1, "Sending request to backend...")
            
            # Call FastAPI backend to process the paper
            response = requests.post(
                f"{self.backend_url}/pdf/process",
                json={"arxiv_url": arxiv_url},
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code != 200:
                return f"Error: {response.status_code} - {response.text}"
            
            result = response.json()
            
            if not result["success"]:
                return result["error"]
            
            # Store paper content for chat
            self.paper_content["text"] = result["paper_content"]
            
            progress(1.0, "Ready for chat!")
            return f"Total {result['total_word_count']} words and {result['num_references']} references ingested. You can now chat about the paper and citations."
            
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The paper might be too large or the server is busy."
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to backend server. Make sure the FastAPI server is running on localhost:8001"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat_with_paper(self, message: str, history: List[List[str]]) -> tuple:
        """Chat about the paper using FastAPI backend"""
        if not message or not self.paper_content["text"]:
            return history, ""
        
        # Append user message immediately
        history.append([message, ""])
        
        try:
            # Call FastAPI backend for paper chat
            response = requests.post(
                f"{self.backend_url}/paper/chat",
                json={
                    "message": message,
                    "paper_content": self.paper_content["text"]
                },
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = f"Error: {response.status_code} - {response.text}"
                history[-1][1] = error_msg
                return history, ""
            
            result = response.json()
            full_response = result["response"]
            
            # Update the last message in history
            history[-1][1] = full_response
            
            return history, ""
            
        except requests.exceptions.Timeout:
            error_msg = "Error: Request timed out. Please try again."
            history[-1][1] = error_msg
            return history, ""
        except requests.exceptions.ConnectionError:
            error_msg = "Error: Cannot connect to backend server. Make sure the FastAPI server is running."
            history[-1][1] = error_msg
            return history, ""
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            history[-1][1] = error_msg
            return history, ""
    
    def clear_chat_history(self) -> tuple:
        """Clear chat history"""
        return [], ""
    
    def create_interface(self):
        """Create the Gradio interface"""
        with gr.Blocks(css=".orange-button {background-color: #FF7C00 !important; color: white;}") as demo:
            gr.Markdown("# Research Analyzer - FastAPI Backend")
            gr.Markdown("This interface uses the FastAPI backend for PDF processing and paper analysis.")
            
            with gr.Column():
                input_text = gr.Textbox(
                    label="ArXiv URL", 
                    placeholder="https://arxiv.org/abs/1706.03762v7"
                )
                status_text = gr.Textbox(
                    label="Status", 
                    interactive=False,
                    placeholder="Enter an arXiv URL and click Ingest to process the paper"
                )
                submit_btn = gr.Button("Ingest", elem_classes="orange-button")
                submit_btn.click(
                    fn=self.process_arxiv_paper, 
                    inputs=input_text, 
                    outputs=status_text
                )
                
                gr.Markdown("## Chat with Llama")
                chatbot = gr.Chatbot(
                    label="Chat History",
                    height=400
                )
                
            with gr.Row():
                msg = gr.Textbox(
                    label="Ask about the paper", 
                    scale=5,
                    placeholder="Ask questions about the ingested paper..."
                )
                submit_chat_btn = gr.Button("➤", elem_classes="orange-button", scale=1)
                
            submit_chat_btn.click(
                self.chat_with_paper, 
                [msg, chatbot], 
                [chatbot, msg]
            )
            msg.submit(
                self.chat_with_paper, 
                [msg, chatbot], 
                [chatbot, msg]
            )
            
            # Clear button
            clear_btn = gr.Button("Clear Chat", elem_classes="orange-button")
            clear_btn.click(
                self.clear_chat_history,
                outputs=[chatbot, msg]
            )
            
            # Backend status
            with gr.Accordion("Backend Status", open=False):
                status_btn = gr.Button("Check Backend Status")
                backend_status = gr.Textbox(label="Backend Status", interactive=False)
                
                def check_backend_status():
                    try:
                        response = requests.get(f"{self.backend_url}/health", timeout=5)
                        if response.status_code == 200:
                            return "✅ Backend is running and healthy"
                        else:
                            return f"❌ Backend error: {response.status_code}"
                    except requests.exceptions.ConnectionError:
                        return "❌ Cannot connect to backend. Make sure FastAPI server is running on localhost:8001"
                    except Exception as e:
                        return f"❌ Error: {str(e)}"
                
                status_btn.click(
                    check_backend_status,
                    outputs=backend_status
                )
        
        return demo

def main():
    """Main function to launch the Gradio interface"""
    frontend = GradioFrontend()
    demo = frontend.create_interface()
    
    print("Starting Gradio frontend...")
    print("Make sure the FastAPI backend is running on http://localhost:8001")
    print("You can start the backend with: python src/main.py")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )

if __name__ == "__main__":
    main() 
import os
import requests
import json
import time
import gradio as gr
from gradio.themes import Soft
from typing import List, Dict, Any

# FastAPI backend URL
FASTAPI_URL = "http://localhost:8001"

class GradioFrontend:
    def __init__(self):
        self.paper_content = {"text": ""}
        self.backend_url = FASTAPI_URL
    
    def process_arxiv_paper(self, arxiv_url: str, progress=gr.Progress()) -> tuple:
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
                error_msg = f"Error: {response.status_code} - {response.text}"
                return error_msg, gr.update(interactive=False)
            
            result = response.json()
            
            if not result["success"]:
                return result["error"], gr.update(interactive=False)
            
            # Store paper content for chat
            self.paper_content["text"] = result["paper_content"]
            
            progress(1.0, "Ready to generate code!")
            status_message = f"Total {result['total_word_count']} words and {result['num_references']} references ingested. You can now generate code."
            return status_message, gr.update(interactive=True)
            
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The paper might be too large or the server is busy.", gr.update(interactive=False)
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to backend server. Make sure the FastAPI server is running on localhost:8001", gr.update(interactive=False)
        except Exception as e:
            return f"Error: {str(e)}", gr.update(interactive=False)

    def generate_code(self, progress=gr.Progress()) -> tuple:
        """Generate code from the paper content using FastAPI backend"""
        if not self.paper_content["text"]:
            return "Please process a paper first.", "", "", ""

        try:
            progress(0.1, "Sending request to code generation endpoint...")

            # Format paper content in one line with proper delimiters
            formatted_content = self.paper_content["text"].replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')

            # Debug: Print the request payload
            request_payload = {"paper_content": formatted_content}
            print(f"DEBUG: Sending request payload: {request_payload}")
            print(f"DEBUG: Paper content length: {len(formatted_content)}")

            response = requests.post(
                f"{self.backend_url}/code_gen",
                json=request_payload,
                timeout=600  # 10 minutes timeout for code gen
            )

            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response text: {response.text[:500]}...")  # First 500 chars

            if response.status_code != 200:
                error_msg = f"Error: {response.status_code} - {response.text}"
                return error_msg, "", "", ""

            progress(0.8, "Decoding response...")
            
            try:
                result = response.json()
                
                # Extract the components from the clean JSON response
                python_code = result.get("python_code", "")
                requirements = result.get("requirements_txt", "")
                tests = result.get("tests_code", "")
                
                # Debug: Print what we extracted
                print(f"DEBUG: Frontend extracted - Python code length: {len(python_code)}")
                print(f"DEBUG: Frontend extracted - Requirements length: {len(requirements)}")
                print(f"DEBUG: Frontend extracted - Tests length: {len(tests)}")
                
                return "Code generated successfully!", python_code, requirements, tests
            except json.JSONDecodeError as e:
                print(f"DEBUG: Frontend JSON decode error: {str(e)}")
                print(f"DEBUG: Response text: {response.text[:500]}...")
                return f"Error: Could not decode JSON from response. {str(e)}", response.text, "", ""

        except requests.exceptions.Timeout:
            return "Error: Request timed out. Code generation is taking too long.", "", "", ""
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to backend server.", "", "", ""
        except Exception as e:
            return f"Error: {str(e)}", "", "", ""

    def create_interface(self):
        """Create the Gradio interface"""
        with gr.Blocks(theme=Soft(), css=".gradio-container {max-width: 960px !important; margin: auto !important;}") as demo:
            gr.Markdown("# CICK - Cursor but In Context knowledge")
            gr.Markdown("Enter an arXiv URL to process a research paper and generate Python code implementation.")
            
            with gr.Row():
                with gr.Column(scale=2):
                    arxiv_input = gr.Textbox(
                        label="ArXiv URL", 
                        placeholder="e.g., https://arxiv.org/abs/1706.03762"
                    )
                    status_output = gr.Textbox(
                        label="Status", 
                        interactive=False,
                        placeholder="Status will be shown here..."
                    )
                    with gr.Row():
                        ingest_button = gr.Button("Ingest Paper", variant="secondary")
                        generate_button = gr.Button("Generate Code", variant="primary", interactive=False)

            with gr.Accordion("Generated Code", open=True):
                python_output = gr.Code(label="Python Code", language="python", interactive=False)

            ingest_button.click(
                fn=self.process_arxiv_paper,
                inputs=arxiv_input,
                outputs=[status_output, generate_button]
            )

            generate_button.click(
                fn=self.generate_code,
                inputs=None,
                outputs=[status_output, python_output],
                api_name="generate_code"
            )

            # Backend status check
            with gr.Accordion("Backend Status", open=False):
                status_btn = gr.Button("Check Backend Status")
                backend_status = gr.Textbox(label="Backend Status", interactive=False)
                
                def check_backend_status():
                    try:
                        response = requests.get(f"{self.backend_url}/", timeout=5)
                        if response.status_code == 200:
                            return "✅ Backend is running."
                        else:
                            return f"❌ Backend returned status {response.status_code}"
                    except requests.exceptions.ConnectionError:
                        return "❌ Cannot connect to backend. Make sure FastAPI server is running."
                    except Exception as e:
                        return f"❌ Error: {str(e)}"
                
                status_btn.click(
                    fn=check_backend_status,
                    inputs=None,
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
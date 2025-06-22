import os
import requests
import json
import time
import io
import re
import PyPDF2
from typing import List, Dict, Any, Optional, Tuple
from llama_api_caller import llama_service

class PDFProcessor:
    def __init__(self):
        self.download_dir = "downloads"
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
    
    def download_pdf(self, url: str, save_path: Optional[str] = None) -> Optional[bytes]:
        """Download PDF from URL"""
        if url is None or 'arxiv.org' not in url:
            return None
        try:
            response = requests.get(url)
            response.raise_for_status()
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
            return response.content
        except Exception as e:
            print(f"Error downloading PDF: {e}")
            return None

    def extract_arxiv_pdf_url(self, arxiv_url: str) -> Optional[str]:
        """Extract PDF URL from arXiv URL"""
        # Check if URL is already in PDF format
        if 'arxiv.org/pdf/' in arxiv_url:
            return arxiv_url
        
        # Extract arxiv_id from different URL formats
        arxiv_id = None
        if 'arxiv.org/abs/' in arxiv_url:
            arxiv_id = arxiv_url.split('arxiv.org/abs/')[1].split()[0]
        elif 'arxiv.org/html/' in arxiv_url:
            arxiv_id = arxiv_url.split('arxiv.org/html/')[1].split()[0]
        
        if arxiv_id:
            return f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        
        return None

    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            pdf_file = io.BytesIO(pdf_content)
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

    def extract_references_with_llm(self, pdf_content: bytes) -> List[Dict[str, str]]:
        """Extract references from PDF using LLM"""
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_content)
        
        # Truncate if too long
        max_length = 50000
        if len(text) > max_length:
            text = text[:max_length] + "..."

        # First pass: Extract citations
        citations_prompt = f"Extract all the arXiv citations from Reference section of the paper including their title, authors and origins. Paper: {text}"
        
        citations_response = llama_service.text_chat(
            message=citations_prompt,
            temperature=0.3,
            max_tokens=2048
        )
        
        citations = citations_response["response"]
        
        # Second pass: Extract arXiv IDs
        arxiv_extraction_prompt = f"""   
        Extract the arXiv ID from the list of citations provided, including preprint arXiv ID. If there is no arXiv ID presented with the list, skip that citations.
        
        Here are some examples on arXiv ID format:
        1. arXiv preprint arXiv:1607.06450, where 1607.06450 is the arXiv ID.
        2. CoRR, abs/1409.0473, where 1409.0473 is the arXiv ID.

        Then, return a JSON array of objects with 'title' and 'ID' fields strictly in the following format, only return the paper title if it's arXiv ID is extracted:

        Output format: [{{"title": "Paper Title", "ID": "arXiv ID"}}]

        DO NOT return any other text.

        List of citations:
        {citations}
        """

        response = llama_service.text_chat(
            message=arxiv_extraction_prompt,
            temperature=0.3,
            max_tokens=2048
        )
        
        response_json = response["response"]

        # Convert the JSON string to a Python object
        references = []
        try:
            references = json.loads(response_json)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            # Try to extract JSON from the response
            try:
                # Look for JSON pattern in the response
                json_match = re.search(r'\[.*\]', response_json, re.DOTALL)
                if json_match:
                    references = json.loads(json_match.group())
            except:
                print("Could not parse references from response")

        return references

    def is_valid_arxiv_id(self, ref_id: str) -> bool:
        """Check if ref_id is a valid arXiv ID"""
        return bool(re.match(r'^\d{4}\.\d{4,5}$', ref_id) or re.match(r'^\d{7}$', ref_id))

    def download_arxiv_paper_and_citations(self, arxiv_url: str) -> Tuple[Optional[str], int, List[str]]:
        """Download main paper and its references"""
        # Download main paper PDF
        pdf_url = self.extract_arxiv_pdf_url(arxiv_url)
        if not pdf_url:
            return None, 0, []
        
        main_pdf_path = os.path.join(self.download_dir, 'main_paper.pdf')
        main_pdf_content = self.download_pdf(pdf_url, main_pdf_path)
        
        if main_pdf_content is None:
            return None, 0, []

        # Extract references using LLM
        references = self.extract_references_with_llm(main_pdf_content)
        
        # Download reference PDFs
        all_pdf_paths = [main_pdf_path]
        downloaded_references = []
        
        for i, reference in enumerate(references):
            ref_title = reference.get("title", f"reference_{i}")
            ref_id = reference.get("ID")
            if ref_id and self.is_valid_arxiv_id(ref_id):
                ref_url = f'https://arxiv.org/pdf/{ref_id}.pdf'
                ref_pdf_path = os.path.join(self.download_dir, f'{ref_title}.pdf')
                try:
                    if self.download_pdf(ref_url, ref_pdf_path):
                        all_pdf_paths.append(ref_pdf_path)
                        downloaded_references.append(ref_title)
                except Exception as e:
                    print(f"Error downloading {ref_url}: {str(e)}")
        
        # Create a list of all PDF paths
        paths_file = os.path.join(self.download_dir, 'pdf_paths.txt')
        with open(paths_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_pdf_paths))
        
        return paths_file, len(references), downloaded_references

    def ingest_paper_content(self, paths_file: str) -> Tuple[str, int]:
        """Extract text content from all PDFs"""
        total_text = ""
        total_word_count = 0

        with open(paths_file, 'r', encoding='utf-8') as f:
            pdf_paths = f.read().splitlines()

        for i, pdf_path in enumerate(pdf_paths):
            try:
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_content = pdf_file.read()
                    text = self.extract_text_from_pdf(pdf_content)
                    total_text += text + "\n\n"
                    total_word_count += len(text.split())
            except Exception as e:
                print(f"Error processing {pdf_path}: {e}")

        return total_text, total_word_count

    def process_arxiv_paper(self, arxiv_url: str) -> Dict[str, Any]:
        """Complete pipeline to process an arXiv paper"""
        try:
            # Download paper and references
            paths_file, num_references, downloaded_refs = self.download_arxiv_paper_and_citations(arxiv_url)
            
            if paths_file is None:
                return {
                    "success": False,
                    "error": "Invalid URL. Valid example: https://arxiv.org/abs/1706.03762v7"
                }
            
            # Extract text content
            paper_content, total_word_count = self.ingest_paper_content(paths_file)
            
            return {
                "success": True,
                "paper_content": paper_content,
                "total_word_count": total_word_count,
                "num_references": num_references,
                "downloaded_references": downloaded_refs,
                "paths_file": paths_file
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Create a global instance
pdf_processor = PDFProcessor() 
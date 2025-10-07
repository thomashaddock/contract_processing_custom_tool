import re
import requests
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import PyPDF2
import io


class PDFDownloadToolInput(BaseModel):
    """Input schema for PDFDownloadTool."""
    url: str = Field(..., description="The public URL to download the PDF from (Google Drive or Dropbox)")


class PDFDownloadTool(BaseTool):
    name: str = "PDF Download Tool"
    description: str = (
        "Downloads and extracts text content from PDF files hosted on Google Drive or Dropbox. "
        "Accepts public sharing URLs and returns the full text content of the PDF document. "
        "Useful for processing contract documents, legal agreements, and other PDF files from cloud storage."
    )
    args_schema: Type[BaseModel] = PDFDownloadToolInput

    def _run(self, url: str) -> str:
        """Download PDF from URL and extract text content."""
        try:
            # Download the PDF content
            pdf_content = self._download_pdf(url)
            
            if not pdf_content:
                return "Error: Could not download PDF content from the provided URL."
            
            # Extract text from PDF
            text_content = self._extract_text_from_pdf(pdf_content)
            
            if not text_content.strip():
                return "Error: Could not extract text content from the PDF. The file might be image-based or corrupted."
            
            return f"Successfully extracted text from PDF:\n\n{text_content}"
            
        except Exception as e:
            return f"Error processing PDF: {str(e)}"

    def _download_pdf(self, url: str) -> bytes:
        """Download PDF content from various sources."""
        try:
            # Handle Google Drive URLs
            if "drive.google.com" in url:
                return self._download_google_drive_pdf(url)
            
            # Handle Dropbox URLs
            elif "dropbox.com" in url:
                return self._download_dropbox_pdf(url)
            
            # Handle direct PDF URLs
            else:
                return self._download_direct_pdf(url)
                
        except Exception as e:
            raise Exception(f"Failed to download PDF: {str(e)}")

    def _download_google_drive_pdf(self, url: str) -> bytes:
        """Download PDF from Google Drive."""
        # Extract file ID from Google Drive URL
        file_id_match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if not file_id_match:
            raise Exception("Could not extract file ID from Google Drive URL")
        
        file_id = file_id_match.group(1)
        
        # Create direct download URL
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        # Simple download with timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(download_url, headers=headers, allow_redirects=True, timeout=30)
        response.raise_for_status()
        
        return response.content

    def _download_dropbox_pdf(self, url: str) -> bytes:
        """Download PDF from Dropbox."""
        # Convert Dropbox sharing URL to direct download URL
        if "?dl=0" in url:
            download_url = url.replace("?dl=0", "?dl=1")
        elif "?dl=1" not in url:
            download_url = f"{url}?dl=1"
        else:
            download_url = url
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(download_url, headers=headers, allow_redirects=True, timeout=30)
        response.raise_for_status()
        
        return response.content

    def _download_direct_pdf(self, url: str) -> bytes:
        """Download PDF from direct URL."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, allow_redirects=True, timeout=30)
        response.raise_for_status()
        
        return response.content

    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text content from PDF bytes."""
        try:
            # Create a file-like object from the PDF content
            pdf_file = io.BytesIO(pdf_content)
            
            # Create PDF reader
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            text_content = []
            for page_num in range(len(pdf_reader.pages)):
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(f"--- Page {page_num + 1} ---\n{text}")
                except Exception as e:
                    # Skip problematic pages but continue processing
                    continue
            
            return "\n\n".join(text_content)
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
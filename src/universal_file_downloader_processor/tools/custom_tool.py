import re
import requests
from typing import Type, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import PyPDF2
import io


class PDFDownloadToolInput(BaseModel):
    """Input schema for PDFDownloadTool."""
    url: str = Field(..., description="Google Drive or Dropbox sharing URL to download PDF from")


class PDFDownloadTool(BaseTool):
    name: str = "PDF Download Tool"
    description: str = (
        "Downloads and extracts text from PDF files on Google Drive or Dropbox. "
        "Use for processing contract documents and legal agreements from cloud storage."
    )
    args_schema: Type[BaseModel] = PDFDownloadToolInput
    package_dependencies: List[str] = ["requests", "PyPDF2"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Lazy import validation
        try:
            import requests  # noqa: F401
            import PyPDF2  # noqa: F401
        except ImportError as e:
            raise ImportError(
                f"Missing required dependencies for PDFDownloadTool. Install with:\n"
                f"  pip install requests PyPDF2\n"
                f"or\n"
                f"  uv add requests PyPDF2"
            ) from e

    def _run(self, url: str) -> str:
        """Download PDF from Google Drive or Dropbox and extract text content."""
        try:
            pdf_content = self._download_pdf(url)
            text_content = self._extract_text_from_pdf(pdf_content)
            
            if not text_content.strip():
                return "Error: Could not extract text from PDF. File might be image-based."
            
            return f"Successfully extracted text from PDF:\n\n{text_content}"
            
        except requests.RequestException as e:
            return f"Network error downloading PDF: {str(e)}"
        except Exception as e:
            return f"Error processing PDF: {str(e)}"

    def _download_pdf(self, url: str) -> bytes:
        """Download PDF from Google Drive or Dropbox."""
        if "drive.google.com" in url:
            return self._download_google_drive_pdf(url)
        elif "dropbox.com" in url:
            return self._download_dropbox_pdf(url)
        else:
            raise ValueError("Only Google Drive and Dropbox URLs are supported")

    def _download_google_drive_pdf(self, url: str) -> bytes:
        """Download PDF from Google Drive."""
        file_id_match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if not file_id_match:
            raise ValueError("Invalid Google Drive URL format")
        
        file_id = file_id_match.group(1)
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(download_url, headers=headers, allow_redirects=True, timeout=30)
        response.raise_for_status()
        
        return response.content

    def _download_dropbox_pdf(self, url: str) -> bytes:
        """Download PDF from Dropbox."""
        download_url = url.replace("?dl=0", "?dl=1") if "?dl=0" in url else f"{url}?dl=1"
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(download_url, headers=headers, allow_redirects=True, timeout=30)
        response.raise_for_status()
        
        return response.content


    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text content from PDF bytes."""
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text_content = []
        for page_num in range(len(pdf_reader.pages)):
            try:
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text.strip():
                    text_content.append(f"--- Page {page_num + 1} ---\n{text}")
            except Exception:
                continue  # Skip problematic pages
        
        return "\n\n".join(text_content)

    async def _arun(self, url: str) -> str:
        """Async version of _run - delegates to sync version since requests is thread-safe."""
        return self._run(url)
import os
import sys
import PyPDF2
from pdf2image import convert_from_path
import tempfile
from PIL import Image
import cv2
import numpy as np

class PDFHandler:
    def __init__(self, pdf_folder="Lectii"):
        self.pdf_folder = pdf_folder
        self.pdf_files = []
        self.current_file_index = 0
        self.current_pdf = None
        self.current_page = 0
        self.total_pages = 0
        self.page_images = {}  # Cache for rendered pages
        self.scan_folder()
        
    def scan_folder(self):
        """Scan the PDF folder for PDF files"""
        if not os.path.exists(self.pdf_folder):
            os.makedirs(self.pdf_folder)
            
        self.pdf_files = [f for f in os.listdir(self.pdf_folder) 
                          if f.lower().endswith('.pdf')]
        self.pdf_files.sort()
        
    def get_file_list(self):
        """Get list of PDF files"""
        return self.pdf_files
    
    def navigate(self, direction):
        """Navigate in the PDF file list (direction: 1 = next, -1 = previous)"""
        if not self.pdf_files:
            return None
            
        self.current_file_index = (self.current_file_index + direction) % len(self.pdf_files)
        return self.pdf_files[self.current_file_index]
    
    def get_current_file(self):
        """Get the currently selected file"""
        if not self.pdf_files:
            return None
        return self.pdf_files[self.current_file_index]
    
    def open_pdf(self, filename=None):
        """Open the currently selected PDF file or a specific file"""
        if not self.pdf_files:
            return False
            
        if filename is None:
            filename = self.pdf_files[self.current_file_index]
        
        file_path = os.path.join(self.pdf_folder, filename)
        if not os.path.exists(file_path):
            return False
            
        try:
            # Close previous PDF if open
            if self.current_pdf:
                self.current_pdf = None
                
            # Open the PDF file
            self.current_pdf = PyPDF2.PdfReader(file_path)
            self.total_pages = len(self.current_pdf.pages)
            self.current_page = 0
            self.page_images = {}  # Clear the cached pages
            
            return True
        except Exception as e:
            print(f"Error opening PDF file: {e}")
            return False
    
    def close_pdf(self):
        """Close the currently open PDF file"""
        if self.current_pdf:
            self.current_pdf = None
            self.current_page = 0
            self.total_pages = 0
            self.page_images = {}
            return True
        return False
    
    def navigate_pdf(self, direction):
        """Navigate in the PDF (direction: 1 = next page, -1 = previous page)"""
        if not self.current_pdf:
            return False
            
        new_page = self.current_page + direction
        if 0 <= new_page < self.total_pages:
            self.current_page = new_page
            return True
        return False
    
    def get_text_from_pdf(self):
        """Extract all text from the current PDF file"""
        if not self.current_pdf:
            return ""
            
        text = ""
        for page in self.current_pdf.pages:
            text += page.extract_text() + "\n\n"
        return text
    
    def get_current_page_image(self, scale=1.0):
        """Get the current page as a PIL Image object"""
        if not self.current_pdf:
            return None
            
        # Check if the page is already cached
        if self.current_page in self.page_images:
            return self.page_images[self.current_page]
            
        try:
            file_path = os.path.join(self.pdf_folder, self.pdf_files[self.current_file_index])
            
            # Try to find Poppler automatically on Windows
            poppler_path = self._find_poppler_path()
            
            # Convert PDF page to image
            with tempfile.TemporaryDirectory() as path:
                images = convert_from_path(file_path, dpi=150, first_page=self.current_page+1, 
                                          last_page=self.current_page+1, poppler_path=poppler_path)
                
                if images:
                    # Resize if needed
                    if scale != 1.0:
                        width, height = images[0].size
                        new_size = (int(width * scale), int(height * scale))
                        resized_img = images[0].resize(new_size, Image.LANCZOS)
                        self.page_images[self.current_page] = resized_img
                        return resized_img
                    else:
                        self.page_images[self.current_page] = images[0]
                        return images[0]
        except Exception as e:
            print(f"Error rendering PDF page: {e}")
            return self._create_placeholder_image()
        
        return None
    
    def _find_poppler_path(self):
        """Try to find Poppler installation on Windows"""
        possible_paths = [
            r"C:\Program Files\poppler\bin",
            r"C:\Program Files (x86)\poppler\bin", 
            r"C:\poppler\bin",
            r"C:\tools\poppler\bin"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _create_placeholder_image(self):
        """Create a placeholder image when PDF rendering fails"""
        # Create a simple placeholder image
        img = Image.new('RGB', (800, 600), color='white')
        return img
    
    def get_current_page_as_cv2(self, target_height=None):
        """Get the current page as a CV2 compatible image (numpy array)"""
        pil_img = self.get_current_page_image()
        if pil_img:
            # Convert PIL to cv2
            cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            
            # Resize to target height if specified
            if target_height:
                h, w = cv_img.shape[:2]
                scale = target_height / h
                new_w = int(w * scale)
                cv_img = cv2.resize(cv_img, (new_w, target_height))
                
            return cv_img
        return None
    
    def create_text_files(self, basename, summary_text, test_text):
        """Create summary and test PDF files with Romanian diacritics support"""
        try:
            from fpdf import FPDF
            
            # Create summary PDF
            summary_pdf = FPDF()
            summary_pdf.add_page()
            
            # Try to use Unicode font for Romanian diacritics
            try:
                summary_pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
                summary_pdf.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf', uni=True)
                font_family = 'DejaVu'
            except:
                # Fallback to Arial if DejaVu is not available
                font_family = 'Arial'
            
            # Use proper font for Romanian support
            summary_pdf.set_font(font_family, 'B', 16)
            summary_pdf.cell(0, 10, f"Rezumat: {basename}", ln=True, align='C')
            summary_pdf.ln(10)
            
            summary_pdf.set_font(font_family, '', 12)
            # Split text into lines and add to PDF
            lines = summary_text.split('\n')
            for line in lines:
                if line.strip():
                    # Handle long lines by wrapping them - now with proper UTF-8 support
                    try:
                        if font_family == 'DejaVu':
                            summary_pdf.multi_cell(0, 8, line)
                        else:
                            # Use transliteration for Romanian characters with Arial
                            line = self._transliterate_romanian(line)
                            summary_pdf.multi_cell(0, 8, line)
                        summary_pdf.ln(2)
                    except:
                        # Fallback to safe characters if font fails
                        safe_line = line.encode('ascii', 'ignore').decode('ascii')
                        summary_pdf.multi_cell(0, 8, safe_line)
                        summary_pdf.ln(2)
            
            summary_path = os.path.join(self.pdf_folder, f"{basename}_rezumat.pdf")
            summary_pdf.output(summary_path)
            
            # Create test PDF
            test_pdf = FPDF()
            test_pdf.add_page()
            
            # Try to use Unicode font for Romanian diacritics
            try:
                test_pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
                test_pdf.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf', uni=True)
                font_family = 'DejaVu'
            except:
                # Fallback to Arial if DejaVu is not available
                font_family = 'Arial'
            
            test_pdf.set_font(font_family, 'B', 16)
            test_pdf.cell(0, 10, f"Test: {basename}", ln=True, align='C')
            test_pdf.ln(10)
            
            test_pdf.set_font(font_family, '', 12)
            # Split text into lines and add to PDF
            lines = test_text.split('\n')
            for line in lines:
                if line.strip():
                    # Handle long lines by wrapping them - now with proper UTF-8 support
                    try:
                        if font_family == 'DejaVu':
                            test_pdf.multi_cell(0, 8, line)
                        else:
                            # Use transliteration for Romanian characters with Arial
                            line = self._transliterate_romanian(line)
                            test_pdf.multi_cell(0, 8, line)
                        test_pdf.ln(2)
                    except:
                        # Fallback to safe characters if font fails
                        safe_line = line.encode('ascii', 'ignore').decode('ascii')
                        test_pdf.multi_cell(0, 8, safe_line)
                        test_pdf.ln(2)
            
            test_path = os.path.join(self.pdf_folder, f"{basename}_test.pdf")
            test_pdf.output(test_path)
            
            return True
            
        except ImportError:
            print("Error: fpdf2 not installed. Installing...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2"])
            return self.create_text_files(basename, summary_text, test_text)
        except Exception as e:
            print(f"Error creating PDF files: {e}")
            # Fallback to text files
            return self.create_text_files_fallback(basename, summary_text, test_text)
    
    def create_text_files_fallback(self, basename, summary_text, test_text):
        """Fallback method to create text files if PDF creation fails"""
        base_path = os.path.join(self.pdf_folder, basename)
        
        # Create summary file
        with open(f"{base_path}_rezumat.txt", 'w', encoding='utf-8') as f:
            f.write(summary_text)
            
        # Create test file
        with open(f"{base_path}_test.txt", 'w', encoding='utf-8') as f:
            f.write(test_text)
            
        return True
        
    def open_text_file(self, filename):
        """Open and read a text file"""
        if not filename.endswith('.txt'):
            return None
            
        file_path = os.path.join(self.pdf_folder, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading text file: {e}")
            return None
    
    def _transliterate_romanian(self, text):
        """Transliterate Romanian diacritics to ASCII characters"""
        # Romanian diacritics mapping
        romanian_chars = {
            'ă': 'a', 'â': 'a', 'î': 'i', 'ș': 's', 'ț': 't',
            'Ă': 'A', 'Â': 'A', 'Î': 'I', 'Ș': 'S', 'Ț': 'T',
            'ş': 's', 'ţ': 't', 'Ş': 'S', 'Ţ': 'T'  # Alternative forms
        }
        
        for romanian_char, ascii_char in romanian_chars.items():
            text = text.replace(romanian_char, ascii_char)
        
        return text 
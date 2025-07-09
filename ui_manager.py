import pygame
import cv2
import numpy as np
import time
import os

class UIManager:
    def __init__(self, width=1280, height=720):
        """Initialize the UI manager with pygame"""
        pygame.init()
        pygame.display.set_caption('EduGesture')
        
        # Set up display
        self.width = width
        self.height = height
        self.display = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Modern color palette
        self.WHITE = (255, 255, 255)
        self.BLACK = (40, 40, 40)
        self.GRAY = (120, 120, 120)
        self.LIGHT_GRAY = (245, 245, 245)
        self.DARK_GRAY = (60, 60, 60)
        self.BLUE = (52, 152, 219)
        self.LIGHT_BLUE = (174, 214, 241)
        self.DARK_BLUE = (41, 128, 185)
        self.GREEN = (46, 204, 113)
        self.DARK_GREEN = (39, 174, 96)
        self.RED = (231, 76, 60)
        self.ORANGE = (230, 126, 34)
        self.PURPLE = (155, 89, 182)
        self.BACKGROUND = (248, 249, 250)
        
        # Fonts
        pygame.font.init()
        self.font_small = pygame.font.SysFont('Arial', 14)
        self.font_medium = pygame.font.SysFont('Arial', 18)
        self.font_large = pygame.font.SysFont('Arial', 24)
        self.font_title = pygame.font.SysFont('Arial', 32, bold=True)
        
        # UI state
        self.current_view = "menu"  # "menu", "document"
        self.selected_file = None
        self.log_messages = []
        self.max_log_messages = 10
        self.last_update = time.time()
        self.show_exit_modal = False
        
        # Layout
        self.camera_preview_rect = pygame.Rect(20, 20, 320, 240)
        self.file_list_rect = pygame.Rect(20, 280, 320, 400)
        self.document_view_rect = pygame.Rect(360, 20, 640, 680)
        self.log_rect = pygame.Rect(1020, 20, 240, 680)
        self.legend_rect = pygame.Rect(20, 680, 980, 30)
        
    def add_log(self, message):
        """Add a message to the log"""
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        self.log_messages.append(f"[{timestamp}] {message}")
        
        # Keep only the last N messages
        if len(self.log_messages) > self.max_log_messages:
            self.log_messages = self.log_messages[-self.max_log_messages:]
    
    def clear_display(self):
        """Clear the display with a modern background"""
        self.display.fill(self.BACKGROUND)
    
    def update_camera_preview(self, frame):
        """Update the camera preview with the latest frame and modern styling"""
        # Draw background with shadow effect
        shadow_rect = pygame.Rect(self.camera_preview_rect.x + 3, self.camera_preview_rect.y + 3, 
                                self.camera_preview_rect.width, self.camera_preview_rect.height)
        pygame.draw.rect(self.display, (200, 200, 200), shadow_rect)
        
        # Draw camera frame border
        pygame.draw.rect(self.display, self.WHITE, self.camera_preview_rect)
        pygame.draw.rect(self.display, self.DARK_GRAY, self.camera_preview_rect, 3)
        
        # Add title bar
        title_rect = pygame.Rect(self.camera_preview_rect.x, self.camera_preview_rect.y, 
                               self.camera_preview_rect.width, 25)
        pygame.draw.rect(self.display, self.GREEN, title_rect)
        title = self.font_small.render("Camera Live", True, self.WHITE)
        title_rect_center = title.get_rect(center=title_rect.center)
        self.display.blit(title, title_rect_center)
        
        # Adjust frame area
        frame_area = pygame.Rect(self.camera_preview_rect.x + 3, self.camera_preview_rect.y + 25, 
                               self.camera_preview_rect.width - 6, self.camera_preview_rect.height - 28)
        
        if frame is None:
            # Draw a placeholder if no camera frame
            pygame.draw.rect(self.display, self.BLACK, frame_area)
            text = self.font_medium.render("Camera nu este disponibila", True, self.WHITE)
            text_rect = text.get_rect(center=frame_area.center)
            self.display.blit(text, text_rect)
            return
            
        # Convert OpenCV BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize to fit the preview area
        frame_resized = cv2.resize(frame_rgb, (frame_area.width, frame_area.height))
        
        # Convert to pygame surface
        surface = pygame.surfarray.make_surface(frame_resized.swapaxes(0, 1))
        
        # Display the frame
        self.display.blit(surface, (frame_area.x, frame_area.y))
        
    def render_file_list(self, files, current_index=0):
        """Render the file list with modern design"""
        # Draw background with shadow effect
        shadow_rect = pygame.Rect(self.file_list_rect.x + 3, self.file_list_rect.y + 3, 
                                self.file_list_rect.width, self.file_list_rect.height)
        pygame.draw.rect(self.display, (200, 200, 200), shadow_rect)
        pygame.draw.rect(self.display, self.WHITE, self.file_list_rect)
        pygame.draw.rect(self.display, self.DARK_GRAY, self.file_list_rect, 2)
        
        # Draw title with modern styling
        title_rect = pygame.Rect(self.file_list_rect.x, self.file_list_rect.y, 
                               self.file_list_rect.width, 35)
        pygame.draw.rect(self.display, self.DARK_BLUE, title_rect)
        title = self.font_large.render("Fisiere disponibile", True, self.WHITE)
        title_rect_center = title.get_rect(center=title_rect.center)
        self.display.blit(title, title_rect_center)
        
        # Draw files with improved styling
        y_offset = 45
        for i, file in enumerate(files):
            # Determine colors based on selection
            if i == current_index:
                bg_color = self.LIGHT_BLUE
                text_color = self.DARK_BLUE
                border_color = self.BLUE
            else:
                bg_color = self.WHITE
                text_color = self.BLACK
                border_color = self.LIGHT_GRAY
            
            # Draw selection background with rounded corners effect
            item_rect = pygame.Rect(
                self.file_list_rect.x + 8, 
                self.file_list_rect.y + y_offset - 3, 
                self.file_list_rect.width - 16, 
                28
            )
            pygame.draw.rect(self.display, bg_color, item_rect)
            pygame.draw.rect(self.display, border_color, item_rect, 1)
            
            # Add file type indicator
            if file.endswith('.pdf'):
                indicator_color = self.RED
                indicator_text = "PDF"
            elif file.endswith('.txt'):
                indicator_color = self.GREEN
                indicator_text = "TXT"
            else:
                indicator_color = self.GRAY
                indicator_text = "???"
                
            # Draw file type indicator
            indicator_rect = pygame.Rect(item_rect.right - 45, item_rect.y + 4, 40, 20)
            pygame.draw.rect(self.display, indicator_color, indicator_rect)
            indicator_surface = self.font_small.render(indicator_text, True, self.WHITE)
            indicator_text_rect = indicator_surface.get_rect(center=indicator_rect.center)
            self.display.blit(indicator_surface, indicator_text_rect)
            
            # Draw file name
            display_name = file[:25] + "..." if len(file) > 25 else file
            text = self.font_medium.render(display_name, True, text_color)
            self.display.blit(text, (self.file_list_rect.x + 15, self.file_list_rect.y + y_offset))
            y_offset += 35
            
            # Stop if we run out of space
            if y_offset > self.file_list_rect.height - 20:
                break
    
    def render_document(self, document_image):
        """Render a document in the document view area"""
        # Draw background
        pygame.draw.rect(self.display, self.WHITE, self.document_view_rect)
        pygame.draw.rect(self.display, self.BLACK, self.document_view_rect, 1)
        
        if document_image is None:
            # No document loaded
            text = self.font_large.render("Niciun document încărcat", True, self.BLACK)
            text_rect = text.get_rect(center=self.document_view_rect.center)
            self.display.blit(text, text_rect)
            return
            
        # Convert OpenCV BGR to RGB
        if len(document_image.shape) == 3 and document_image.shape[2] == 3:
            document_rgb = cv2.cvtColor(document_image, cv2.COLOR_BGR2RGB)
        else:
            document_rgb = document_image
            
        # Scale to fit the document view area while maintaining aspect ratio
        h, w = document_rgb.shape[:2]
        view_ratio = self.document_view_rect.width / self.document_view_rect.height
        img_ratio = w / h
        
        if img_ratio > view_ratio:
            # Image is wider than the view area
            new_w = self.document_view_rect.width
            new_h = int(new_w / img_ratio)
        else:
            # Image is taller than the view area
            new_h = self.document_view_rect.height
            new_w = int(new_h * img_ratio)
            
        document_resized = cv2.resize(document_rgb, (new_w, new_h))
        
        # Convert to pygame surface
        surface = pygame.surfarray.make_surface(document_resized.swapaxes(0, 1))
        
        # Calculate position to center the image
        x = self.document_view_rect.x + (self.document_view_rect.width - new_w) // 2
        y = self.document_view_rect.y + (self.document_view_rect.height - new_h) // 2
        
        # Display the document
        self.display.blit(surface, (x, y))
        
    def render_text_document(self, text, page_num=0, lines_per_page=25):
        """Render a text document in the document view area"""
        # Draw background
        pygame.draw.rect(self.display, self.WHITE, self.document_view_rect)
        pygame.draw.rect(self.display, self.BLACK, self.document_view_rect, 1)
        
        if not text:
            # No text to display
            message = self.font_large.render("Document text gol", True, self.BLACK)
            message_rect = message.get_rect(center=self.document_view_rect.center)
            self.display.blit(message, message_rect)
            return
            
        # Split text into lines
        lines = text.split('\n')
        
        # Calculate total pages
        total_pages = (len(lines) + lines_per_page - 1) // lines_per_page
        
        # Validate page number
        page_num = max(0, min(page_num, total_pages - 1))
        
        # Get lines for current page
        start_line = page_num * lines_per_page
        end_line = min(start_line + lines_per_page, len(lines))
        current_page_lines = lines[start_line:end_line]
        
        # Render lines
        y_offset = self.document_view_rect.y + 20
        for line in current_page_lines:
            # Skip empty lines
            if not line.strip():
                y_offset += 20
                continue
                
            # Render line with wrapping
            words = line.split()
            current_line = ""
            max_width = self.document_view_rect.width - 40
            
            for word in words:
                test_line = current_line + word + " "
                # Test if line exceeds the width
                width = self.font_medium.size(test_line)[0]
                if width > max_width:
                    # Render current line and start a new one
                    text_surface = self.font_medium.render(current_line, True, self.BLACK)
                    self.display.blit(text_surface, (self.document_view_rect.x + 20, y_offset))
                    y_offset += 25
                    current_line = word + " "
                else:
                    current_line = test_line
                    
            # Render the last line
            if current_line:
                text_surface = self.font_medium.render(current_line, True, self.BLACK)
                self.display.blit(text_surface, (self.document_view_rect.x + 20, y_offset))
                y_offset += 25
                
            # Check if we've run out of vertical space
            if y_offset > self.document_view_rect.y + self.document_view_rect.height - 30:
                break
                
        # Render page counter
        page_text = f"Pagina {page_num + 1} din {total_pages}"
        page_surface = self.font_small.render(page_text, True, self.BLACK)
        page_rect = page_surface.get_rect(bottomright=(self.document_view_rect.right - 10, self.document_view_rect.bottom - 10))
        self.display.blit(page_surface, page_rect)
    
    def render_log(self):
        """Render the log messages with modern design"""
        # Draw background with shadow effect
        shadow_rect = pygame.Rect(self.log_rect.x + 3, self.log_rect.y + 3, 
                                self.log_rect.width, self.log_rect.height)
        pygame.draw.rect(self.display, (200, 200, 200), shadow_rect)
        pygame.draw.rect(self.display, self.WHITE, self.log_rect)
        pygame.draw.rect(self.display, self.DARK_GRAY, self.log_rect, 2)
        
        # Draw title with modern styling
        title_rect = pygame.Rect(self.log_rect.x, self.log_rect.y, 
                               self.log_rect.width, 35)
        pygame.draw.rect(self.display, self.PURPLE, title_rect)
        title = self.font_large.render("Status / Log", True, self.WHITE)
        title_rect_center = title.get_rect(center=title_rect.center)
        self.display.blit(title, title_rect_center)
        
        # Draw messages with color coding
        y_offset = 45
        for message in self.log_messages:
            # Determine message color based on content
            if "Eroare" in message or "Error" in message:
                text_color = self.RED
                bg_color = (255, 240, 240)
            elif "✓" in message or "succes" in message:
                text_color = self.GREEN
                bg_color = (240, 255, 240)
            elif "Generare" in message or "Ollama" in message:
                text_color = self.ORANGE
                bg_color = (255, 250, 240)
            else:
                text_color = self.BLACK
                bg_color = None
                
            # Draw message background if needed
            if bg_color:
                msg_rect = pygame.Rect(self.log_rect.x + 5, self.log_rect.y + y_offset - 2, 
                                     self.log_rect.width - 10, 18)
                pygame.draw.rect(self.display, bg_color, msg_rect)
                
            # Truncate long messages
            display_message = message[:35] + "..." if len(message) > 35 else message
            text = self.font_small.render(display_message, True, text_color)
            self.display.blit(text, (self.log_rect.x + 8, self.log_rect.y + y_offset))
            y_offset += 20
            
            # Stop if we run out of space
            if y_offset > self.log_rect.height - 20:
                break
    
    def render_gesture_legend(self):
        """Render the gesture legend at the bottom"""
        # Draw background with gradient effect
        pygame.draw.rect(self.display, (240, 240, 240), self.legend_rect)
        pygame.draw.rect(self.display, (100, 100, 100), self.legend_rect, 2)
        
        # Define gestures with clear text based on current state
        if self.show_exit_modal:
            gestures = [
                "PALMA: Confirma iesire din aplicatie",
                "ORICE ALT GEST: Anuleaza",
                "", "", ""
            ]
            colors = [
                self.RED,         # Red for confirm exit
                self.GREEN,       # Green for cancel
                self.GRAY, self.GRAY, self.GRAY
            ]
        else:
            gestures = [
                "DREAPTA: Inainte",
                "STANGA: Inapoi", 
                "DOUA DEGETE: Genereaza",
                "OK: Deschide",
                "PALMA: Inchide" if self.current_view == "document" else "PALMA: Iesire"
            ]
            
            # Define colors for different gestures
            colors = [
                self.BLUE,        # Blue for navigation
                self.BLUE,        # Blue for navigation
                self.GREEN,       # Green for generate
                self.ORANGE,      # Orange for open
                self.RED          # Red for close/exit
            ]
        
        # Render gestures with colored backgrounds
        x_offset = 15
        for i, gesture in enumerate(gestures):
            if not gesture:  # Skip empty gestures
                x_offset += 190
                continue
                
            # Create colored background for each gesture
            gesture_width = 180
            gesture_rect = pygame.Rect(
                self.legend_rect.x + x_offset - 5,
                self.legend_rect.y + 3,
                gesture_width,
                24
            )
            
            # Draw gesture background
            pygame.draw.rect(self.display, colors[i], gesture_rect)
            pygame.draw.rect(self.display, self.WHITE, gesture_rect, 1)
            
            # Draw gesture text
            text = self.font_small.render(gesture, True, self.WHITE)
            text_rect = text.get_rect(center=gesture_rect.center)
            self.display.blit(text, text_rect)
            
            x_offset += 190
    
    def render_exit_modal(self):
        """Render the exit confirmation modal"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill(self.BLACK)
        self.display.blit(overlay, (0, 0))
        
        # Modal dimensions and position
        modal_width = 500
        modal_height = 200
        modal_x = (self.width - modal_width) // 2
        modal_y = (self.height - modal_height) // 2
        
        modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)
        
        # Draw modal shadow
        shadow_rect = pygame.Rect(modal_x + 5, modal_y + 5, modal_width, modal_height)
        pygame.draw.rect(self.display, (50, 50, 50), shadow_rect)
        
        # Draw modal background
        pygame.draw.rect(self.display, self.WHITE, modal_rect)
        pygame.draw.rect(self.display, self.RED, modal_rect, 4)
        
        # Draw title
        title_rect = pygame.Rect(modal_x, modal_y, modal_width, 50)
        pygame.draw.rect(self.display, self.RED, title_rect)
        title_text = self.font_title.render("Confirmare iesire", True, self.WHITE)
        title_text_rect = title_text.get_rect(center=title_rect.center)
        self.display.blit(title_text, title_text_rect)
        
        # Draw message
        message_y = modal_y + 70
        message_text = self.font_large.render("Sunteti sigur ca doriti sa", True, self.BLACK)
        message_rect = message_text.get_rect(centerx=modal_rect.centerx, y=message_y)
        self.display.blit(message_text, message_rect)
        
        message_text2 = self.font_large.render("inchideti aplicatia?", True, self.BLACK)
        message_rect2 = message_text2.get_rect(centerx=modal_rect.centerx, y=message_y + 30)
        self.display.blit(message_text2, message_rect2)
        
        # Draw instructions
        instruction_y = modal_y + 140
        instruction_text = self.font_medium.render("Folositi gesturile pentru a raspunde:", True, self.DARK_GRAY)
        instruction_rect = instruction_text.get_rect(centerx=modal_rect.centerx, y=instruction_y)
        self.display.blit(instruction_text, instruction_rect)
        
        # Draw gesture options
        option_y = modal_y + 170
        palm_text = self.font_small.render("PALMA = DA", True, self.RED)
        other_text = self.font_small.render("ORICE ALT GEST = NU", True, self.GREEN)
        
        palm_rect = palm_text.get_rect(centerx=modal_rect.centerx - 80, y=option_y)
        other_rect = other_text.get_rect(centerx=modal_rect.centerx + 80, y=option_y)
        
        self.display.blit(palm_text, palm_rect)
        self.display.blit(other_text, other_rect)
    
    def show_exit_confirmation(self):
        """Show the exit confirmation modal"""
        self.show_exit_modal = True
        
    def hide_exit_confirmation(self):
        """Hide the exit confirmation modal"""
        self.show_exit_modal = False
        
    def is_exit_modal_showing(self):
        """Check if exit modal is currently showing"""
        return self.show_exit_modal
    
    def draw(self, camera_frame, files=None, current_file_index=0, document_image=None, 
            text_document=None, text_page=0):
        """Draw the full UI"""
        self.clear_display()
        
        # Draw camera preview
        self.update_camera_preview(camera_frame)
        
        # Draw document or file list based on current view
        if self.current_view == "menu":
            # Draw file list in menu view
            if files:
                self.render_file_list(files, current_file_index)
            else:
                self.render_file_list(["No files found"])
                
            # Draw empty document area
            pygame.draw.rect(self.display, self.WHITE, self.document_view_rect)
            pygame.draw.rect(self.display, self.BLACK, self.document_view_rect, 1)
            text = self.font_large.render("Selectați un document", True, self.BLACK)
            text_rect = text.get_rect(center=self.document_view_rect.center)
            self.display.blit(text, text_rect)
        else:
            # Document view
            if text_document:
                # This is a text document (TXT)
                self.render_text_document(text_document, text_page)
            else:
                # This is an image document (PDF page)
                self.render_document(document_image)
        
        # Draw log and legend
        self.render_log()
        self.render_gesture_legend()
        
        # Draw exit modal if showing
        if self.show_exit_modal:
            self.render_exit_modal()
        
        # Update display
        pygame.display.flip()
        self.clock.tick(self.fps)
        
    def set_view(self, view):
        """Set the current view (menu or document)"""
        self.current_view = view
        
    def get_view(self):
        """Get the current view"""
        return self.current_view
        
    def check_events(self):
        """Check for pygame events and return if quit is requested"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
        return False
        
    def cleanup(self):
        """Clean up pygame resources"""
        pygame.quit() 
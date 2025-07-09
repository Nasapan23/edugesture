import os
import cv2
import numpy as np
import time
import csv
from datetime import datetime

class Stats:
    """Class for tracking and logging application statistics"""
    def __init__(self, log_file="app_stats.csv"):
        self.log_file = log_file
        self.init_log()
        
        # Statistics
        self.gesture_counts = {
            "right": 0,
            "left": 0,
            "two_fingers": 0,
            "ok": 0,
            "palm": 0
        }
        self.navigation_counts = {
            "menu_navigations": 0,
            "document_navigations": 0
        }
        self.ollama_times = []
        
    def init_log(self):
        """Initialize the CSV log file"""
        # Check if file already exists
        file_exists = os.path.isfile(self.log_file)
        
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            
            # Write header only if file doesn't exist
            if not file_exists:
                writer.writerow([
                    'Timestamp', 
                    'Event', 
                    'Value', 
                    'Success', 
                    'Context'
                ])
    
    def log_event(self, event_type, value, success=True, context=""):
        """Log an event to the CSV file"""
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                event_type,
                value,
                success,
                context
            ])
    
    def log_gesture(self, gesture, success=True, context=""):
        """Log a gesture event"""
        if gesture in self.gesture_counts:
            self.gesture_counts[gesture] += 1
        self.log_event("gesture", gesture, success, context)
    
    def log_navigation(self, navigation_type, success=True):
        """Log a navigation event"""
        if navigation_type in self.navigation_counts:
            self.navigation_counts[navigation_type] += 1
        self.log_event("navigation", navigation_type, success)
    
    def log_ollama(self, execution_time, success=True):
        """Log an Ollama execution time"""
        self.ollama_times.append(execution_time)
        self.log_event("ollama", execution_time, success)
    
    def get_stats_summary(self):
        """Get a summary of the collected stats"""
        summary = {
            "gestures": self.gesture_counts,
            "navigations": self.navigation_counts,
            "ollama": {
                "calls": len(self.ollama_times),
                "avg_time": sum(self.ollama_times) / max(1, len(self.ollama_times)),
                "max_time": max(self.ollama_times) if self.ollama_times else 0,
                "min_time": min(self.ollama_times) if self.ollama_times else 0
            }
        }
        return summary


def create_blank_image(width, height, color=(255, 255, 255)):
    """Create a blank image with the specified dimensions"""
    image = np.ones((height, width, 3), dtype=np.uint8)
    image[:] = color
    return image


def text_to_image(text, width=800, height=600, font=cv2.FONT_HERSHEY_SIMPLEX, 
                 font_scale=0.7, color=(0, 0, 0), line_spacing=30):
    """Convert text to an image"""
    # Create blank image
    image = create_blank_image(width, height)
    
    # Split text into lines
    lines = text.split('\n')
    
    # Draw text on image
    y_position = 50
    for line in lines:
        if not line.strip():
            y_position += line_spacing // 2
            continue
            
        # Wrap text if it's too long
        words = line.split()
        wrapped_lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            # Get text size
            (text_width, _), _ = cv2.getTextSize(test_line, font, font_scale, 1)
            
            if text_width > width - 100:
                wrapped_lines.append(current_line)
                current_line = word + " "
            else:
                current_line = test_line
                
        if current_line:
            wrapped_lines.append(current_line)
            
        # Draw wrapped lines
        for wrapped_line in wrapped_lines:
            cv2.putText(image, wrapped_line, (50, y_position), font, font_scale, color, 1)
            y_position += line_spacing
            
            # Check if we've reached the bottom of the image
            if y_position >= height - 50:
                break
                
        if y_position >= height - 50:
            # Add ellipsis to indicate truncated text
            cv2.putText(image, "...", (50, height - 30), font, font_scale, color, 1)
            break
            
    return image


def is_pdf_file(filename):
    """Check if a file is a PDF file"""
    return filename.lower().endswith('.pdf')


def is_text_file(filename):
    """Check if a file is a text file"""
    return filename.lower().endswith('.txt')


def get_file_extension(filename):
    """Get the file extension"""
    _, ext = os.path.splitext(filename)
    return ext.lower()


def get_base_filename(filename):
    """Get the base filename without extension"""
    base, _ = os.path.splitext(filename)
    return base 
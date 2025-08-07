import os
import cv2
import time
import argparse
import threading
from dotenv import load_dotenv
import numpy as np

# Import our modules
from gesture_detector import GestureDetector
from pdf_handler import PDFHandler
from ollama_connector import OllamaConnector
from ui_manager import UIManager
from utils import Stats, is_pdf_file, is_text_file, get_base_filename

# Load environment variables
load_dotenv()

class EduGesture:
    def __init__(self, ollama_host="http://localhost:11434", ollama_model="llama3.2:1b"):
        """Initialize the EduGesture application"""
        # Modules
        self.gesture_detector = GestureDetector()
        self.pdf_handler = PDFHandler()
        self.ollama = OllamaConnector(host=ollama_host, model=ollama_model)
        self.ui = UIManager()
        self.stats = Stats()
        
        # Application state
        self.running = False
        self.camera = None
        self.camera_id = 0
        self.current_gesture = None
        self.current_text = None
        self.text_page = 0
        self.ollama_running = False
        self.shutdown_event = threading.Event()
        
    def init_camera(self):
        """Initialize the camera"""
        try:
            # Release existing camera if open
            if self.camera is not None and self.camera.isOpened():
                self.camera.release()
                
            # Re-initialize camera with DirectShow backend
            time.sleep(0.5)  
            self.camera = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
            time.sleep(0.5)  # Allow camera time to initialize properly
            
            if not self.camera.isOpened():
                self.ui.add_log("Eroare: Camera nu poate fi inițializată")
                return False
            
            # Set properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            # Try to read a test frame
            ret, test_frame = self.camera.read()
            if not ret or test_frame is None:
                self.ui.add_log("Eroare: Nu se poate citi frame de test de la cameră")
                return False
                
            self.ui.add_log(f"Cameră inițializată: {test_frame.shape}")
            return True
        except Exception as e:
            self.ui.add_log(f"Eroare cameră: {e}")
            return False
    
    def handle_menu_gesture(self, gesture):
        """Handle gestures in the menu view"""
        # Handle exit confirmation modal first
        if self.ui.is_exit_modal_showing():
            if gesture == "palm":
                # Confirm exit - close the application
                self.ui.add_log("Aplicatie inchisa de catre utilizator")
                self.running = False
                return
            else:
                # Cancel exit - hide modal
                self.ui.hide_exit_confirmation()
                self.ui.add_log("Iesire anulata")
                return
        
        # Handle palm gesture in menu - show exit confirmation
        if gesture == "palm":
            self.ui.show_exit_confirmation()
            self.ui.add_log("Confirmare iesire - folositi PALMA pentru a confirma")
            return
        
        files = self.pdf_handler.get_file_list()
        current_file = self.pdf_handler.get_current_file()
        
        if not files:
            self.ui.add_log("Nu exista fisiere in directorul Lectii/")
            return
        
        if gesture == "right":
            # Navigate to next file
            next_file = self.pdf_handler.navigate(1)
            self.ui.add_log(f"Selectat: {next_file}")
            self.stats.log_navigation("menu_navigations")
            
        elif gesture == "left":
            # Navigate to previous file
            prev_file = self.pdf_handler.navigate(-1)
            self.ui.add_log(f"Selectat: {prev_file}")
            self.stats.log_navigation("menu_navigations")
            
        elif gesture == "ok":
            # Open the selected file
            current_file = self.pdf_handler.get_current_file()
            if current_file:
                # Check if it's a PDF or TXT file
                if is_pdf_file(current_file):
                    if self.pdf_handler.open_pdf():
                        self.ui.add_log(f"Deschis PDF: {current_file}")
                        self.ui.set_view("document")
                        self.current_text = None
                    else:
                        self.ui.add_log(f"Eroare la deschiderea PDF: {current_file}")
                elif is_text_file(current_file):
                    # Open text file
                    self.current_text = self.pdf_handler.open_text_file(current_file)
                    if self.current_text:
                        self.ui.add_log(f"Deschis Text: {current_file}")
                        self.ui.set_view("document")
                        self.text_page = 0
                    else:
                        self.ui.add_log(f"Eroare la deschiderea Text: {current_file}")
                else:
                    self.ui.add_log(f"Tip fișier nesuportat: {current_file}")
            else:
                self.ui.add_log("Niciun fișier selectat")
                
        elif gesture == "two_fingers" and not self.ollama_running:
            # Generate summary and test with Ollama
            current_file = self.pdf_handler.get_current_file()
            if current_file and is_pdf_file(current_file):
                # Start Ollama processing in a separate thread
                self.ollama_running = True
                self.ui.add_log("Generare cu Ollama începută...")
                
                # Start thread
                threading.Thread(target=self.generate_with_ollama, daemon=True).start()
            else:
                self.ui.add_log("Selectați un fișier PDF pentru a genera rezumat și test")
    
    def generate_with_ollama(self):
        """Generate summary and test with Ollama in a separate thread"""
        try:
            # Open the PDF
            current_file = self.pdf_handler.get_current_file()
            if not self.pdf_handler.open_pdf():
                self.ui.add_log(f"Eroare la deschiderea PDF pentru Ollama: {current_file}")
                self.ollama_running = False
                return
                
            # Extract text
            self.ui.add_log("Extragere text din PDF...")
            pdf_text = self.pdf_handler.get_text_from_pdf()
            
            if not pdf_text.strip():
                self.ui.add_log("PDF-ul nu conține text care poate fi extras")
                self.ollama_running = False
                return
            
            # Test Ollama connection first
            self.ui.add_log("Testare conexiune Ollama...")
            test_response = self.ollama.generate("Test", max_tokens=10)
            if test_response.startswith("Error:") or test_response.startswith("Exception:"):
                self.ui.add_log("EROARE: Ollama nu este disponibil!")
                self.ui.add_log("Verifică dacă Ollama rulează: 'ollama serve'")
                self.ollama_running = False
                return
                
            # Generate summary
            self.ui.add_log("Generare rezumat cu Ollama...")
            summary = self.ollama.generate_summary(pdf_text)
            
            # Check if summary generation failed
            if summary.startswith("Error:") or summary.startswith("Exception:"):
                self.ui.add_log(f"Eroare la generarea rezumatului: {summary}")
                self.ollama_running = False
                return
            
            # Generate test
            self.ui.add_log("Generare test cu Ollama...")
            test = self.ollama.generate_test(pdf_text)
            
            # Check if test generation failed
            if test.startswith("Error:") or test.startswith("Exception:"):
                self.ui.add_log(f"Eroare la generarea testului: {test}")
                self.ollama_running = False
                return
            
            # Save files
            base_filename = get_base_filename(current_file)
            self.pdf_handler.create_text_files(base_filename, summary, test)
            
            # Log execution time
            execution_time = self.ollama.get_execution_time()
            self.stats.log_ollama(execution_time)
            
            self.ui.add_log(f"✓ Rezumat si test generate in {execution_time:.2f} secunde")
            self.ui.add_log(f"Fisiere PDF salvate: {base_filename}_rezumat.pdf, {base_filename}_test.pdf")
            
            # Refresh file list
            self.pdf_handler.scan_folder()
            
        except Exception as e:
            self.ui.add_log(f"Eroare Ollama: {e}")
        finally:
            self.ollama_running = False
    
    def handle_document_gesture(self, gesture):
        """Handle gestures in the document view"""
        if gesture == "palm":
            # Close document and return to menu
            if self.pdf_handler.close_pdf():
                self.ui.set_view("menu")
                self.ui.add_log("Document închis")
                self.current_text = None
            
        elif gesture == "right":
            # Navigate to next page
            if self.current_text:
                # Text document navigation
                self.text_page += 1
                self.stats.log_navigation("document_navigations")
            else:
                # PDF navigation
                if self.pdf_handler.navigate_pdf(1):
                    self.ui.add_log(f"Pagina {self.pdf_handler.current_page + 1} din {self.pdf_handler.total_pages}")
                    self.stats.log_navigation("document_navigations")
            
        elif gesture == "left":
            # Navigate to previous page
            if self.current_text:
                # Text document navigation
                self.text_page = max(0, self.text_page - 1)
                self.stats.log_navigation("document_navigations")
            else:
                # PDF navigation
                if self.pdf_handler.navigate_pdf(-1):
                    self.ui.add_log(f"Pagina {self.pdf_handler.current_page + 1} din {self.pdf_handler.total_pages}")
                    self.stats.log_navigation("document_navigations")
        
        elif gesture == "two_fingers" and not self.ollama_running:
            # Generate summary and test with Ollama (also available in document view)
            current_file = self.pdf_handler.get_current_file()
            if current_file and is_pdf_file(current_file):
                # Start Ollama processing in a separate thread
                self.ollama_running = True
                self.ui.add_log("Generare cu Ollama începută...")
                
                # Start thread
                threading.Thread(target=self.generate_with_ollama, daemon=True).start()
            else:
                self.ui.add_log("Selectați un fișier PDF pentru a genera rezumat și test")
    
    def handle_gesture(self, gesture):
        """Handle detected gestures based on the current view"""
        if gesture:
            # Log gesture detection for debugging
            self.ui.add_log(f"Gest detectat: {gesture} (View: {self.ui.get_view()})")
            self.stats.log_gesture(gesture, context=self.ui.get_view())
            
            if self.ui.get_view() == "menu":
                self.handle_menu_gesture(gesture)
            else:
                self.handle_document_gesture(gesture)
    
    def main_loop(self):
        """Run the main application loop"""
        self.running = True
        last_frame_time = time.time()
        
        # Initial setup for UI display
        default_frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
        cv2.putText(
            default_frame, 
            "Waiting for camera...", 
            (100, 240), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1, 
            (0, 0, 255), 
            2
        )
        
        while self.running and not self.shutdown_event.is_set():
            # Check if quit is requested
            if self.ui.check_events():
                self.running = False
                break
                
            # Calculate FPS
            current_time = time.time()
            fps = 1 / max(0.001, current_time - last_frame_time)
            last_frame_time = current_time
            
            try:
                # Capture camera frame
                ret, frame = self.camera.read()
                if not ret:
                    # Use default frame if camera read fails
                    frame = default_frame.copy()
                    cv2.putText(
                        frame, 
                        "Camera error - reconnecting...", 
                        (100, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        1, 
                        (0, 0, 255), 
                        2
                    )
                    # Try to reinitialize camera occasionally
                    if int(time.time()) % 5 == 0:  # Every 5 seconds
                        self.init_camera()
                else:
                    # Flip the frame horizontally (mirror)
                    frame = cv2.flip(frame, 1)
                    
                    # Detect hand gestures
                    gesture, landmarks, confidence = self.gesture_detector.detect_gesture(frame)
                    
                    # Update gesture text on frame
                    self.gesture_detector.draw_gesture_text(frame, gesture)
                    
                    # Add FPS counter
                    cv2.putText(
                        frame, 
                        f"FPS: {fps:.2f}", 
                        (10, frame.shape[0] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, 
                        (0, 255, 0), 
                        1
                    )
                    
                    # Handle detected gestures
                    if gesture:
                        self.handle_gesture(gesture)
                
                # Get current PDF page image or None
                document_image = None
                if self.ui.get_view() == "document" and not self.current_text:
                    document_image = self.pdf_handler.get_current_page_as_cv2()
                
                # Draw UI
                self.ui.draw(
                    camera_frame=frame, 
                    files=self.pdf_handler.get_file_list(), 
                    current_file_index=self.pdf_handler.current_file_index,
                    document_image=document_image,
                    text_document=self.current_text,
                    text_page=self.text_page
                )
                
            except Exception as e:
                self.ui.add_log(f"Eroare în bucla principală: {e}")
                # Brief pause to avoid tight loop on error
                time.sleep(0.1)
            
            # Sleep to control frame rate and reduce CPU usage
            time.sleep(0.01)
    
    def run(self):
        """Run the application"""
        try:
            # Initial log
            self.ui.add_log("Inițializare EduGesture...")
            
            # Initialize camera
            if not self.init_camera():
                self.ui.add_log("Avertisment: Probleme cu camera, vom continua să încercăm...")
                
            # Initial log
            self.ui.add_log("Scanare directorul Lectii/")
            
            # Scan the PDF folder
            self.pdf_handler.scan_folder()
            files = self.pdf_handler.get_file_list()
            if files:
                self.ui.add_log(f"Gasite {len(files)} fisiere")
            else:
                self.ui.add_log("Nu s-au gasit fisiere PDF. Adaugati fisiere in directorul Lectii/")
            
            # Run the main loop
            self.main_loop()
            
        except KeyboardInterrupt:
            self.ui.add_log("Oprire la solicitarea utilizatorului")
        except Exception as e:
            self.ui.add_log(f"Eroare: {e}")
        finally:
            # Clean up
            if self.camera:
                self.camera.release()
            
            self.gesture_detector.close()
            self.ui.cleanup()
            
            # Print stats on exit
            stats = self.stats.get_stats_summary()
            print("\nStatistici aplicație:")
            print(f"Gesturi detectate: {stats['gestures']}")
            print(f"Navigări: {stats['navigations']}")
            print(f"Executări Ollama: {stats['ollama']['calls']}")
            if stats['ollama']['calls'] > 0:
                print(f"Timp mediu Ollama: {stats['ollama']['avg_time']:.2f} secunde")


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="EduGesture - Aplicație educațională cu gesturi")
    parser.add_argument("--camera", type=int, default=0, help="ID-ul camerei (implicit: 0)")
    parser.add_argument("--ollama-host", type=str, default="http://localhost:11434", help="Host-ul Ollama (implicit: http://localhost:11434)")
    parser.add_argument("--ollama-model", type=str, default="llama3.2:1b", help="Modelul Ollama (implicit: llama3.2:1b)")
    parser.add_argument("--debug", action="store_true", help="Pornește în modul debug cu simulare utilizatori")
    parser.add_argument("--debug-users", type=int, default=10, help="Numărul de utilizatori simulați (implicit: 10)")
    args = parser.parse_args()
    
    if args.debug:
        # Run debug mode
        run_debug_mode(args.debug_users)
    else:
        # Create and run the normal application
        app = EduGesture(
            ollama_host=args.ollama_host,
            ollama_model=args.ollama_model
        )
        app.camera_id = args.camera
        app.run()


def run_debug_mode(num_users: int = 10):
    """Run the application in debug mode with user simulation"""
    try:
        import pygame
        from debug_simulator import DebugSimulator
        from debug_ui import DebugUI
        
        print("🐛 Starting EduGesture in DEBUG MODE")
        print(f"👥 Simulating {num_users} users")
        print("=" * 50)
        
        # Initialize debug components
        simulator = DebugSimulator(num_users=num_users)
        debug_ui = DebugUI()
        debug_ui.initialize()
        
        # Control variables
        simulation_running = False
        last_export_time = 0
        
        print("🎮 Debug Controls:")
        print("  [S] - Start/Stop Simulation")
        print("  [E] - Export Results")
        print("  [R] - Reset Simulation")
        print("  [Q] - Quit Debug Mode")
        print("=" * 50)
        
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                        
                    elif event.key == pygame.K_s:
                        if not simulation_running:
                            print("🚀 Starting user simulation...")
                            simulator.start_simulation()
                            simulation_running = True
                        else:
                            print("🛑 Stopping user simulation...")
                            simulator.stop_simulation()
                            simulation_running = False
                    
                    elif event.key == pygame.K_e:
                        if simulator.user_actions:
                            print("📊 Exporting simulation results...")
                            actions_file, summary_file = simulator.export_results()
                            print(f"✅ Results exported successfully!")
                            last_export_time = time.time()
                        else:
                            print("⚠️  No data to export. Start simulation first.")
                    
                    elif event.key == pygame.K_r:
                        print("🔄 Resetting simulation...")
                        if simulation_running:
                            simulator.stop_simulation()
                            simulation_running = False
                        
                        # Create new simulator
                        simulator = DebugSimulator(num_users=num_users)
                        print("✅ Simulation reset complete")
            
            # Get current stats
            stats = simulator.get_real_time_stats() if simulation_running else {}
            
            # Update debug UI
            debug_ui.update(stats)
            
            # Auto-export every 5 minutes if simulation is running
            current_time = time.time()
            if (simulation_running and 
                current_time - last_export_time > 300 and  # 5 minutes
                simulator.user_actions):
                print("📊 Auto-exporting results (5 min interval)...")
                simulator.export_results()
                last_export_time = current_time
        
        # Cleanup
        if simulation_running:
            print("🛑 Stopping simulation...")
            simulator.stop_simulation()
        
        print("🧹 Cleaning up debug mode...")
        debug_ui.cleanup()
        
        # Final export if there's data
        if simulator.user_actions:
            print("📊 Final export of results...")
            actions_file, summary_file = simulator.export_results()
            
            # Show summary
            stats = simulator.get_real_time_stats()
            print("\n" + "=" * 50)
            print("📈 DEBUG SESSION SUMMARY")
            print("=" * 50)
            print(f"⏱️  Total Time: {stats.get('simulation_time', 0):.1f} seconds")
            print(f"🎯 Total Actions: {stats.get('total_actions', 0)}")
            print(f"✅ Overall Accuracy: {stats.get('overall_accuracy', 0):.1f}%")
            print(f"👥 Active Users: {stats.get('active_users', 0)}/{num_users}")
            print(f"📊 Results saved to: {summary_file}")
            print("=" * 50)
        
    except ImportError as e:
        print(f"❌ Error: Debug mode requires additional dependencies: {e}")
        print("💡 Make sure debug_simulator.py and debug_ui.py are available")
    except Exception as e:
        print(f"❌ Debug mode error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # For exception debugging
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc() 
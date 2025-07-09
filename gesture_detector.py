import cv2
import mediapipe as mp
import numpy as np
import time
import csv
from datetime import datetime

class GestureDetector:
    def __init__(self, log_path="gesture_log.csv"):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Gesture detection params
        self.last_gesture = None
        self.gesture_timestamp = 0
        self.gesture_cooldown = 0.8  # seconds
        
        # Logging
        self.log_path = log_path
        self.log_file = None
        self.init_log()
        
    def init_log(self):
        """Initialize CSV log file for gesture metrics"""
        self.log_file = open(self.log_path, 'w', newline='')
        self.log_writer = csv.writer(self.log_file)
        self.log_writer.writerow([
            'Timestamp', 'Gesture', 'Confidence', 'Success'
        ])
        
    def log_gesture(self, gesture, confidence, success=True):
        """Log a detected gesture for metrics"""
        if self.log_file:
            self.log_writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                gesture,
                confidence,
                success
            ])
            self.log_file.flush()
    
    def detect_gesture(self, frame):
        """
        Detect hand gestures in the frame
        Returns: (gesture_name, hand_landmarks, confidence)
        """
        # Convert the BGR image to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the image and detect hands
        results = self.hands.process(frame_rgb)
        
        gesture = None
        confidence = 0
        
        # If hands are detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw the hand landmarks on the image
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
                
                # Get hand landmarks as array
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    landmarks.append([landmark.x, landmark.y, landmark.z])
                landmarks = np.array(landmarks)
                
                # Get gesture
                gesture, confidence = self._classify_gesture(landmarks)
                
                # Apply cooldown to prevent rapid gesture detection
                current_time = time.time()
                if current_time - self.gesture_timestamp < self.gesture_cooldown:
                    return None, hand_landmarks, 0
                
                if gesture:
                    self.gesture_timestamp = current_time
                    self.last_gesture = gesture
                    self.log_gesture(gesture, confidence)
                    return gesture, hand_landmarks, confidence
                
        return None, None, 0
    
    def _classify_gesture(self, landmarks):
        """
        Classify the gesture based on hand landmarks
        Returns: (gesture_name, confidence)
        """
        # Extract finger tip and landmark positions
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        wrist = landmarks[0]
        
        # Compute distances between tips and base of the hand
        thumb_extended = self._is_finger_extended(landmarks, 4)
        index_extended = self._is_finger_extended(landmarks, 8)
        middle_extended = self._is_finger_extended(landmarks, 12)
        ring_extended = self._is_finger_extended(landmarks, 16)
        pinky_extended = self._is_finger_extended(landmarks, 20)
        
        # Direction vector (wrist to index finger tip)
        direction = index_tip[:2] - wrist[:2]
        direction_norm = np.linalg.norm(direction)
        if direction_norm > 0:
            direction = direction / direction_norm
        
        # Pointing right (more lenient)
        if (index_extended and not middle_extended and not ring_extended and not pinky_extended and
            direction[0] > 0.5):
            return "right", 0.85
        
        # Pointing left (more lenient)
        if (index_extended and not middle_extended and not ring_extended and not pinky_extended and
            direction[0] < -0.5):
            return "left", 0.85
        
        # Two fingers (peace sign)
        if (index_extended and middle_extended and not ring_extended and not pinky_extended):
            return "two_fingers", 0.9
        
        # OK sign (thumb and index touch, other fingers extended)
        if (middle_extended and ring_extended and pinky_extended):
            thumb_index_dist = np.linalg.norm(thumb_tip[:2] - index_tip[:2])
            if thumb_index_dist < 0.08:
                return "ok", 0.85
        
        # Open palm (all fingers extended)
        if all([thumb_extended, index_extended, middle_extended, ring_extended, pinky_extended]):
            return "palm", 0.9
        
        # No recognized gesture
        return None, 0
    
    def _is_finger_extended(self, landmarks, finger_tip_idx):
        """Check if a finger is extended - improved version"""
        # MediaPipe hand landmark indices
        if finger_tip_idx == 4:  # Thumb
            ip_idx = 3
            mcp_idx = 2
        elif finger_tip_idx == 8:  # Index
            ip_idx = 7
            mcp_idx = 5
        elif finger_tip_idx == 12:  # Middle
            ip_idx = 11
            mcp_idx = 9
        elif finger_tip_idx == 16:  # Ring
            ip_idx = 15
            mcp_idx = 13
        elif finger_tip_idx == 20:  # Pinky
            ip_idx = 19
            mcp_idx = 17
        else:
            return False
        
        # Get positions
        tip = landmarks[finger_tip_idx]
        ip = landmarks[ip_idx]
        mcp = landmarks[mcp_idx]
        wrist = landmarks[0]
        
        # Method 1: Check if tip is further from wrist than IP joint
        tip_to_wrist = np.linalg.norm(tip[:2] - wrist[:2])
        ip_to_wrist = np.linalg.norm(ip[:2] - wrist[:2])
        
        # Method 2: Check if finger is pointing outward
        wrist_to_mcp = mcp[:2] - wrist[:2]
        mcp_to_tip = tip[:2] - mcp[:2]
        
        # Normalize vectors
        if np.linalg.norm(wrist_to_mcp) > 0:
            wrist_to_mcp = wrist_to_mcp / np.linalg.norm(wrist_to_mcp)
        if np.linalg.norm(mcp_to_tip) > 0:
            mcp_to_tip = mcp_to_tip / np.linalg.norm(mcp_to_tip)
        
        # Check if vectors point in similar direction (finger extended)
        dot_product = np.dot(wrist_to_mcp, mcp_to_tip)
        
        # Combined criteria (more lenient)
        distance_criterion = tip_to_wrist > ip_to_wrist * 0.9
        direction_criterion = dot_product > 0.3
        
        return distance_criterion and direction_criterion
    
    def draw_gesture_text(self, frame, gesture):
        """Draw the detected gesture as text on the frame"""
        if gesture:
            gesture_text = {
                "right": "DREAPTA",
                "left": "STANGA",
                "two_fingers": "DOUA DEGETE",
                "ok": "OK",
                "palm": "PALMA"
            }.get(gesture, gesture.upper())
            
            # Draw background for better readability
            cv2.rectangle(frame, (5, 5), (300, 40), (0, 0, 0), -1)
            cv2.rectangle(frame, (5, 5), (300, 40), (0, 255, 0), 2)
            
            cv2.putText(
                frame, 
                f"Gest: {gesture_text}", 
                (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.8, 
                (0, 255, 0), 
                2
            )
    
    def close(self):
        """Clean up resources"""
        if self.log_file:
            self.log_file.close() 
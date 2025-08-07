"""
Debug UI for EduGesture Application
Real-time visualization of user simulation data
"""

import pygame
import time
import math
from typing import Dict, List, Any, Optional
from debug_simulator import DebugSimulator

class DebugUI:
    """UI for displaying debug simulation data in real-time"""
    
    def __init__(self, width: int = 1400, height: int = 900):
        self.width = width
        self.height = height
        self.display = None
        self.clock = None
        self.font_title = None
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.running = False
        
        # Colors - Modern debug theme
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.DARK_GRAY = (40, 40, 40)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (200, 200, 200)
        self.GREEN = (46, 204, 113)
        self.RED = (231, 76, 60)
        self.BLUE = (52, 152, 219)
        self.ORANGE = (230, 126, 34)
        self.PURPLE = (155, 89, 182)
        self.YELLOW = (241, 196, 15)
        
        # Skill level colors
        self.SKILL_COLORS = {
            "beginner": self.RED,
            "intermediate": self.ORANGE,
            "advanced": self.GREEN
        }
        
        # Layout areas
        self.header_rect = None
        self.stats_rect = None
        self.users_rect = None
        self.chart_rect = None
        self.controls_rect = None
        
        # Animation and data
        self.last_update = 0
        self.animation_offset = 0
        self.chart_data = []  # For real-time charts
        self.max_chart_points = 60  # 1 minute of data at 1 second intervals
        
    def initialize(self):
        """Initialize Pygame and UI components"""
        pygame.init()
        
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("EduGesture Debug Monitor")
        self.clock = pygame.time.Clock()
        
        # Initialize fonts
        self.font_title = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)
        
        # Setup layout
        self.setup_layout()
        
        print("🖥️  Debug UI initialized")
    
    def setup_layout(self):
        """Setup UI layout rectangles"""
        margin = 10
        
        # Header area
        self.header_rect = pygame.Rect(margin, margin, self.width - 2*margin, 80)
        
        # Main content area
        content_y = self.header_rect.bottom + margin
        content_height = self.height - content_y - margin - 60  # Leave space for controls
        
        # Left side - Statistics
        stats_width = 400
        self.stats_rect = pygame.Rect(margin, content_y, stats_width, content_height)
        
        # Middle - User grid
        users_x = self.stats_rect.right + margin
        users_width = 600
        self.users_rect = pygame.Rect(users_x, content_y, users_width, content_height)
        
        # Right side - Real-time chart
        chart_x = self.users_rect.right + margin
        chart_width = self.width - chart_x - margin
        self.chart_rect = pygame.Rect(chart_x, content_y, chart_width, content_height)
        
        # Controls at bottom
        controls_y = self.height - 50
        self.controls_rect = pygame.Rect(margin, controls_y, self.width - 2*margin, 40)
    
    def draw_header(self, stats: Dict[str, Any]):
        """Draw the header with overall statistics"""
        # Background
        pygame.draw.rect(self.display, self.DARK_GRAY, self.header_rect)
        pygame.draw.rect(self.display, self.BLUE, self.header_rect, 3)
        
        # Title
        title = self.font_title.render("EduGesture Debug Monitor", True, self.WHITE)
        title_rect = title.get_rect(left=self.header_rect.left + 20, centery=self.header_rect.centery - 15)
        self.display.blit(title, title_rect)
        
        # Overall stats
        if stats:
            sim_time = stats.get("simulation_time", 0)
            total_actions = stats.get("total_actions", 0)
            accuracy = stats.get("overall_accuracy", 0)
            active_users = stats.get("active_users", 0)
            
            # Format time
            minutes = int(sim_time // 60)
            seconds = int(sim_time % 60)
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            stats_text = [
                f"Time: {time_str}",
                f"Actions: {total_actions}",
                f"Accuracy: {accuracy:.1f}%",
                f"Active Users: {active_users}/10"
            ]
            
            x_offset = self.header_rect.left + 20
            y_offset = self.header_rect.centery + 5
            
            for i, text in enumerate(stats_text):
                color = self.WHITE
                if i == 2:  # Accuracy
                    color = self.GREEN if accuracy > 80 else self.ORANGE if accuracy > 60 else self.RED
                elif i == 3:  # Active users
                    color = self.GREEN if active_users > 7 else self.ORANGE if active_users > 4 else self.RED
                
                rendered = self.font_medium.render(text, True, color)
                self.display.blit(rendered, (x_offset + i * 150, y_offset))
    
    def draw_statistics_panel(self, stats: Dict[str, Any]):
        """Draw detailed statistics panel"""
        # Background
        pygame.draw.rect(self.display, self.DARK_GRAY, self.stats_rect)
        pygame.draw.rect(self.display, self.WHITE, self.stats_rect, 2)
        
        # Title
        title = self.font_large.render("Statistics", True, self.WHITE)
        title_rect = title.get_rect(centerx=self.stats_rect.centerx, y=self.stats_rect.y + 10)
        self.display.blit(title, title_rect)
        
        if not stats:
            return
        
        y_offset = self.stats_rect.y + 50
        line_height = 25
        
        # General stats
        general_stats = [
            ("Simulation Time", f"{stats.get('simulation_time', 0):.1f}s"),
            ("Total Actions", str(stats.get("total_actions", 0))),
            ("Actions/Second", f"{stats.get('actions_per_second', 0):.2f}"),
            ("Overall Accuracy", f"{stats.get('overall_accuracy', 0):.1f}%"),
            ("Active Users", f"{stats.get('active_users', 0)}/10")
        ]
        
        for label, value in general_stats:
            # Label
            label_text = self.font_small.render(f"{label}:", True, self.LIGHT_GRAY)
            self.display.blit(label_text, (self.stats_rect.x + 20, y_offset))
            
            # Value
            value_text = self.font_small.render(value, True, self.WHITE)
            value_rect = value_text.get_rect(right=self.stats_rect.right - 20, y=y_offset)
            self.display.blit(value_text, value_rect)
            
            y_offset += line_height
        
        # Skill level distribution
        y_offset += 20
        skill_title = self.font_medium.render("Skill Distribution", True, self.YELLOW)
        self.display.blit(skill_title, (self.stats_rect.x + 20, y_offset))
        y_offset += 30
        
        if "user_stats" in stats:
            skill_counts = {"beginner": 0, "intermediate": 0, "advanced": 0}
            for user_stat in stats["user_stats"]:
                skill_counts[user_stat["skill_level"]] += 1
            
            bar_width = self.stats_rect.width - 80
            bar_height = 20
            
            for skill, count in skill_counts.items():
                # Skill label
                skill_text = self.font_small.render(f"{skill.title()}:", True, self.LIGHT_GRAY)
                self.display.blit(skill_text, (self.stats_rect.x + 20, y_offset))
                
                # Progress bar
                bar_rect = pygame.Rect(self.stats_rect.x + 120, y_offset + 2, bar_width - 100, bar_height - 4)
                pygame.draw.rect(self.display, self.GRAY, bar_rect)
                
                if count > 0:
                    fill_width = int((count / 10) * (bar_width - 100))
                    fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height)
                    pygame.draw.rect(self.display, self.SKILL_COLORS[skill], fill_rect)
                
                # Count
                count_text = self.font_small.render(str(count), True, self.WHITE)
                count_rect = count_text.get_rect(right=self.stats_rect.right - 20, y=y_offset)
                self.display.blit(count_text, count_rect)
                
                y_offset += 30
    
    def draw_users_grid(self, stats: Dict[str, Any]):
        """Draw grid of user information"""
        # Background
        pygame.draw.rect(self.display, self.DARK_GRAY, self.users_rect)
        pygame.draw.rect(self.display, self.WHITE, self.users_rect, 2)
        
        # Title
        title = self.font_large.render("User Activity", True, self.WHITE)
        title_rect = title.get_rect(centerx=self.users_rect.centerx, y=self.users_rect.y + 10)
        self.display.blit(title, title_rect)
        
        if not stats or "user_stats" not in stats:
            return
        
        # Grid setup
        cols = 2
        rows = 5
        cell_width = (self.users_rect.width - 40) // cols
        cell_height = (self.users_rect.height - 80) // rows
        
        start_x = self.users_rect.x + 20
        start_y = self.users_rect.y + 50
        
        user_stats = stats["user_stats"]
        
        for i, user_stat in enumerate(user_stats[:10]):  # Limit to 10 users
            row = i // cols
            col = i % cols
            
            cell_x = start_x + col * cell_width
            cell_y = start_y + row * cell_height
            
            cell_rect = pygame.Rect(cell_x, cell_y, cell_width - 10, cell_height - 10)
            
            # Cell background based on skill level
            skill_color = self.SKILL_COLORS[user_stat["skill_level"]]
            pygame.draw.rect(self.display, skill_color, cell_rect, 2)
            
            # User info
            name_text = self.font_medium.render(user_stat["name"], True, self.WHITE)
            name_rect = name_text.get_rect(centerx=cell_rect.centerx, y=cell_rect.y + 5)
            self.display.blit(name_text, name_rect)
            
            # Stats
            info_lines = [
                f"Level: {user_stat['skill_level'].title()}",
                f"Actions: {user_stat['actions']}",
                f"Accuracy: {user_stat['accuracy']:.0f}%",
                f"Avg Time: {user_stat['avg_response_time']:.0f}ms",
                f"Context: {user_stat['current_context'].title()}"
            ]
            
            y_pos = cell_rect.y + 30
            for line in info_lines:
                text = self.font_small.render(line, True, self.WHITE)
                text_rect = text.get_rect(centerx=cell_rect.centerx, y=y_pos)
                self.display.blit(text, text_rect)
                y_pos += 16
            
            # Activity indicator (animated dot)
            if user_stat["actions"] > 0:
                dot_radius = 5 + int(3 * math.sin(time.time() * 3 + i))
                dot_center = (cell_rect.right - 15, cell_rect.y + 15)
                pygame.draw.circle(self.display, self.GREEN, dot_center, dot_radius)
    
    def draw_realtime_chart(self, stats: Dict[str, Any]):
        """Draw real-time performance chart"""
        # Background
        pygame.draw.rect(self.display, self.DARK_GRAY, self.chart_rect)
        pygame.draw.rect(self.display, self.WHITE, self.chart_rect, 2)
        
        # Title
        title = self.font_large.render("Real-time Metrics", True, self.WHITE)
        title_rect = title.get_rect(centerx=self.chart_rect.centerx, y=self.chart_rect.y + 10)
        self.display.blit(title, title_rect)
        
        # Add current data point
        if stats:
            self.chart_data.append({
                "timestamp": time.time(),
                "accuracy": stats.get("overall_accuracy", 0),
                "actions_per_sec": stats.get("actions_per_second", 0),
                "active_users": stats.get("active_users", 0)
            })
            
            # Keep only recent data
            if len(self.chart_data) > self.max_chart_points:
                self.chart_data.pop(0)
        
        if len(self.chart_data) < 2:
            return
        
        # Chart area
        chart_area = pygame.Rect(
            self.chart_rect.x + 20, 
            self.chart_rect.y + 50,
            self.chart_rect.width - 40,
            self.chart_rect.height - 100
        )
        
        # Draw chart background
        pygame.draw.rect(self.display, self.BLACK, chart_area)
        
        # Draw grid lines
        for i in range(5):
            y = chart_area.y + (chart_area.height // 4) * i
            pygame.draw.line(self.display, self.GRAY, (chart_area.x, y), (chart_area.right, y), 1)
        
        # Draw data lines
        if len(self.chart_data) > 1:
            # Accuracy line (0-100%)
            accuracy_points = []
            for i, data in enumerate(self.chart_data):
                x = chart_area.x + (i / (self.max_chart_points - 1)) * chart_area.width
                y = chart_area.bottom - (data["accuracy"] / 100) * chart_area.height
                accuracy_points.append((x, y))
            
            if len(accuracy_points) > 1:
                pygame.draw.lines(self.display, self.GREEN, False, accuracy_points, 2)
            
            # Active users line (0-10)
            user_points = []
            for i, data in enumerate(self.chart_data):
                x = chart_area.x + (i / (self.max_chart_points - 1)) * chart_area.width
                y = chart_area.bottom - (data["active_users"] / 10) * chart_area.height
                user_points.append((x, y))
            
            if len(user_points) > 1:
                pygame.draw.lines(self.display, self.BLUE, False, user_points, 2)
        
        # Legend
        legend_y = self.chart_rect.bottom - 30
        legend_items = [
            ("Accuracy %", self.GREEN),
            ("Active Users", self.BLUE)
        ]
        
        x_offset = self.chart_rect.x + 20
        for label, color in legend_items:
            # Color dot
            pygame.draw.circle(self.display, color, (x_offset, legend_y), 5)
            
            # Label
            text = self.font_small.render(label, True, self.WHITE)
            self.display.blit(text, (x_offset + 15, legend_y - 8))
            
            x_offset += 120
    
    def draw_controls(self):
        """Draw control panel"""
        # Background
        pygame.draw.rect(self.display, self.DARK_GRAY, self.controls_rect)
        pygame.draw.rect(self.display, self.GRAY, self.controls_rect, 1)
        
        # Control instructions
        controls_text = "Controls: [S] Start/Stop Simulation | [E] Export Results | [R] Reset | [Q] Quit"
        text = self.font_small.render(controls_text, True, self.WHITE)
        text_rect = text.get_rect(center=self.controls_rect.center)
        self.display.blit(text, text_rect)
    
    def handle_events(self) -> bool:
        """Handle UI events. Returns False if should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                elif event.key == pygame.K_s:
                    # Start/stop simulation handled by main loop
                    pass
                elif event.key == pygame.K_e:
                    # Export results handled by main loop
                    pass
                elif event.key == pygame.K_r:
                    # Reset handled by main loop
                    pass
        return True
    
    def update(self, stats: Dict[str, Any]):
        """Update and draw the UI"""
        # Clear display
        self.display.fill(self.BLACK)
        
        # Draw all components
        self.draw_header(stats)
        self.draw_statistics_panel(stats)
        self.draw_users_grid(stats)
        self.draw_realtime_chart(stats)
        self.draw_controls()
        
        # Update display
        pygame.display.flip()
        self.clock.tick(60)  # 60 FPS for smooth animation
    
    def cleanup(self):
        """Clean up Pygame resources"""
        if pygame.get_init():
            pygame.quit()


if __name__ == "__main__":
    # Test the debug UI
    debug_ui = DebugUI()
    debug_ui.initialize()
    
    # Create a test simulator
    simulator = DebugSimulator(num_users=5)
    
    try:
        print("🎮 Debug UI Test - Press 'S' to start simulation, 'Q' to quit")
        
        running = True
        simulation_started = False
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_s:
                        if not simulation_started:
                            simulator.start_simulation()
                            simulation_started = True
                            print("🚀 Simulation started!")
                        else:
                            simulator.stop_simulation()
                            simulation_started = False
                            print("🛑 Simulation stopped!")
                    elif event.key == pygame.K_e:
                        simulator.export_results()
                        print("📊 Results exported!")
            
            # Get current stats
            stats = simulator.get_real_time_stats() if simulation_started else {}
            
            # Update UI
            debug_ui.update(stats)
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    finally:
        if simulation_started:
            simulator.stop_simulation()
        debug_ui.cleanup()
        print("👋 Debug UI closed")
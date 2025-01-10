import pygame
import sqlite3
from pygame.locals import *
import os
from PIL import Image
from io import BytesIO


class Database_Search:
    def __init__(self, width, height, playground_rect, base_path, current_background, dark_mode, music_play, music_rect,
                 button_rect):
        self.width = width
        self.height = height
        self.playground_rect = playground_rect
        self.base_path = base_path
        self.current_background = current_background
        self.dark_mode = dark_mode
        self.music_play = music_play
        self.music_rect = music_rect
        self.button_rect = button_rect

        # Initialize hover states
        self.button_hovered = False
        self.music_hovered = False
        self.return_button_hovered = False

        # Initialize SQLite connection
        self.conn = sqlite3.connect('ochem.db')
        self.cursor = self.conn.cursor()

        # Search box properties
        self.search_box = pygame.Rect(
            self.playground_rect.centerx - 200,
            self.playground_rect.top + 100,
            400,
            50
        )
        self.search_text = ""
        self.search_active = False

        # Search results properties
        self.search_results = []
        self.selected_result = None

        # Create return to menu button
        button_width = 200
        button_height = 50
        self.return_to_menu_rect = pygame.Rect(
            self.playground_rect.right - button_width - 20,
            self.playground_rect.top + 20,
            button_width,
            button_height
        )

        # Font initialization
        self.font = pygame.font.SysFont('comicsansms', 32)
        self.results_font = pygame.font.SysFont('comicsansms', 24)

        self.scale_factor = min(width / 1600, height / 1000)
        self.result_button_extra_width = 400
        self.result_button_height = 45
        self.result_button_spacing = 60
        self.result_hover_states = []

        self.detail_view = False
        self.current_molecule = None
        self.detail_rect = None
        self.molecule_image = None

        # Define detail view dimensions
        self.detail_width = 800
        self.detail_height = 500

    def on_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            # Check if search box is clicked
            if self.search_box.collidepoint(event.pos):
                self.search_active = True
            else:
                self.search_active = False

            if not self.detail_view:
                for i, result in enumerate(self.search_results):
                    result_rect = pygame.Rect(
                        self.search_box.centerx - (self.search_box.width + self.result_button_extra_width * self.scale_factor) / 2,
                        self.search_box.bottom + self.scale_factor * 20 + (i * self.result_button_spacing * self.scale_factor),
                        self.search_box.width + self.result_button_extra_width * self.scale_factor,
                        self.result_button_height * self.scale_factor
                    )
                    if result_rect.collidepoint(event.pos):
                        self.selected_result = result
                        self.detail_view = True
                        self.current_molecule = result
                        # Load molecule image directly from binary data
                        self.molecule_image = self.load_and_scale_image(result[3])

            # Check if return to menu button is clicked
            if self.return_to_menu_rect.collidepoint(event.pos):
                return "return_to_menu"

        elif event.type == VIDEORESIZE:
            width, height = event.size
            display_surface = pygame.display.set_mode((width, height), RESIZABLE)
            self.resize_elements(width, height)
            # Reload current molecule image with new scale if in detail view
            if self.detail_view and self.current_molecule:
                self.molecule_image = self.load_and_scale_image(self.current_molecule[3])

        elif event.type == MOUSEMOTION:
            # Update hover states
            self.button_hovered = self.button_rect.collidepoint(event.pos)
            self.music_hovered = self.music_rect.collidepoint(event.pos)
            self.return_button_hovered = self.return_to_menu_rect.collidepoint(event.pos)
            self.result_hover_states = []
            for i, _ in enumerate(self.search_results):
                result_rect = pygame.Rect(
                    self.search_box.centerx - (self.search_box.width + 400 * self.scale_factor) / 2,
                    self.search_box.bottom + self.scale_factor * 20 + (i * 60 * self.scale_factor),
                    self.search_box.width + 400 * self.scale_factor,
                    45 * self.scale_factor
                )
                self.result_hover_states.append(result_rect.collidepoint(event.pos))

        elif event.type == KEYDOWN and self.search_active:
            if event.key == K_RETURN:
                self.perform_search()
            elif event.key == K_BACKSPACE:
                self.search_text = self.search_text[:-1]
            elif event.key == K_ESCAPE:
                self.search_active = False
            else:
                self.search_text += event.unicode

        return None

    def load_and_scale_image(self, image_data):
        """Load and scale image from binary data"""
        if not image_data:
            return None

        try:
            # Open image from binary data using PIL
            pil_image = Image.open(BytesIO(image_data))

            # Calculate scaled dimensions for detail view
            scale = min(
                (self.detail_width * 0.6 * self.scale_factor) / pil_image.width,
                (self.detail_height * 0.6 * self.scale_factor) / pil_image.height
            )

            new_size = (
                int(pil_image.width * scale),
                int(pil_image.height * scale)
            )

            # Resize image
            pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)

            # Convert to pygame surface
            mode = pil_image.mode
            size = pil_image.size
            data = pil_image.tobytes()
            return pygame.image.fromstring(data, size, mode)
        except Exception as e:
            print(f"Error loading molecule image: {e}")
            return None

    def perform_search(self):
        search_query = f"%{self.search_text}%"
        try:
            self.cursor.execute("""
                SELECT chemical_formula, pH, iupac, image_data 
                FROM ochem_table 
                WHERE chemical_formula LIKE ? OR iupac LIKE ?
                LIMIT 10
            """, (search_query, search_query))
            self.search_results = self.cursor.fetchall()
            self.result_hover_states = [False] * len(self.search_results)
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            self.search_results = []
            self.result_hover_states = []

    def pil_image_to_pygame(self, pil_image):
        """Convert PIL Image to Pygame Surface"""
        byte_array = io.BytesIO()
        pil_image.save(byte_array, format='PNG')
        byte_array.seek(0)
        return pygame.image.load(io.BytesIO(byte_array.read()))

    def resize_elements(self, new_width, new_height):
        # Update instance variables
        self.width = new_width
        self.height = new_height

        # Calculate new scale factor
        self.scale_factor = min(new_width / 1600, new_height / 1000)

        # Update playground rectangle
        playground_width = int(new_width * 0.8)
        playground_height = int(new_height * 0.8)
        playground_x = (new_width - playground_width) // 2
        playground_y = (new_height - playground_height) // 2
        self.playground_rect = pygame.Rect(playground_x, playground_y, playground_width, playground_height)

        # Update search box
        search_box_width = min(400, int(playground_width * 0.6))
        search_box_height = int(50 * self.scale_factor)
        self.search_box = pygame.Rect(
            self.playground_rect.centerx - search_box_width // 2,
            self.playground_rect.top + int(100 * self.scale_factor),
            search_box_width,
            search_box_height
        )

        # Update return to menu button
        button_width = int(200 * self.scale_factor)
        button_height = int(50 * self.scale_factor)
        self.return_to_menu_rect = pygame.Rect(
            self.playground_rect.right - button_width - int(20 * self.scale_factor),
            self.playground_rect.top + int(20 * self.scale_factor),
            button_width,
            button_height
        )

        font_size = max(10, int(32 * self.scale_factor))
        results_font_size = max(10, int(24 * self.scale_factor))
        self.font = pygame.font.SysFont('comicsansms', font_size)
        self.results_font = pygame.font.SysFont('comicsansms', results_font_size)

    def perform_search(self):
        search_query = f"%{self.search_text}%"
        try:
            self.cursor.execute("""
                SELECT chemical_formula, pH, iupac, image_file 
                FROM ochem_table 
                WHERE chemical_formula LIKE ? OR iupac LIKE ?
                LIMIT 10
            """, (search_query, search_query))
            self.search_results = self.cursor.fetchall()
            self.result_hover_states = [False] * len(self.search_results)  # Initialize hover states for new results
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            self.search_results = []
            self.result_hover_states = []

    def truncate_text(self, text, max_length=50):
        if len(text) <= max_length:
            return text
        return text[:max_length] + '...'

    def run_once(self, display_surface):
        # Draw background
        display_surface.blit(self.current_background.image, self.current_background.rect)

        # Draw top buttons (light/dark mode and music)
        scale_factor = min(self.width / 1600, self.height / 1000)
        font_size = max(10, int(20 * scale_factor))

        button_color = (100, 100, 100) if self.button_hovered else (169, 169, 169) if self.dark_mode else (
        230, 230, 230)
        pygame.draw.rect(display_surface, button_color, self.button_rect, border_radius=10)

        music_button_color = (100, 100, 100) if self.music_hovered else (169, 169, 169) if self.dark_mode else (
        230, 230, 230)
        pygame.draw.rect(display_surface, music_button_color, self.music_rect, border_radius=10)

        # Button text
        text_color = (255, 255, 255) if self.dark_mode else (0, 0, 0)
        button_font = pygame.font.Font('freesansbold.ttf', font_size)

        button_text = "Light" if self.dark_mode else "Lighter"
        button_text_surface = button_font.render(button_text, True, text_color)
        button_text_rect = button_text_surface.get_rect(center=self.button_rect.center)
        display_surface.blit(button_text_surface, button_text_rect)

        music_text = "Playing" if self.music_play else "Paused"
        music_text_surface = button_font.render(music_text, True, text_color)
        music_text_rect = music_text_surface.get_rect(center=self.music_rect.center)
        display_surface.blit(music_text_surface, music_text_rect)

        # Draw playground background
        playground_surface = pygame.Surface(
            (self.playground_rect.width, self.playground_rect.height),
            pygame.SRCALPHA
        )
        playground_color = (150, 150, 150, 180) if self.dark_mode else (180, 180, 180, 150)
        pygame.draw.rect(
            playground_surface,
            playground_color,
            playground_surface.get_rect(),
            border_radius=50
        )
        display_surface.blit(playground_surface, self.playground_rect)

        # Draw search box
        box_color = (200, 200, 200) if self.search_active else (169, 169, 169)
        pygame.draw.rect(display_surface, box_color, self.search_box, border_radius = 5)

        # Draw search text
        text_surface = self.font.render(self.search_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.search_box.center)
        display_surface.blit(text_surface, text_rect)

        # Draw placeholder text if search box is empty
        if not self.search_text and not self.search_active:
            placeholder = self.font.render("Search molecules...", True, (100, 100, 100))
            placeholder_rect = placeholder.get_rect(center=self.search_box.center)
            display_surface.blit(placeholder, placeholder_rect)

        scale_factor = self.scale_factor
        # Draw search results
        if self.detail_view and self.current_molecule:
            # Create detail view rectangle
            detail_rect = pygame.Rect(
                self.playground_rect.centerx - (self.detail_width * self.scale_factor) / 2,
                self.playground_rect.top + 150 * self.scale_factor,
                self.detail_width * self.scale_factor,
                self.detail_height * self.scale_factor
            )

            # Draw detail view background
            pygame.draw.rect(display_surface, (200, 200, 200), detail_rect, border_radius=10)

            # Draw molecule image if available
            if self.molecule_image:
                image_rect = self.molecule_image.get_rect()
                image_rect.centerx = detail_rect.centerx
                image_rect.top = detail_rect.top + 20 * self.scale_factor
                display_surface.blit(self.molecule_image, image_rect)

            # Draw molecule information
            formula, ph, iupac, _ = self.current_molecule

            # Draw IUPAC name
            iupac_text = self.results_font.render(f"IUPAC: {iupac}", True, (0, 0, 0))
            iupac_rect = iupac_text.get_rect()
            iupac_rect.centerx = detail_rect.centerx
            iupac_rect.top = detail_rect.bottom - 100 * self.scale_factor
            display_surface.blit(iupac_text, iupac_rect)

            # Draw pH
            ph_text = self.results_font.render(f"pH: {ph}", True, (0, 0, 0))
            ph_rect = ph_text.get_rect()
            ph_rect.centerx = detail_rect.centerx
            ph_rect.top = iupac_rect.bottom + 20 * self.scale_factor
            display_surface.blit(ph_text, ph_rect)

        elif not self.detail_view:
            # Existing search results drawing code...
            for i, result in enumerate(self.search_results):
                result_rect = pygame.Rect(
                    self.search_box.centerx - (self.search_box.width + 400 * self.scale_factor) / 2,
                    self.search_box.bottom + self.scale_factor * 20 + (i * 60 * self.scale_factor),
                    self.search_box.width + 400 * self.scale_factor,
                    45 * self.scale_factor
                )

                # Determine button color based on hover and selection state
                if self.result_hover_states[i]:
                    color = (100, 100, 100)  # Darker when hovered, like other buttons
                elif result == self.selected_result:
                    color = (169, 169, 169)  # Selected color
                else:
                    color = (230, 230, 230) if not self.dark_mode else (169, 169, 169)  # Normal color

                pygame.draw.rect(display_surface, color, result_rect,
                                 border_radius=10)  # Changed border_radius to match other buttons

                # Display molecule information
                formula, ph, iupac, image = result
                text = self.truncate_text(iupac)
                text_surface = self.results_font.render(text, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=result_rect.center)
                display_surface.blit(text_surface, text_rect)

        # Draw return to menu button
        return_button_color = (100, 100, 100) if self.return_button_hovered else (169, 169, 169)
        pygame.draw.rect(
            display_surface,
            return_button_color,
            self.return_to_menu_rect,
            border_radius=10
        )
        menu_text = self.results_font.render("Return to Menu", True, (0, 0, 0))
        menu_rect = menu_text.get_rect(center=self.return_to_menu_rect.center)
        display_surface.blit(menu_text, menu_rect)

    def __del__(self):
        # Close database connection when object is destroyed
        self.conn.close()
import pygame
import sqlite3
from pygame.locals import *
import os


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

    def on_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            # Check if search box is clicked
            if self.search_box.collidepoint(event.pos):
                self.search_active = True
            else:
                self.search_active = False

            # Check if return to menu button is clicked
            if self.return_to_menu_rect.collidepoint(event.pos):
                return "return_to_menu"

            # Check if a result is clicked
            for i, result in enumerate(self.search_results):
                result_rect = pygame.Rect(
                    self.search_box.left,
                    self.search_box.bottom + 20 + (i * 40),
                    self.search_box.width,
                    35
                )
                if result_rect.collidepoint(event.pos):
                    self.selected_result = result

        elif event.type == MOUSEMOTION:
            # Update hover states
            self.button_hovered = self.button_rect.collidepoint(event.pos)
            self.music_hovered = self.music_rect.collidepoint(event.pos)
            self.return_button_hovered = self.return_to_menu_rect.collidepoint(event.pos)

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
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            self.search_results = []

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
        pygame.draw.rect(display_surface, box_color, self.search_box, border_radius=10)

        # Draw search text
        text_surface = self.font.render(self.search_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.search_box.center)
        display_surface.blit(text_surface, text_rect)

        # Draw placeholder text if search box is empty
        if not self.search_text and not self.search_active:
            placeholder = self.font.render("Search molecules...", True, (100, 100, 100))
            placeholder_rect = placeholder.get_rect(center=self.search_box.center)
            display_surface.blit(placeholder, placeholder_rect)

        # Draw search results
        for i, result in enumerate(self.search_results):
            result_rect = pygame.Rect(
                self.search_box.left,
                self.search_box.bottom + 20 + (i * 40),
                self.search_box.width,
                35
            )

            # Highlight if this is the selected result
            if result == self.selected_result:
                pygame.draw.rect(display_surface, (200, 200, 200), result_rect, border_radius=5)
            else:
                pygame.draw.rect(display_surface, (169, 169, 169), result_rect, border_radius=5)

            # Display molecule information
            formula, ph, iupac, image = result
            text = f"{formula} - pH: {ph} - {iupac}"
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
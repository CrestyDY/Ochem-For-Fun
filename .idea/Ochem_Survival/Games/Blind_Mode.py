import pygame
import background
import sqlite3 as sql
import random as rd
import os
import time
from PIL import Image
from io import BytesIO


class Blind_Mode():
    def __init__(self, width, height, playground_rect, base_path, current_background, dark_mode, music_play, music_rect,
                 button_rect):
        
        self.width = width
        self.height = height
        self.size = (width, height)
        self.playground_rect = playground_rect
        self.scale_factor = min(width / 1600, height / 1000)
        self.base_path = base_path
        self.background_light = background.Background(os.path.join(base_path, 'images', 'background.jpg'), [0, 0])
        self.background_dark = background.Background(os.path.join(base_path, 'images', 'background-dark-mode.jpg'),[0, 0])
        self.current_background = current_background
        self.dark_mode = dark_mode
        self.music_play = music_play
        self.button_hovered = False

        self.Minigame_dictionary = {1: "Name To Structure", 2: "Structure To Name"}
        self.current_minigame = None
        self.current_compound = None
        self.cached_images = []

        
        self.answer_revealed = False
        self.show_next_button = False

        
        self.reveal_button_width = int(200 * self.scale_factor)
        self.reveal_button_height = int(50 * self.scale_factor)

        
        self.reveal_button_rect = pygame.Rect(
            (self.playground_rect.centerx - self.reveal_button_width // 2,
             self.playground_rect.bottom - 450 * self.scale_factor),
            (self.reveal_button_width, self.reveal_button_height)
        )

        
        self.next_button_rect = pygame.Rect(
            (self.playground_rect.centerx - self.reveal_button_width // 2,
             self.reveal_button_rect.bottom + 20 * self.scale_factor),
            (self.reveal_button_width, self.reveal_button_height)
        )

        
        self.reveal_button_hover = False
        self.next_button_hover = False

        self.button_rect = button_rect
        self.music_rect = music_rect
        self.button_hovered = False
        self.music_hovered = False
        self.return_to_menu = False
        self.menu_hover_state = False
        self.return_to_menu_hovered = False

        self.return_to_menu_rect = pygame.Rect(
            (self.playground_rect.topleft[0] + 20, self.playground_rect.topleft[1] + 20),
            (100, 50)
        )

        self.initialize_ui_elements()

        self.next_question = False

        self._running = True
        self.current_screen = "blind_mode"

    def select_random_minigame(self):
        """Randomly selects between Name To Structure and Structure To Name"""
        self.current_minigame = rd.choice(list(self.Minigame_dictionary.values()))
        self.answer_revealed = False
        self.show_next_button = False

    def toggle_background(self):
        "Toggle between light and dark backgrounds."
        if self.dark_mode:
            self.current_background = self.background_light
        else:
            self.current_background = self.background_dark
        self.dark_mode = not self.dark_mode

    def resize(self, new_width, new_height):

        self.width = new_width
        self.height = new_height
        self.size = (new_width, new_height)

        
        self.scale_factor = min(new_width / 1600, new_height / 1000)

        
        playground_width = int(1200 * self.scale_factor)
        playground_height = int(800 * self.scale_factor)

        
        playground_left = (new_width - playground_width) // 2
        playground_top = (new_height - playground_height) // 2

        self.playground_rect = pygame.Rect(
            playground_left,
            playground_top,
            playground_width,
            playground_height
        )

        self.reveal_button_width = int(200 * self.scale_factor)
        self.reveal_button_height = int(50 * self.scale_factor)

        self.reveal_button_rect = pygame.Rect(
            (self.playground_rect.centerx - self.reveal_button_width // 2,
             self.playground_rect.bottom - 450 * self.scale_factor),
            (self.reveal_button_width, self.reveal_button_height)
        )

        
        self.next_button_rect = pygame.Rect(
            (self.playground_rect.centerx - self.reveal_button_width // 2,
             self.reveal_button_rect.bottom + 20 * self.scale_factor),
            (self.reveal_button_width, self.reveal_button_height)
        )

        
        self.initialize_ui_elements()

        
        if self.current_compound:
            self.rescale_cached_images()

    def rescale_cached_images(self):

        if not self.current_compound:
            return

        self.cached_images = []
        image_data = self.current_compound[0]
        if image_data:
            pil_image = Image.open(BytesIO(image_data))

            
            print("Resizing occured. Button width: ", self.button_width, "\n self.button_height: ", self.button_height)
            scale = min(
                (self.button_width * 0.7) / pil_image.width,
                (self.button_height * 0.7) / pil_image.height
            )

            new_size = (
                int(pil_image.width * scale),
                int(pil_image.height * scale)
            )
            print("New size: ", new_size)

            pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)

            
            mode = pil_image.mode
            size = pil_image.size
            data = pil_image.tobytes()
            pygame_image = pygame.image.fromstring(data, size, mode)
            self.cached_images.append(pygame_image)
        else:
            self.cached_images.append(None)

    def initialize_ui_elements(self):
        scale_factor = self.scale_factor

        button_width = int(100 * scale_factor)
        button_height = int(50 * scale_factor)
        self.button_rect = pygame.Rect(self.width - button_width, 0, button_width, button_height)
        self.music_rect = pygame.Rect(self.width - button_width, button_height, button_width, button_height)

        self.return_to_menu_rect = pygame.Rect(
            (self.playground_rect.topleft[0] + int(20 * scale_factor),
             self.playground_rect.topleft[1] + int(20 * scale_factor)),
            (int(100 * scale_factor), int(50 * scale_factor))
        )

        self.button_width = int(300 * scale_factor)
        self.button_height = int(300 * scale_factor)
        self.button_margin = int(50 * scale_factor)

        title_font_size = max(int(36 * scale_factor), 12)
        small_font_size = max(int(16 * scale_factor), 10)

        self.font = pygame.font.SysFont('comicsansms', title_font_size)
        self.small_font = pygame.font.SysFont('comicsansms', small_font_size)

    def pause_music(self):
        if self.music_play:
            self.music_play = False
            pygame.mixer_music.pause()
        elif not self.music_play:
            self.music_play = True
            pygame.mixer_music.unpause()

    def load_new_question(self):
        try:
            ochem_database = sql.connect("ochem.db")
            cursor = ochem_database.cursor()

            cursor.execute("SELECT MIN(id), MAX(id) FROM ochem_table;")
            min_id, max_id = cursor.fetchone()

            if min_id is None or max_id is None:
                raise ValueError("Not enough compounds in database")

            random_compounds = rd.sample(range(min_id, max_id + 1), 1)

            if self.current_minigame == "Name To Structure":
                extract_query = """
                SELECT image_file, iupac from ochem_table
                WHERE id in (?)"""

                cursor.execute(extract_query, random_compounds)
                self.current_compound = cursor.fetchone()


                if not self.current_compound:
                    print("No compounds found for Name To Structure")
                    return False

            elif self.current_minigame == "Structure To Name":
                extract_query = """
                SELECT image_file, iupac from ochem_table
                WHERE id in (?)"""

                cursor.execute(extract_query, random_compounds)
                self.current_compound = cursor.fetchone()

                if not self.current_compound:
                    print("No compounds found for Structure To Name")
                    return False

            self.cached_images = []

            image_data = self.current_compound[0]
            if image_data:
                pil_image = Image.open(BytesIO(image_data))
                img_width, img_height = pil_image.size
                scale = min(self.button_width / img_width, self.button_height / img_height)
                new_size = (int(img_width * scale * 0.8), int(img_height * scale * 0.8))
                pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)

                
                mode = pil_image.mode
                size = pil_image.size
                data = pil_image.tobytes()
                pygame_image = pygame.image.fromstring(data, size, mode)
                self.cached_images.append(pygame_image)
            else:
                self.cached_images.append(None)
            ochem_database.close()
            return True

        except Exception as e:
            print(f"Database error in load_new_question: {e}")
            return False

    def Structure_To_Name(self, surface):
        if not self.current_compound:
            print("No compounds available for Structure to Name")
            return

        
        instructions_text = "Name the following structure:"
        instructions_surface = self.font.render(instructions_text, True, (0, 0, 0))
        instructions_rect = instructions_surface.get_rect(
            center=(self.playground_rect.centerx, self.playground_rect.y + 50)
        )
        surface.blit(instructions_surface, instructions_rect)

        
        if self.cached_images[0]:
            structure_image = self.cached_images[0]
            image_rect = structure_image.get_rect(
                centerx=self.playground_rect.centerx,
                top=instructions_rect.bottom + 50  
            )
            surface.blit(structure_image, image_rect)

            
            self.reveal_button_rect.centerx = self.playground_rect.centerx
            self.reveal_button_rect.top = image_rect.bottom + 50

    def Name_To_Structure(self, surface):
        if not self.current_compound:
            print("No compounds available for Name to Structure")
            return

        
        instructions_font = self.font
        instructions_text = "Draw the structure of the following compound: "
        instructions_surface = instructions_font.render(instructions_text, True, (0, 0, 0))
        instructions_rect = instructions_surface.get_rect(
            center=(self.playground_rect.centerx, self.playground_rect.y + 50))
        surface.blit(instructions_surface, instructions_rect)

        
        compound_font = pygame.font.SysFont('comicsansms', int(24 * self.scale_factor))
        compound_text = str(self.current_compound[1])
        wrapped_lines = self.render_wrapped_text(compound_text, compound_font, self.playground_rect.width - 40)

        
        text_bottom = instructions_rect.bottom + 20
        for i, line in enumerate(wrapped_lines):
            line_rect = line.get_rect(
                centerx=self.playground_rect.centerx,
                top=text_bottom + (i * compound_font.get_linesize())
            )
            surface.blit(line, line_rect)

            
            self.reveal_button_rect.centerx = self.playground_rect.centerx
            self.reveal_button_rect.top = line_rect.bottom + 50

    def draw_reveal_button(self, surface):
        """Draws the reveal answer button"""
        button_color = (100, 100, 100) if self.reveal_button_hover else (169, 169, 169)
        pygame.draw.rect(surface, button_color, self.reveal_button_rect, border_radius=10)

        button_text = "Reveal Answer"
        text_color = (255, 255, 255) if self.dark_mode else (0, 0, 0)
        button_font = pygame.font.SysFont('comicsansms', int(24 * self.scale_factor))
        text_surface = button_font.render(button_text, True, text_color)
        text_rect = text_surface.get_rect(center=self.reveal_button_rect.center)
        surface.blit(text_surface, text_rect)

    def draw_next_button(self, surface):
        """Draws the next question button"""
        button_color = (100, 100, 100) if self.next_button_hover else (169, 169, 169)
        pygame.draw.rect(surface, button_color, self.next_button_rect, border_radius=10)

        button_text = "Next Question"
        text_color = (255, 255, 255) if self.dark_mode else (0, 0, 0)
        button_font = pygame.font.SysFont('comicsansms', int(24 * self.scale_factor))
        text_surface = button_font.render(button_text, True, text_color)
        text_rect = text_surface.get_rect(center=self.next_button_rect.center)
        surface.blit(text_surface, text_rect)

    def draw_answer(self, surface):
        """Draws the answer for the current question"""
        if self.current_minigame == "Name To Structure":
            
            
            compound_font = pygame.font.SysFont('comicsansms', int(24 * self.scale_factor))
            compound_text = str(self.current_compound[1])
            wrapped_lines = self.render_wrapped_text(compound_text, compound_font, self.playground_rect.width - 40)

            
            text_bottom = (self.playground_rect.y + 50 +  
                           compound_font.get_linesize() +  
                           (len(wrapped_lines) * compound_font.get_linesize()))

            if self.cached_images[0]:
                image = self.cached_images[0]
                image_rect = image.get_rect(
                    centerx=self.playground_rect.centerx,
                    top=text_bottom + 50  
                )
                surface.blit(image, image_rect)

                self.next_button_rect.centerx = self.playground_rect.centerx
                self.next_button_rect.top = image_rect.bottom + 50

        else:  
            
            
            if self.cached_images[0]:
                image = self.cached_images[0]
                image_rect = image.get_rect(
                    centerx=self.playground_rect.centerx,
                    top=self.playground_rect.y + 100  
                )

                
                answer_font = pygame.font.SysFont('comicsansms', int(24 * self.scale_factor))
                answer_text = self.current_compound[1]
                answer_lines = self.render_wrapped_text(answer_text, answer_font, self.playground_rect.width - 40)

                text_top = image_rect.bottom + 50  
                for i, line in enumerate(answer_lines):
                    line_rect = line.get_rect(
                        centerx=self.playground_rect.centerx,
                        top=text_top + (i * answer_font.get_linesize())
                    )
                    surface.blit(line, line_rect)

                
                self.next_button_rect.centerx = self.playground_rect.centerx
                self.next_button_rect.top = text_top + (len(answer_lines) * answer_font.get_linesize()) + 50

        
        self.reveal_button_rect.centerx = self.playground_rect.centerx
        self.reveal_button_rect.top = self.next_button_rect.top

    def render_wrapped_text(self, text, font, max_width):
        """Helper function to wrap text to multiple lines"""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            test_surface = font.render(test_line, True, (0, 0, 0))

            if test_surface.get_width() > max_width:
                current_line.pop()
                if current_line:
                    lines.append(font.render(' '.join(current_line), True, (0, 0, 0)))
                current_line = [word]

        if current_line:
            lines.append(font.render(' '.join(current_line), True, (0, 0, 0)))

        return lines

    def on_event(self, event):
        """Handle mouse events for the buttons"""
        if event.type == pygame.MOUSEMOTION:
            self.button_hovered = self.button_rect.collidepoint(event.pos)
            self.music_hovered = self.music_rect.collidepoint(event.pos)
            self.return_to_menu_hovered = self.return_to_menu_rect.collidepoint(event.pos)
            mouse_pos = pygame.mouse.get_pos()
            self.reveal_button_hover = self.reveal_button_rect.collidepoint(mouse_pos)
            self.next_button_hover = self.next_button_rect.collidepoint(mouse_pos) if self.show_next_button else False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.reveal_button_rect.collidepoint(mouse_pos) and not self.answer_revealed:
                self.answer_revealed = True
                self.show_next_button = True
            elif self.next_button_rect.collidepoint(mouse_pos) and self.show_next_button:
                self.next_question = True
            elif self.music_rect.collidepoint(event.pos):
                self.pause_music()
            elif self.button_rect.collidepoint(event.pos):
                self.toggle_background()
            elif self.return_to_menu_rect.collidepoint(event.pos):
                self.return_to_menu = True
                self._running = False

        elif event.type == pygame.VIDEORESIZE:
            if event.type == pygame.VIDEORESIZE:
                new_width, new_height = event.w, event.h
                self.resize(new_width, new_height)

                
                self._display_surf = pygame.display.set_mode(
                    (new_width, new_height),
                    pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
                )

    def run_once(self, surface):
        
        surface.blit(self.current_background.image, self.current_background.rect)

        playground_surface = pygame.Surface(
            (self.playground_rect.width, self.playground_rect.height), pygame.SRCALPHA)
        playground_color = (150, 150, 150, 180) if self.dark_mode else (169, 169, 169, 180)
        pygame.draw.rect(playground_surface, playground_color,
                         playground_surface.get_rect(), border_radius=50)
        surface.blit(playground_surface, self.playground_rect)

        
        scale_factor = min(self.width / 1600, self.height / 1000)
        font_size = max(10, int(20 * scale_factor))

        
        button_color = (100, 100, 100) if self.button_hovered else (169, 169, 169) if self.dark_mode else (
        230, 230, 230)
        pygame.draw.rect(surface, button_color, self.button_rect, border_radius=10)

        
        music_button_color = (100, 100, 100) if self.music_hovered else (169, 169, 169) if self.dark_mode else (
        230, 230, 230)
        pygame.draw.rect(surface, music_button_color, self.music_rect, border_radius=10)

        
        text_color = (255, 255, 255) if self.dark_mode else (0, 0, 0)
        button_font = pygame.font.Font('freesansbold.ttf', font_size)

        
        button_text = "Light" if self.dark_mode else "Lighter"
        button_text_surface = button_font.render(button_text, True, text_color)
        button_text_rect = button_text_surface.get_rect(center=self.button_rect.center)
        surface.blit(button_text_surface, button_text_rect)

        
        music_button_text = "Playing" if self.music_play else "Paused"
        music_button_text_surface = button_font.render(music_button_text, True, text_color)
        music_button_text_rect = music_button_text_surface.get_rect(center=self.music_rect.center)
        surface.blit(music_button_text_surface, music_button_text_rect)

        
        menu_color = (140, 140, 140) if self.return_to_menu_hovered else (169, 169, 169) if self.dark_mode else (
        230, 230, 230)
        pygame.draw.rect(surface, menu_color, self.return_to_menu_rect, border_radius=10)
        menu_font = pygame.font.SysFont('comicsansms', font_size)
        menu_text = "Menu"
        menu_surface = menu_font.render(menu_text, True, text_color)
        menu_rect = menu_surface.get_rect(center=self.return_to_menu_rect.center)
        surface.blit(menu_surface, menu_rect)

        
        if not self.current_compound or self.next_question:
            self.select_random_minigame()
            if self.load_new_question():
                self.next_question = False
                self.answer_revealed = False
                self.show_next_button = False
            else:
                print("Failed to load new question")
                return

        
        if self.current_minigame == "Name To Structure":
            self.Name_To_Structure(surface)
        else:
            self.Structure_To_Name(surface)

        
        if not self.answer_revealed:
            self.draw_reveal_button(surface)
        else:
            
            self.draw_answer(surface)

            
            if self.show_next_button:
                self.draw_next_button(surface)

        pygame.display.flip()

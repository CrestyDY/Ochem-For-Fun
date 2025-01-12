import pygame
import time
import background
import sqlite3 as sql
import random as rd
import os
from PIL import Image
from io import BytesIO
import math

class Time_Trial:
    def __init__(self, width, height, playground_rect, base_path, current_background, dark_mode, music_play, music_rect,button_rect):
        
        self.playground_rect = playground_rect
        self.scale_factor = min(width / 1600, height / 1000)
        self.width = width
        self.height = height
        self.size = (width, height)

        
        self.base_path = base_path

        
        self.background_light = background.Background(os.path.join(base_path, 'images', 'background.jpg'), [0, 0])
        self.background_dark = background.Background(os.path.join(base_path, 'images', 'background-dark-mode.jpg'), [0, 0])

        
        self.clock = pygame.time.Clock()
        self.start_time = None
        self.time_limit = 60
        self.time_left = self.time_limit
        pygame.font.init()
        self.font = pygame.font.SysFont('comicsansms', 36)

        
        self.selected_answer = None
        self.current_compounds = None
        self.correct_answer = None
        self.score = 0
        self.current_question_start = None
        self.question_duration = 60  
        self.feedback_displayed = False
        self.feedback_start = None
        self.feedback_duration = 0.5

        
        self.Minigame_dictionary = {1: "Most Acidic", 2: "Name To Structure", 3: "Structure To Name"}
        self.current_minigame = None
        self.question_answered = False

        
        self.button_width = 300
        self.button_height = 300
        self.button_margin = 50
        self.button_rects = []
        self.button_color = (200, 200, 200)

        self.cached_images = []

        
        self.button_hover_states = [False, False, False, False]
        self.game_over_button_hover = False

        
        self.game_over_button_rect = pygame.Rect(
            self.playground_rect.centerx - 150,
            self.playground_rect.centery + 100,
            300,
            50
        )
        self.return_to_menu = False
        self.menu_hover_state = False

        

        
        self.button_rect = button_rect
        self.music_rect = music_rect
        self.button_hovered = False
        self.music_hovered = False

        
        self.return_to_menu_rect = pygame.Rect(
            (self.playground_rect.topleft[0] + 20, self.playground_rect.topleft[1] + 20),
            (100, 50)
        )
        self.initialize_ui_elements()
        self.setup_button_rects()


        
        self._running = True
        self.current_screen = "time_trial"


        self.high_score = self.load_high_score()

        
        self.current_background = current_background
        self.dark_mode = dark_mode
        self.music_play = music_play

    def get_image_path(self, filename):
        return os.path.join(self.base_path, 'images', filename)

    def initialize_ui_elements(self):
        """
        Reinitialize all UI elements with proper scaling
        """

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


        self.game_over_button_rect = pygame.Rect(
            self.playground_rect.centerx - int(150 * scale_factor),
            self.playground_rect.centery + int(100 * scale_factor),
            int(300 * scale_factor),
            int(50 * scale_factor)
        )


        self.button_width = int(300 * scale_factor)
        self.button_height = int(300 * scale_factor)
        self.button_margin = int(50 * scale_factor)


        title_font_size = max(int(36 * scale_factor), 12)
        small_font_size = max(int(16 * scale_factor), 10)


        self.font = pygame.font.SysFont('comicsansms', title_font_size)
        self.small_font = pygame.font.SysFont('comicsansms', small_font_size)

    def load_high_score(self):
        """Load the high score from a file"""
        try:
            with open('High_Scores.txt', 'r') as file:
                return int(file.read().strip())
        except (FileNotFoundError, ValueError):
            return 0

    def save_high_score(self):
        """Save the high score to a file if current score is higher"""
        if self.score > self.high_score:
            with open('High_Scores.txt', 'w') as file:
                file.write(str(self.score))
            self.high_score = self.score

    def select_random_minigame(self):
        """Randomly select a minigame type"""
        game_type = rd.randint(1, 3)
        self.current_minigame = self.Minigame_dictionary[game_type]
        print(f"Selected minigame: {self.current_minigame}")
    def start_timer(self):
        self.start_time = time.time()

    def update_timer(self):
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            self.time_left = max(0, self.time_limit - int(elapsed_time))
        return self.time_left

    def pause_music(self):
        if self.music_play:
            self.music_play = False
            pygame.mixer_music.pause()
        elif not self.music_play:
            self.music_play = True
            pygame.mixer_music.unpause()

    def draw_timer(self, surface):
        time_text = f"Time Left: {self.time_left}s"
        text_surface = self.font.render(time_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.centerx = self.playground_rect.centerx
        text_rect.y = self.playground_rect.y
        surface.blit(text_surface, text_rect)

    def draw_game_over(self, surface):
        game_over_text = "Time's Up! Game Over!"
        text_surface = self.font.render(game_over_text, True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 50))
        surface.blit(text_surface, text_rect)


        score_text = f"Final Score: {self.score}"
        score_surface = self.font.render(score_text, True, (0, 0, 0))
        score_rect = score_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        surface.blit(score_surface, score_rect)


        button_color = (140, 140, 140) if self.game_over_button_hover else (200, 200, 200)
        pygame.draw.rect(surface, button_color, self.game_over_button_rect, border_radius=10)
        button_font = pygame.font.SysFont('comicsansms', 24)
        button_text = "Return to Menu"
        button_text_surface = button_font.render(button_text, True, (0, 0, 0))
        button_text_rect = button_text_surface.get_rect(center=self.game_over_button_rect.center)
        surface.blit(button_text_surface, button_text_rect)

        self.save_high_score()
        high_score_font = pygame.font.SysFont('comicsansms', 24)
        high_score_text = f"High Score: {self.high_score}"
        high_score_surface = high_score_font.render(high_score_text, True, (0, 0, 0))
        high_score_rect = high_score_surface.get_rect(
            center=(surface.get_width() // 2, surface.get_height() // 2 + 50)
        )
        surface.blit(high_score_surface, high_score_rect)

    def toggle_background(self):
        """Toggle between light and dark backgrounds."""
        if self.dark_mode:
            self.current_background = self.background_light
        else:
            self.current_background = self.background_dark
        self.dark_mode = not self.dark_mode


    def truncate_text(self, text, max_length=50):
        if len(text) <= max_length:
            return text
        return text[:max_length] + '...'

    def render_wrapped_text(self, text, font, max_width, color=(0, 0, 0)):
        """
        Render text that wraps or truncates to fit within max_width
        """
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, color)

            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:

                if not current_line:
                    test_surface = font.render(word[:int(max_width / font.get_height())] + '...', True, color)
                    lines.append(test_surface)
                    break


                lines.append(font.render(' '.join(current_line), True, color))
                current_line = [word]

        if current_line:
            lines.append(font.render(' '.join(current_line), True, color))

        return lines

    def setup_button_rects(self):
        """
        Create button rectangles dynamically based on minigame type and scaling
        with positioning relative to the playground rect
        """
        if self.current_minigame is None:
            self.select_random_minigame()

        scale_factor = self.scale_factor
        playground_width = self.playground_rect.width
        playground_height = self.playground_rect.height


        button_width = int(playground_width * 0.20)
        button_height = int(playground_height * 0.31)
        button_margin = int(playground_width * 0.03)


        total_grid_width = 2 * button_width + button_margin
        total_grid_height = 2 * button_height + button_margin

        start_x = self.playground_rect.x + (self.playground_rect.width - total_grid_width) // 2
        start_y = self.playground_rect.y + (self.playground_rect.height - total_grid_height) // 1.60


        if self.current_minigame == "Structure To Name":
            button_width = int(playground_width * 0.40)
            button_height = int(playground_height * 0.15)
            button_margin = int(playground_width * 0.02)

            start_x = self.playground_rect.x + (self.playground_rect.width - (2 * button_width) - button_margin) // 2
            start_y = self.playground_rect.y + self.playground_rect.height * 0.5


        self.button_rects = [
            pygame.Rect(start_x, start_y, button_width, button_height),
            pygame.Rect(start_x + button_width + button_margin, start_y, button_width, button_height),
            pygame.Rect(start_x, start_y + button_height + button_margin, button_width, button_height),
            pygame.Rect(start_x + button_width + button_margin, start_y + button_height + button_margin,
                        button_width, button_height)
        ]

    def resize(self, new_width, new_height):
        """
        Comprehensive window resizing method
        """

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


        self.initialize_ui_elements()
        self.setup_button_rects()


        if self.current_compounds:
            self.rescale_cached_images()

    def check_hover(self, mouse_pos):

        if self.time_left > 0:
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(mouse_pos):
                    self.button_hover_states[i] = True
                else:
                    self.button_hover_states[i] = False
            if self.return_to_menu_rect.collidepoint(mouse_pos):
                self.menu_hover_state = True
            else:
                self.menu_hover_state = False


        if self.time_left <= 0:
            self.game_over_button_hover = self.game_over_button_rect.collidepoint(mouse_pos)

    def rescale_cached_images(self):
        """
        Rescale cached images based on current button dimensions
        This method can be called during window resize events
        """
        if not self.current_compounds:
            return


        self.cached_images = []
        for compound in self.current_compounds:
            image_data = compound[3] if self.current_minigame == "Most Acidic" else compound[0]
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

    def load_new_question(self):
        try:
            ochem_database = sql.connect("ochem.db")
            cursor = ochem_database.cursor()

            cursor.execute("SELECT MIN(id), MAX(id) FROM ochem_table;")
            min_id, max_id = cursor.fetchone()

            if min_id is None or max_id is None or max_id - min_id + 1 < 4:
                raise ValueError("Not enough compounds in database")

            random_compounds = rd.sample(range(min_id, max_id + 1), 4)

            if self.current_minigame == "Most Acidic":
                extract_query = """
                    SELECT DISTINCT pH, chemical_formula, iupac, image_file 
                    FROM ochem_table WHERE id IN (?, ?, ?, ?);
                """
                cursor.execute(extract_query, random_compounds)
                compounds = cursor.fetchall()

                if not compounds:
                    print("No compounds found for Most Acidic")
                    return False


                compounds = sorted(compounds, key=lambda x: x[0])
                self.correct_answer = 0


                display_order = list(range(4))
                rd.shuffle(display_order)
                self.current_compounds = [compounds[i] for i in display_order]

                self.correct_answer = display_order.index(0)

            elif self.current_minigame == "Name To Structure":
                extract_query = """
                SELECT image_file, iupac from ochem_table
                WHERE id in (?,?,?,?)"""

                cursor.execute(extract_query, random_compounds)
                compounds = cursor.fetchall()

                if not compounds:
                    print("No compounds found for Name To Structure")
                    return False

                self.correct_answer = 0

                display_order = list(range(4))
                rd.shuffle(display_order)
                self.current_compounds = [compounds[i] for i in display_order]
                self.correct_answer = display_order.index(0)

            elif self.current_minigame == "Structure To Name":
                extract_query = """
                SELECT image_file, iupac from ochem_table
                WHERE id in (?,?,?,?)"""

                cursor.execute(extract_query, random_compounds)
                compounds = cursor.fetchall()

                if not compounds:
                    print("No compounds found for Structure To Name")
                    return False
                self.corrent_answer = 0
                display_order = list(range(4))
                rd.shuffle(display_order)
                self.current_compounds = compounds
                self.correct_answer = display_order.index(0)


            self.cached_images = []
            for compound in self.current_compounds:
                image_data = compound[3] if self.current_minigame == "Most Acidic" else compound[0]
                if image_data:
                    pil_image = Image.open(BytesIO(image_data))



                    scale = min(
                        (self.button_width * 0.7) / pil_image.width,
                        (self.button_height * 0.7) / pil_image.height
                    )

                    new_size = (
                        int(pil_image.width * scale),
                        int(pil_image.height * scale)
                    )

                    pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)


                    mode = pil_image.mode
                    size = pil_image.size
                    data = pil_image.tobytes()
                    pygame_image = pygame.image.fromstring(data, size, mode)
                    self.cached_images.append(pygame_image)
                else:
                    self.cached_images.append(None)

            ochem_database.close()

            self.current_question_start = time.time()
            self.feedback_displayed = False
            self.selected_answer = None

            return True

        except Exception as e:
            print(f"Database error in load_new_question: {e}")
            return False

    def Most_Acidic(self, surface):
        if not self.current_compounds:
            if not self.load_new_question():
                print("No Compounds")
                return


        self.draw_timer(surface)


        timer_rect = self.font.render(f"Time Left: {self.time_left}s", True, (255, 255, 255)).get_rect()
        timer_bottom = self.playground_rect.y + timer_rect.height + 10


        instructions_font = self.font
        instructions_text = "Select The Most Acidic Compound:"
        instructions_surface = instructions_font.render(instructions_text, True, (0, 0, 0))
        instructions_rect = instructions_surface.get_rect(
            center=(self.playground_rect.centerx, timer_bottom + 20))
        surface.blit(instructions_surface, instructions_rect)


        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, (0, 0, 0))
        score_rect = score_surface.get_rect(topright=(self.playground_rect.right - 20, self.playground_rect.y + 20))
        surface.blit(score_surface, score_rect)

        if not self.button_rects or not self.current_compounds:
            print("Button rects or compounds are not initialized!")
            print("Button rects:", self.button_rects)
            return


        for i, (compound, button_rect) in enumerate(zip(self.current_compounds, self.button_rects)):

            button_color = (140, 140, 140) if self.button_hover_states[i] else self.button_color
            if self.feedback_displayed and i == self.selected_answer:
                button_color = (0, 255, 0) if i == self.correct_answer else (255, 0, 0)
            pygame.draw.rect(surface, button_color, button_rect, border_radius=10)


            if self.cached_images[i]:
                image_rect = self.cached_images[i].get_rect(center=button_rect.center)
                surface.blit(self.cached_images[i], image_rect)












        current_time = time.time()

        if self.feedback_displayed and current_time - self.feedback_start >= self.feedback_duration:
            print("Loading new question due to feedback duration")
            self.select_random_minigame()
            self.load_new_question()
        elif not self.feedback_displayed and current_time - self.current_question_start >= self.question_duration:

            self.selected_answer = -1
            self.handle_answer()

    def Name_To_Structure(self, surface):
        if not self.current_compounds:
            print("No compounds available for Name to Structure")
            return


        self.draw_timer(surface)


        timer_rect = self.font.render(f"Time Left: {self.time_left}s", True, (255, 255, 255)).get_rect()
        timer_bottom = self.playground_rect.y + timer_rect.height + 10


        instructions_font = self.font
        instructions_text = "Match the following IUPAC name to its structure:"
        instructions_surface = instructions_font.render(instructions_text, True, (0, 0, 0))
        instructions_rect = instructions_surface.get_rect(
            center=(self.playground_rect.centerx, timer_bottom + 20))
        surface.blit(instructions_surface, instructions_rect)


        compound_font = pygame.font.SysFont('comicsansms', 20)
        compound_text = str(self.current_compounds[self.correct_answer][1])
        compound_surface = compound_font.render(compound_text, True, (0, 0, 0))
        compound_rect = compound_surface.get_rect(
            center=(self.playground_rect.centerx, instructions_rect.bottom + 20)
        )
        surface.blit(compound_surface, compound_rect)


        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, (0, 0, 0))
        score_rect = score_surface.get_rect(topright=(self.playground_rect.right - 20, self.playground_rect.y + 20))
        surface.blit(score_surface, score_rect)


        for i, (compound, button_rect) in enumerate(zip(self.current_compounds, self.button_rects)):

            button_color = (140, 140, 140) if self.button_hover_states[i] else self.button_color
            if self.feedback_displayed and i == self.selected_answer:
                button_color = (0, 255, 0) if i == self.correct_answer else (255, 0, 0)
            pygame.draw.rect(surface, button_color, button_rect, border_radius=10)


            if self.cached_images[i]:
                image_rect = self.cached_images[i].get_rect(center=button_rect.center)
                surface.blit(self.cached_images[i], image_rect)


        current_time = time.time()
        if self.feedback_displayed and current_time - self.feedback_start >= self.feedback_duration:
            self.select_random_minigame()
            self.load_new_question()
        elif not self.feedback_displayed and current_time - self.current_question_start >= self.question_duration:

            self.selected_answer = -1
            self.handle_answer()

    def Structure_To_Name(self, surface):
        if not self.current_compounds:
            print("No compounds available for Structure to Name")
            return


        timer_text = f"Time Left: {self.time_left}s"
        timer_surface = self.font.render(timer_text, True, (255, 255, 255))
        timer_rect = timer_surface.get_rect(
            topleft=(self.playground_rect.x + 20, self.playground_rect.y + 20)
        )
        timer_bottom = timer_rect.bottom + int(self.scale_factor * 10)


        instructions_text = "Match the structure to its IUPAC name:"
        instructions_surface = self.font.render(instructions_text, True, (0, 0, 0))
        instructions_rect = instructions_surface.get_rect(
            center=(self.playground_rect.centerx, timer_bottom + int(self.scale_factor * 40))

        )
        surface.blit(instructions_surface, instructions_rect)


        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, (0, 0, 0))
        score_rect = score_surface.get_rect(topright=(self.playground_rect.right - 20, self.playground_rect.y + 20))
        surface.blit(score_surface, score_rect)


        for i, (compound, button_rect) in enumerate(zip(self.current_compounds, self.button_rects)):

            button_color = (140, 140, 140) if self.button_hover_states[i] else self.button_color
            if self.feedback_displayed and i == self.selected_answer:
                button_color = (0, 255, 0) if i == self.correct_answer else (255, 0, 0)
            pygame.draw.rect(surface, button_color, button_rect, border_radius=10)

            name_font = pygame.font.SysFont('comicsansms', 16)
            name_lines = self.render_wrapped_text(compound[1], name_font, button_rect.width - 10)
            total_text_height = len(name_lines) * name_font.get_linesize()


            start_y = button_rect.centery - total_text_height // 2

            for i, line_surface in enumerate(name_lines):
                line_rect = line_surface.get_rect(
                    centerx=button_rect.centerx,
                    top=start_y + i * name_font.get_linesize()
                )
                surface.blit(line_surface, line_rect)

        image_y = instructions_rect.bottom


        if self.cached_images[self.correct_answer]:
            structure_image = self.cached_images[self.correct_answer]
            image_rect = structure_image.get_rect(
                center=(self.playground_rect.centerx, instructions_rect.centery + structure_image.get_height() // 2 + self.scale_factor * 40)
            )
            surface.blit(structure_image, image_rect)


        current_time = time.time()
        if self.feedback_displayed and current_time - self.feedback_start >= self.feedback_duration:
            self.select_random_minigame()
            self.load_new_question()
        elif not self.feedback_displayed and current_time - self.current_question_start >= self.question_duration:

            self.selected_answer = -1
            self.handle_answer()
























    def update_playground_rect(self):
        scale_factor = min(self.width / 1600, self.height / 1000)
        playground_width = int(1200 * scale_factor)
        playground_height = int(800 * scale_factor)


        playground_left = (self.width - playground_width) // 2
        playground_top = (self.height - playground_height) // 2

        self.playground_rect = pygame.Rect(
            playground_left,
            playground_top,
            playground_width,
            playground_height
        )

    def update_layout(self):

        scale_factor = min(self.width / 1600, self.height / 1000)

        self.update_playground_rect()


        button_width = int(100 * scale_factor)
        button_height = int(1000 * scale_factor)
        button_x = self.width - button_width
        button_y = 0

        self.button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    def handle_answer(self):
        """Process the selected answer and update game state"""
        if self.selected_answer == self.correct_answer:
            self.score += 1


        self.feedback_displayed = True
        self.feedback_start = time.time()

    def handle_click(self, pos):
        """Handle mouse clicks for answer selection"""
        
        if not self.current_compounds or self.feedback_displayed:
            return
        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(pos):
                self.selected_answer = i
                self.handle_answer()
                break

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
        button_color = (100,100,100) if self.button_hovered else (169, 169, 169) if self.dark_mode else (230, 230, 230)
        pygame.draw.rect(surface, button_color, self.button_rect, border_radius=10)  
        music_button_color = (100,100,100) if self.music_hovered else (169, 169, 169) if self.dark_mode else (230, 230, 230)
        pygame.draw.rect(surface, music_button_color, self.music_rect, border_radius=10)

        button_text = "Light" if self.dark_mode else "Lighter"
        text_color = (255, 255, 255) if self.dark_mode else (0, 0, 0)
        button_font = pygame.font.Font('freesansbold.ttf', font_size)
        button_text_surface = button_font.render(button_text, True, text_color)
        button_text_rect = button_text_surface.get_rect(center=self.button_rect.center)
        surface.blit(button_text_surface, button_text_rect)

        music_button_text = "Playing" if self.music_play else "Paused"
        text_color = (255, 255, 255) if self.dark_mode else (0, 0, 0)
        music_button_font = pygame.font.Font('freesansbold.ttf', font_size)
        music_button_text_surface = music_button_font.render(music_button_text, True, text_color)
        music_button_text_rect = music_button_text_surface.get_rect(center = self.music_rect.center)
        surface.blit(music_button_text_surface, music_button_text_rect)

        
        menu_color = (140, 140, 140) if self.menu_hover_state else (169, 169, 169) if self.dark_mode else (
        230, 230, 230)
        pygame.draw.rect(surface, menu_color, self.return_to_menu_rect, border_radius=10)
        menu_font = pygame.font.SysFont('comicsansms', font_size)
        menu_text = "Menu"
        menu_surface = menu_font.render(menu_text, True, text_color)
        menu_rect = menu_surface.get_rect(center=self.return_to_menu_rect.center)
        surface.blit(menu_surface, menu_rect)

        
        if self.start_time is None:
            self.start_timer()

        self.time_left = self.update_timer()

        if self.time_left > 0:
            self.draw_timer(surface)

            
            if not self.current_compounds or self.question_answered:
                
                self.select_random_minigame()
                self.load_new_question()

                
                if self.load_new_question():
                    self.question_answered = False
                else:
                    print("Failed to load new question")
                    return

            
            if self.current_minigame == "Most Acidic":
                self.setup_button_rects()
                self.Most_Acidic(surface)
            elif self.current_minigame == "Name To Structure":
                self.setup_button_rects()
                self.Name_To_Structure(surface)
            elif self.current_minigame == "Structure To Name":
                self.setup_button_rects()
                self.Structure_To_Name(surface)

        else:
            self.draw_game_over(surface)

        pygame.display.flip()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

        if event.type == pygame.VIDEORESIZE:
            new_width, new_height = event.w, event.h
            self.resize(new_width, new_height)

            
            self._display_surf = pygame.display.set_mode(
                (new_width, new_height),
                pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
            )

        elif event.type == pygame.MOUSEMOTION:
            
            self.check_hover(event.pos)
            self.button_hovered = self.button_rect.collidepoint(event.pos)
            self.music_hovered = self.music_rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            
            if self.time_left <= 0 and self.game_over_button_rect.collidepoint(event.pos):
                self.return_to_menu = True
                self._running = False
            
            if self.music_rect.collidepoint(event.pos):
                self.pause_music()
            
            elif self.button_rect.collidepoint(event.pos):
                self.toggle_background()
            
            elif self.return_to_menu_rect.collidepoint(event.pos):
                print("Return to Menu button clicked!")
                print(f"Time left: {self.time_left}")
                self.return_to_menu = True
                self._running = False
            elif self.time_left > 0:  
                self.handle_click(event.pos)

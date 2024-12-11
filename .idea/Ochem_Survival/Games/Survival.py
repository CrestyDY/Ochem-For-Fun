import pygame
import background
import sqlite3 as sql
import random as rd
import os
import time
from PIL import Image
from io import BytesIO

class Survival:
    def __init__(self, width, height, playground_rect, base_path, current_background, dark_mode, music_play):
        # Playground rect from App
        self.playground_rect = playground_rect
        self.scale_factor = min(width / 1600, height / 1000)
        self.width = width
        self.height = height
        self.size = (width, height)

        # Background and mode
        self.base_path = base_path

        # Background setup
        self.background_light = background.Background(os.path.join(base_path, 'images', 'background.jpg'), [0, 0])
        self.background_dark = background.Background(os.path.join(base_path, 'images', 'background-dark-mode.jpg'), [0, 0])

        # Game state
        self.selected_answer = None
        self.current_compounds = None
        self.correct_answer = None
        self.score = 0
        self.current_question_start = None
        self.question_duration = float("inf")
        self.feedback_displayed = False
        self.feedback_start = None
        self.feedback_duration = 0.5

        # Minigames
        self.Minigame_dictionary = {1: "Most Acidic", 2: "Name To Structure", 3: "Structure To Name"}
        self.current_minigame = None
        self.question_answered = False

        # Button dimensions for answers
        self.button_width = 300
        self.button_height = 300
        self.button_margin = 50
        self.button_rects = []
        self.button_color = (200, 200, 200)

        self.cached_images = []

        # Hover effect
        self.button_hover_states = [False, False, False, False]
        self.game_over_button_hover = False

        # Game over button
        self.game_over_button_rect = pygame.Rect(
            self.playground_rect.centerx - 150,
            self.playground_rect.centery + 100,
            300,
            50
        )
        self.return_to_menu = False
        self.menu_hover_state = False

        # Initialize UI elements with initial scaling

        # Button rects based on App's width
        self.button_rect = pygame.Rect(width - 100, 0, 100, 50)
        self.music_rect = pygame.Rect(width - 100, 50, 100, 50)

        # Return to menu button
        self.return_to_menu_rect = pygame.Rect(
            (self.playground_rect.topleft[0] + 20, self.playground_rect.topleft[1] + 20),
            (100, 50)
        )
        self.initialize_ui_elements()
        self.setup_button_rects()


        # Remove duplicate initialization of these attributes
        self._running = True
        self.current_screen = "survival"

        # Use passed background and dark mode
        self.current_background = current_background
        self.dark_mode = dark_mode
        self.music_play = music_play


        self.remaining_lives = 3

    def get_image_path(self, filename):
        return os.path.join(self.base_path, 'images', filename)

    def initialize_ui_elements(self):
        """
        Reinitialize all UI elements with proper scaling
        """
        # Calculate scaled dimensions
        scale_factor = self.scale_factor

        # Button rects based on scaled width
        button_width = int(100 * scale_factor)
        button_height = int(50 * scale_factor)
        self.button_rect = pygame.Rect(self.width - button_width, 0, button_width, button_height)
        self.music_rect = pygame.Rect(self.width - button_width, button_height, button_width, button_height)

        # Return to menu button with scaling
        self.return_to_menu_rect = pygame.Rect(
            (self.playground_rect.topleft[0] + int(20 * scale_factor),
             self.playground_rect.topleft[1] + int(20 * scale_factor)),
            (int(100 * scale_factor), int(50 * scale_factor))
        )

        # Game over button with scaling
        self.game_over_button_rect = pygame.Rect(
            self.playground_rect.centerx - int(150 * scale_factor),
            self.playground_rect.centery + int(100 * scale_factor),
            int(300 * scale_factor),
            int(50 * scale_factor)
        )

        # Scaled button dimensions for answer buttons
        self.button_width = int(300 * scale_factor)
        self.button_height = int(300 * scale_factor)
        self.button_margin = int(50 * scale_factor)

        # Scale font sizes
        title_font_size = max(int(36 * scale_factor), 12)
        small_font_size = max(int(16 * scale_factor), 10)

        # Reinitialize fonts with scaled sizes
        self.font = pygame.font.SysFont('comicsansms', title_font_size)
        self.small_font = pygame.font.SysFont('comicsansms', small_font_size)

    def Wrong_answer(self, surface):
        if self.remaining_lives > 1:
            self.remaining_lives -= 1
        elif self.remaining_lives == 1:
            self.draw_game_over(surface)

    def select_random_minigame(self):
        """Randomly select a minigame type"""
        game_type = rd.randint(1, 3)
        self.current_minigame = self.Minigame_dictionary[game_type]
        print(f"Selected minigame: {self.current_minigame}")

    def draw_game_over(self, surface):
        game_over_text = "Time's Up! Game Over!"
        text_surface = self.font.render(game_over_text, True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 50))
        surface.blit(text_surface, text_rect)

        # Display final score
        score_text = f"Final Score: {self.score}"
        score_surface = self.font.render(score_text, True, (0, 0, 0))
        score_rect = score_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        surface.blit(score_surface, score_rect)

        # Draw Return to Menu button with hover effect
        button_color = (140, 140, 140) if self.game_over_button_hover else (200, 200, 200)
        pygame.draw.rect(surface, button_color, self.game_over_button_rect, border_radius=10)
        button_font = pygame.font.SysFont('comicsansms', 24)
        button_text = "Return to Menu"
        button_text_surface = button_font.render(button_text, True, (0, 0, 0))
        button_text_rect = button_text_surface.get_rect(center=self.game_over_button_rect.center)
        surface.blit(button_text_surface, button_text_rect)

    def toggle_background(self):
        "Toggle between light and dark backgrounds."
        if self.dark_mode:
            self.current_background = self.background_light
        else:
            self.current_background = self.background_dark
        self.dark_mode = not self.dark_mode


    def truncate_text(self, text, max_length=50):
        if len(text) <= max_length:
            return text
        return text[:max_length] + '...'

    def setup_button_rects(self):
        """Create rectangles for answer buttons dynamically based on minigame type"""
        start_x = None
        start_y = None
        button_width = None
        button_height = None
        button_margin = None

        if self.current_minigame is None:
            # Select a random minigame if none is selected
            self.select_random_minigame()


        if self.current_minigame == "Most Acidic":
            # Keep existing settings for Most Acidic (image-based)
            start_x = self.playground_rect.x + 350
            start_y = self.playground_rect.y + 100
            button_width = self.button_width
            button_height = self.button_height
            button_margin = self.button_margin

        elif self.current_minigame == "Name To Structure":
            # Adjust for Name to Structure (image-based buttons)
            start_x = self.playground_rect.x + 350
            start_y = self.playground_rect.y + 100
            button_width = self.button_width
            button_height = self.button_height
            button_margin = self.button_margin

        elif self.current_minigame == "Structure To Name":
            # Text-based buttons for Structure to Name
            start_x = self.playground_rect.x + 185  # More horizontal space
            start_y = self.playground_rect.y + 400  # Lower on the screen
            button_width = 475  # Wider to accommodate text
            button_height = 100  # Shorter
            button_margin = 30  # Smaller margin

        # Only create button rects if all parameters are set
        if all(v is not None for v in [start_x, start_y, button_width, button_height, button_margin]):
            self.button_rects = [
                pygame.Rect(start_x, start_y, button_width, button_height),
                pygame.Rect(start_x + button_width + button_margin, start_y,
                            button_width, button_height),
                pygame.Rect(start_x, start_y + button_height + button_margin,
                            button_width, button_height),
                pygame.Rect(start_x + button_width + button_margin,
                            start_y + button_height + button_margin,
                            button_width, button_height)
            ]
        else:
            print("Could not set up button rectangles")
            self.button_rects = []

    def check_hover(self, mouse_pos):
        # Check hover for game option buttons
        if self.remaining_lives > 0:
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(mouse_pos):
                    self.button_hover_states[i] = True
                else:
                    self.button_hover_states[i] = False

        # Check hover for game over button
        if self.remaining_lives <= 0:
            self.game_over_button_hover = self.game_over_button_rect.collidepoint(mouse_pos)

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

                # Sort by pH to know which is most acidic
                compounds = sorted(compounds, key=lambda x: x[0])
                self.correct_answer = 0  # Index of most acidic compound

                # Shuffle the compounds for display
                display_order = list(range(4))
                rd.shuffle(display_order)
                self.current_compounds = [compounds[i] for i in display_order]
                # Update correct_answer to track shuffled position
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
                self.correct_answer = 0
                display_order = list(range(4))
                rd.shuffle(display_order)
                self.current_compounds = compounds
                self.correct_answer = display_order.index(0)

            # Cache images
            self.cached_images = []
            for compound in self.current_compounds:
                image_data = compound[3] if self.current_minigame == "Most Acidic" else compound[0]
                if image_data:
                    pil_image = Image.open(BytesIO(image_data))
                    # Scale image
                    img_width, img_height = pil_image.size
                    scale = min(self.button_width / img_width, self.button_height / img_height)
                    new_size = (int(img_width * scale * 0.8), int(img_height * scale * 0.8))
                    pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)

                    # Convert to pygame surface
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
        """Display the Most Acidic minigame"""
        if not self.current_compounds:
            if not self.load_new_question():
                print("No Compounds")
                return

        # Draw instructions
        instructions_font = pygame.font.SysFont('comicsansms', 36)
        instructions_text = "Select The Most Acidic Compound:"
        instructions_surface = instructions_font.render(instructions_text, True, (0, 0, 0))
        instructions_rect = instructions_surface.get_rect(
            center=(self.playground_rect.centerx, self.playground_rect.y + 50))
        surface.blit(instructions_surface, instructions_rect)

        # Draw score
        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, (0, 0, 0))
        score_rect = score_surface.get_rect(topright=(self.playground_rect.right - 20, self.playground_rect.y + 20))
        surface.blit(score_surface, score_rect)

        if not self.button_rects or not self.current_compounds:
            print("Button rects or compounds are not initialized!")
            print("Button rects:", self.button_rects)
            return

        # Draw compound options
        for i, (compound, button_rect) in enumerate(zip(self.current_compounds, self.button_rects)):
            # Draw button background
            button_color = (140, 140, 140) if self.button_hover_states[i] else self.button_color
            if self.feedback_displayed and i == self.selected_answer:
                button_color = (0, 255, 0) if i == self.correct_answer else (255, 0, 0)
            pygame.draw.rect(surface, button_color, button_rect, border_radius=10)

            # Draw image
            if self.cached_images[i]:
                image_rect = self.cached_images[i].get_rect(center=button_rect.center)
                surface.blit(self.cached_images[i], image_rect)

            # Draw formula
            formula_font = pygame.font.SysFont('comicsansms', 14)
            formula_text = self.truncate_text(compound[2]) # iupac
            formula_surface = formula_font.render(formula_text, True, (0, 0, 0))
            formula_rect = formula_surface.get_rect(
                centerx=button_rect.centerx,
                top=button_rect.bottom + 10
            )
            surface.blit(formula_surface, formula_rect)

        if self.feedback_displayed:
            print("Loading new question due to feedback duration")
            self.select_random_minigame()
            self.load_new_question()
        elif not self.feedback_displayed:
            # Time's up for this question
            self.selected_answer = -1  # Force incorrect
            self.handle_answer()
    def Name_To_Structure(self, surface):

        if not self.current_compounds:
            print("No compounds available for Name to Structure")
            return

        # Draw instructions
        instructions_font = pygame.font.SysFont('comicsansms', 36)
        instructions_text = "Match the following IUPAC name to its structure :"
        instructions_surface = instructions_font.render(instructions_text, True, (0, 0, 0))
        instructions_rect = instructions_surface.get_rect(
            center=(self.playground_rect.centerx, self.playground_rect.y + 50))
        surface.blit(instructions_surface, instructions_rect)

        # Safely access the IUPAC name
        compound_font = pygame.font.SysFont('comicsansms', 20)
        compound_text = str(self.current_compounds[self.correct_answer][1])
        compound_surface = compound_font.render(compound_text, True, (0, 0, 0))
        compound_rect = compound_surface.get_rect(
            center=(self.playground_rect.centerx, self.playground_rect.y + 75)
        )
        surface.blit(compound_surface, compound_rect)

        # Draw score
        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, (0, 0, 0))
        score_rect = score_surface.get_rect(topright=(self.playground_rect.right - 20, self.playground_rect.y + 20))
        surface.blit(score_surface, score_rect)

        # Draw compound options
        for i, (compound, button_rect) in enumerate(zip(self.current_compounds, self.button_rects)):
            # Draw button background
            button_color = (140, 140, 140) if self.button_hover_states[i] else self.button_color
            if self.feedback_displayed and i == self.selected_answer:
                button_color = (0, 255, 0) if i == self.correct_answer else (255, 0, 0)
            pygame.draw.rect(surface, button_color, button_rect, border_radius=10)

            # Draw image
            if self.cached_images[i]:
                image_rect = self.cached_images[i].get_rect(center=button_rect.center)
                surface.blit(self.cached_images[i], image_rect)

        if self.feedback_displayed:
            self.select_random_minigame()
            self.load_new_question()
        elif not self.feedback_displayed:
            # Time's up for this question
            self.selected_answer = -1  # Force incorrect
            self.handle_answer()

    def Structure_To_Name(self, surface):
        if not self.current_compounds:
            print("No compounds available for Structure to Name")
            return

        # Draw instructions
        instructions_font = pygame.font.SysFont('comicsansms', 36)
        instructions_text = "Select the IUPAC name for the given structure:"
        instructions_surface = instructions_font.render(instructions_text, True, (0, 0, 0))
        instructions_rect = instructions_surface.get_rect(
            center=(self.playground_rect.centerx, self.playground_rect.y + 50))
        surface.blit(instructions_surface, instructions_rect)

        # Draw score
        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, (0, 0, 0))
        score_rect = score_surface.get_rect(topright=(self.playground_rect.right - 20, self.playground_rect.y + 20))
        surface.blit(score_surface, score_rect)

        # Draw compound options
        for i, (compound, button_rect) in enumerate(zip(self.current_compounds, self.button_rects)):
            # Draw button background
            button_color = (140, 140, 140) if self.button_hover_states[i] else self.button_color
            if self.feedback_displayed and i == self.selected_answer:
                button_color = (0, 255, 0) if i == self.correct_answer else (255, 0, 0)
            pygame.draw.rect(surface, button_color, button_rect, border_radius=10)

            # Draw button text (IUPAC name)
            name_font = pygame.font.SysFont('comicsansms', 16)
            name_text = self.truncate_text(compound[1], max_length=50)  # Truncate long names
            name_surface = name_font.render(name_text, True, (0, 0, 0))
            name_rect = name_surface.get_rect(center=button_rect.center)
            surface.blit(name_surface, name_rect)

        # Draw the structure to identify
        if self.cached_images[self.correct_answer]:
            structure_image = self.cached_images[self.correct_answer]
            image_rect = structure_image.get_rect(
                center=(self.playground_rect.centerx, self.playground_rect.y + 225)
            )
            surface.blit(structure_image, image_rect)

        if self.feedback_displayed:
            self.select_random_minigame()
            self.load_new_question()
        elif not self.feedback_displayed:
            # Time's up for this question
            self.selected_answer = -1  # Force incorrect
            self.handle_answer()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.toggle_background()
            elif self.remaining_lives > 0:  # Only handle clicks if the game is still running
                self.handle_click(event.pos)

    def handle_answer(self):
        """Process the selected answer and update game state"""
        if self.selected_answer == self.correct_answer:
            self.score += 1
        else:
            self.remaining_lives -= 1
        self.feedback_displayed = True

    def handle_click(self, pos):
        """Handle mouse clicks for answer selection"""
        # Prevent multiple clicks during feedback or if compounds not loaded
        if not self.current_compounds or self.feedback_displayed:
            return
        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(pos):
                self.selected_answer = i
                self.handle_answer()
                break

    def run_once(self, surface):
        # Draw background and playground
        surface.blit(self.current_background.image, self.current_background.rect)

        playground_surface = pygame.Surface(
            (self.playground_rect.width, self.playground_rect.height), pygame.SRCALPHA)
        playground_color = (150, 150, 150, 180) if self.dark_mode else (169, 169, 169, 180)
        pygame.draw.rect(playground_surface, playground_color,
                         playground_surface.get_rect(), border_radius=50)
        surface.blit(playground_surface, self.playground_rect)

        # Draw the button with smooth corners (rounded rectangle)
        button_color = (169, 169, 169) if self.dark_mode else (230, 230, 230)
        pygame.draw.rect(surface, button_color, self.button_rect, border_radius=10)  # Rounded corners

        button_text = "Light" if self.dark_mode else "Lighter"
        text_color = (255, 255, 255) if self.dark_mode else (0, 0, 0)

        # Render the button text in white and position it in the center of the button
        button_font = pygame.font.Font('freesansbold.ttf', 20)
        button_text_surface = button_font.render(button_text, True, text_color)
        button_text_rect = button_text_surface.get_rect(center=self.button_rect.center)
        surface.blit(button_text_surface, button_text_rect)

        if self.remaining_lives > 0:

            # If no current question or previous question was answered, load a new question
            if not self.current_compounds or self.question_answered:
                # Randomly select a new minigame type
                self.select_random_minigame()
                self.load_new_question()

                # Load new question
                if self.load_new_question():
                    self.question_answered = False
                else:
                    print("Failed to load new question")
                    return

            # Run the selected minigame
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
        elif event.type == pygame.MOUSEMOTION:
            # Check hover states for buttons
            self.check_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.remaining_lives <= 0 and self.game_over_button_rect.collidepoint(event.pos):
                # Return to menu button clicked
                self.return_to_menu = True
                self._running = False
            elif self.button_rect.collidepoint(event.pos):
                self.toggle_background()
            elif self.remaining_lives > 0:  # Only handle clicks if the game is still running
                self.handle_click(event.pos)
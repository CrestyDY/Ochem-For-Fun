import pygame
import time
import background
import sqlite3 as sql
import random as rd
from PIL import Image
from io import BytesIO


class Time_Trial:
    def __init__(self):
        self._running = True
        self.size = self.weight, self.height = 1600, 1000
        self.current_screen = "time_trial"

        # Clock and timer
        self.clock = pygame.time.Clock()
        self.start_time = None
        self.time_limit = 60
        self.time_left = self.time_limit
        pygame.font.init()
        self.font = pygame.font.SysFont('comicsansms', 36)

        # Background setup
        self.background_light = background.Background('images/background.jpg', [0, 0])
        self.background_dark = background.Background('images/background-dark-mode.jpg', [0, 0])
        self.current_background = self.background_dark
        self.dark_mode = True
        self.button_rect = pygame.Rect(1460, 0, 100, 50)

        # Playground
        self.playground_rect = pygame.Rect(120, 75, 1360, 850)

        # Game state
        self.selected_answer = None
        self.current_compounds = None
        self.correct_answer = None
        self.score = 0
        self.current_question_start = None
        self.question_duration = 60  # Time per question in seconds
        self.feedback_displayed = False
        self.feedback_start = None
        self.feedback_duration = 0.5

        # Minigames
        self.Minigame_dictionary = {1: "Most Acidic", 2: "Name To Structure"}
        self.current_minigame = None
        self.question_answered = False

        # Button dimensions for answers
        self.button_width = 300
        self.button_height = 300
        self.button_margin = 50
        self.button_rects = []
        self.button_color = (200,200,200)
        self.setup_button_rects()

        self.cached_images = []

        #Hover effect
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

    def select_random_minigame(self):
        """Randomly select a minigame type"""
        game_type = rd.randint(1, 2)
        self.current_minigame = self.Minigame_dictionary[game_type]
        print(f"Selected minigame: {self.current_minigame}")
    def start_timer(self):
        self.start_time = time.time()

    def update_timer(self):
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            self.time_left = max(0, self.time_limit - int(elapsed_time))
        return self.time_left

    def draw_timer(self, surface):
        time_text = f"Time Left: {self.time_left}s"
        text_surface = self.font.render(time_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(surface.get_width() // 2, 50))
        surface.blit(text_surface, text_rect)

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
        """Create rectangles for the four answer buttons in a 2x2 grid"""
        start_x = self.playground_rect.x + 350
        start_y = self.playground_rect.y + 100

        self.button_rects = [
            pygame.Rect(start_x, start_y, self.button_width, self.button_height),
            pygame.Rect(start_x + self.button_width + self.button_margin, start_y,
                        self.button_width, self.button_height),
            pygame.Rect(start_x, start_y + self.button_height + self.button_margin,
                        self.button_width, self.button_height),
            pygame.Rect(start_x + self.button_width + self.button_margin,
                        start_y + self.button_height + self.button_margin,
                        self.button_width, self.button_height)
        ]

    def check_hover(self, mouse_pos):
        # Check hover for game option buttons
        if self.time_left > 0:
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(mouse_pos):
                    self.button_hover_states[i] = True
                else:
                    self.button_hover_states[i] = False

        # Check hover for game over button
        if self.time_left <= 0:
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
            print("Current compounds:", self.current_compounds)
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

        # Check if it's time for a new question
        current_time = time.time()

        if self.feedback_displayed and current_time - self.feedback_start >= self.feedback_duration:
            print("Loading new question due to feedback duration")
            self.select_random_minigame()
            self.load_new_question()
        elif not self.feedback_displayed and current_time - self.current_question_start >= self.question_duration:
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

        # Check if it's time for a new question
        current_time = time.time()
        if self.feedback_displayed and current_time - self.feedback_start >= self.feedback_duration:
            self.select_random_minigame()
            self.load_new_question()
        elif not self.feedback_displayed and current_time - self.current_question_start >= self.question_duration:
            # Time's up for this question
            self.selected_answer = -1  # Force incorrect
            self.handle_answer()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.toggle_background()
            elif self.time_left > 0:  # Only handle clicks if the game is still running
                self.handle_click(event.pos)

    def handle_answer(self):
        """Process the selected answer and update game state"""
        if self.selected_answer == self.correct_answer:
            self.score += 1


        self.feedback_displayed = True
        self.feedback_start = time.time()

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

        # Update and draw timer
        if self.start_time is None:
            self.start_timer()

        self.time_left = self.update_timer()

        if self.time_left > 0:
            self.draw_timer(surface)

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
                self.Most_Acidic(surface)
            elif self.current_minigame == "Name To Structure":
                self.Name_To_Structure(surface)

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
            if self.time_left <= 0 and self.game_over_button_rect.collidepoint(event.pos):
                # Return to menu button clicked
                self.return_to_menu = True
                self._running = False
            elif self.button_rect.collidepoint(event.pos):
                self.toggle_background()
            elif self.time_left > 0:  # Only handle clicks if the game is still running
                self.handle_click(event.pos)


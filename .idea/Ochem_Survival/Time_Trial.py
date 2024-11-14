import pygame
import time
import background


class Time_Trial:
    def __init__(self):
        self._running = True
        self.size = self.weight, self.height = 1600, 1000
        self.current_screen = "time_trial"

        # Clock and timer
        self.clock = pygame.time.Clock()
        self.start_time = None
        self.time_limit = 60  # 60 seconds
        self.time_left = self.time_limit
        pygame.font.init()
        self.font = pygame.font.SysFont('comicsansms', 36)

        # Background images
        self.background_light = background.Background('images/background.jpg', [0, 0])
        self.background_dark = background.Background('images/background-dark-mode.jpg', [0, 0])
        self.current_background = self.background_dark
        self.dark_mode = True
        self.button_rect = pygame.Rect(1500, 0, 100, 50)

        # Playground
        self.playground_rect = pygame.Rect(120, 75, 1360, 850)

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
        text_rect = text_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        surface.blit(text_surface, text_rect)

    def toggle_background(self):
        self.current_background = self.background_light if self.dark_mode else self.background_dark
        self.dark_mode = not self.dark_mode

    def run_once(self, surface):
        self.update_timer()

        # Set the background
        surface.blit(self.current_background.image, self.current_background.rect)

        # Draw button
        button_color = (169, 169, 169) if self.dark_mode else (230, 230, 230)
        pygame.draw.rect(surface, button_color, self.button_rect, border_radius=10)
        button_text = "Light" if self.dark_mode else "Dark"
        text_color = (255, 255, 255) if self.dark_mode else (0, 0, 0)
        button_font = pygame.font.Font('freesansbold.ttf', 20)
        button_text_surface = button_font.render(button_text, True, text_color)
        button_text_rect = button_text_surface.get_rect(center=self.button_rect.center)
        surface.blit(button_text_surface, button_text_rect)

        # Draw playground
        playground_surface = pygame.Surface((self.playground_rect.width, self.playground_rect.height), pygame.SRCALPHA)
        playground_color = (150, 150, 150, 180) if self.current_background == self.background_dark else (
        169, 169, 169, 180)
        pygame.draw.rect(playground_surface, playground_color, playground_surface.get_rect(), border_radius=50)
        surface.blit(playground_surface, self.playground_rect)

        # Draw timer or game over screen
        if self.time_left > 0:
            self.draw_timer(surface)
        else:
            self.draw_game_over(surface)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.toggle_background()

    def on_cleanup(self):
        pygame.quit()

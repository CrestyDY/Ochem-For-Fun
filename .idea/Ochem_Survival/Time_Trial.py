import pygame
import time
import background

class Time_Trial:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 1600, 1000
        self.current_screen = "time_trial"

        #Create a clock
        self.clock = pygame.time.Clock()
        self.start_time = None
        self.time_limit = 60  # 60 seconds for the time trial
        self.time_left = self.time_limit
        pygame.font.init()
        self.font = pygame.font.SysFont('comicsansms', 36)

        # Background images
        self.background_light = background.Background('background.jpg', [0, 0])
        self.background_dark = background.Background('background-dark-mode.jpg', [0, 0])
        self.current_background = self.background_dark
        self.dark_mode = True
        self.button_rect = pygame.Rect(1500, 0, 100, 50)

        # Playground
        self.playground_rect = pygame.Rect(120, 75, 1360, 850)

    def start_timer(self):
        # Record the start time
        self.start_time = time.time()

    def update_timer(self):
        # Calculate the remaining time
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            self.time_left = max(0, self.time_limit - int(elapsed_time))
        return self.time_left

    def draw(self, surface):
        # Draw the timer on the screen
        time_text = f"Time Left: {self.time_left}s"
        text_surface = self.font.render(time_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(surface.get_width() // 2, 50))  # Center at the top
        surface.blit(text_surface, text_rect)

    def game_over(self, surface):
        # When time runs out, display a game over message
        game_over_text = "Time's Up! Game Over!"
        text_surface = self.font.render(game_over_text, True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        surface.blit(text_surface, text_rect)

    def run(self, surface):
        # This method will be called to run the time trial
        self.start_timer()  # Start the timer when the game starts

        # Game loop for time trial mode
        running = True
        while running:
            surface.fill((0, 0, 0))  # Fill the screen with black

            # Handle events (like quitting the game)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Update timer
            time_left = self.update_timer()

            # If time runs out, show the game over screen
            if time_left == 0:
                self.game_over(surface)
            else:
                self.draw(surface)

            # Update the screen
            pygame.display.flip()
            self.clock.tick(30)  # 30 FPS for the time trial mode
        pygame.quit()  # Clean up pygame resources when exiting the loop

    def on_init(self):
        pygame.init()
        pygame.font.init()

        # Display
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)

        # Title and Icon
        pygame.display.set_caption('Ochem Battle')
        Icon = pygame.image.load('background.png')
        pygame.display.set_icon(Icon)

        pygame.display.flip()
        self._running = True

    def toggle_background(self):
        "Toggle between light and dark backgrounds."
        if self.dark_mode:
            self.current_background = self.background_light
        else:
            self.current_background = self.background_dark
        self.dark_mode = not self.dark_mode

    def on_event(self, event):
        pass
    def on_loop(self):
        pass

    def on_render(self):
        # Update the display
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()
if __name__ == "__main__":
    theApp = Time_Trial()
    theApp.on_execute()


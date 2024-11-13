import pygame
import background
from pygame.locals import *
import HexagonButton
from Time_Trial import Time_Trial  # Import the Time_Trial class



class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 1600, 1000
        self.current_screen = "playground"

        # Background images
        self.background_light = background.Background('images/background.jpg', [0, 0])
        self.background_dark = background.Background('images/background-dark-mode.jpg', [0, 0])
        self.current_background = self.background_dark
        self.dark_mode = True
        self.button_rect = pygame.Rect(1500, 0, 100, 50)

        # Playground
        self.playground_rect = pygame.Rect(120, 75, 1360, 850)
        self.gamemode = ""
        self.gamemode1 = HexagonButton.HexButton(550, 500, 120, (150, 150, 150), (245, 245, 220), "SURVIVAL")
        self.gamemode2 = HexagonButton.HexButton(1050, 500, 120, (150, 150, 150), (245, 245, 220), "TIME TRIAL")

    def on_init(self):
        pygame.init()
        pygame.font.init()

        # Display
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)

        # Title and Icon
        pygame.display.set_caption('Ochem Battle')
        Icon = pygame.image.load('images/background.png')
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
        if event.type == pygame.QUIT:
            self._running = False

        # Handle mouse clicks for button toggle
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.toggle_background()

            # Handle gamemode button clicks
            if self.gamemode1.is_clicked(event.pos):
                self.current_screen = "survival"  # Switch to survival screen
            elif self.gamemode2.is_clicked(event.pos):
                self.current_screen = "time_trial"  # Switch to time trial screen

        # Handle mouse motion for hover effect
        if event.type == pygame.MOUSEMOTION:
            self.gamemode1.check_hover(event.pos)  # Check hover on gamemode1
            self.gamemode2.check_hover(event.pos)  # Check hover on gamemode2

    def on_loop(self):
        pass

    def on_render(self):
        if self.current_screen == "playground":
            # Set the background
            self._display_surf.blit(self.current_background.image, self.current_background.rect)

            # Draw the button with smooth corners (rounded rectangle)
            button_color = (169, 169, 169) if self.dark_mode else (230, 230, 230)
            pygame.draw.rect(self._display_surf, button_color, self.button_rect, border_radius=10)  # Rounded corners

            button_text = "Light" if self.dark_mode else "Lighter"
            text_color = (255, 255, 255) if self.dark_mode else (0, 0, 0)

            # Render the button text in white and position it in the center of the button
            button_font = pygame.font.Font('freesansbold.ttf', 20)
            button_text_surface = button_font.render(button_text, True, text_color)
            button_text_rect = button_text_surface.get_rect(center=self.button_rect.center)
            self._display_surf.blit(button_text_surface, button_text_rect)

            # Set the transparent playground surface with rounded corners
            playground_surface = pygame.Surface((self.playground_rect.width, self.playground_rect.height), pygame.SRCALPHA)
            playground_color = (150, 150, 150, 180) if self.current_background == self.background_dark else (169, 169, 169, 180)
            pygame.draw.rect(playground_surface, playground_color, playground_surface.get_rect(), border_radius=50)
            self._display_surf.blit(playground_surface, self.playground_rect)

            # Game Title
            title_text = "WELCOME TO OCHEM SURVIVAL !"
            title_font = pygame.font.SysFont('comicsansms', 50)
            title_surface = title_font.render(title_text, True, (0, 0, 0))
            self._display_surf.blit(title_surface, (self.playground_rect.x + 275, self.playground_rect.y + 5))

            # Subtitle
            subtitle_text = "Are You Ready To Take On This Challenge ?"
            subtitle_font = pygame.font.SysFont('comicsansms', 30)
            subtitle_surface = subtitle_font.render(subtitle_text, True, (0, 0, 0))
            self._display_surf.blit(subtitle_surface, (self.playground_rect.x + 375, self.playground_rect.y + 75))

            # Sub-subtitle
            subsubtitle_text = "Select a Gamemode"
            subsubtitle_font = pygame.font.SysFont('comicsansms', 30)
            subsubtitle_surface = subsubtitle_font.render(subsubtitle_text, True, (0, 0, 0))
            self._display_surf.blit(subsubtitle_surface, (self.playground_rect.x + 525, self.playground_rect.y + 125))

            # Display Gamemode buttons
            self.gamemode1.draw(self._display_surf)
            self.gamemode2.draw(self._display_surf)

        elif self.current_screen == "time_trial":
            # If time trial mode is selected, run the Time_Trial class
            time_trial = Time_Trial()
            time_trial.run(self._display_surf)

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
    theApp = App()
    theApp.on_execute()

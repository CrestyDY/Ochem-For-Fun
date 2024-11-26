import pygame
import background
from pygame.locals import *
import HexagonButton
from Time_Trial import Time_Trial  # Import the Time_Trial class
import sys



class App:
    def __init__(self):
        # Get desktop sizes and choose the first (primary) display
        pygame.init()
        desktop_sizes = pygame.display.get_desktop_sizes()
        self.max_width, self.max_height = desktop_sizes[0]

        # Scale window to 90% of screen size while maintaining original aspect ratio
        scale_factor = min(self.max_width / 1600, self.max_height / 1000)
        self.width = int(1600 * scale_factor * 0.9)
        self.height = int(1000 * scale_factor * 0.9)
        self.size = (self.width, self.height)

        self._running = True
        self._display_surf = None
        self.current_screen = "playground"

        # Background images
        self.background_light = background.Background('images/background.jpg', [0, 0])
        self.background_dark = background.Background('images/background-dark-mode.jpg', [0, 0])
        self.current_background = self.background_light
        self.dark_mode = True

        # Dynamically position button
        self.button_rect = pygame.Rect(self.width - 100, 0, 100, 50)

        # Playground scaling with centering
        playground_width = int(1200 * scale_factor)
        playground_height = int(800 * scale_factor)

        # Calculate left and top margins to center the playground
        playground_left = (self.width - playground_width) // 2
        playground_top = (self.height - playground_height) // 2

        self.playground_rect = pygame.Rect(
            playground_left,
            playground_top,
            playground_width,
            playground_height
        )

        # Text scaling with scaled offsets relative to playground
        self.base_title_font_size = int(50 * scale_factor)
        self.base_subtitle_font_size = int(30 * scale_factor)
        self.base_subsubtitle_font_size = int(30 * scale_factor)

        # Scaled offsets relative to playground
        self.base_title_offset = (
            int(275 * scale_factor),
            int(5 * scale_factor)
        )
        self.base_subtitle_offset = (
            int(375 * scale_factor),
            int(75 * scale_factor)
        )
        self.base_subsubtitle_offset = (
            int(525 * scale_factor),
            int(125 * scale_factor)
        )

        # Gamemode buttons scaling with centering
        button_radius = int(120 * scale_factor)

        # Position gamemode buttons relative to playground
        self.gamemode1 = HexagonButton.HexButton(
            playground_left + int(((playground_width+240) * 0.3) - button_radius),
            playground_top + int(playground_height * 0.5),
            button_radius,
            (169, 169, 169),
            (245, 245, 220),
            "SURVIVAL"
        )
        self.gamemode2 = HexagonButton.HexButton(
            playground_left + int(((playground_width+240) * 0.7) - button_radius),
            playground_top + int(playground_height * 0.5),
            button_radius,
            (169, 169, 169),
            (245, 245, 220),
            "TIME TRIAL"
        )

        self.time_trial = None

    def on_init(self):
        pygame.init()
        pygame.font.init()

        pygame.mixer_music.load("Ochem_Music.mp3")
        pygame.mixer_music.set_volume(0.5)
        pygame.mixer_music.play(-1)

        # Use dynamic sizing
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)

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

    def calculate_scaling_factor(self):
        # Calculate scaling factors based on the current size and original dimensions
        return self._display_surf.get_width() / 1600, self._display_surf.get_height() / 1000

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

        if event.type == pygame.VIDEORESIZE:
            self.width, self.height = event.w, event.h
            self.size = (self.width, self.height)
            self._display_surf = pygame.display.set_mode(self.size,
                                                         pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
            self.update_layout()

        # Handle mouse clicks for button toggle
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.toggle_background()

            # Handle gamemode button clicks only in playground screen
            if self.current_screen == "playground":
                if self.gamemode1.is_clicked(event.pos):
                    self.current_screen = "survival"
                elif self.gamemode2.is_clicked(event.pos):
                    self.current_screen = "time_trial"
                    self.time_trial = Time_Trial()
                    self.time_trial.start_timer()

        # Handle mouse motion for hover effect in playground screen
        if event.type == pygame.MOUSEMOTION and self.current_screen == "playground":
            self.gamemode1.check_hover(event.pos)
            self.gamemode2.check_hover(event.pos)

        # Delegate events to Time_Trial mode if active
        if self.current_screen == "time_trial" and self.time_trial:
            self.time_trial.on_event(event)

    def update_layout(self):
        # Recalculate positions and sizes based on new window dimensions
        # Update background, button, and playground dimensions if needed
        self.playground_rect = pygame.Rect(120, 75, self.width - 240, self.height - 150)
        self.button_rect = pygame.Rect(self.width - 100, 0, 100, 50)

        # If buttons need to scale or reposition, update here
        self.gamemode1.x = int(self.width * 0.35)  # Roughly 35% from the left for gamemode1
        self.gamemode1.y = int(self.height * 0.5)  # Centered vertically

        self.gamemode2.x = int(self.width * 0.65)  # Roughly 65% from the left for gamemode2
        self.gamemode2.y = int(self.height * 0.5)  # Centered vertically
    def on_loop(self):
        if self.current_screen == "time_trial" and self.time_trial:
            # Update the time trial timer
            self.time_trial.update_timer()

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
            playground_color = (150, 150, 150, 180) if self.current_background == self.background_dark else (180, 180, 180, 150)
            pygame.draw.rect(playground_surface, playground_color, playground_surface.get_rect(), border_radius=50)
            self._display_surf.blit(playground_surface, self.playground_rect)

            # Scaling factors
            width_scale, height_scale = self.calculate_scaling_factor()

            # Title text
            title_font = pygame.font.SysFont('comicsansms', int(self.base_title_font_size * height_scale))
            title_text = "WELCOME TO OCHEM SURVIVAL !"
            title_surface = title_font.render(title_text, True, (0, 0, 0) if self.current_background == self.background_dark else (255,255,255))
            title_position = (
                int(self.playground_rect.x + self.base_title_offset[0] * width_scale),
                int(self.playground_rect.y + self.base_title_offset[1] * height_scale)
            )
            self._display_surf.blit(title_surface, title_position)

            # Subtitle text
            subtitle_font = pygame.font.SysFont('comicsansms', int(self.base_subtitle_font_size * height_scale))
            subtitle_text = "Are You Ready To Take On This Challenge ?"
            subtitle_surface = subtitle_font.render(subtitle_text, True, (0, 0, 0) if self.current_background == self.background_dark else (255,255,255))
            subtitle_position = (
                int(self.playground_rect.x + self.base_subtitle_offset[0] * width_scale),
                int(self.playground_rect.y + self.base_subtitle_offset[1] * height_scale)
            )
            self._display_surf.blit(subtitle_surface, subtitle_position)

            # Sub-subtitle text
            subsubtitle_font = pygame.font.SysFont('comicsansms', int(self.base_subsubtitle_font_size * height_scale))
            subsubtitle_text = "Select a Gamemode"
            subsubtitle_surface = subsubtitle_font.render(subsubtitle_text, True, (0, 0, 0) if self.current_background == self.background_dark else (255,255,255))
            subsubtitle_position = (
                int(self.playground_rect.x + self.base_subsubtitle_offset[0] * width_scale),
                int(self.playground_rect.y + self.base_subsubtitle_offset[1] * height_scale)
            )
            self._display_surf.blit(subsubtitle_surface, subsubtitle_position)
            # Display Gamemode buttons
            self.gamemode1.draw(self._display_surf)
            self.gamemode2.draw(self._display_surf)

        elif self.current_screen == "time_trial" and self.time_trial:
            self.time_trial.run_once(self._display_surf)

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

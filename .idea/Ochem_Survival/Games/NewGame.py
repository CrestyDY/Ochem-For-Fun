import pygame
import background
from pygame.locals import *
from Time_Trial import Time_Trial
from Survival import Survival
from Database_Search import Database_Search
from Blind_Mode import Blind_Mode
import math
import sys
import os

class App:
    class HexButton:
        def __init__(self, x, y, base_size, scale_factor, color, hover_color, text, text_color=(0, 0, 0)):
            self.base_size = base_size
            self.size = int(base_size * scale_factor)

            self.x = x
            self.y = y

            self.color = color
            self.hover_color = hover_color
            self.text = text
            self.text_color = text_color
            self.is_hovered = False
            self.points = []

        def calculate_hex_points(self, size_adjustment=0):
            
            points = []
            for i in range(6):
                angle_deg = 60 * i
                angle_rad = math.radians(angle_deg + 30)
                x = self.x + (self.size + size_adjustment) * math.cos(angle_rad)
                y = self.y + (self.size + size_adjustment) * math.sin(angle_rad)
                points.append((x, y))
            return points

        def draw(self, surface):
            
            hex_color = self.hover_color if self.is_hovered else self.color

            
            self.points = self.calculate_hex_points()

            
            border_points = self.calculate_hex_points(size_adjustment=5)  
            pygame.draw.polygon(surface, (0, 0, 0), border_points)  

            
            pygame.draw.polygon(surface, hex_color, self.points)

            
            font_size = max(int(self.size / 4), 12)  
            font = pygame.font.SysFont('comicsansms', font_size)
            text_surface = font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=(self.x, self.y))
            surface.blit(text_surface, text_rect)

        def is_clicked(self, pos):
            
            poly_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.polygon(poly_surface, (255, 255, 255, 255), self.points)
            return poly_surface.get_rect(topleft=(self.x - self.size, self.y - self.size)).collidepoint(pos)

        def check_hover(self, mouse_pos):
            
            self.is_hovered = pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2,
                                          self.size * 2).collidepoint(mouse_pos)
    def __init__(self):

        
        pygame.init()
        desktop_sizes = pygame.display.get_desktop_sizes()
        self.max_width, self.max_height = desktop_sizes[0]

        
        scale_factor = min(self.max_width / 1600, self.max_height / 1000)
        self.width = int(1600 * scale_factor * 0.9)
        self.height = int(1000 * scale_factor * 0.9)
        self.size = (self.width, self.height)
        self._running = True
        self._display_surf = None
        self.current_screen = "playground"

        
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.background_light = background.Background(self.get_image_path('background.jpg'), [0, 0])
        self.background_dark = background.Background(self.get_image_path('background-dark-mode.jpg'), [0, 0])
        self.current_background = self.background_light
        self.dark_mode = False

        
        self.button_rect = pygame.Rect(self.width - scale_factor*100, 0, scale_factor*100, scale_factor*50)
        self.music_rect = pygame.Rect(self.width - scale_factor*100, scale_factor*50, scale_factor*100, scale_factor*50)
        self.music_play = True
        self.button_hovered = False
        self.music_hovered = False

        
        playground_width = int(1200 * scale_factor)
        playground_height = int(800 * scale_factor)

        
        playground_left = (self.width - playground_width) // 2
        button_spacing = playground_width // 3
        playground_top = (self.height - playground_height) // 2

        self.playground_rect = pygame.Rect(
            playground_left,
            playground_top,
            playground_width,
            playground_height
        )

        
        self.base_title_font_size = int(50 * scale_factor)
        self.base_subtitle_font_size = int(30 * scale_factor)
        self.base_subsubtitle_font_size = int(30 * scale_factor)

        
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

        
        button_radius = int(120 * scale_factor)
        
        base_button_radius = 120

        self.gamemode1 = self.HexButton(
            playground_left + button_spacing - 100*scale_factor,  
            playground_top + int(playground_height * 0.5),
            base_button_radius,
            scale_factor,
            (169, 169, 169),
            (245, 245, 220),
            "SURVIVAL"
        )

        self.gamemode2 = self.HexButton(
            playground_left + (button_spacing * 1.5),  
            playground_top + int(playground_height * 0.5),
            base_button_radius,
            scale_factor,
            (169, 169, 169),
            (245, 245, 220),
            "TIME TRIAL"
        )

        self.gamemode3 = self.HexButton(
            playground_left + (button_spacing * 2) + 100*scale_factor,
            playground_top + int(playground_height * 0.5),
            base_button_radius,
            scale_factor,
            (169, 169, 169),
            (245, 245, 220),
            "BLIND MODE"
        )

        self.time_trial_high_score = None
        self.time_trial = None
        self.survival_high_score = None
        self.survival = None
        self.blind_mode = None

        scale_factor = min(self.width / 1600, self.height / 1000)
        button_width = int(180 * scale_factor)
        button_height = int(40 * scale_factor)
        self.database_button_rect = pygame.Rect(
            10,  
            10,  
            button_width,
            button_height
        )
        self.database_button_hovered = False

    def get_image_path(self, filename):
        return os.path.join(self.base_path, 'images', filename)

    def on_init(self):
        pygame.init()
        pygame.font.init()

        music_path = os.path.join(self.base_path, 'Ochem_Music.mp3')
        pygame.mixer_music.load(music_path)
        pygame.mixer_music.set_volume(0.5)
        pygame.mixer_music.play(-1)

        
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)

        
        pygame.display.set_caption('Ochem For Fun')
        Icon = pygame.image.load(self.get_image_path("background.png"))
        pygame.display.set_icon(Icon)

        try:
            with open('High_Scores.txt', 'r') as file:
                print("Succesfully read file")
                self.time_trial_high_score = int(file.read().strip())
        except (FileNotFoundError, ValueError):
            print("Error finding file")
            self.time_trial_high_score = 0

        try:
            with open("Survival_High_Scores.txt", "r") as file:
                print("Succesfully read file")
                self.survival_high_score = int(file.read().strip())
        except (FileNotFoundError, ValueError):
            print("Error finding file")
            self.survival_high_score = 0

        pygame.display.flip()
        self._running = True

    def toggle_background(self):
        "Toggle between light and dark backgrounds."
        if self.dark_mode:
            self.current_background = self.background_light
        else:
            self.current_background = self.background_dark
        self.dark_mode = not self.dark_mode

    def pause_music(self):
        if self.music_play:
            self.music_play = False
            pygame.mixer_music.pause()
        elif not self.music_play:
            self.music_play = True
            pygame.mixer_music.unpause()


    def calculate_scaling_factor(self):
        
        return self._display_surf.get_width() / 1600, self._display_surf.get_height() / 1000

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

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

        if event.type == pygame.VIDEORESIZE:
            self.width, self.height = event.w, event.h
            self.size = (self.width, self.height)
            self._display_surf = pygame.display.set_mode(self.size,
                                                         pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
            self.update_layout()

        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.toggle_background()

            if self.music_rect.collidepoint(event.pos):
                self.pause_music()

            
            if self.current_screen == "playground":
                if self.database_button_rect.collidepoint(event.pos):
                    self.current_screen = "database_search"
                    self.database_search = Database_Search(
                        width=self.width,
                        height=self.height,
                        playground_rect=self.playground_rect,
                        base_path=self.base_path,
                        current_background=self.current_background,
                        dark_mode=self.dark_mode,
                        music_play=self.music_play,
                        music_rect=self.music_rect,
                        button_rect=self.button_rect,
                    )
                if self.gamemode1.is_clicked(event.pos):
                    self.current_screen = "survival"
                    self.survival = Survival(
                        width=self.width,
                        height=self.height,
                        playground_rect=self.playground_rect,
                        base_path=self.base_path,
                        current_background=self.current_background,
                        dark_mode=self.dark_mode,
                        music_play= self.music_play,
                        music_rect=self.music_rect,
                        button_rect=self.button_rect,
                    )
                if self.gamemode2.is_clicked(event.pos):
                    self.current_screen = "time_trial"
                    self.time_trial = Time_Trial(
                        width=self.width,
                        height=self.height,
                        playground_rect=self.playground_rect,
                        base_path=self.base_path,
                        current_background=self.current_background,
                        dark_mode=self.dark_mode,
                        music_play= self.music_play,
                        music_rect=self.music_rect,
                        button_rect=self.button_rect,
                    )
                    self.time_trial.start_timer()
                if self.gamemode3.is_clicked(event.pos):
                    self.current_screen = "blind_mode"
                    self.blind_mode = Blind_Mode(
                        width=self.width,
                        height=self.height,
                        playground_rect=self.playground_rect,
                        base_path=self.base_path,
                        current_background=self.current_background,
                        dark_mode=self.dark_mode,
                        music_play=self.music_play,
                        music_rect=self.music_rect,
                        button_rect=self.button_rect,
                    )


            if self.current_screen == "time_trial" and self.time_trial:
                if self.time_trial.return_to_menu_rect.collidepoint(event.pos):
                    self.current_screen = "playground"
                    self.time_trial = None
                elif self.time_trial.time_left <= 0 and self.time_trial.game_over_button_rect.collidepoint(event.pos):
                    
                    self.current_screen = "playground"
                    self.time_trial = None
            if self.current_screen == "survival" and self.survival:
                if self.survival.return_to_menu_rect.collidepoint(event.pos):
                    self.current_screen = "playground"
                    self.survival = None
                elif self.survival.lives == 0 and self.survival.game_over_button_rect.collidepoint(event.pos):
                    self.current_screen = "playground"
                    self.survival = None
            if self.current_screen == "database_search" and self.database_search:
                if self.database_search.return_to_menu_rect.collidepoint(event.pos):
                    self.current_screen = "playground"
                    self.database_search = None
            if self.current_screen == "blind_mode" and self.blind_mode:
                if self.blind_mode.return_to_menu_rect.collidepoint(event.pos):
                    self.current_screen = "playground"
                    self.blind_mode = None

        
        if event.type == pygame.MOUSEMOTION and self.current_screen == "playground":
            self.gamemode1.check_hover(event.pos)
            self.gamemode2.check_hover(event.pos)
            self.gamemode3.check_hover(event.pos)
            self.database_button_hovered = self.database_button_rect.collidepoint(event.pos)
            self.button_hovered = self.button_rect.collidepoint(event.pos)
            self.music_hovered = self.music_rect.collidepoint(event.pos)

        
        if self.current_screen == "time_trial" and self.time_trial:
            event_result = self.time_trial.on_event(event)
            if event_result == "return_to_menu":
                self.current_screen = "playground"
                self.time_trial = None
        if self.current_screen == "survival" and self.survival:
            event_result = self.survival.on_event(event)
            if event_result == "return_to_menu":
                self.current_screen = "playground"
                self.survival = None
        if self.current_screen == "blind_mode" and self.blind_mode:
            event_result = self.blind_mode.on_event(event)
            if event_result == "return_to_menu":
                self.current_screen = "playground"
                self.blind_mode = None
        if self.current_screen == "database_search" and self.database_search:
            event_result = self.database_search.on_event(event)
            if event_result == "return_to_menu":
                self.current_screen = "playground"
                self.database_search = None

    def update_layout(self):
        
        scale_factor = min(self.width / 1600, self.height / 1000)

        self.update_playground_rect()

        
        button_width = int(100 * scale_factor)
        button_height = int(50 * scale_factor)
        button_x = self.width - button_width
        button_y = 0  

        music_x = self.width - button_width
        music_y = button_height  

        self.button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        self.music_rect = pygame.Rect(music_x, music_y, button_width, button_height)

        playground_left = (self.width - self.playground_rect.width) // 2
        button_spacing = self.playground_rect.width // 3

        self.gamemode1.x = playground_left + button_spacing
        self.gamemode1.y = int(self.height * 0.5)
        self.gamemode1.size = int(self.gamemode1.base_size * scale_factor)

        self.gamemode2.x = playground_left + (button_spacing * 1.5)
        self.gamemode2.y = int(self.height * 0.5)
        self.gamemode2.size = int(self.gamemode2.base_size * scale_factor)

        self.gamemode3.x = playground_left + (button_spacing * 2)
        self.gamemode3.y = int(self.height * 0.5)
        self.gamemode3.size = int(self.gamemode3.base_size * scale_factor)

        button_width = int(180 * scale_factor)
        button_height = int(40 * scale_factor)
        self.database_button_rect = pygame.Rect(
            10*scale_factor,  
            10*scale_factor,  
            button_width,
            button_height
        )

    def on_loop(self):
        if self.current_screen == "time_trial" and self.time_trial:
            
            self.time_trial.update_timer()

    def on_render(self):

        if self.current_screen == "playground":
            
            self._display_surf.blit(self.current_background.image, self.current_background.rect)

            scale_factor = min(self.width / 1600, self.height / 1000)
            font_size = max(10, int(20 * scale_factor))  

            
            button_color = (100,100,100) if self.button_hovered else (169, 169, 169) if self.dark_mode else (230, 230, 230)
            pygame.draw.rect(self._display_surf, button_color, self.button_rect, border_radius=int(10 * scale_factor))  

            
            button_text = "Lighter" if not self.dark_mode else "Light"
            text_color = (255, 255, 255) if self.dark_mode else (0, 0, 0)
            button_font = pygame.font.Font('freesansbold.ttf', font_size)  
            button_text_surface = button_font.render(button_text, True, text_color)
            button_text_rect = button_text_surface.get_rect(center=self.button_rect.center)
            self._display_surf.blit(button_text_surface, button_text_rect)

            
            music_button_color = (100,100,100) if self.music_hovered else (169, 169, 169) if self.dark_mode else (230, 230, 230)
            pygame.draw.rect(self._display_surf, music_button_color, self.music_rect,
                             border_radius=int(10 * scale_factor))  

            
            music_text = "Paused" if not self.music_play else "Playing"
            music_font = pygame.font.Font('freesansbold.ttf', font_size)  
            music_text_surface = music_font.render(music_text, True, text_color)
            music_text_rect = music_text_surface.get_rect(center=self.music_rect.center)
            self._display_surf.blit(music_text_surface, music_text_rect)

            button_color = (100, 100, 100) if self.database_button_hovered else (169, 169, 169)
            pygame.draw.rect(self._display_surf, button_color, self.database_button_rect, border_radius=int(10 * scale_factor))
            database_text = "DATABASE"
            database_font = pygame.font.Font('freesansbold.ttf', font_size)  
            database_text_surface = database_font.render(database_text, True, (255, 255, 255) if self.dark_mode else (0, 0, 0))
            database_text_rect = database_text_surface.get_rect(center=self.database_button_rect.center)
            self._display_surf.blit(database_text_surface, database_text_rect)

            
            playground_surface = pygame.Surface((self.playground_rect.width, self.playground_rect.height), pygame.SRCALPHA)
            playground_color = (150, 150, 150, 180) if self.current_background == self.background_dark else (180, 180, 180, 150)
            pygame.draw.rect(playground_surface, playground_color, playground_surface.get_rect(), border_radius=50)
            self._display_surf.blit(playground_surface, self.playground_rect)

            
            width_scale, height_scale = self.calculate_scaling_factor()

            
            title_font = pygame.font.SysFont('comicsansms', int(self.base_title_font_size * height_scale))

            
            title_text = "WELCOME TO OCHEM FOR FUN !"
            text_color = (0, 0, 0)
            title_surface = title_font.render(title_text, True, text_color)

            
            title_rect = title_surface.get_rect()
            title_rect.centerx = self.playground_rect.centerx
            title_rect.y = int(self.playground_rect.y + self.base_title_offset[1] * height_scale)  
            self._display_surf.blit(title_surface, title_rect.topleft)

            
            subtitle_font = pygame.font.SysFont('comicsansms', int(self.base_subtitle_font_size * height_scale))
            subtitle_text = "Are You Ready To Take On This Challenge ?"
            subtitle_surface = subtitle_font.render(subtitle_text, True, (0, 0, 0) )
            subtitle_rect = subtitle_surface.get_rect()
            subtitle_rect.centerx = self.playground_rect.centerx
            subtitle_rect.y = int(self.playground_rect.y + self.base_subtitle_offset[1] * height_scale)
            self._display_surf.blit(subtitle_surface, subtitle_rect.topleft)

            
            subsubtitle_font = pygame.font.SysFont('comicsansms', int(self.base_subsubtitle_font_size * height_scale))
            subsubtitle_text = "Select a Gamemode"
            subsubtitle_surface = subsubtitle_font.render(subsubtitle_text, True, (0, 0, 0))
            subsubtitle_rect = subsubtitle_surface.get_rect()
            subsubtitle_rect.centerx = self.playground_rect.centerx
            subsubtitle_rect.y = int(self.playground_rect.y + self.base_subsubtitle_offset[1]*height_scale)
            self._display_surf.blit(subsubtitle_surface, subsubtitle_rect.topleft)

            self.gamemode1.draw(self._display_surf)
            self.gamemode2.draw(self._display_surf)
            self.gamemode3.draw(self._display_surf)
            high_score_font = pygame.font.SysFont('comicsansms', max(int(self.gamemode2.size / 6), 10))

            if hasattr(self, 'time_trial_high_score') and self.time_trial_high_score is not None:
                
                time_trial_score_text = f"High Score:"
                time_trial_score_value_text = f"{self.time_trial_high_score}"

                
                time_trial_score_surface = high_score_font.render(time_trial_score_text, True, (0, 0, 0))
                time_trial_score_value_surface = high_score_font.render(time_trial_score_value_text, True, (0, 0, 0))

                
                time_trial_score_rect = time_trial_score_surface.get_rect(
                    centerx=self.gamemode2.x,
                    centery=self.gamemode2.y + self.gamemode2.size // 3  
                )
                time_trial_score_value_rect = time_trial_score_value_surface.get_rect(
                    centerx=self.gamemode2.x,
                    centery=self.gamemode2.y + self.gamemode2.size // 3 + high_score_font.get_height()
                )

                
                self._display_surf.blit(time_trial_score_surface, time_trial_score_rect)
                self._display_surf.blit(time_trial_score_value_surface, time_trial_score_value_rect)

            
            if hasattr(self, 'survival_high_score') and self.survival_high_score is not None:
                
                survival_score_text = f"High Score:"
                survival_score_value_text = f"{self.survival_high_score}"

                
                survival_score_surface = high_score_font.render(survival_score_text, True, (0, 0, 0))
                survival_score_value_surface = high_score_font.render(survival_score_value_text, True, (0, 0, 0))

                
                survival_score_rect = survival_score_surface.get_rect(
                    centerx=self.gamemode1.x,
                    centery=self.gamemode1.y + self.gamemode1.size // 3  
                )
                survival_score_value_rect = survival_score_value_surface.get_rect(
                    centerx=self.gamemode1.x,
                    centery=self.gamemode1.y + self.gamemode1.size // 3 + high_score_font.get_height()
                )

                
                self._display_surf.blit(survival_score_surface, survival_score_rect)
                self._display_surf.blit(survival_score_value_surface, survival_score_value_rect)

        elif self.current_screen == "time_trial" and self.time_trial:
            self.time_trial.run_once(self._display_surf)
        elif self.current_screen == "survival" and self.survival:
            self.survival.run_once(self._display_surf)
        elif self.current_screen == "database_search" and self.database_search:
            self.database_search.run_once(self._display_surf)
        elif self.current_screen == "blind_mode" and self.blind_mode:
            self.blind_mode.run_once(self._display_surf)

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

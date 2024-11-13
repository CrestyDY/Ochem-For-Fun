import pygame
import math

class HexButton:
    def __init__(self, x, y, size, color, hover_color, text, text_color=(0, 0, 0)):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.hover_color = hover_color  # Color when hovered
        self.text = text
        self.text_color = text_color
        self.points = self.calculate_hex_points()
        self.is_hovered = False  # Track if the mouse is over the button

    def calculate_hex_points(self, size_adjustment=0):
        # Calculates the six points of a hexagon with an optional size adjustment for border
        points = []
        for i in range(6):
            angle_deg = 60 * i
            angle_rad = math.radians(angle_deg)
            x = self.x + (self.size + size_adjustment) * math.cos(angle_rad)
            y = self.y + (self.size + size_adjustment) * math.sin(angle_rad)
            points.append((x, y))
        return points

    def draw(self, surface):
        # Change color if hovered
        hex_color = self.hover_color if self.is_hovered else self.color

        # Draw border hexagon (slightly larger than the main hexagon)
        border_color = (0, 0, 0)  # Black border color
        border_points = self.calculate_hex_points(size_adjustment=5)  # Adjust size for the border
        pygame.draw.polygon(surface, border_color, border_points)

        # Draw main hexagon with hover effect
        pygame.draw.polygon(surface, hex_color, self.points)

        # Draw text inside hexagon
        font = pygame.font.SysFont('comicsansms', 24)  # Font for button text
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        # Check if the mouse position is within the hexagon
        poly_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.polygon(poly_surface, (255, 255, 255, 255), self.points)
        return poly_surface.get_rect(topleft=(self.x - self.size, self.y - self.size)).collidepoint(pos)

    def check_hover(self, mouse_pos):
        # Check if mouse is over the hexagon
        self.is_hovered = pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2).collidepoint(mouse_pos)

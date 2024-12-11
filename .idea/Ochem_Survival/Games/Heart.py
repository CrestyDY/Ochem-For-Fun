import pygame
import sys
import os

def get_image_path(self, filename):
    return os.path.join(self.base_path, 'images', filename)
full_heart = pygame.image.load(get_image_path('full_heart.png')).convert_alpha()
empty_heart = pygame.image.load(get_image_path('empty_heart.png')).convert_alpha()
#class(pygame.sprite.Sprite):

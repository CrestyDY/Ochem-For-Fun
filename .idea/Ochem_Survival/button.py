class Button(pygame.sprite.Sprite):

    def _create_image(self, color, outline, text, rect):

        img = pygame.Surface(rect.size, pygame.SRCALPHA)  # <---

        if outline:
            img.fill(outline)
            img.fill(color, rect.inflate(-4, -4))
        else:
            img.fill(color)
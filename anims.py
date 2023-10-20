import pygame
import math
class Scroll(pygame.sprite.Sprite):
	def __init__(self, x, y, done):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1,11):
			img = pygame.image.load(f"assets/images/scroll_anim_frames/frame_{num}.png")
			img = pygame.transform.scale(img, (86*11, 56*11))
			self.images.append(img)
		self.index = 0
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.counter = 0
		self.done = done

	def update(self):
		scroll_speed = 2.2 # lower is faster
		
		#update explosion animation
		self.counter += 1

		if self.counter >= scroll_speed and self.index < len(self.images) - 1:
			self.counter = 0
			self.index += 1
			self.image = self.images[self.index]

		#if the animation is complete, reset animation index
		if self.index >= len(self.images) - 1 and self.counter >= scroll_speed:
			self.done = True
			
		if self.done == True:
			self.kill()

class Background(pygame.sprite.Sprite):
    def __init__(self, x, y, done, loop=True):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 39):
            img = pygame.image.load(f"assets/images/bg_anim_frames/bg_frame_{num}.png")
            img = pygame.transform.scale(img, (1200, 730))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0
        self.done = done
        self.loop = loop  # Added loop option

    def update(self):
        scroll_speed = 8.5  # Lower is faster

        # Update the explosion animation
        self.counter += 1

        if self.counter >= scroll_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        # If the animation is complete
        if self.index >= len(self.images) - 1 and self.counter >= scroll_speed:
            if self.loop:
                # Reset the animation
                self.index = 0
                self.image = self.images[self.index]
            else:
                self.done = True

        if self.done == True:
            self.kill()
		
background_group = pygame.sprite.Group()
scroll_group = pygame.sprite.Group()


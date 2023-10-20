# Export
# Itch and github
# remove this lol
import pygame
import pymunk
import pymunk.pygame_util
import math
import asyncio

from anims import Scroll, Background
from anims import scroll_group, background_group


# Load and play the background music
pygame.mixer.init()
pygame.mixer.music.load("assets/jazz_music.mp3")  # Replace with your audio file
pygame.mixer.music.set_volume(0.12)  # Adjust volume if needed
pygame.mixer.music.play(-1)  # Play on loop indefinitely

class PoolGame:
    def __init__(self):
        pygame.init()

        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 678
        self.BOTTOM_PANEL = 50

        # Game window
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT + self.BOTTOM_PANEL))
        pygame.display.set_caption("Pool")

        # Pymunk space
        self.space = pymunk.Space()
        self.static_body = self.space.static_body
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        # Clock
        self.clock = pygame.time.Clock()
        self.FPS = 300

        # Game variables
        self.red_lives = 3
        self.blue_lives = 3
        self.red_points = 0
        self.blue_points = 0

        self.slidieness = 40  # Lower is more slidy
        self.dia = 36
        self.pocket_dia = 66
        self.force = 0
        self.max_force = 22000
        self.force_direction = 1

        self.game_running = True
        self.cue_ball_potted = False
        self.taking_shot = True
        self.powering_up = False
        self.shot_taken = True
        self.quit_started = False
        self.info_anim_done = False

        self.player_turn = 1

        self.potted_balls = []
        self.balls = []  # Initialize balls here

        self.game_mode = ""
        self.game_text = ""
        self.game_text_colour = (255,255,255)

        # Colors
        self.BG = (70, 70, 70)
        self.RED = (255, 0, 0)
        self.WHITE = (255, 255, 255)

        self.TEAM_RED = (211,44,33)
        self.TEAM_BLUE = (14,55,204)
        self.TEAM_TRAINING = (255, 160, 0)

        self.TEXT_RED = (255,135,135)
        self.TEXT_BLUE = (135,135,255)
        self.TEXT_TRAINING = (255, 150, 0)

        self.img_scale = (44,44)

        # Fonts
        self.font = pygame.font.SysFont("Lato", 30)
        self.large_font = pygame.font.SysFont("Lato", 60)
        self.pixel_font = pygame.font.Font("assets/Pixel_font.ttf", 15)
        self.pixel_large_font = pygame.font.Font("assets/Pixel_font.ttf", 40)
        # Load images
        self.red_heart = pygame.image.load("assets/images/red_heart.png").convert_alpha()
        self.red_heart = pygame.transform.scale(self.red_heart, (36, 32))
        self.blue_heart = pygame.image.load("assets/images/blue_heart.png").convert_alpha()
        self.blue_heart = pygame.transform.scale(self.blue_heart, (36, 32))

        self.red_cue_image = pygame.image.load("assets/images/red_cue.png").convert_alpha()
        self.blue_cue_image = pygame.image.load("assets/images/blue_cue.png").convert_alpha()

        self.table_image_border = pygame.image.load("assets/images/pool_table_border_fix.png").convert_alpha()
        self.table_image_ice = pygame.image.load("assets/images/pool_table_ice_fix.png").convert_alpha()
        self.table_image_border = pygame.transform.scale(self.table_image_border, (1200, 678))
        self.table_image_ice = pygame.transform.scale(self.table_image_ice, (1200,678))

        self.ice_button = pygame.image.load("assets/images/button.png").convert_alpha()
        self.ice_button = pygame.transform.scale(self.ice_button, (208*1.5, 122*1.5))
        self.ice_button_small = pygame.transform.scale(self.ice_button, (208, 122))
        self.button_offset = self.ice_button.get_size()
        self.title = pygame.image.load("assets/images/title.png").convert_alpha()
        self.title = pygame.transform.scale(self.title, (1200,400))
        self.full_scroll_img = pygame.image.load(f"assets/images/scroll_anim_frames/frame_10.png")
        self.full_scroll_img = pygame.transform.scale(self.full_scroll_img, (86*11, 56*11))

        self.ball_images = []

        #sounds
        self.sfx = {
            'putt' : pygame.mixer.Sound('assets/sfx/putt.wav'),
            'click' : pygame.mixer.Sound('assets/sfx/click.wav'),
            'shoot' : pygame.mixer.Sound('assets/sfx/shoot.wav'),
            'hooray' : pygame.mixer.Sound('assets/sfx/hooray.wav'),
            'hurt' : pygame.mixer.Sound('assets/sfx/hurt.wav'),
            'whoosh' : pygame.mixer.Sound('assets/sfx/whoosh.wav'),
        }

        self.sfx['putt'].set_volume(0.30)
        self.sfx['click'].set_volume(0.50)
        self.sfx['shoot'].set_volume(0.50)
        self.sfx['hooray'].set_volume(0.45)
        self.sfx['hurt'].set_volume(0.65)
        self.sfx['whoosh'].set_volume(0.48)

        #anim stuff
        self.scroll_group = scroll_group
        self.scroll = Scroll(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2, False)

        self.bg_group = background_group
        self.background = Background(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2+25, False, loop=True)

        for i in range(1, 17):
            ball_image = pygame.image.load(f"assets/images/ball_{i}.png").convert_alpha()
            ball_image = pygame.transform.scale(ball_image, self.img_scale)
            self.ball_images.append(ball_image)

        # Create power bars to show how hard the cue ball will be hit
        self.power_bar = pygame.Surface((10, 20))
        self.power_bar.fill(self.RED)  # Change to blit a pixel art thing

        # Create pool cue
        self.cue = None  # Cue will be initialized later

    def create_cue(self, pos, turn, mode):
        cue = {}
        if mode != "Training Mode":
            if turn == 1:
                cue["original_image"] = pygame.image.load("assets/images/red_cue.png").convert_alpha()
            else:
                cue["original_image"] = pygame.image.load("assets/images/blue_cue.png").convert_alpha()
        else:
            cue["original_image"] = pygame.image.load("assets/images/orange_cue.png").convert_alpha()
        cue["angle"] = 0
        cue["image"] = pygame.transform.rotate(cue["original_image"], cue["angle"])
        cue["rect"] = cue["image"].get_rect()
        cue["rect"].center = pos

        return cue

    def update_cue(self, cue, angle):
        cue["angle"] = angle

    def draw_cue(self, cue, surface):
        cue["image"] = pygame.transform.rotate(cue["original_image"], cue["angle"])
        surface.blit(cue["image"],
                     (cue["rect"].centerx - cue["image"].get_width() / 2,
                      cue["rect"].centery - cue["image"].get_height() / 2)
                     )

    def create_ball(self, radius, pos):
        body = pymunk.Body()
        body.position = pos
        shape = pymunk.Circle(body, radius)
        shape.mass = 5
        shape.elasticity = 0.8
        # Use pivot joint to add friction
        pivot = pymunk.PivotJoint(self.static_body, body, (0, 0), (0, 0))
        pivot.max_bias = 0  # Disable joint correction
        pivot.max_force = self.slidieness  # Emulate linear friction

        self.space.add(body, shape, pivot)
        return shape

    def remove_ball(self, ball_shape):
        # Remove the shape, its body, and any associated joints
        self.space.remove(ball_shape)
        self.space.remove(ball_shape.body)
        for constraint in self.space.constraints:
            if isinstance(constraint, pymunk.PivotJoint) and (constraint.a == self.static_body or constraint.b == ball_shape.body):
                self.space.remove(constraint)

    def setup_balls(self):
        # Setup game balls
        balls = []
        rows = 5
        # Potting balls
        for col in range(rows):
            for row in range(rows):
                pos = (250 + (col * (self.dia + 1)), 267 + (row * (self.dia + 1)) + (col * self.dia / 2))
                new_ball = self.create_ball(self.dia / 2, pos)
                balls.append(new_ball)
            rows -= 1
        # Cue ball
        pos = (888, self.SCREEN_HEIGHT / 2)
        cue_ball = self.create_ball(self.dia / 2, pos)
        balls.append(cue_ball)
        return balls

    def create_cushion(self, poly_dims):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = (0, 0)
        shape = pymunk.Poly(body, poly_dims)
        shape.elasticity = 0.8
        self.space.add(body, shape)

    def reset_game(self):
        for ball in self.balls:
            # self.space.remove(ball.body)
            self.remove_ball(ball_shape=ball)
        self.potted_balls = []

        self.red_lives = 3
        self.blue_lives = 3
        self.red_points = 0
        self.blue_points = 0

        self.game_running = True
        self.cue_ball_potted = False
        self.taking_shot = True
        self.powering_up = False
        
        self.scroll_group = scroll_group
        self.scroll = Scroll(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2, False)

        self.bg_group = background_group
        self.background = Background(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2+25, False, loop=True)

        self.ball_images = []  # Initialize ball images here
        for i in range(1, 17):
            ball_image = pygame.image.load(f"assets/images/ball_{i}.png").convert_alpha()
            ball_image = pygame.transform.scale(ball_image, self.img_scale)
            self.ball_images.append(ball_image)
        self.balls = self.setup_balls()
        self.cue = self.create_cue(self.balls[-1].body.position, self.player_turn, self.game_mode)

    def run_game(self):
        run = True
        pygame.mixer.music.set_volume(0.12)  # Adjust volume if needed
        while run:
            self.clock.tick(self.FPS)
            self.space.step(1 / self.FPS)

            # Fill background
            self.screen.fill(self.BG)

            # Draw pool table
            self.screen.blit(self.table_image_border, (0, 0))
            self.screen.blit(self.table_image_ice, (0, 0))

            
            # Check if any balls have been potted 
            for i, ball in enumerate(self.balls):
                for pocket in self.pockets:
                    ball_x_dist = abs(ball.body.position[0] - pocket[0])
                    ball_y_dist = abs(ball.body.position[1] - pocket[1])
                    ball_dist = math.sqrt((ball_x_dist ** 2) + (ball_y_dist ** 2))
                    if ball_dist <= self.pocket_dia / 2:
                        # Check if the potted ball was the cue ball
                        if i == len(self.balls) - 1:
                            if self.player_turn == -1:
                                self.red_lives -= 1
                            else:
                                self.blue_lives -= 1
                            self.sfx['hurt'].play()
                            self.cue_ball_potted = True
                            ball.body.position = (-100, -100)
                            ball.body.velocity = (0.0, 0.0)
                        else:
                            ball.body.position = (-200, -200)
                            self.space.remove(ball.body)
                            self.balls.remove(ball)
                            self.potted_balls.append(self.ball_images[i])
                            self.ball_images.pop(i)
                            self.sfx['putt'].play()
                            if self.player_turn == -1: #its reversed cuz the teams change instantly, you cant see that cuz the stick is hidden tho lol
                                self.red_points += 1
                            else:
                                self.blue_points += 1
            for pocket_loc in self.pockets:
                pygame.draw.circle(self.screen, (0, 0, 0), pocket_loc, 30)

            for c in self.cushions:
                pygame.draw.polygon(self.screen, (255, 255, 255), c)

            # Draw pool balls
            for ball, ball_image in zip(self.balls, self.ball_images):
                self.screen.blit(ball_image, (ball.body.position[0] - ball.radius, ball.body.position[1] - ball.radius))

            # Check if all the balls have stopped moving
            self.taking_shot = True
            for ball in self.balls:
                if int(ball.body.velocity[0]) != 0 or int(ball.body.velocity[1]) != 0:
                    self.taking_shot = False

            # Change player turn when a shot is taken and balls have stopped moving
            if self.shot_taken and not self.taking_shot:
                if self.game_mode != "Training Mode":
                    self.player_turn *= -1
                else:
                    self.player_turn = -1
                self.shot_taken = False
                    
            # Draw pool cue
            if self.taking_shot == True and self.game_running == True:
                self.shot_taken = True
                if self.cue_ball_potted == True:
                    # Reposition cue ball
                    self.balls[-1].body.position = (888, self.SCREEN_HEIGHT / 2)
                    self.cue_ball_potted = False
                # Calculate pool cue angle
                mouse_pos = pygame.mouse.get_pos()
                self.cue = self.create_cue(self.balls[-1].body.position, self.player_turn, self.game_mode)
                x_dist = self.balls[-1].body.position[0] - mouse_pos[0]
                y_dist = -(self.balls[-1].body.position[1] - mouse_pos[1])  # -ve because pygame y coordinates increase down the screen
                cue_angle = math.degrees(math.atan2(y_dist, x_dist))
                self.update_cue(self.cue, cue_angle)
                self.draw_cue(self.cue, self.screen)

            # Power up pool cue
            if self.powering_up == True and self.game_running == True:
                self.force += 100 * self.force_direction
                if self.force >= self.max_force or self.force <= 0:
                    self.force_direction *= -1
                # Draw power bars
                for b in range(math.ceil(self.force / 2000)):
                    self.screen.blit(self.power_bar,
                                     (self.balls[-1].body.position[0] - (math.ceil(self.force / 2000) * 6.3) + (b * 15),
                                      self.balls[-1].body.position[1] + 30))
            elif self.powering_up == False and self.taking_shot == True:
                x_impulse = math.cos(math.radians(self.cue["angle"]))
                y_impulse = math.sin(math.radians(self.cue["angle"]))
                self.balls[-1].body.apply_impulse_at_local_point((self.force * -x_impulse, self.force * y_impulse), (0, 0))
                self.force = 0
                self.force_direction = 1

            #overlay panel so that nothing clips in
            pygame.draw.rect(self.screen, (self.BG), (0, self.SCREEN_HEIGHT, self.SCREEN_WIDTH, self.BOTTOM_PANEL))
            # Draw hearts
            if self.game_mode != "Training Mode":
                for i in range(self.red_lives):
                    self.screen.blit(self.red_heart, (425 - (i * 40), 15))

                for i in range(self.blue_lives):
                    self.screen.blit(self.blue_heart, (715 + (i * 40), 15))
            else:
                for i in range(self.red_lives):
                    self.screen.blit(self.red_heart, (655 + (i * 40), 15))
            # Draw points 
            if self.game_mode != "Training Mode":
                self.draw_text(str(self.red_points), self.pixel_large_font, self.TEAM_RED, self.SCREEN_WIDTH/2 - 115, 8) 
                self.draw_text(str(self.blue_points), self.pixel_large_font, self.TEAM_BLUE, self.SCREEN_WIDTH/2 + 55, 8)
            else:
                self.draw_text(str(self.red_points), self.pixel_large_font, self.TEAM_TRAINING, self.SCREEN_WIDTH/2 - 115, 8)

            # Draw potted balls in the bottom panel 
            for i, ball in enumerate(self.potted_balls):
                self.screen.blit(ball, (10 + (i * 50), self.SCREEN_HEIGHT + 5))

            #draws scroll here so it isnt behind anything except text
            self.scroll_group.draw(self.screen)
            self.scroll_group.update()

            # Game over + info screen
            if self.red_lives <= 0 or self.blue_lives <= 0 or (len(self.balls) == 1 and self.red_points == self.blue_points) or (len(self.balls) == 1 and self.red_points > self.blue_points) or (len(self.balls) == 1 and self.red_points > self.blue_points):
                self.scroll_group.add(self.scroll)
                if self.scroll.done == False:
                    self.sfx['hooray'].play()
                else:
                    if self.game_mode == "Training Mode":
                        self.game_text = "Good Job Kid!"
                        self.game_text_colour = self.TEXT_TRAINING
                    elif self.red_lives > self.blue_lives or self.red_points > self.blue_points:
                        self.game_text = "Red Victory"
                        self.game_text_colour = self.TEXT_RED
                    elif self.blue_lives > self.red_lives or self.blue_points > self.red_points:
                        self.game_text = "Blue Victory"
                        self.game_text_colour = self.TEXT_BLUE
                    elif self.blue_lives == self.red_lives or (len(self.balls) == 1 and self.red_points == self.blue_points): # first statement may cause bugs its just there in case
                        self.game_text = "Twas a Tie"
                        self.game_text_colour = self.WHITE
                    #final points (left)
                    if self.game_mode != "Training Mode":
                        self.draw_text(f"{self.game_text}!", self.pixel_large_font, self.game_text_colour, self.SCREEN_WIDTH / 2 - (21*len(self.game_text)), self.SCREEN_HEIGHT / 2 - 170) # Result text
                        self.draw_text(f"{self.red_points} points!", self.pixel_font, self.TEXT_RED, self.SCREEN_WIDTH / 2 - (25*len(self.game_text)), self.SCREEN_HEIGHT / 2 - 105) 
                        self.draw_text(f"{self.blue_points} points!", self.pixel_font, self.TEXT_BLUE, self.SCREEN_WIDTH / 2 + (12*len(self.game_text)), self.SCREEN_HEIGHT / 2 - 105) 
                        #lives (right)
                        self.draw_text(f"{self.red_lives} lives left!", self.pixel_font, self.TEXT_RED, self.SCREEN_WIDTH / 2 - (25*len(self.game_text)), self.SCREEN_HEIGHT / 2 - 85) 
                        self.draw_text(f"{self.blue_lives} lives left!", self.pixel_font, self.TEXT_BLUE, self.SCREEN_WIDTH / 2 + (12*len(self.game_text)), self.SCREEN_HEIGHT / 2 - 85) 
                    else:
                        self.draw_text(f"{self.game_text}!", self.pixel_large_font, self.game_text_colour, self.SCREEN_WIDTH / 2 - (19*len(self.game_text)), self.SCREEN_HEIGHT / 2 - 170) # Result text
                        self.draw_text(f"{self.red_points} points!", self.pixel_font, self.TEXT_TRAINING, self.SCREEN_WIDTH / 2 - (5*len(self.game_text)), self.SCREEN_HEIGHT / 2 - 105) 
                        self.draw_text(f"{self.red_lives} lives left!", self.pixel_font, self.TEXT_TRAINING, self.SCREEN_WIDTH / 2 - (5*len(self.game_text)), self.SCREEN_HEIGHT / 2 - 85) 

                    # Buttons (main menu, play again)
                    self.game_running = False

            # Event handler
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit_started = True
                if event.type == pygame.KEYUP and self.quit_started == True:
                    self.quit_started = False
                    if event.key == pygame.K_ESCAPE:
                        self.sfx['whoosh'].play()
                        self.main_menu()
                        self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and self.game_running == False:
                    self.click_started = True
                if event.type == pygame.MOUSEBUTTONUP and self.game_running == False and self.click_started == True:
                    self.click_started = False
                if event.type == pygame.MOUSEBUTTONDOWN and self.taking_shot == True:
                    self.powering_up = True
                if event.type == pygame.MOUSEBUTTONUP and self.taking_shot == True and self.game_running:
                    self.powering_up = False
                    self.sfx['shoot'].play()
                if event.type == pygame.QUIT:
                    run = False

            #Post-Game GUI buttons
            if self.game_running == False:
                mx, my = pygame.mouse.get_pos()

                self.button_1 = pygame.Rect(self.SCREEN_WIDTH/2-300, 400, 200, 110)
                self.button_2 = pygame.Rect(self.SCREEN_WIDTH/2+75, 400, 200, 110)

                self.screen.blit(self.ice_button_small, (self.SCREEN_WIDTH/2-308, 500-100))
                self.draw_text("Main Menu", self.pixel_font, (0, 0, 0), self.SCREEN_WIDTH/2-270, 500-64)

                self.screen.blit(self.ice_button_small, (self.SCREEN_WIDTH/2+70, 500-100))
                self.draw_text("Play Again", self.pixel_font, (0, 0, 0), self.SCREEN_WIDTH/2+105, 500-64)

                #pygame.draw.rect(self.screen, (255,0,0), self.button_1)
                #pygame.draw.rect(self.screen, (255,0,0), self.button_2)

                if self.button_1.collidepoint((mx, my)):
                    if self.click_started:
                        self.sfx['click'].play()
                        self.click_started = False
                        self.main_menu()
                        self.run = False
                if self.button_2.collidepoint((mx, my)):
                    if self.click_started:
                        self.sfx['click'].play()
                        self.click_started = False
                        self.reset_game()
                        self.run = False

            pygame.display.update()

        pygame.quit()

    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def main_menu(self):
        run = True
        self.clicking = False
        pygame.mixer.music.set_volume(0.045)  # Adjust volume if needed
        while run:
            self.bg_group.draw(self.screen)

            self.bg_group.add(self.background)
            self.bg_group.update()

            mx, my = pygame.mouse.get_pos()

            self.button_1 = pygame.Rect(self.SCREEN_WIDTH/2-150, 140-1+10, 300, 120)
            self.button_2 = pygame.Rect(self.SCREEN_WIDTH/2-150, 325+12+10, 300, 120)
            self.button_3 = pygame.Rect(self.SCREEN_WIDTH/2-150, 510+20+10, 300, 120)

            
            self.screen.blit(self.ice_button, (self.SCREEN_WIDTH/2-160, 500+20+10))
            self.screen.blit(self.ice_button, (self.SCREEN_WIDTH/2-160, 320+12+10))
            self.screen.blit(self.ice_button, (self.SCREEN_WIDTH/2-160, 120+12+10))
            self.draw_text("PvP", self.pixel_large_font, (0, 0, 0), self.SCREEN_WIDTH/2-70, 170+12+10)
            self.draw_text("Train", self.pixel_large_font, (0, 0, 0), self.SCREEN_WIDTH/2-100, 370+12+10)
            self.draw_text("Info", self.pixel_large_font, (0, 0, 0), self.SCREEN_WIDTH/2-85, 540+20+10)
            
            #pygame.draw.rect(self.screen, (255,0,0), self.button_1)
            #pygame.draw.rect(self.screen, (255,0,0), self.button_2)
            #pygame.draw.rect(self.screen, (255,0,0), self.button_3)
            
            self.screen.blit(self.title, (self.SCREEN_WIDTH/2-560, -120))

            if self.button_1.collidepoint((mx,my)):
                if self.clicking:
                    self.sfx['click'].play()
                    self.game_mode = "LPVP"
                    self.main()
                    self.run = False
            if self.button_2.collidepoint((mx,my)):
                if self.clicking:
                    self.sfx['click'].play()
                    self.game_mode = "Training Mode"
                    self.main()
                    self.run = False
            if self.button_3.collidepoint((mx,my)):
                if self.clicking:
                    self.sfx['click'].play()
                    self.instructions()
                    self.run = False
            
            self.clicking = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.click_started = True
                if event.type == pygame.MOUSEBUTTONUP and self.click_started:
                    self.click_started = False
                    self.clicking = True
            pygame.display.update()
            self.clock.tick(self.FPS)

    def instructions(self):
        run = True
        self.clicking = False
        pygame.mixer.music.set_volume(0.045)  # Adjust volume if needed
        while run:
            self.bg_group.draw(self.screen)
            self.bg_group.add(self.background)
            self.bg_group.update()

            if self.info_anim_done == False:
                self.scroll_group.update()
                self.scroll_group.add(self.scroll)
                self.scroll_group.draw(self.screen)

            if self.scroll.done:
                self.info_anim_done = True
            if self.info_anim_done:
                self.screen.blit(self.full_scroll_img, (127, 31))
            

            mx, my = pygame.mouse.get_pos()

            self.button_1 = pygame.Rect(self.SCREEN_WIDTH/2-140, 510, 300, 130)
            if self.info_anim_done:
                self.screen.blit(self.ice_button, (self.SCREEN_WIDTH/2-150, 500))
                self.draw_text("Back", self.pixel_large_font, (0, 0, 0), self.SCREEN_WIDTH/2-85, 500+50)

                self.draw_text("See which player is up to hit by the stick tint!", self.pixel_font, (0, 0, 0), self.SCREEN_WIDTH/2-331, 100+90)
                self.draw_text("Hit any ball into the holes to gain points!", self.pixel_font, (0, 0, 0), self.SCREEN_WIDTH/2-285, 200+90)
                self.draw_text("You lose lives if the cue ball falls into a hole", self.pixel_font, (0, 0, 0), self.SCREEN_WIDTH/2-322, 300+110)
                self.draw_text("dont lose them all!", self.pixel_font, (0, 0, 0), self.SCREEN_WIDTH/2-130, 320+110)

            #pygame.draw.rect(self.screen, (255,0,0), self.button_1)

            
            if self.button_1.collidepoint((mx,my)):
                if self.clicking:
                    self.sfx['whoosh'].play()
                    self.main_menu()
                    self.scroll_group.remove()
                    self.run = False
            
            self.clicking = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.click_started = True
                if event.type == pygame.MOUSEBUTTONUP and self.click_started:
                    self.click_started = False
                    self.clicking = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit_started = True
                if event.type == pygame.KEYUP and self.quit_started == True:
                    self.quit_started = False
                    if event.key == pygame.K_ESCAPE:
                        self.sfx['whoosh'].play()
                        self.main_menu()
                        self.running = False
            pygame.display.update()
            self.clock.tick(self.FPS)

    def main(self):
        # Create six pockets on the table
        self.pockets = [
            (55, 63),
            (592, 48),
            (1134, 64),
            (55, 616),
            (592, 629),
            (1134, 616)
        ]

        # Create pool table cushions
        self.cushions = [
            [(88, 56), (109, 77), (555, 77), (561, 56)],
            [(621, 56), (630, 77), (1081, 77), (1102, 56)],
            [(89, 621), (110, 600), (556, 600), (562, 621)], # bottom left
            [(622, 621), (630, 600), (1081, 600), (1102, 621)],
            [(56, 96), (77, 117), (77, 560), (56, 581)],
            [(1143, 96), (1122, 117), (1122, 560), (1143, 581)]
        ]

        # Create cushions
        for c in self.cushions:
            self.create_cushion(c)

        if self.game_mode == "LPVP":
            self.reset_game() # Initialize balls here
            self.run_game()
        if self.game_mode == "Training Mode":
            self.reset_game() # Initialize balls here
            self.run_game()

async def main():
    try:
        ran = False
        if __name__ == "__main__" and ran != True:
            ran = True
            pool_game = PoolGame()
            pool_game.main_menu()
            await asyncio.sleep(0)
    except:
        pass

asyncio.run(main())

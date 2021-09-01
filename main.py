  
import pygame
import os
import random
import math

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

FPS = 60
BULLET_VEL = 7

class Bullet:
    def __init__(self, display_surface, x, y, player_aligned, bounds):
        # create collision boundary
        self.size = self.width, self.height = 40, 20
        self.rect = pygame.Rect(x - self.width / 2, y - self.height / 2, self.width, self.height)
        self.bounds = bounds

        # load sprite image and create sprite
        self.sprite_image = pygame.image.load(
            os.path.join('Assets', 'projectile.png'))

        if player_aligned:
            # scale sprite to be size of collision box
            self.sprite = pygame.transform.scale(self.sprite_image, (self.width, self.height))
            # shooting to the right
            self.horizontal_velocity = 14
        else:
            # scale, rotate 180 degrees so its facing leftwards
            self.sprite = pygame.transform.rotate(pygame.transform.scale(self.sprite_image, (self.width, self.height)), 180)
            # shooting to the left
            self.horizontal_velocity = -6

        # save the main display surface so we can draw our sprite to it
        self.display_surf = display_surface

    def on_loop(self, targets): 
        # method returns false if the bullet collides with object or goes oout of bounds
        self.rect.x += self.horizontal_velocity

        # check if the bullet is out of bounds
        if not self.bounds.colliderect(self.rect):
            return False
        
        # check if any of the targets are colliding with the bullet
        for target in targets:
            if target.rect.colliderect(self.rect):
                pygame.event.post(pygame.event.Event(target.hit_event))
                return False

        return True

    def on_render(self): 
        self.display_surf.blit(self.sprite, (self.rect.x, self.rect.y))

class Player:
    def __init__(self, display_surface, bounds):
        # create collision boundary
        self.size = self.width, self.height = 55, 40
        self.rect = pygame.Rect(200, 300, self.width, self.height)
        self.bounds = bounds
        
        # stats
        self.max_bullets = 3
        self.max_speed = 5
        self.acceleration = .25
        self.screen_movement = .05

        # load sprite image and create sprite
        self.sprite_image = pygame.image.load(
            os.path.join('Assets', 'player.png'))
        # rotate 270 degrees so that its facing rightwards and scale to be the size of the collision box
        self.sprite = pygame.transform.rotate(pygame.transform.scale(self.sprite_image, (self.width, self.height)), 270)

        # set up heart images used for health display
        self.heart_sprite_size = self.heart_sprite_width, self.heart_sprite_height = 20, 20
        self.heart_sprite_image = pygame.image.load(
            os.path.join('Assets', 'fullheart.png'))
        self.heart_sprite = pygame.transform.scale(self.heart_sprite_image, (self.heart_sprite_width, self.heart_sprite_height))
        
        # save the main display surface so we can draw our sprite to it
        self.display_surf = display_surface

        # gameplay variables
        self.bullets = []
        self.health = 5
        self.vertical_velocity = 0
        self.horizontal_velocity = 0

        # create an event that is called when the ship collides with an enemy's bullet
        self.hit_event = pygame.USEREVENT + 1
    
    def on_event(self, event):
        if event.type == self.hit_event:
            self.health -= 1
    
        if event.type == pygame.KEYDOWN:
            # if holding control and there arent already too many of your bullets on screen
            if event.key == pygame.K_LCTRL and len(self.bullets) < self.max_bullets:
                # create a rectangle that starts on the right side of the ship and in the middle vertically
                bullet = Bullet(self.display_surf, self.rect.x + self.width, self.rect.y + self.height//2 - 2, True, self.bounds)
                self.bullets.append(bullet)

    
    def on_loop(self, keys_pressed, targets):
        # check each key to accelerate the velocity in that direction
        if keys_pressed[pygame.K_LEFT]:
            self.horizontal_velocity -= self.acceleration
        elif keys_pressed[pygame.K_RIGHT]:
            self.horizontal_velocity += self.acceleration

        if keys_pressed[pygame.K_UP]:
            self.vertical_velocity -= self.acceleration
        elif keys_pressed[pygame.K_DOWN]:
            self.vertical_velocity += self.acceleration
        
        # create illusion of screen movement by having horizontal velocity naturally move towards the left
        self.horizontal_velocity -= self.screen_movement

        # limit each component of velocity separately
        self.horizontal_velocity = min(self.max_speed, self.horizontal_velocity)
        self.vertical_velocity = min(self.max_speed, self.vertical_velocity)

        # if you wouldnt move out of bounds, move horizontally
        if self.rect.x + self.horizontal_velocity > self.bounds.x and self.rect.x + self.horizontal_velocity + self.width < self.bounds.x + self.bounds.width:
            self.rect.x += self.horizontal_velocity
        else:
            # since we cannot move horizontal, we must have collided with an edge. therefore, lose all horizontal velocity
            self.horizontal_velocity = 0

        # if you wouldnt move out of bounds, move vertically
        if self.rect.y + self.vertical_velocity > self.bounds.y and self.rect.y + self.vertical_velocity + self.height < self.bounds.y + self.bounds.height:
            self.rect.y += self.vertical_velocity
        else:
            # since we cannot move vertically, we must have collided with an edge. therefore, lose all vertical velocity
            self.vertical_velocity = 0
        
        for bullet in self.bullets:
            # bullet loop function returns False if the bullet is out of bounds and needs to be removed
            if not bullet.on_loop(targets):
                self.bullets.remove(bullet)
    1
    def on_render(self):
        self.display_surf.blit(self.sprite, (self.rect.x, self.rect.y))

        for i in range(self.health):
            position_x = self.rect.x - self.heart_sprite_width - 10
            position_y = self.rect.y + self.height / 2  + (i - float(self.health) / 2) * (self.heart_sprite_height + 10)
            self.display_surf.blit(self.heart_sprite, (position_x,position_y))

        for bullet in self.bullets:
            bullet.on_render()

class Enemy:
    def __init__(self, display_surface, id, bounds):
        # create collision boundary
        self.size = self.width, self.height = 55, 40
        self.spawn_x = bounds.width - self.width - random.randint(0, 120)
        self.spawn_y = random.randint(0, bounds.height - self.height)
        self.rect = pygame.Rect(self.spawn_x, self.spawn_y, self.width, self.height)
        self.bounds = bounds
        
        # stats
        self.max_bullets = 3
        self.speed = 5
        self.oscillate_speed = random.random() * .05

        # load sprite image and create sprite
        self.sprite_image = pygame.image.load(
            os.path.join('Assets', 'enemy.png'))
        # rotate 270 degrees so that its facing leftwards and scale to be the size of the collision box
        self.sprite = pygame.transform.rotate(pygame.transform.scale(self.sprite_image, (self.width, self.height)), 90)
        
        # save the main display surface so we can draw our sprite to it
        self.display_surf = display_surface

        # gameplay variables
        self.bullets = []
        self.health = 1
        self.bullet_timer = 1
        self.oscillate_timer_x = 0.0
        self.oscillate_timer_y = 0.0

        # create an event that is called when the ship collides with the player's bullet
        self.hit_event = pygame.USEREVENT + 1 + id
    
    def on_event(self, event):
        if event.type == self.hit_event:
            self.health -= 1
            #BULLET_HIT_SOUND.play()

    def on_loop(self, keys_pressed, target):
        for bullet in self.bullets:
            # bullet loop function returns False if the bullet is out of bounds and needs to be removed
            if not bullet.on_loop([target]):
                self.bullets.remove(bullet)
        
        # if alive and not at max bullets, check to see if its time to shoot a bullet
        if self.health > 0 and len(self.bullets) < self.max_bullets:
            self.bullet_timer -= 1
            # after decrementing timer then check if weve waited long enough
            if self.bullet_timer == 0:
                bullet = Bullet(self.display_surf, self.rect.x, self.rect.y + self.height//2 - 2, False, self.bounds)
                self.bullets.append(bullet)
                # set timer to random value to determine how long to wait
                self.bullet_timer = random.randint(150, 350)
        
        self.oscillate_timer_x += self.oscillate_speed
        self.rect.x = self.spawn_x + math.cos(self.oscillate_timer_x * math.pi) * 12
        self.oscillate_timer_y += self.oscillate_speed * .8
        self.rect.y = self.spawn_y + math.cos(self.oscillate_timer_y * math.pi) * 8 

        # return false if dead and bullets are gone
        if self.health <= 0 and len(self.bullets) == 0:
            return False
        
        return True
    
    def on_render(self):
        # only render self if no dead
        if self.health > 0:
            self.display_surf.blit(self.sprite, (self.rect.x, self.rect.y))

        for bullet in self.bullets:
            bullet.on_render()

class Game:
    def __init__(self):
        self.size = self.width, self.height = 1000, 600
        self.title = "Shoot-Em-Up"

        # initialize pygame
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()

        # set up font used for the score display
        self.score_font = pygame.font.SysFont('comicsans', 40)

        # create pygame window
        self.display_surf = pygame.display.set_mode(self.size)
        pygame.display.set_caption(self.title)
                
        # set the bounds that limits where the player can move
        self.bounds = pygame.Rect(0, 0, self.width, self.height)

        # initialize game objects
        self.player = Player(self.display_surf, self.bounds)
        self.enemies = []

        # load the background images and scale them to the size of the screen
        self.background_list = [
            {"image": pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'bg.png')).convert_alpha(), (self.width, self.height)), "x": 0, "speed": 0},
            {"image": pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'purple.png')).convert_alpha(), (self.width, self.height)), "x": 0, "speed": 0},
            {"image": pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'star1.png')).convert_alpha(), (self.width, self.height)), "x": 0, "speed": 5},
            {"image": pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'star2.png')).convert_alpha(), (self.width, self.height)), "x": 0, "speed": 2},
            {"image": pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'star3.png')).convert_alpha(), (self.width, self.height)), "x": 0, "speed": 3}
        ]

        # gameplay variables
        self.clock = pygame.time.Clock()
        self.score = 0
        self.enemies_created = 0
        self.enemy_spawn_timer = 1

        # used to determine if the game should stop running when "X" on window is pressed
        self.running = True
 
    def spawn_enemy(self):
        self.enemies_created += 1
        new_enemy = Enemy(self.display_surf, self.enemies_created, self.bounds)
        self.enemies.append(new_enemy)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        
        # pass event to children
        self.player.on_event(event)
        for enemy in self.enemies:
            enemy.on_event(event)
    
    def on_loop(self):
        # tick the clock to keep things smooth
        self.clock.tick(FPS)

        # move the background by a certain amount each frame, different depending on its distance to create an illusion of depth
        # use a mod function so that it loops once it has scrolled the length of the screen horizontally
        for background in self.background_list:
            background["x"] = (background["x"] + background["speed"]) % self.width

        # determine which keys are pressed and pass them to children
        keys_pressed = pygame.key.get_pressed()
        self.player.on_loop(keys_pressed, self.enemies)

        # spawn more enemies if enough have been defeated, but only after enough time passes
        if len(self.enemies) < 4:
            self.enemy_spawn_timer -= 1
            if self.enemy_spawn_timer == 0:
                self.spawn_enemy()
                # set a random respawn time so they arent predictable
                self.enemy_spawn_timer = random.randint(25,40)

        for enemy in self.enemies:
            # enemy on_loop returns False when dead
            if not enemy.on_loop(keys_pressed, self.player):
                self.enemies.remove(enemy)
                self.score += 10
    
    def on_render(self):
        # go through each background and render it twice to create a seemless loop
        for background in self.background_list:
            self.display_surf.blit(background["image"], (-background["x"], 0))
            self.display_surf.blit(background["image"], (-background["x"] + self.width, 0))

        # display the score ui in text
        score_text = self.score_font.render(
            "Score: " + str(self.score), 1, WHITE)
        self.display_surf.blit(score_text, (self.width - score_text.get_width() - 10, 10))

        self.player.on_render()

        for enemy in self.enemies:
            enemy.on_render()

        pygame.display.update()

    def on_quit(self):
        pygame.quit()
 
    def on_execute(self):
        # main game loop that continues until window is shut
        while self.running:
            # loop through each event pygame gives us and call our event function for it
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_quit()



if __name__ == "__main__":
    game = Game()
    game.on_execute()

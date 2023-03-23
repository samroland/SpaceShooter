import sys
import pygame, pymunk
from pymunk.vec2d import Vec2d
from collision import CollisionHandler
import color
from entity import EntitySet
from player import Player
from border import Border
from enemies import Square, Spawner, Diamond, Circle, BlackHole
from sprites import Sprite
from display import build_menu, Hud
import params
import utils
from random import randint, random
from numpy import pi, log2

state_map = {"play":0, "pause":1, "game_over":2}

class Session():
    def __init__(self, background=color.dark_gray, framerate=params.framerate, ticks_per_frame=params.ticks_per_frame):
        self.background = background
        self.framerate = framerate
        self.ticks_per_frame = ticks_per_frame
        self.event_list = []

        pygame.init()

        self.flags = pygame.FULLSCREEN
        display_size = pygame.display.list_modes()[0] 
        # size=display_size, for max resolution
        # size=(0,0) for lower resolution
        self.screen = pygame.display.set_mode(size=(0,0), flags=self.flags, vsync=1)
        self.screen_size = pygame.display.get_window_size()
        self.clock = pygame.time.Clock()

        self.dim_rgba = self.background.rgb + (200,)
        self.dim_surface = pygame.Surface(self.screen_size, flags = pygame.SRCALPHA)
        self.dim_surface.fill(self.dim_rgba)

        self.xlim = [params.wall_offset, self.screen_size[0]-params.wall_offset]
        self.ylim = [params.wall_offset, self.screen_size[1]-params.wall_offset]

        self.player_sprite = Sprite(self, "images/Player.png")
        self.bullet_sprite = Sprite(self, "images/Bullet.png")
        
        mini_scale = 0.5

        self.square_sprite = Sprite(self, "images/Square.png")
        self.mini_square_sprite = Sprite(self, "images/Square.png", image_scale=params.image_scale*mini_scale)
        
        self.diamond_sprite = Sprite(self, "images/Diamond.png")
        self.mini_diamond_sprite = Sprite(self, "images/Diamond.png", image_scale=params.image_scale*mini_scale)

        self.circle_sprite = Sprite(self, "images/Circle.png", angle_resolution=360)
        self.mini_circle_sprite = Sprite(self, "images/Circle.png", image_scale=params.image_scale*mini_scale, angle_resolution=360)
        
        self.spawner_sprite = Sprite(self, "images/Spawner.png", angle_resolution=360)

        self.black_hole_sprite = Sprite(self, "images/BlackHole.png", angle_resolution=360)

        self.menu = build_menu(self)
        self.hud = Hud(self)

        self.lives = params.player_init_lives
        self.score = 0

        self.start_new_round()
        return
    
    def start_new_round(self):
        self.space = pymunk.Space()
        self.entity_set = EntitySet(self.space)
        self.border = Border(self)
        self.menu["main"].active_item_index = 0
        self.collision_handler = CollisionHandler(self)

        # initialize player
        start_position = Vec2d(self.screen_size[0]/2, self.screen_size[1]/2)
        self.player = Player(session=self, position=start_position, init_angle=-pi/2, sprite=self.player_sprite)
        self.set_state("play")

        # add black hole
        exclusion = (self.player.body.position, min(self.screen_size)*params.player_spawn_exclusion_fraction)
        position = utils.random_position(self.xlim, self.ylim, exclusion=exclusion)
        BlackHole(self, sprite=self.black_hole_sprite, position=position)

        # spawn enemies
        for i in range(50):
            self.spawn_enemy(Diamond, self.diamond_sprite)
        for i in range(3):
            self.spawn_spawners()

        return

    def start_new_game(self):
        self.lives = params.player_init_lives
        self.score = 0
        self.start_new_round()
        return
    
    def kill_player(self):
        if self.lives == 0:
            self.set_state("game_over")
        else:
            self.lives -= 1
            self.start_new_round()

    def set_state(self, state):
        self.state = state_map[state]

    def is_state(self, state):
        return self.state == state_map[state]
    
    def run(self):
        while True:
            self.event_list = pygame.event.get(pump=True)
            self.update()
    
    def update(self):
        self.update_state()
        self.clock.tick(self.framerate)
        self.screen.fill(self.background.rgb)
        self.draw_entities()
        self.border.draw()
        self.hud.draw()

        if self.is_state("play"):
            self.update_entities()
            
        elif self.is_state("pause"):
            self.screen.blit(self.dim_surface, dest=(0,0))
            self.menu["main"].draw()
            self.menu["main"].update()

        elif self.is_state("game_over"):
            self.screen.blit(self.dim_surface, dest=(0,0))
            self.menu["game_over"].draw()
            self.menu["game_over"].update()

        pygame.display.update()
        return

    def update_state(self):
        for event in self.event_list:
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.set_state("pause")
        return
    
    def spawn_enemy(self, enemy_class, enemy_sprite):
        exclusion = (self.player.body.position, min(self.screen_size)*params.player_spawn_exclusion_fraction)
        position = utils.random_position(self.xlim, self.ylim, exclusion=exclusion)
        enemy_class(self, position=position, init_angle=2*pi*random(), sprite=enemy_sprite)
    
    def spawn_spawners(self):
        exclusion = (self.player.body.position, min(self.screen_size)*params.player_spawn_exclusion_fraction)
        position = utils.random_position(self.xlim, self.ylim, exclusion=exclusion)
        mode = randint(1,2)
        if mode == 1:
            Spawner(
                self, position=position, sprite=self.spawner_sprite, 
                spawn_entity=Square, spawn_sprite=self.square_sprite,
                mini_sprite=self.mini_square_sprite, spawn_wait=60
            )
        elif mode == 2:
            Spawner(
                self, position=position, sprite=self.spawner_sprite, 
                spawn_entity=Diamond, spawn_sprite=self.diamond_sprite,
                mini_sprite=self.mini_diamond_sprite, spawn_wait=120
            )
        elif mode == 3:
            Spawner(
                self, position=position, sprite=self.spawner_sprite, 
                spawn_entity=Circle, spawn_sprite=self.circle_sprite,
                mini_sprite=self.mini_circle_sprite, spawn_wait=400
            )
        return

    def update_entities(self):
        for i in range(self.ticks_per_frame):
            self.space.step(1/(self.framerate*self.ticks_per_frame))
            for e in self.entity_set.list:
                e.update()
        return

    def draw_entities(self):
        for e in self.entity_set.list:
            e.draw()
        return

    def quit(self):
        pygame.quit()
        sys.exit()
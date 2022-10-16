from turtle import pos
from cv2 import transform
import pygame, pymunk
from pymunk.vec2d import Vec2d
from numpy import array, where, arctan2, pi, sin, cos, matmul, absolute
from itertools import product
from entity import Entity
import utils
import params
import sprites

class Player(Entity):
    def __init__(self, session, position, init_angle, sprite):
        # vertices = [
        #     (250,  25),
        #     (450, 425),
        #     (50,  425),
        # ]
        # transform = pymunk.Transform()
        # transform = transform.scaled(params.image_scale)
        # transform = transform.rotated(pi/2)
        # transform = transform.translated(-250,-250)
        # shape = pymunk.Poly(body=None, vertices=vertices, transform=transform)
        shape = pymunk.Circle(body=None, radius=100*params.image_scale)

        super().__init__(
            body_type=pymunk.Body.DYNAMIC, session=session, kind="player", 
            shape=shape, collision_category=params.cc_player, 
            collision_mask=pymunk.ShapeFilter.ALL_MASKS()^(params.cc_bullet|params.cc_player),
            sprite=sprite, position=position, init_angle=init_angle
        )
        self.direction = init_angle
        self.target_direction = init_angle
        self.shape.mass = 1.0
        self.shape.elasticity = 0.0
        self.speed = params.player_speed
        self.moving = False
        self.shooting = False
        self.shoot_cooldown = params.player_shoot_wait
        self.shoot_direction = 0
        self.keymap = self.generate_keymap()
        return

    def generate_keymap(self):
        a = array([[0,-1],[1,0],[0,1],[-1,0]])
        keymap = dict()
        for k in product([True,False], repeat=4):
            vx,vy = a[where(k)].sum(axis=0)
            direction = int(arctan2(vy,vx)/(pi/4)) % 8
            keymap[k] = direction
        return keymap

    def calculate_velocity(self, body, gravity, damping, dt):
        if self.moving:
            th = self.target_direction
            v = self.speed*Vec2d(cos(th), sin(th))  
        else:
            if body.velocity.get_length_sqrd() <= params.player_deceleration**2:
                v = Vec2d(0,0)
            else:
                th = body.velocity.angle
                v = body.velocity - params.player_deceleration*Vec2d(cos(th), sin(th)) 
        body.velocity = v
        super().calculate_velocity(body, gravity, damping, dt)
        return

    def get_position(self):
        return Vec2d(self.body.position.x, self.body.position.y)

    def get_shoot_direction(self):
        return self.shoot_direction

    def get_rotation_increment(self, current_direction, target_direction):
        diff = (target_direction - current_direction) % (2*pi)
        if diff > pi:
            diff -= 2*pi
        out = 0
        if diff != 0:
            if absolute(diff) <= params.player_rotation_speed:
                out = target_direction - current_direction
            elif diff > 0:
                out = params.player_rotation_speed
            else:
                out = -params.player_rotation_speed
        return out

    def update(self):
        super().update()
        pressed = pygame.key.get_pressed()
        wdsa = (pressed[pygame.K_w], pressed[pygame.K_d], pressed[pygame.K_s], pressed[pygame.K_a])
        urdl = (pressed[pygame.K_o], pressed[pygame.K_SEMICOLON], pressed[pygame.K_l], pressed[pygame.K_k])
        
        # direction updates
        if any(wdsa):
            self.moving = True
            self.target_direction = (pi/4)*self.keymap[wdsa]
        else:
            self.moving = False
        inc = self.get_rotation_increment(self.direction, self.target_direction)
        self.direction = (self.direction + inc) % (2*pi)
        self.body.angle = self.direction
        
        # shooting updates
        if any(urdl):
            self.shooting = True
            self.shoot_direction = (pi/4)*self.keymap[urdl]
        else:
            self.shooting = False
        if self.shooting:
            self.shoot_cooldown -= 1
            if self.shoot_cooldown == 0:
                new_bullet = Bullet(
                    session=self.session, position=self.body.position, 
                    init_angle=self.shoot_direction, sprite=self.session.bullet_sprite
                )
                self.shoot_cooldown = params.player_shoot_wait
        return

class Bullet(Entity):
    def __init__(self, session, position, init_angle, sprite):
        shape_radius = 18*params.image_scale
        shape = pymunk.Circle(None, radius=shape_radius)
        super().__init__(
            body_type=pymunk.Body.DYNAMIC, session=session, kind="bullet", 
            shape=shape, collision_category=params.cc_bullet, 
            collision_mask=pymunk.ShapeFilter.ALL_MASKS()^(params.cc_bullet|params.cc_player),
            sprite=sprite, position=position, init_angle=init_angle
        )
        self.shape.mass = 1.0
        self.speed = params.bullet_speed

        impulse = params.bullet_speed*self.shape.mass*Vec2d(cos(init_angle), sin(init_angle))
        self.body.apply_impulse_at_world_point(impulse, point=position)
        return

    # def calculate_velocity(self, body, gravity, damping, dt):
    #     th = self.body.angle
    #     v = self.speed*Vec2d(cos(th), sin(th))   
    #     body.velocity = v
    #     super().calculate_velocity(body, gravity, damping, dt)

    def draw(self):
        dest = self.body.position - self.sprite.sprite_size/2
        sprite_surface = self.sprite.get_surface(self.body.velocity.angle_degrees)
        self.session.screen.blit(sprite_surface, dest)
        return

        return
import pygame, pymunk
from pymunk.vec2d import Vec2d
from numpy import absolute, array, pi, sin, cos, clip, sign
from random import random, randint
from entity import Entity
from sprites import Sprite
import utils
import params
from color import white

class Square(Entity):
    value = 1
    def __init__(self, session, position, init_angle, sprite):
        square_len = 350
        vertices = [
            ( square_len/2, square_len/2),
            ( square_len/2,-square_len/2),
            (-square_len/2,-square_len/2),
            (-square_len/2, square_len/2),
        ]
        transform = pymunk.Transform(
            a=params.image_scale, 
            d=params.image_scale, 
        )
        shape = pymunk.Poly(body=None, vertices=vertices, transform=transform)
        super().__init__(
            body_type=pymunk.Body.DYNAMIC, session=session, kind="square", 
            shape=shape, collision_category=params.cc_enemy, 
            collision_mask=pymunk.ShapeFilter.ALL_CATEGORIES(),
            sprite=sprite, position=position, init_angle=init_angle
        )
        self.shape.mass = 1.0
        impulse = utils.random_vec(magnitude=params.square_speed*self.shape.mass)
        self.body.apply_impulse_at_local_point(impulse)
        self.shape.elasticity = 0.99

class Diamond(Entity):
    value = 2
    def __init__(self, session, position, init_angle, sprite):
        vertices = [
            (250, 25),
            (425, 250),
            (250, 475),
            (75, 250)
        ]
        transform = pymunk.Transform()
        transform = transform.scaled(params.image_scale)
        transform = transform.rotated(pi/2)
        transform = transform.translated(-250,-250)
        shape = pymunk.Poly(body=None, vertices=vertices, transform=transform)
        super().__init__(
            body_type=pymunk.Body.DYNAMIC, session=session, kind="diamond", 
            shape=shape, collision_category=params.cc_enemy, 
            collision_mask=pymunk.ShapeFilter.ALL_CATEGORIES(),
            sprite=sprite, position=position, init_angle=init_angle
        )
       
        self.shape.mass = 1.0
        impulse = utils.random_vec(magnitude=params.diamond_speed*self.shape.mass)
        self.body.apply_impulse_at_local_point(impulse)
        self.shape.elasticity = 0.0
        self.dodge = False
        self.dodge_angle = 0
        self.was_dodging = False

    def update(self):
        # dodge logic
        self.was_dodging = self.dodge
        if self.session.player.shooting:
            shoot_direction = self.session.player.shoot_direction
            shoot_v = Vec2d(cos(shoot_direction), sin(shoot_direction))
            player_v = self.body.position - self.session.player.body.position
            ps_angle = shoot_v.get_angle_between(player_v)
            if absolute(ps_angle) <= pi/2:
                self.dodge = True
                self.dodge_angle = shoot_v.angle + sign(ps_angle)*pi/2
            else:
                self.dodge = False
        else:
            self.dodge = False
        super().update()
        return

    def calculate_velocity(self, body, gravity, damping, dt):
        if self.dodge:
            target_velocity = params.diamond_speed*Vec2d(cos(self.dodge_angle), sin(self.dodge_angle))
            self.change_velocity(body, gravity, damping, dt, target_velocity, params.diamond_acceleration)
        elif self.was_dodging:
            body.velocity = utils.random_vec(magnitude=params.diamond_speed)
        super().calculate_velocity(body, gravity, damping, dt)
        return

class Circle(Entity):
    value = 5
    def __init__(self, session, position, init_angle, sprite):
        shape = pymunk.Circle(body=None, radius=params.image_scale*250/2)
        super().__init__(
            body_type=pymunk.Body.DYNAMIC, session=session, kind="circle", 
            shape=shape, collision_category=params.cc_enemy, 
            collision_mask=pymunk.ShapeFilter.ALL_CATEGORIES(),
            sprite=sprite, position=position, init_angle=init_angle
        )
       
        self.shape.mass = 0.5
        self.shape.elasticity = 0.0
        return

    def calculate_velocity(self, body, gravity, damping, dt):
        player_v = self.session.player.body.position - self.body.position
        target_velocity = (params.circle_speed/player_v.length)*player_v
        self.change_velocity(body, gravity, damping, dt, target_velocity, params.circle_acceleration)
        super().calculate_velocity(body, gravity, damping, dt)
        return

class Spawner(Entity):
    def __init__(self, session, position, sprite, spawn_entity, spawn_sprite, mini_sprite, spawn_wait):
        square_len = 300*params.image_scale
        square_vertices = [
            ( square_len/2, square_len/2),
            ( square_len/2,-square_len/2),
            (-square_len/2,-square_len/2),
            (-square_len/2, square_len/2),
        ]
        shape = pymunk.Poly(body=None, vertices=square_vertices)
        super().__init__(
            body_type=pymunk.Body.STATIC, session=session, kind="spawner", 
            shape=shape, collision_category=params.cc_spawner, 
            collision_mask=pymunk.ShapeFilter.ALL_CATEGORIES(),
            sprite=sprite, position=position, init_angle=0
        )
        self.spawn_entity = spawn_entity
        self.spawn_sprite = spawn_sprite
        self.mini_sprite = mini_sprite
        self.mini_angle = 0
        self.spawn_displacement = 0.02*min(session.screen_size)
        self.spawn_wait = spawn_wait
        self.spawn_cooldown = self.spawn_wait
        self.health = 10
        self.value = 5*self.spawn_entity.value

    def update(self):
        self.spawn_cooldown -= 1
        if self.spawn_cooldown == 0:
            self.spawn_cooldown = self.spawn_wait
            self.spawn()
        if self.health == 0:
            self.remove = True
            self.session.score += self.value
        self.mini_angle += params.mini_rotation_speed
        super().update()
        return

    def draw(self):
        dest = self.body.position - self.mini_sprite.sprite_size/2
        angle_degree = self.mini_angle*(180/pi)
        sprite_surface = self.mini_sprite.get_surface(angle_degree)
        self.session.screen.blit(sprite_surface, dest)
        super().draw()
        return

    def spawn(self):
        position = self.body.position + utils.random_vec(magnitude=self.spawn_displacement)
        px = clip(position.x, 0, self.session.screen_size[0])
        py = clip(position.y, 0, self.session.screen_size[1])
        position = Vec2d(px, py)
        init_angle = 2*pi*random()
        self.spawn_entity(session=self.session, position=position, init_angle=init_angle, sprite=self.spawn_sprite)

    def hurt(self):
        self.health -= 1
        return

class BlackHole(Entity):
    def __init__(self, session, sprite, position):
        radius = 5#params.image_scale*(350/2)
        shape = pymunk.Circle(body=None, radius=radius)
        super().__init__(
            body_type=pymunk.Body.DYNAMIC, session=session, kind="black_hole", 
            shape=shape, collision_category=params.cc_bh, 
            collision_mask=pymunk.ShapeFilter.ALL_CATEGORIES(),
            sprite=sprite, position=position, init_angle=0
        )
        self.value = 10
        self.shape.mass = 0.5
        self.shape.elasticity = 0.99
        self.max_dist_sqrd = params.g_max_dist_fraction**2 * min(self.session.screen_size)**2
        self.g_mass = 1.0

    def calculate_velocity(self, body, gravity, damping, dt):
        damping = 0.95
        super().calculate_velocity(body, gravity, damping, dt)
        return
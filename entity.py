from turtle import screensize
import params
import pymunk
import pygame
from collections import defaultdict, Counter
from numpy import pi, sqrt

class Entity():
    def __init__(self, body_type, session, kind, shape, collision_category, collision_mask, sprite, position, init_angle):
        self.session = session
        self.body_type = body_type
        self.body = pymunk.Body(body_type=self.body_type)
        self.kind = kind
        self.id = self.session.entity_set.generate_id(self.kind)
        self.shape = shape
        self.shape.body = self.body
        self.sprite = sprite
        self.body.position = position
        self.body.angle = init_angle
        
        self.session.entity_set.add(self)
        self.session.space.add(self.body, self.shape)

        self.shape.collision_type = collision_category
        self.shape.filter = pymunk.ShapeFilter(categories=collision_category, mask=collision_mask)
        self.body.velocity_func = self.calculate_velocity
        self.remove = False
        return

    def update(self):
        # out of bounds check
        if self.kind != "player":
            position = self.body.position
            if position.x < params.wall_offset or position.x > self.session.screen_size[0] - params.wall_offset:
                self.remove = True
            if position.y < params.wall_offset or position.y > self.session.screen_size[1] - params.wall_offset:
                self.remove = True
        
        if self.remove:
            self.delete()
        return
    
    def draw(self):
        # shape_color = (255,0,0)
        # if isinstance(self.shape, pymunk.Poly):
        #     points = []
        #     for v in self.shape.get_vertices():
        #         points.append(v.rotated(self.body.angle) + self.body.position)
        #     pygame.draw.polygon(self.session.screen, color=shape_color, points=points)
        # elif isinstance(self.shape, pymunk.Circle):
        #     pygame.draw.circle(self.session.screen, color=shape_color, center=self.body.position, radius=self.shape.radius)
        
        dest = self.body.position - self.sprite.sprite_size/2
        angle_degree = self.body.angle*(180/pi)
        sprite_surface = self.sprite.get_surface(angle_degree)
        self.session.screen.blit(sprite_surface, dest)
        return

    def delete(self):
        self.session.entity_set.delete(self)
        return

    def calculate_velocity(self, body, gravity, damping, dt):
        g = pymunk.Vec2d(0,0)
        for bh in self.session.entity_set.black_hole_list:
            if body != bh.body:
                r = bh.body.position - body.position
                d2 = r.get_length_sqrd()
                if d2 < bh.max_dist_sqrd:
                    g += params.g_constant * bh.g_mass * r / d2
        body.update_velocity(body, g, damping, dt)
        return

    def change_velocity(self, body, gravity, damping, dt, target_velocity, acceleration):
        a = target_velocity - body.velocity
        alen = a.length
        if alen > 0:
            a = (acceleration/alen)*a
            body.update_velocity(body, a, damping, dt)
        return
    
class EntitySet():
    def __init__(self, space):
        self.list = []
        self.space = space
        self.shape_to_entity = defaultdict(None)
        self.id_counter = 0
        self.counter = Counter()
        self.black_hole_list = []
        return

    def add(self, e):
        self.list.append(e)
        self.counter[e.kind]+=1
        if hasattr(e, "shape"):
            self.shape_to_entity[e.shape] = e
        if e.kind == "black_hole":
            self.black_hole_list.append(e)
        return

    def contains(self, e):
        return e in self.list
    
    def delete(self, e):
        if self.contains(e):
            self.list.remove(e)
            self.counter[e.kind] -= 1
            if hasattr(e, "shape"):
                self.space.remove(e.shape)
            if hasattr(e, "body"):
                self.space.remove(e.body)
            if e.kind == "black_hole":
                self.black_hole_list.remove(e)
        return
            
    def generate_id(self, tag):
        self.id_counter += 1
        return tag+"{}".format(self.id_counter)
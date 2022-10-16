import pygame, pymunk
import params
from entity import Entity
from pymunk.vec2d import Vec2d

class Wall(Entity):
    def __init__(self, session, a, b, width):
        self.a = a
        self.b = b
        self.width = width
        self.session = session
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.shape = pymunk.Segment(body=self.body, a=self.a, b=self.b, radius=self.width) 
        self.session.space.add(self.body, self.shape)
        self.shape.collision_type = params.cc_wall
        self.shape.filter = pymunk.ShapeFilter(categories=params.cc_wall, mask=pymunk.ShapeFilter.ALL_MASKS())
        self.shape.elasticity = 0.99
        return

class Border():
    def __init__(self, session):
        self.session = session
        # coordinates for centers of wall endpoints
        self.tl = Vec2d(-params.wall_width/2 + params.wall_offset, -params.wall_width/2 + params.wall_offset)
        self.tr = Vec2d(self.session.screen_size[0] + params.wall_width/2 - params.wall_offset, -params.wall_width/2 + params.wall_offset)
        self.bl = Vec2d(-params.wall_width/2 + params.wall_offset, self.session.screen_size[1] + params.wall_width/2 - params.wall_offset)
        self.br = Vec2d(self.session.screen_size[0] + params.wall_width/2 - params.wall_offset, self.session.screen_size[1] + params.wall_width/2 - params.wall_offset)
        
        self.wall_list = [
            Wall(self.session, a=self.tl, b=self.tr, width=params.wall_width),
            Wall(self.session, a=self.tr, b=self.br, width=params.wall_width),
            Wall(self.session, a=self.br, b=self.bl, width=params.wall_width),
            Wall(self.session, a=self.bl, b=self.tl, width=params.wall_width),
        ]
        self.border_color = params.wall_line_color.rgb
        return

    def draw(self):
        # draw opaque rectangles outside walls
        rect_list = [
             pygame.Rect(0, 0, params.wall_offset, self.session.screen_size[0]), # left
            pygame.Rect(0, 0, self.session.screen_size[0], params.wall_offset), # top
            pygame.Rect(self.session.screen_size[0]-params.wall_offset, 0, params.wall_offset, self.session.screen_size[0]), # right
            pygame.Rect(0, self.session.screen_size[1]-params.wall_offset, self.session.screen_size[0], params.wall_offset), # bottom
        ]
        for rect in rect_list:
            pygame.draw.rect(surface=self.session.screen, color=self.session.background.rgb, rect=rect)
        
        # draw lines
        points = [
            self.tl + Vec2d( params.wall_width/2,  params.wall_width/2),
            self.bl + Vec2d( params.wall_width/2, -params.wall_width/2),
            self.br + Vec2d(-params.wall_width/2, -params.wall_width/2),
            self.tr + Vec2d(-params.wall_width/2,  params.wall_width/2),
        ]
        pygame.draw.lines(surface=self.session.screen, color=self.border_color, closed=True, points=points, width=params.wall_line_width)

        # draw corners
        for p in points:
            l = p.x - params.wall_line_width/2 + 1
            t = p.y - params.wall_line_width/2 + 1
            h = params.wall_line_width
            w = params.wall_line_width
            pygame.draw.rect(surface=self.session.screen, color=self.border_color, rect=pygame.Rect(l,t,w,h))

        return


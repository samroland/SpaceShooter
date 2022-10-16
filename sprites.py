import pygame
from numpy import array
import params

class Sprite:
    def __init__(self, session, image_file, angle_resolution=params.sprite_angle_resolution, image_scale=params.image_scale):
        self.session = session
        self.image = pygame.image.load(image_file).convert_alpha()
        self.image_size = array(self.image.get_size())
        self.image_scale = image_scale
        self.sprite_size = self.image_scale*self.image_size
        self.angle_resolution = angle_resolution
        self.sprite_map = self.generate_sprite_map()
        return

    def rotate_scale_image(self, angle, scale, image):
        # the angle here is in the left handed coordinate system of the game
        # angle=0 is left, angle=90 is down
        # the rotate function uses the opposite orientation
        # also need to account for the starting angle of the image
        rot_image = pygame.transform.rotate(image, -angle-90)
        rot_size = array(rot_image.get_size())
        crop_pos = (rot_size-self.image_size)/2
        crop_area = pygame.Rect(*crop_pos, *self.image_size)
        crop_image = pygame.Surface(self.image_size, flags=pygame.SRCALPHA)
        crop_image.blit(rot_image, (0,0), area=crop_area)
        scale_image = pygame.transform.smoothscale(crop_image, scale*self.image_size)
        return scale_image

    def generate_sprite_map(self):
        sprite_map = dict()
        for angle in range(0, 360, self.angle_resolution):
            sprite_map[angle] = self.rotate_scale_image(angle, self.image_scale, self.image)
        return sprite_map

    def get_surface(self, angle):
        angle_key = ((angle//self.angle_resolution)*self.angle_resolution) % 360
        return self.sprite_map[angle_key]
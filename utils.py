from turtle import Vec2D
import pygame
from numpy import array, pi, sin, cos
import params
from pymunk.vec2d import Vec2d
from random import random, randint
from numpy import absolute



def random_position(xlim, ylim, exclusion = None):
    """exclusion = (position, radius)
    """
    x = (xlim[1]-xlim[0])*random() + xlim[0]
    
    ymin, ymax = ylim
    if exclusion:  # modify ymin, ymax
        ex_position, ex_radius = exclusion
        if absolute(x-ex_position.x) <= ex_radius:
            # first decide if y will be above or below
            if ex_position.y - ex_radius <= ymin:
                above = 0 # below
            elif ex_position.y + ex_radius >= ymax:
                above = 1 # above
            else:
                above = randint(0,1)
            # set ybounds
            if above:
                ymax = ex_position.y - ex_radius
            else:
                ymin = ex_position.y + ex_radius
        
    y = (ymax-ymin)*random() + ymin
    return Vec2d(x,y)



def random_vec(magnitude=1.0):
    th = 2*pi*random()
    return magnitude*Vec2d(cos(th), sin(th))

def rot_mtx(th):
    return array([[cos(th), sin(th)],[-sin(th), cos(th)]])

    
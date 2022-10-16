import color

# images
image_scale = 0.08
sprite_angle_resolution = 1

# screen
framerate = 120
ticks_per_frame = 1

# player
player_speed = 300.0
player_deceleration = 50.0
player_rotation_speed = 0.2
player_shoot_wait = 10 # int
player_border_color = color.white
player_border_thickness = 2
player_spawn_exclusion_fraction = 0.2 # fraction of screen size
player_init_lives = 2

# bullet
bullet_speed = 600.0

# enemy
square_speed = 50.0
diamond_speed = 75.0
diamond_acceleration = 300.0
circle_speed = player_speed*0.75
circle_acceleration = 500.0

# black hole
g_constant = 1e4
g_max_dist_fraction = 0.5 # fraction of screen size

# spawner
mini_rotation_speed = 0.01

# wall
wall_width = 10 # thickness of wall shape
wall_offset = 50
wall_line_width = 2
wall_line_color = color.Color(0.0, 0.0, 0.5)

# HUD
hud_offset = 5

# menu
menu_font_height = 50

# collision categories
cc_player   = 0b000001
cc_bullet   = 0b000010
cc_enemy    = 0b000100
cc_wall     = 0b001000
cc_spawner  = 0b010000
cc_bh       = 0b100000
import pygame
pygame.init()
out_file = "text.png"
cursor_x = 0
cursor_y = 0
total_width = 0
font_list = pygame.font.get_fonts()
font_data = [] # list of (font_surface, dest)
for font_name in font_list:
    try:
        dest = (cursor_x, cursor_y)
        font_file = pygame.font.match_font(font_name)
        font = pygame.font.Font(font_file, 36)
        text = font_name + ": the quick brown fox jumped over the lazy dog"
        font_surface = pygame.font.Font.render(font, text, True, (255,255,255))
        text_size = font.size(text)
        font_data.append((font_surface, dest))
        cursor_y += text_size[1]
        total_width = max(total_width, text_size[0])
    except Exception as e:
        continue
surface = pygame.Surface((total_width, cursor_y))
surface.fill((0,0,0))
for font_surface,dest in font_data:
    surface.blit(font_surface, dest)
pygame.image.save(surface, out_file)
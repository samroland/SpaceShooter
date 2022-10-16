import pygame, os
pygame.init()
font_dir = "AltMono"
font_files = os.listdir(font_dir)
out_file = f"{font_dir}_Sample.png"
cursor_x = 0
cursor_y = 0
total_width = 0
font_data = [] # list of (font_surface, dest)
text_list = ["The quick brown fox jumped over the lazy dog", "0123456789", "1234567890"]
for font_file in font_files:
    file_path = os.path.join(font_dir,font_file)
    print(file_path)
    font = pygame.font.Font(file_path, 36)
    for text in text_list:
    # text = "The quick brown fox jumped over the lazy dog. " + font_file
        font_surface = pygame.font.Font.render(font, text, True, (255,255,255))
        text_size = font.size(text)
        dest = (cursor_x, cursor_y)
        font_data.append((font_surface, dest))
        cursor_y += text_size[1]
        total_width = max(total_width, text_size[0])
    
surface = pygame.Surface((total_width, cursor_y))
surface.fill((0,0,0))
for font_surface,dest in font_data:
    surface.blit(font_surface, dest)
pygame.image.save(surface, out_file)
print(out_file)
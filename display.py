from collections import defaultdict
import color
import pygame
from pygame.font import Font
import params

class Writer():
    def __init__(self, font_height):
        self.file_list = [
            "fonts/Sono/Sono-ExtraLight.ttf", 
            "fonts/Sono/Sono-Light.ttf", 
            "fonts/Sono/Sono-Medium.ttf",
        ]
        
        self.font_list = [Font(file, 100) for file in self.file_list]
        self.rgb = color.white.rgb

        # calculate correct width for characters
        test_surface = self.font_list[0].render("1", True, self.rgb)
        test_size = test_surface.get_size()
        self.font_height = font_height
        self.font_width = self.font_height*test_size[0]/test_size[1]

        letter_list = "qwertyuiopasdfghjklzxcvbnm"
        char_list = "1234567890.:!?- "
        char_list += letter_list + letter_list.upper()
        self.char_map = defaultdict(list)
        for font in self.font_list:
            for char in char_list:
                char_surface = font.render(char, True, self.rgb)
                char_surface = pygame.transform.smoothscale(char_surface, (self.font_width, self.font_height))
                self.char_map[char].append(char_surface)
        return

    def write(self, text, surface, dest, boldness=0):
        cursor_x, cursor_y = dest
        for char in text:
            try:
                surface.blit(self.char_map[char][boldness], (cursor_x, cursor_y))
            except Exception as e:
                print(char)
            cursor_x += self.font_width
        return cursor_x, cursor_y

class Menu():
    def __init__(self, session, title = None):
        self.session = session
        self.title = title
        self.writer = Writer(params.menu_font_height)
        self.size = 0
        
        if self.title:
            self.title_height = 1.2*self.writer.font_height
            self.height = self.title_height
            self.width = self.writer.font_width*len(title)
        else:
            self.height = 0
            self.width = 0

        
        self.text_list = []
        self.action_list = []
        self.surface = None
        self.active_item_index = 0
        
        return

    def add_item(self, text, action):
        self.size += 1
        self.text_list.append(text)
        self.action_list.append(action)
        self.height += self.writer.font_height
        self.width = max(self.width, self.writer.font_width*len(text))
        self.surface = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA)
        return

    def do_action(self, index):
        self.action_list[index]()
        return
    
    def update(self):
        for event in self.session.event_list:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.active_item_index = (self.active_item_index - 1) % self.size
                elif event.key == pygame.K_DOWN:
                    self.active_item_index = (self.active_item_index + 1) % self.size
                elif event.key == pygame.K_RETURN:
                    self.do_action(self.active_item_index)
        return

    def draw(self):
        self.surface.fill((0,0,0,0))
        cursor_x = 0
        cursor_y = 0
        if self.title:
            self.writer.write(self.title, self.surface, (cursor_x, cursor_y), boldness=2)
            start_pos = (0, 0.9*self.writer.font_height)
            end_pos = (self.writer.font_width*len(self.title), 0.9*self.writer.font_height)
            width = params.wall_line_width
            pygame.draw.line(self.surface, self.writer.rgb, start_pos=start_pos, end_pos=end_pos, width=width)
            cursor_y += self.title_height
        for i,text in enumerate(self.text_list):
            boldness = 2 if i == self.active_item_index else 0
            self.writer.write(text, self.surface, (cursor_x, cursor_y), boldness=boldness)
            cursor_y += self.writer.font_height
        menu_x = (self.session.screen_size[0] - self.width) / 2
        menu_y = (self.session.screen_size[1] - self.height) / 2
        self.session.screen.blit(self.surface, (menu_x, menu_y))
        return

def build_menu(session):

    menu_map = dict()
    
    def restart_action():
        session.start_new_game()
        return
    def continue_action():
        session.set_state("play")
        return
    def quit_action():
        session.quit()
        return

    menu_map["main"] = Menu(session)
    menu_map["main"].add_item("Continue", continue_action)
    menu_map["main"].add_item("Restart", restart_action)
    menu_map["main"].add_item("Quit", quit_action)

    menu_map["game_over"] = Menu(session, title="Game Over")
    menu_map["game_over"].add_item("Restart", restart_action)
    menu_map["game_over"].add_item("Quit", quit_action)

   # menu_map["options"] = Menu(session)

    return menu_map


class Hud():
    def __init__(self, session):
        self.session = session
        self.offset = params.hud_offset
        self.height = params.wall_offset - 2*self.offset
        self.width = self.session.screen_size[0] - 2*self.offset
        self.surface = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA)
        
        self.icon_width = self.height
        self.player_icon = self.session.player_sprite.get_surface(270)
        self.player_icon = pygame.transform.smoothscale(self.player_icon, (self.icon_width, self.icon_width))
        
        self.writer = Writer(self.height)
        return

    def draw(self):
        self.surface.fill((0,0,0,0))
        cursor_x = 0
        cursor_y = 0

        score_string = f"Score:{self.session.score}"
        cursor_x, cursor_y = self.writer.write(score_string, self.surface, (cursor_x, cursor_y), boldness=1)

        lives_string = str(self.session.lives)
        cursor_x = (self.width - self.icon_width - self.writer.font_width*len(lives_string))/2
        self.surface.blit(self.player_icon, (cursor_x, cursor_y))
        cursor_x += self.height
        self.writer.write(lives_string, self.surface, (cursor_x, cursor_y), boldness=1)

        fps_string = f"{int(self.session.clock.get_fps()):03d} FPS"
        cursor_x = self.width - self.writer.font_width*len(fps_string)
        self.writer.write(fps_string, self.surface, (cursor_x, cursor_y), boldness=1)
        
        self.session.screen.blit(self.surface, (self.offset, self.offset))

        return

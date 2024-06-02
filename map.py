import os
import warnings
import pygame
import subprocess
import sys

# 환경 변수 설정
os.environ['PYTHONWARNINGS'] = "ignore"

# 로깅 레벨 설정
import logging
logging.basicConfig(level=logging.CRITICAL)

# Builder 클래스 정의
class GameBuilder:
    def __init__(self):
        self._game = GameFacade()

    def set_screen(self, width, height):
        self._game.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Tile Game")
        return self

    def set_clock(self):
        self._game.clock = pygame.time.Clock()
        return self

    def set_images(self, map_image_path, character_image_path):
        self._game.image = self._game._load_image(map_image_path, (640, 640))
        self._game.character = self._game._load_image(character_image_path, (100, 100))
        return self

    def set_initial_position(self, x, y):
        self._game.character_x_pos = x
        self._game.character_y_pos = y
        return self

    def set_speed(self, speed):
        self._game.character_speed = speed
        return self

    def reset_success_status(self):
        self._game.reset_success_status()
        return self

    def build(self):
        self._game.running = True
        return self._game

# Facade 클래스 정의
class GameFacade:
    def __init__(self):
        self._initialize_pygame()
        self.screen = None
        self.clock = None
        self.image = None
        self.character = None
        self.character_x_pos = 0
        self.character_y_pos = 300
        self.to_x = 0
        self.to_y = 0
        self.character_speed = 0.6
        self.reset_success_status()
        self.running = True

    def _initialize_pygame(self):
        pygame.init()

    def _load_image(self, path, size):
        image = pygame.image.load(path)
        return pygame.transform.scale(image, size)

    def reset_success_status(self):
        for i in range(1, 4):
            with open(f'success_status_{i}.txt', 'w') as file:
                file.write('')

    def check_success(self, map_number):
        try:
            with open(f'success_status_{map_number}.txt', 'r') as file:
                status = file.read().strip()
                return status == 'success'
        except FileNotFoundError:
            return False

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            self._handle_keydown(event.key)
        elif event.type == pygame.KEYUP:
            self._handle_keyup(event.key)

    def _handle_keydown(self, key):
        if key == pygame.K_LEFT:
            self.to_x -= self.character_speed
        elif key == pygame.K_RIGHT:
            self.to_x += self.character_speed
        elif key == pygame.K_UP:
            self.to_y -= self.character_speed
        elif key == pygame.K_DOWN:
            self.to_y += self.character_speed
        elif key == pygame.K_RETURN:
            self._handle_return_key()

    def _handle_keyup(self, key):
        if key in [pygame.K_LEFT, pygame.K_RIGHT]:
            self.to_x = 0
        elif key in [pygame.K_UP, pygame.K_DOWN]:
            self.to_y = 0

    def _handle_return_key(self):
        if 200 <= self.character_x_pos <= 436 and 82 <= self.character_y_pos <= 308:
            self._run_map_script('map1.py')
        elif 10 <= self.character_x_pos <= 266 and 316 <= self.character_y_pos <= 606:
            if self.check_success(1):
                self._run_map_script('map2.py')
            else:
                print("Complete map1 first!")
        elif 344 <= self.character_x_pos <= 634 and 324 <= self.character_y_pos <= 628:
            if self.check_success(1) and self.check_success(2):
                self._run_map_script('map3.py')
            else:
                print("Complete map2 first!")

    def _run_map_script(self, script_name):
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NEW_CONSOLE
        else:
            creationflags = 0
        subprocess.Popen(['python', script_name], creationflags=creationflags)

    def update_character_position(self, dt):
        self.character_x_pos += self.to_x * dt
        self.character_y_pos += self.to_y * dt
        self.character_x_pos = max(0, min(self.character_x_pos, 640 - self.character.get_rect().width))
        self.character_y_pos = max(0, min(self.character_y_pos, 640 - self.character.get_rect().height))

    def draw(self):
        self.screen.blit(self.image, (0, 0))
        self.screen.blit(self.character, (self.character_x_pos, self.character_y_pos))
        pygame.display.update()

    def run(self):
        while self.running:
            dt = self.clock.tick(30)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update_character_position(dt)
            self.draw()
        pygame.quit()
        sys.exit()

# Chain 패턴을 위한 이벤트 핸들러 정의
class EventHandler:
    def __init__(self, next_handler=None):
        self._next_handler = next_handler

    def handle(self, event, game):
        if self._next_handler:
            self._next_handler.handle(event, game)

class QuitEventHandler(EventHandler):
    def handle(self, event, game):
        if event.type == pygame.QUIT:
            game.running = False
        else:
            super().handle(event, game)

class KeyDownEventHandler(EventHandler):
    def handle(self, event, game):
        if event.type == pygame.KEYDOWN:
            game._handle_keydown(event.key)
        else:
            super().handle(event, game)

class KeyUpEventHandler(EventHandler):
    def handle(self, event, game):
        if event.type == pygame.KEYUP:
            game._handle_keyup(event.key)
        else:
            super().handle(event, game)

if __name__ == "__main__":
    builder = (GameBuilder()
               .set_screen(640, 640)
               .set_clock()
               .set_images("image/mapworld.png", "image/berry.png")
               .set_initial_position(0, 300)
               .set_speed(0.6)
               .reset_success_status())
    
    game = builder.build()

    quit_handler = QuitEventHandler()
    keydown_handler = KeyDownEventHandler(quit_handler)
    keyup_handler = KeyUpEventHandler(keydown_handler)
    
    while game.running:
        dt = game.clock.tick(30)
        for event in pygame.event.get():
            keyup_handler.handle(event, game)
        game.update_character_position(dt)
        game.draw()
    
    pygame.quit()
    sys.exit()

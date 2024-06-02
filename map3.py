import os
import pygame
import random
import sys

# 환경 변수 설정
os.environ['PYTHONWARNINGS'] = "ignore"

# 로깅 레벨 설정
import logging
logging.basicConfig(level=logging.CRITICAL)

class GameObjectFactory:
    @staticmethod
    def create_object(obj_type, screen_width, screen_height):
        if obj_type == "tile":
            return GameObject("image/tiles.png", 10, screen_width, screen_height)
        elif obj_type == "bomb":
            return GameObject("image/bombs.png", 8, screen_width, screen_height)
        elif obj_type == "cake":
            return GameObject("image/cake.png", 12, screen_width, screen_height)
        elif obj_type == "character":
            return GameObject("image/berry.png", 0, screen_width, screen_height, screen_width // 2, screen_height - 100)
        elif obj_type == "background":
            return GameObject("image/Butterflies-2-2-2-2.jpg", 0, screen_width, screen_height)
        else:
            raise ValueError(f"Unknown object type: {obj_type}")

class GameObject:
    def __init__(self, image_path, speed, screen_width, screen_height, x_pos=None, y_pos=None):
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.speed = speed
        self.screen_width = screen_width
        self.screen_height = screen_height
        if x_pos is None:
            self.rect.x = random.randint(0, screen_width - self.rect.width)
        else:
            self.rect.x = x_pos
        if y_pos is None:
            self.rect.y = 0
        else:
            self.rect.y = y_pos

    def update_position(self):
        self.rect.y += self.speed
        if self.rect.y > self.screen_height:
            self.rect.y = 0
            self.rect.x = random.randint(0, self.screen_width - self.rect.width)

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

class GameFacade:
    def __init__(self):
        self._initialize_pygame()
        self.screen = self._setup_screen()
        self.clock = pygame.time.Clock()
        self.background = GameObjectFactory.create_object("background", 480, 640)
        self.character = GameObjectFactory.create_object("character", 480, 640)
        self.tile = GameObjectFactory.create_object("tile", 480, 640)
        self.bomb = GameObjectFactory.create_object("bomb", 480, 640)
        self.cake = GameObjectFactory.create_object("cake", 480, 640)
        self.character_speed = 15
        self.to_x = 0
        self.score = 0
        self.quiz_mode = False
        self.quiz_question = ""
        self.quiz_answer = ""
        self.quizzes = [
            ("SOLID pattern을 잘 지켜야한다", "O"),
            ("o", "O"),
            ("x", "X"),
            ("o", "O"),
            ("x", "X"),
            ("o", "O"),
            ("o", "O"),
            ("o", "O"),
            ("o", "O"),
            ("x", "X")
        ]
        self.quiz_index = 0
        self.quiz_answered = []
        self.running = True
        self.game_over = False
        self.game_success = False
        self.font_path = "image/AppleSDGothicNeo.ttc"
        self.game_font = pygame.font.Font(self.font_path, 40)

    def _initialize_pygame(self):
        pygame.init()

    def _setup_screen(self):
        screen = pygame.display.set_mode((480, 640))
        pygame.display.set_caption("QuizBeatTiles")
        return screen

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

    def _handle_keyup(self, key):
        if key in [pygame.K_LEFT, pygame.K_RIGHT]:
            self.to_x = 0

    def update_character_position(self):
        self.character.rect.x += self.to_x
        if self.character.rect.x < 0:
            self.character.rect.x = 0
        elif self.character.rect.x > self.screen.get_width() - self.character.rect.width:
            self.character.rect.x = self.screen.get_width() - self.character.rect.width

    def update_objects(self):
        self.tile.update_position()
        self.bomb.update_position()
        self.cake.update_position()

    def check_collisions(self):
        if self.character.rect.colliderect(self.tile.rect):
            self.score += 10
            self.tile.rect.y = 0
            self.tile.rect.x = random.randint(0, self.screen.get_width() - self.tile.rect.width)

        if self.character.rect.colliderect(self.cake.rect):
            self.score += 15
            self.cake.rect.y = 0
            self.cake.rect.x = random.randint(0, self.screen.get_width() - self.cake.rect.width)

        if self.character.rect.colliderect(self.bomb.rect):
            self.game_over = True

    def render_text_centered(self, text, font, surface, color, pos):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=pos)
        surface.blit(text_surface, text_rect)

    def draw(self):
        self.background.draw(self.screen)
        self.character.draw(self.screen)
        self.tile.draw(self.screen)
        self.bomb.draw(self.screen)
        self.cake.draw(self.screen)

        score_text = self.game_font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (self.screen.get_width() / 2 - score_text.get_width() / 2, 10))

        pygame.display.update()

    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if self.quiz_mode:
                    self.handle_quiz_event(event)
                else:
                    self.handle_event(event)

            if not self.game_over and not self.game_success:
                if not self.quiz_mode:
                    self.update_character_position()
                    self.update_objects()
                    self.check_collisions()

                    if self.score >= 500 and len(self.quiz_answered) < len(self.quizzes):
                        self.quiz_mode = True
                        self.quiz_question, self.quiz_answer = self.quizzes[self.quiz_index]
                        self.quiz_index += 1

                    self.draw()
                else:
                    self.draw_quiz()

            elif self.game_success:
                self.show_success_screen()
            else:
                self.show_game_over_screen()

        pygame.quit()
        sys.exit()

    def handle_quiz_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_o:
                if self.quiz_answer == "O":
                    self.score += 500
                self.quiz_mode = False
                self.quiz_answered.append(self.quiz_question)
            elif event.key == pygame.K_x:
                if self.quiz_answer == "X":
                    self.score += 500
                self.quiz_mode = False
                self.quiz_answered.append(self.quiz_question)

        if self.score >= 5000:
            self.game_success = True
        elif len(self.quiz_answered) == len(self.quizzes) and self.score < 5000:
            self.game_over = True

    def draw_quiz(self):
        font_size = 40
        quiz_font = pygame.font.Font(self.font_path, font_size)
        quiz_text = quiz_font.render(self.quiz_question, True, (255, 255, 255))
        while quiz_text.get_width() > self.screen.get_width() - 20:
            font_size -= 2
            quiz_font = pygame.font.Font(self.font_path, font_size)
            quiz_text = quiz_font.render(self.quiz_question, True, (255, 255, 255))

        self.background.draw(self.screen)
        self.render_text_centered(self.quiz_question, quiz_font, self.screen, (255, 255, 255), (self.screen.get_width() / 2, self.screen.get_height() / 2))
        pygame.display.update()

    def show_success_screen(self):
        start_ticks = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_ticks < 3000:  # 3초 동안 축하 메시지와 효과를 표시합니다.
            self.background.draw(self.screen)
            if (pygame.time.get_ticks() // 500) % 2 == 0:  # 텍스트 깜빡임 효과
                self.render_text_centered("Congratulations!", self.game_font, self.screen, (255, 255, 0), (self.screen.get_width() / 2, self.screen.get_height() / 2))
            pygame.display.update()
            self.clock.tick(60)
        self.running = False
        with open('success_status_3.txt', 'w') as file:
            file.write('success')
        print("Success status written for map3")

    def show_game_over_screen(self):
        self.background.draw(self.screen)
        self.render_text_centered("Game Over", self.game_font, self.screen, (255, 0, 0), (self.screen.get_width() / 2, self.screen.get_height() / 2))
        pygame.display.update()
        pygame.time.delay(2000)
        self.running = False

if __name__ == "__main__":
    game = GameFacade()
    game.run()

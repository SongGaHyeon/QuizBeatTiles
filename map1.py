import pygame
import random
import sys

class GameFacade:
    def __init__(self):
        self.screen_width = 480
        self.screen_height = 640
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("QuizBeatTiles")
        self.clock = pygame.time.Clock()
        self.background = self._load_image("image/Butterflies-2-2-2-2.jpg")
        self.character = self._load_image("image/berry.png")
        self.character_size = self.character.get_rect().size
        self.character_width = self.character_size[0]
        self.character_height = self.character_size[1]
        self.character_x_pos = (self.screen_width / 2) - (self.character_width / 2)
        self.character_y_pos = self.screen_height - self.character_height
        self.to_x = 0
        self.character_speed = 10

        # Font
        self.font_path = "image/AppleSDGothicNeo.ttc"
        self.game_font = pygame.font.Font(self.font_path, 40)

        # Score
        self.score = 0
        self.quiz_mode = False
        self.quiz_question = ""
        self.quiz_answer = ""
        self.quizzes = [
            ("Visitor Pattern은 데이터구조와 처리를 분리하는 패턴이다", "O"),
            ("객체는 속성과 함수로 구성된다", "O"),
            ("동일한 것을 분리해서 낭비를 없애는 건 Flyweight Pattern이다", "X"),
            ("OOP는 Object-Oriented Programming의 약자다", "O"),
            ("Bride Pattern은 클래스 계층과 구현의 클래스 계층을 합치는거다", "X"),
            ("상속은 클래스를 확장하기 위한 편리한 방법이지만 클래스간 강한연결을 만든다", "O"),
            ("약한 연결을 하고, 클래스를 확장시키기 위해 '위임'을 사용하는 것이 적절하다", "O"),
            ("상자안의 상자 같은 재귀적 구조를 갖는 패턴은 composite 패턴이다", "O")
        ]
        self.quiz_index = 0
        self.quiz_answered = []
        self.running = True
        self.game_over = False
        self.game_success = False

        # Factory Pattern을 이용한 객체 생성
        self.tile = self.create_object("tile")
        self.bomb = self.create_object("bomb")
        self.cake = self.create_object("cake")

        # Background Music
        self.background_music_path = "image/quizmusic.mp3"
        pygame.mixer.music.load(self.background_music_path)
        pygame.mixer.music.play(-1)  # Play the music in a loop

    def _load_image(self, path):
        return pygame.image.load(path)

    def create_object(self, obj_type):
        return GameObjectFactory.create_object(obj_type, self.screen_width)

    def reset_success_status(self):
        for i in range(1, 4):
            with open(f'success_status_{i}.txt', 'w') as file:
                file.write('')

    def render_text_centered(self, text, font, surface, color, pos):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=pos)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.to_x -= self.character_speed
            elif event.key == pygame.K_RIGHT:
                self.to_x += self.character_speed
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                self.to_x = 0

    def update_character_position(self):
        self.character_x_pos += self.to_x
        if self.character_x_pos < 0:
            self.character_x_pos = 0
        elif self.character_x_pos > self.screen_width - self.character_width:
            self.character_x_pos = self.screen_width - self.character_width

    def update_objects(self):
        self.tile.update_position(self.screen_width)
        self.bomb.update_position(self.screen_width)
        self.cake.update_position(self.screen_width)

    def check_collisions(self):
        character_rect = self.character.get_rect()
        character_rect.left = self.character_x_pos
        character_rect.top = self.character_y_pos

        if character_rect.colliderect(self.tile.rect):
            self.score += 10
            self.tile.reset_position(self.screen_width)

        if character_rect.colliderect(self.cake.rect):
            self.score += 15
            self.cake.reset_position(self.screen_width)

        if character_rect.colliderect(self.bomb.rect):
            self.game_over = True

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.character, (self.character_x_pos, self.character_y_pos))
        self.tile.draw(self.screen)
        self.bomb.draw(self.screen)
        self.cake.draw(self.screen)

        score_text = self.game_font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (self.screen_width / 2 - score_text.get_width() / 2, 10))

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

                    if self.score >= 300 and self.quiz_index < len(self.quizzes):
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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_o:
                if self.quiz_answer == "O":
                    self.score += 1000
                self.quiz_mode = False
                self.quiz_answered.append(self.quiz_question)
            elif event.key == pygame.K_x:
                if self.quiz_answer == "X":
                    self.score += 1000
                self.quiz_mode = False
                self.quiz_answered.append(self.quiz_question)

        if self.score >= 8000:
            self.game_success = True
        elif len(self.quiz_answered) == len(self.quizzes) and self.score < 8000:
            self.game_over = True

    def draw_quiz(self):
        font_size = 40
        quiz_font = pygame.font.Font(self.font_path, font_size)
        while True:
            quiz_text = quiz_font.render(self.quiz_question, True, (255, 255, 255))
            if quiz_text.get_width() <= self.screen_width - 20:
                break
            font_size -= 2
            quiz_font = pygame.font.Font(self.font_path, font_size)

        self.screen.blit(self.background, (0, 0))
        self.render_text_centered(self.quiz_question, quiz_font, self.screen, (255, 255, 255), (self.screen_width / 2, self.screen_height / 2))
        pygame.display.update()

    def show_success_screen(self):
        self.screen.blit(self.background, (0, 0))
        self.render_text_centered("Success", self.game_font, self.screen, (135, 206, 235), (self.screen_width / 2, self.screen_height / 2))
        pygame.display.update()
        pygame.time.delay(2000)
        self.running = False
        with open('success_status_1.txt', 'w') as file:
            file.write('success')
        print("Success status written for map1")

    def show_game_over_screen(self):
        self.screen.blit(self.background, (0, 0))
        self.render_text_centered("Game Over", self.game_font, self.screen, (255, 0, 0), (self.screen_width / 2, self.screen_height / 2))
        pygame.display.update()
        pygame.time.delay(2000)
        self.running = False

class GameObjectFactory:
    @staticmethod
    def create_object(obj_type, screen_width):
        if obj_type == "tile":
            return GameObject("image/tiles.png", 5, screen_width)
        elif obj_type == "bomb":
            return GameObject("image/bombs.png", 4, screen_width)
        elif obj_type == "cake":
            return GameObject("image/cake.png", 8, screen_width)
        else:
            raise ValueError(f"Unknown object type: {obj_type}")

class GameObject:
    def __init__(self, image_path, speed, screen_width):
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.speed = speed
        self.screen_width = screen_width
        self.reset_position(screen_width)

    def reset_position(self, screen_width):
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = 0

    def update_position(self, screen_width):
        self.rect.y += self.speed
        if self.rect.y > self.screen_width:
            self.reset_position(screen_width)

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

if __name__ == "__main__":
    pygame.init()
    game = GameFacade()
    game.run()

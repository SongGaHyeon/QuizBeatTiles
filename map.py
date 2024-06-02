import pygame

pygame.init() #초기화

#화면 크기 설정
screen_width = 480
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

#화면 제목
pygame.display.set_caption("MAP")

clock = pygame.time.Clock()

image = pygame.image.load("C:/Users/ChoiSeunghwan/Desktop/pygame/worldmap.png")
image = pygame.transform.scale(image, (480,600))
background1 = pygame.image.load("C:/Users/ChoiSeunghwan/Desktop/pygame/1.jpg")
background1 = pygame.transform.scale(background1,(60,40))
background2 = pygame.image.load("C:/Users/ChoiSeunghwan/Desktop/pygame/2.jpg")
background2 = pygame.transform.scale(background2,(60,40))
background3 = pygame.image.load("C:/Users/ChoiSeunghwan/Desktop/pygame/3.jpg")
background3 = pygame.transform.scale(background3,(60,40))

background1_rect = background1.get_rect()
background2_rect = background2.get_rect()
background3_rect = background3.get_rect()

def set_image_position(image_rect, position):
    if position =="1":
        image_rect.bottomleft = (55, 200)
    elif position == "2":
        image_rect.center = (250, 20)
    elif position == "3":
        image_rect.topright = (430, 155)
    else:
        raise ValueError("Unknown position: choose from '1', '2', '3'")


# 캐릭터 불러오기
character = pygame.image.load("C:/Users/ChoiSeunghwan/Desktop/pygame/캐릭터.png")
character = pygame.transform.scale(character,(50, 50))
character_size = character.get_rect().size #이미지의 크기를 구함
character_width = character_size[0] #캐릭터의 가로 크기
character_height = character_size[1] #세로
character_x_pos = (screen_width / 2) -(character_width / 2) #화면 가로의 절반크기에 해당하는 곳 위치
character_y_pos = screen_height - character_height # 세로

#이동 할 좌표
to_x = 0
to_y = 0

#이동속도
character_speed = 0.6



#이벤트 루푸 
running = True #겜 진행중?
while running:
    dt = clock.tick(30) # 게임화면 초당 프레임 수 설정... 숫자가 커질수록 빨리 낮을수록 느리게
    for event in pygame.event.get(): #어떤 이벤트가 발생?
        if event.type == pygame.QUIT: #창이 닫히는 이벤트가 발생?
            running = False
        
        if event.type == pygame.KEYDOWN: #키가 눌러졋는지 확인
            if event.key == pygame.K_LEFT: #왼쪽으로가기
                to_x -= character_speed
            elif event.key == pygame.K_RIGHT: #오른쪽으로 가기
                to_x += character_speed
            elif event.key == pygame.K_UP: #위로 가기
                to_y -= character_speed
            elif event.key == pygame.K_DOWN: #아래로 가기
                to_y += character_speed

        if event.type == pygame.KEYUP: #방향키 때면 멈춤
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                to_x = 0
            elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                to_y = 0

    character_x_pos += to_x * dt
    character_y_pos += to_y * dt

    #캐릭터 가로로 못나가게
    if character_x_pos < 0:
        character_x_pos = 0
    elif character_x_pos > screen_width - character_width: 
        character_x_pos = screen_width -character_width
   #세로로 못나가게
    if character_y_pos < 0:
        character_y_pos = 0
    elif character_y_pos > screen_height - character_height:
        character_y_pos = screen_height - character_height


    screen.blit(image,(0,0))

    set_image_position(background1_rect, "1")
    screen.blit(background1, background1_rect)

    set_image_position(background2_rect, "2")
    screen.blit(background2, background2_rect)

    set_image_position(background3_rect, "3")
    screen.blit(background3, background3_rect)






    screen.blit(character,(character_x_pos, character_y_pos)) #캐릭터 그리기


    pygame.display.update()
#겜종료
pygame.quit()


import pygame

pygame.init()

font20 = pygame.font.Font('freesansbold.ttf', 20)
font40 = pygame.font.Font('freesansbold.ttf', 40)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Group1Pong")

clock = pygame.time.Clock()
FPS = 30

def show_start_screen():
    screen.fill(BLACK)
    title_text = font40.render("Group 1 Information Processing Gurus", True, WHITE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    button_text = font20.render("Press SPACE to Play", True, WHITE)
    button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    
    running = True
    while running:
        screen.fill(BLACK)
        screen.blit(title_text, title_rect)
        pygame.draw.rect(screen, WHITE, button_rect, 2)
        screen.blit(button_text, button_text.get_rect(center=button_rect.center))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                running = False
        
        pygame.display.update()
        clock.tick(FPS)

class Striker:
    def __init__(self, posx, posy, width, height, speed, color):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
        self.playerRect = pygame.Rect(posx, posy, width, height)
        self.player = pygame.draw.rect(screen, self.color, self.playerRect)

    def display(self):
        self.player = pygame.draw.rect(screen, self.color, self.playerRect)

    def update(self, yFac):
        self.posy = self.posy + self.speed * yFac
        if self.posy <= 0:
            self.posy = 0
        elif self.posy + self.height >= HEIGHT:
            self.posy = HEIGHT - self.height
        self.playerRect = (self.posx, self.posy, self.width, self.height)

    def displayScore(self, text, score, x, y, color):
        text = font20.render(text + str(score), True, color)
        textRect = text.get_rect()
        textRect.center = (x, y)
        screen.blit(text, textRect)

    def getRect(self):
        return self.playerRect


class Ball:
    def __init__(self, posx, posy, radius, speed, color):
        self.posx = posx
        self.posy = posy
        self.radius = radius
        self.speed = speed
        self.color = color
        self.xFac = 1
        self.yFac = -1
        self.ball = pygame.draw.circle(screen, self.color, (self.posx, self.posy), self.radius)
        self.firstTime = 1

    def display(self):
        self.ball = pygame.draw.circle(screen, self.color, (self.posx, self.posy), self.radius)

    def update(self):
        self.posx += self.speed * self.xFac
        self.posy += self.speed * self.yFac
        if self.posy <= 0 or self.posy >= HEIGHT:
            self.yFac *= -1
        if self.posx <= 0 and self.firstTime:
            self.firstTime = 0
            return 1
        elif self.posx >= WIDTH and self.firstTime:
            self.firstTime = 0
            return -1
        else:
            return 0

    def reset(self):
        self.posx = WIDTH // 2
        self.posy = HEIGHT // 2
        self.xFac *= -1
        self.firstTime = 1

    def hit(self):
        self.xFac *= -1

    def getRect(self):
        return self.ball


def main():
    show_start_screen()
    running = True
    replay_mode = False
    replay_frames = []
    replay_index = 0
    replay_flash = True
    flash_timer = 0

    JFH = Striker(20, 0, 10, 100, 10, RED)
    Noob = Striker(WIDTH - 30, 0, 10, 100, 10, BLUE)
    ball = Ball(WIDTH // 2, HEIGHT // 2, 7, 7, WHITE)

    listOfPlayers = [JFH, Noob]
    JFHScore, NoobScore = 0, 0
    JFHYFac, NoobYFac = 0, 0

    while running:
        screen.fill(BLACK)
        
        if not replay_mode:
            if len(replay_frames) > 30:
                replay_frames.pop(0)
            replay_frames.append({
                "ball_pos": (ball.posx, ball.posy),
                "JFH_pos": JFH.posy,
                "Noob_pos": Noob.posy
            })
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    NoobYFac = -1
                if event.key == pygame.K_DOWN:
                    NoobYFac = 1
                if event.key == pygame.K_w:
                    JFHYFac = -1
                if event.key == pygame.K_s:
                    JFHYFac = 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    NoobYFac = 0
                if event.key == pygame.K_w or event.key == pygame.K_s:
                    JFHYFac = 0

        for player in listOfPlayers:
            if pygame.Rect.colliderect(ball.getRect(), player.getRect()):
                ball.hit()

        if replay_mode:
            if replay_index < len(replay_frames):
                frame = replay_frames[replay_index]
                ball.posx, ball.posy = frame["ball_pos"]
                JFH.posy = frame["JFH_pos"]
                Noob.posy = frame["Noob_pos"]
                replay_index += 2
                flash_timer += 1
                if flash_timer % 10 == 0:
                    replay_flash = not replay_flash
                if replay_flash:
                    text = font20.render("REPLAY", True, WHITE)
                    screen.blit(text, (WIDTH // 2 - 40, HEIGHT // 2 - 10))
            else:
                replay_mode = False
                ball.reset()
        else:
            JFH.update(JFHYFac)
            Noob.update(NoobYFac)
            point = ball.update()
            if point:
                replay_mode = True
                replay_index = 0
                flash_timer = 0
                replay_flash = True
                if point == -1:
                    JFHScore += 1
                elif point == 1:
                    NoobScore += 1

        JFH.display()
        Noob.display()
        ball.display()
        JFH.displayScore("Big Dog JFH : ", JFHScore, 100, 20, WHITE)
        Noob.displayScore("MegaNoob : ", NoobScore, WIDTH - 100, 20, WHITE)

        pygame.display.update()
        clock.tick(FPS if not replay_mode else FPS // 2)

if __name__ == "__main__":
    main()
    pygame.quit()

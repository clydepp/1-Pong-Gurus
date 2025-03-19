import threading
import asyncio
import exportniosconsole  # Import the script that contains the Nios console
import pygame
import time
import json

def start_nios_console():
    #Runs exportniosconsole's main() inside a dedicated asyncio event loop in a thread.
    loop = asyncio.new_event_loop()  # Create a new event loop for the thread
    asyncio.set_event_loop(loop)
    loop.run_until_complete(exportniosconsole.main())  # Run exportniosconsole

# Start exportniosconsole in a separate thread
nios_thread = threading.Thread(target=start_nios_console, daemon=True)
nios_thread.start()



pygame.init()

font20 = pygame.font.Font("freesansbold.ttf", 20)
font40 = pygame.font.Font("freesansbold.ttf", 40)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Group1Pong")

clock = pygame.time.Clock()
FPS = 30
username_opp = None
side_opp = None
opp_username_available = asyncio.Event()
# ballposx_global, ballposy_global = None, None
# ballpos_available = asyncio.Event()

def listen_for_username():
    global username_opp, side_opp
    
    if(exportniosconsole.decoded_msg):
            data = exportniosconsole.decoded_msg
            try:
                data = json.loads(data)
                if isinstance(data, dict) and "username" in data and "side" in data:
                    username_opp = data.get("username")
                    side_opp = data.get("side")
                    print(f"Extracted: Username: {username_opp}, Side: {side_opp}")
            except json.JSONDecodeError:
                pass
            
# async def listen_for_username():
#     global username_opp, side_opp
#     print(f"Listening for username")
#     while True:
#         try:
#             data = json.loads(exportniosconsole.decoded_msg)
#             if isinstance(data, dict) and "username" in data and "side" in data: # check if data is username and side
#                 print(f"Data loop")
#                 username_opp = data.get("username")
#                 side_opp = data.get("side")
#                 print(f"Extracted: Username: {username_opp}, Side: {side_opp}")
#                 opp_username_available.set()
#         except json.JSONDecodeError:
#             print("Not Json data.")
#             break
        
# async def listen_for_ballpos():
#     global ballposx_global, ballposy_global
    
#     while True:
#         try:
#             data = json.loads(exportniosconsole.decoded_msg)
#             if isinstance(data, dict) and "ballposx" in data and "ballposy" in data: # check if data is username and side
#                 ballposx_global = data.get("ballposx")
#                 ballposy_global = data.get("ballposy")
#                 print(f"Extracted: Ball Position: {ballposx_global}, {ballposy_global}")
#                 ballpos_available.set()
#         except json.JSONDecodeError:
#             print("Not Json data.")
#             break
            
# def handle_username_submit(username, side, writer):
    
#     # call exportniosconsole to send username as json packet to server
#     asyncio.ensure_future(exportniosconsole.send_username(username, side, writer))
#     print(f"Username submitted: {username} for {side} side")

# def listen_for_username():
#     while True:
    
#         try:       
#             data = json.loads(exportniosconsole.decoded_msg)
        
#             try:
#                 if isinstance(data, dict) and "username" in data and "side" in data: # check if data is username and side
#                     username = data.get("username")
#                     side = data.get("side")
#                     print(f"Extracted: Username: {username}, Side: {side}")
#                     return username, side
#             except json.JSONDecodeError:
#                 print("Not username data.")
                
#         except json.JSONDecodeError:
#             print("Not Json data.")
    
def enter_username():
    #asks users for username
    username_l, username_r = "", ""
    global input_active #track whose input is active
    input_active = "neither"
    
    screen.fill(BLACK)
    running = True
    
    while running:
        
        screen.fill(BLACK)
        if input_active == "neither":
            prompt_text = font40.render(
            f"Choose Left(<-) Or Right(->) ",
            True,
            WHITE,
            )
            prompt_rect = prompt_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            screen.blit(prompt_text, prompt_rect)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        input_active = "left"
                    elif event.key == pygame.K_RIGHT:
                        input_active = "right"
        else:
                       
            
            prompt_text = font40.render(
                f"Enter {input_active.upper()} Username: {username_l if input_active == 'left' else username_r}",
                True,
                WHITE,
            )
            prompt_rect = prompt_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            screen.blit(prompt_text, prompt_rect)
            
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:

                        if input_active == "left":
                            # handle_username_submit(username_l, "left", writer)
                            exportniosconsole.username = username_l
                            
                        else:
                            # handle_username_submit(username_r, "right", writer)
                            exportniosconsole.username = username_r
                        
                        exportniosconsole.side = input_active
                        exportniosconsole.username_available_event.set()
                        # username_opp, side = listen_for_username()
                        
                        if input_active == "left":
                            username_r = username_opp
                        else:
                            username_l = username_opp
                            
                        # print(f"Username submitted: {username_r} for {side} side")
                        return username_l, username_r
                    
                    elif event.key == pygame.K_BACKSPACE:
                        if input_active == "left":
                            username_l = username_l[:-1]
                        else:
                            username_r = username_r[:-1]
                    else:
                        if input_active == "left":
                            username_l += event.unicode
                        else:
                            username_r += event.unicode
                            
def enter_username_new():
    
    username = ""
    global input_active, side_opp, username_opp

    screen.fill(BLACK)
    running = True
    
    while running:
        
        listen_for_username()
            
        screen.fill(BLACK)
        prompt_text = font40.render(
                f"Enter Username: {username}",
                True,
                WHITE,
            )
        prompt_rect = prompt_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(prompt_text, prompt_rect)
        
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    while True:
                        if(exportniosconsole.decoded_msg):
                            data = exportniosconsole.decoded_msg
                            if isinstance(data, dict) and "username" in data and "side" in data:
                                username_opp = data.get("username")
                                side_opp = data.get("side")
                                print(f"Extracted: Username: {username_opp}, Side: {side_opp}")
                        
                        screen.fill(BLACK)
                        prompt_text = font40.render(
                            f"Choose Left(<-) Or Right(->) ",
                            True,
                            WHITE,
                        )
                        username_text = font20.render(f"Username: {username}", True, WHITE)
                        prompt_rect = prompt_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
                        username_rect = username_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                        
                        screen.blit(prompt_text, prompt_rect)
                        screen.blit(username_text, username_rect)
                        
                        #if opponent has submitted side and username, display it 
                        if(side_opp != None and username_opp != None):
                            opp_username_text = font20.render(f"Opponent {username_opp} has picked {side_opp}", True, WHITE)
                            opp_username_rect = opp_username_text.get_rect(center=(WIDTH // 2, HEIGHT // 1.5))
                            screen.blit(opp_username_text, opp_username_rect)
                        
                        pygame.display.update()
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                quit()
                            if event.type == pygame.KEYDOWN:
                                if (event.key == pygame.K_LEFT and (side_opp == None or side_opp == "right")):
                                    input_active = "left"
                                    exportniosconsole.username = username
                                    exportniosconsole.side = input_active
                                    exportniosconsole.username_available_event.set()
                                    return username                                
                                    
                                elif (event.key == pygame.K_RIGHT and (side_opp == None or side_opp == "left")):
                                    input_active = "right"
                                    exportniosconsole.username = username
                                    exportniosconsole.side = input_active
                                    exportniosconsole.username_available_event.set()
                                    return username   
                                    
                                elif ((event.key == pygame.K_LEFT and side_opp == "left") or (event.key == pygame.K_RIGHT and side_opp == "right")):
                                    subtext_text = font20.render(f"Opponent has already picked {side_opp}", True, RED)
                                    subtext_rect = subtext_text.get_rect(center=(WIDTH // 2, HEIGHT // 1.2))
                                    screen.blit(subtext_text, subtext_rect)
                                    pygame.display.update()
                                    time.sleep(2)
                                    continue
                                
                    
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode        

def show_waiting_screen():
    global username_opp, side_opp
    
    screen.fill(BLACK)
    title_text = font40.render("Waiting for Opponent...", True, WHITE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title_text, title_rect)
    
    running = True
    while running:
        listen_for_username()
        if(username_opp != None and side_opp != None):
            running = False
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        pygame.display.update()

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
        self.ballHit = 0
        self.wins = 0
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
        
        exportniosconsole.ballposx = self.posx
        exportniosconsole.ballposy = self.posy
        
        exportniosconsole.ballpos_available_event.set()
        
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
        self.speed = 7

    def hit(self):
        self.xFac *= -1
        self.speed += 3

    def getRect(self):
        return self.ball


async def main():
    global username_opp
    
    asyncio.create_task(exportniosconsole.main())
    # asyncio.create_task(listen_for_username())
    
    username = enter_username_new()
    if(input_active == "left"):
        username_l = username
    elif(input_active == "right"):
        username_r = username
    
    show_waiting_screen()
    
    if(input_active == "left" and side_opp == "right"):
        username_r = username_opp
    elif(input_active == "right" and side_opp =="left"):
        username_l = username_opp
    
    show_start_screen()

    running = True
    replay_mode = False
    replay_frames = []
    replay_index = 0
    replay_flash = True
    flash_timer = 0

    player_l = Striker(20, 0, 10, 150, 20, RED)
    player_r = Striker(WIDTH - 30, 0, 10, 150, 20, BLUE)
    ball = Ball(WIDTH // 2, HEIGHT // 2, 12, 10, WHITE)

    listOfPlayers = [player_l, player_r]
    player_l_Score, player_r_Score = 0, 0
    player_l_YFac, player_r_YFac = 0, 0
    paddle1_pos = 0
    paddle2_pos = 0

    while running:
        screen.fill(BLACK)
        bit_width = 32
        
        if (player_l_Score == 4 or player_r_Score == 4):
            running = False
            if player_l_Score == 4:
                text = font20.render(username_l + " VICTORY :P", True, WHITE)
                player_l.wins += 4
                
            else:
                text = font20.render(username_r + " VICTORY Bo", True, WHITE)
                player_r.wins += 4
                
            screen.blit(text, (WIDTH // 2 - 40, HEIGHT // 2 - 10))
            pygame.display.update()
            time.sleep(5)
            player_l_Score = 0
            player_r_Score = 0
            replay_mode = False
            ball.reset()
            username_l, username_r = enter_username()
            show_start_screen()
            running = True
            
        if(input_active == "left"):
            left_pos = exportniosconsole.strip_output
            right_pos = exportniosconsole.decoded_msg
        elif(input_active == "right"):
            left_pos = exportniosconsole.decoded_msg
            right_pos = exportniosconsole.strip_output
        
        if isinstance(left_pos, str): 
            try:
                #if (exportniosconsole.strip_output != '\x1b]2;Altera Nios II EDS 18.1 [gcc4]\x07nios2-terminal: connected to hardware target using JTAG UART on cable'): # Ensure it's a string
                if (left_pos.lower().startswith("0x")):    
                    paddle1_value = int(left_pos, 16)  # Convert HEX to int
                    if (paddle1_value & (1 << (bit_width - 1))) != 0:  # Check if the sign bit is set
                        paddle1_pos = paddle1_value - (1 << bit_width)  # Perform two's complement conversion
                    else:
                        paddle1_pos = paddle1_value
            except ValueError:
                pass

        if isinstance(right_pos, str): 
            try:
                #if (exportniosconsole.decoded_msg != '\x1b]2;Altera Nios II EDS 18.1 [gcc4]\x07nios2-terminal: connected to hardware target using JTAG UART on cable'): # Ensure it's a string
                if (right_pos.lower().startswith("0x")):    
                    paddle2_value = int(right_pos, 16)  # Convert HEX to int
                    if (paddle2_value & (1 << (bit_width - 1))) != 0:  # Check if the sign bit is set
                        paddle2_pos = paddle2_value - (1 << bit_width)  # Perform two's complement conversion
                    else:
                        paddle2_pos = paddle2_value 
            except ValueError:
                pass

        
        
        print(paddle1_pos)   
        paddle1_pos =  paddle1_pos / 100
        paddle2_pos =  paddle2_pos / 100
        
        if not replay_mode:
            if len(replay_frames) > 30:
                replay_frames.pop(0)
            replay_frames.append(
                {
                    "ball_pos": (ball.posx, ball.posy),
                    "player_l_pos": player_l.posy,
                    "player_r_pos": player_r.posy,
                }
            )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player_r_YFac = -1
                if event.key == pygame.K_DOWN:
                    player_r_YFac = 1
                if event.key == pygame.K_w:
                    player_l_YFac = -1
                if event.key == pygame.K_s:
                    player_l_YFac = 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    player_r_YFac = 0
                if event.key == pygame.K_w or event.key == pygame.K_s:
                    player_l_YFac = 0

        for player in listOfPlayers:
            if pygame.Rect.colliderect(ball.getRect(), player.getRect()):
                ball.hit()
                player.ballHit += 1

        if replay_mode:
            if replay_index < len(replay_frames)-1:
                frame = replay_frames[replay_index]
                ball.posx, ball.posy = frame["ball_pos"]
                player_l.posy = frame["player_l_pos"]
                player_r.posy = frame["player_r_pos"]
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
            player_l.update(paddle1_pos)
            player_r.update(paddle2_pos)
                
            point = ball.update()
            
            if point:
                replay_mode = True
                replay_index = 0
                flash_timer = 0
                replay_flash = True
                if point == -1:
                    player_l_Score += 1
                elif point == 1:
                    player_r_Score += 1
                    
                    
        player_l.display()
        player_r.display()
        ball.display()

    
        player_l.displayScore(username_l + ": ", player_l_Score, 100, 20, WHITE)
        player_r.displayScore(username_r + ": ", player_r_Score, WIDTH - 100, 20, WHITE)

        pygame.display.update()
        clock.tick(FPS if not replay_mode else FPS // 2)
        

if __name__ == "__main__":
    asyncio.run(main())
    pygame.quit()
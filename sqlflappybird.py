from collections import namedtuple
import pygame
import time
import random
import mysql.connector

# Connect with the database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    database="po9_scores"
)

cursor = db.cursor()

pygame.init()

Point = namedtuple('Point', 'x, y')

# RGB colors
BLACK = (0,0,0)
RED = (200,0,0)
FPS = 120
GAP = 250

font = pygame.font.Font('arial.ttf', 25)

# Images
PIPES = pygame.image.load('images/pipes.png')
BIRB = pygame.image.load('images/birb.png')
BG = pygame.image.load('images/bg.png')

class birbgame():
    def __init__(self, w=640, h=480):
        self.clock = pygame.time.Clock()
        self.why = 1
        self.h = h
        self.z = 0
        self.pipesx = 800
        self.w = w
        self.timer = 0
        # Display the game
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Birb')
        self.bird = Point(100, self.h/6)
        self.pipes = []
        self.score = 0

    def step(self):
        if self.timer < time.time():
            self.JUMP = False
        # Check for inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.timer = time.time() + 0.6
                    self.z = 0
                    self.JUMP = True
        self._frames()
        game_over = False
        if self.dead():
            game_over = True
        
        self.clock.tick(FPS)
        return game_over, int(self.score)

    # Check if the player has died or not
    def dead(self):   
        if self.bird.y > 445:
            return True
        if len(self.pipes) > 3:
            if self.bird.x > self.pipes[-4][0]-40 and self.bird.x < self.pipes[-4][0]+40:
                if self.bird.y < self.pipes[-4][1]+350-(220/2) or self.bird.y > self.pipes[-4][1]+370:
                    return True
                elif (self.pipes[-4][0]+40)-self.bird.x < 2:
                    self.score += 1

    # Display the game
    def _frames(self):
        self.display.blit(BG, (0,0))
        self._moving()
        for x in self.pipes:
            self.display.blit(PIPES, (x[0], x[1]))
        self.display.blit(BIRB, (self.bird.x, self.bird.y))
        scoretext = font.render("Score: " + str(self.score), True, RED)
        self.display.blit(scoretext, [0,0])
        pygame.display.flip()

    # Move the bird and also the pipes
    def _moving(self):
        self.z += 0.05
        self.pipesx -= 1.25
        for t in self.pipes:
            t[0] = self.pipesx + GAP + GAP*self.pipes.index(t)
        x = self.bird.x
        y = self.bird.y
        if self.JUMP == True:
            if self.timer > time.time():
                y -= (-1.5*self.z**2.1) + 3.5*self.z
        elif self.JUMP == False:
            y += 1.5**self.z
        self.bird = Point(x, y) 
        if self.pipesx % GAP == 0:
            self.pipes.append([int(self.pipesx + GAP + GAP*(self.why)), random.randint(-230, 0)])
            self.why += 1

if __name__ == "__main__":
    game = birbgame()

    while True:
        game_over, score = game.step()
        
        if game_over == True:
            break
    # Send the score into the database
    sql = "INSERT INTO scores (score) VALUES (%s)"
    value = (score,)
    cursor.execute(sql, value)
    db.commit()
    print("He died. What a sissy!! Your final score was: " + str(score))  


 
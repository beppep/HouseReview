import pygame
import random

resolution = (1600,900)
gridSize = 64
topLeft = (100,100)

pygame.init()
clock = pygame.time.Clock()
game_display = pygame.display.set_mode(resolution)#, pygame.FULLSCREEN)
pygame.display.set_caption('HouseReview!')
pygame.display.set_icon(pygame.image.load("tiles/window.png"))


def loadImage(name,r):
    image = pygame.image.load("tiles/"+name)
    image = pygame.transform.scale(image, (r, r))
    return image

class Block():

    def __init__(self, x, y, mirrored, name, image):
        self.x = x
        self.y = y
        self.mirrored = mirrored
        self.name = name
        self.image = image

    def land(self):
        highest = game.houseHeight
        for i in game.blocks:
            if i.x == self.x:
                highest = min(i.y, highest)
        self.y = highest - 1
        game.blocks.append(self)
        game.grid[self.y][self.x]=self
        game.newBlock()

    def happiness(self):
        return 0
        
    def draw(self):
        game_display.blit(self.image, (self.x*gridSize+topLeft[0], self.y*gridSize+topLeft[1]))

class Game():

    starters = ["wall","edge","door1",]
    blockNames = ["wall","edge","window","door0","door1","roof0","roof1","plateau"]
    blockWeights = [1,1,0.5,0.4,0.4,1,1,0.5]

    def __init__(self):
        self.houseWidth = random.randint(6,10)
        self.houseHeight = random.randint(6,10)
        self.flyingBlock = None
        self.blocks = []
        self.holdings = [None]*2
        self.grid = []
        for i in range(self.houseHeight):
            self.grid.append([None]*self.houseWidth)
        self.images = {}
        self.mirrorImages = {}
        for i in self.blockNames:
            image = loadImage(i+".png", gridSize)
            self.images[i] = image
            self.mirrorImages[i] = pygame.transform.flip(image, True, False)
        self.newBlock(starter=True)

    def newBlock(self, starter=False):
        if starter:
            name = random.choice(self.starters)
        else:
            name = random.choices(self.blockNames, weights = self.blockWeights, k = 1)[0]
        mirrored = random.randint(0,1)
        if not mirrored:
            img = self.images[name]
        else:
            img = self.mirrorImages[name]
        self.flyingBlock = Block(3,0, mirrored, name, img)

    def rateHouse(self):
        rating = 0
        for b in self.blocks:
            rating+=b.happiness
        for x in self.houseWidth:
            for y in self.grid:
                if self.grid[y][x]:
                    rating += (self.grid[y][x].type=="roof0")
                    reting -= (self.grid[y][x].type=="door1")

    def draw(self):
        for i in range(self.houseHeight+1):
            pygame.draw.line(game_display, (200,200,200), (topLeft[0],topLeft[1]+gridSize*i), (topLeft[0]+self.houseWidth*gridSize, topLeft[1]+gridSize*i), 1)
        for i in range(self.houseWidth+1):
            pygame.draw.line(game_display, (200,200,200), (topLeft[0]+gridSize*i,topLeft[1]), (topLeft[0]+gridSize*i, topLeft[1]+self.houseHeight*gridSize), 1)
        self.flyingBlock.draw()
        for block in self.blocks:
            block.draw()

        for i in range(len(self.holdings)):
            d = gridSize//4
            pygame.draw.rect(game_display, (100,100,100), (topLeft[0]+(self.houseWidth+1+2*i)*gridSize-d, topLeft[1]-d, 2*d+gridSize,2*d+gridSize), 0)
            if not self.holdings[i] == None:
                self.holdings[i].draw()

game = Game()

jump_out=False
while jump_out == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            jump_out = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                jump_out = True
            if event.key == pygame.K_RIGHT:
                if game.flyingBlock.x<game.houseWidth-1:
                    game.flyingBlock.x+=1
            if event.key == pygame.K_LEFT:
                if game.flyingBlock.x>0:
                    game.flyingBlock.x-=1
            if event.key == pygame.K_DOWN:
                game.flyingBlock.land()
            if event.key == pygame.K_RETURN:
                game.flyingBlock=None
                game.rateHouse()
            for i in range(len(game.holdings)):
                if event.key == getattr(pygame,"K_"+str(i+1)):
                    if game.holdings[i]:
                        game.holdings[i].x, game.holdings[i].y = (game.flyingBlock.x, game.flyingBlock.y)
                    game.flyingBlock.x, game.flyingBlock.y = (game.houseWidth+1+2*i, 0)
                    game.holdings[i], game.flyingBlock = (game.flyingBlock, game.holdings[i])
                    if game.flyingBlock == None:
                        game.newBlock()

    game_display.fill((100,100,200))

    game.draw()

    pygame.display.flip()


pygame.quit()
quit()
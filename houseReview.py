import pygame
import pygame_gui
import random

resolution = (1500,700)
gridSize = 64
topLeft = (80,80)

pygame.init()
clock = pygame.time.Clock()
game_display = pygame.display.set_mode(resolution)#, pygame.FULLSCREEN)
pygame.display.set_caption('HouseReview!')
pygame.display.set_icon(pygame.image.load("tiles/window.png"))

managers={
    "":pygame_gui.UIManager(resolution), #Main menu
    "b":pygame_gui.UIManager(resolution), #Build
    "r":pygame_gui.UIManager(resolution), #Review
    "s":pygame_gui.UIManager(resolution), #Shop
}

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
        highest = game.building.height
        for i in game.building.blocks:
            if i.x == self.x:
                highest = min(i.y, highest)
        self.y = highest - 1
        game.building.blocks.append(self)
        game.building.grid[self.y][self.x]=self
        game.building.newBlock(self.x)

    def happiness(self):
        return 0
        
    def draw(self):
        game_display.blit(self.image, (self.x*gridSize+topLeft[0], self.y*gridSize+topLeft[1]))

class Game():

    def __init__(self):
        self.money = 100
        self.mode = ""
        self.baskets = 0
        self.building = None

    def start(self):
        self.building = House(random.randint(6,10), random.randint(6,9), baskets=self.baskets)

    def draw(self):
        if self.building:
            self.building.draw()

class Building():

    def __init__(self, w,h, baskets = 2):
        self.width = w
        self.height = h
        self.flyingBlock = None
        self.blocks = []
        self.holdings = [None]*baskets
        self.grid = []
        for i in range(self.height):
            self.grid.append([None]*self.width)
        self.images = {}
        self.mirrorImages = {}
        for i in self.blockNames:
            image = loadImage(i+".png", gridSize)
            self.images[i] = image
            self.mirrorImages[i] = pygame.transform.flip(image, True, False)
        self.newBlock(starter=True)

    def newBlock(self, x=3, starter=False):
        if starter:
            name = random.choice(self.starters)
        else:
            name = random.choices(self.blockNames, weights = self.blockWeights, k = 1)[0]
        mirrored = random.randint(0,1)
        if not mirrored:
            img = self.images[name]
        else:
            img = self.mirrorImages[name]
        self.flyingBlock = Block(x,0, mirrored, name, img)

    def rate(self):
        rating = 0
        for b in self.blocks:
            rating+=b.happiness()
        for x in range(self.width):
            for y in range(len(self.grid)):
                if self.grid[y][x]:
                    rating += (self.grid[y][x].name=="roof0")
                    rating -= (self.grid[y][x].name=="door1")
        return 5

    def draw(self):
        for i in range(self.height+1):
            pygame.draw.line(game_display, (200,200,200), (topLeft[0],topLeft[1]+gridSize*i), (topLeft[0]+self.width*gridSize, topLeft[1]+gridSize*i), 1)
        for i in range(self.width+1):
            pygame.draw.line(game_display, (200,200,200), (topLeft[0]+gridSize*i,topLeft[1]), (topLeft[0]+gridSize*i, topLeft[1]+self.height*gridSize), 1)
        self.flyingBlock.draw()
        for block in self.blocks:
            block.draw()

        for i in range(len(self.holdings)):
            d = gridSize//4
            pygame.draw.rect(game_display, (100,100,100), (topLeft[0]+(self.width+1+2*i)*gridSize-d, topLeft[1]-d, 2*d+gridSize,2*d+gridSize), 0)
            if not self.holdings[i] == None:
                self.holdings[i].draw()

class House(Building):

    starters = ["wall","edge","door1",]
    blockNames = ["wall","edge","window","door0","door1","roof0","roof1","plateau"]
    blockWeights = [1,1,0.5,0.4,0.4,1,1,0.5]

    def __init__(self, w,h, baskets=0):
        super(House, self).__init__(w,h,baskets)
        self.width = w
        self.height = h
        self.baskets = [None]*baskets
        

# Main Menu
menu_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((20, 25), (200, 75)),html_text="Yo though <br>$100",manager=managers[""])
shop_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((200, 125), (200, 75)),html_text="Yo though <br>$100",manager=managers["s"])
build_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (200, 50)),text='Build Buildings',manager=managers[""])
shop_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 350), (200, 50)),text='Buy Baskets',manager=managers[""])
exit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 425), (200, 50)),text='Bye Bye',manager=managers[""])

back_buttons = [
    pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 50), (100, 50)),text='Back',manager=managers["s"]),
]

# Shop
basket_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (200, 50)),text='Buy Bucket ($100)',manager=managers["s"])

# Review
review_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((20, 25), (300, 175)),html_text="This house is horrendous! I can barely accept this work.",manager=managers["r"])
some_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((600, 125), (200, 200)),html_text="huh",manager=managers["r"])
ok_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((460, 400), (300, 200)),text='You recieved $X money.',manager=managers["r"])

game = Game()

clock = pygame.time.Clock()
jump_out=False
while jump_out == False:
    time_delta = clock.tick(60)/1000.0
    manager=managers[game.mode]
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            jump_out = True
        if event.type == pygame.KEYDOWN:
            if game.building:
                if event.key == pygame.K_RIGHT:
                    if game.building.flyingBlock.x<game.building.width-1:
                        game.building.flyingBlock.x+=1
                if event.key == pygame.K_LEFT:
                    if game.building.flyingBlock.x>0:
                        game.building.flyingBlock.x-=1
                if event.key == pygame.K_DOWN:
                    game.building.flyingBlock.land()
                for i in range(len(game.building.holdings)):
                    if event.key == getattr(pygame,"K_"+str(i+1)):
                        if game.building.holdings[i]:
                            game.building.holdings[i].x, game.building.holdings[i].y = (game.building.flyingBlock.x, game.building.flyingBlock.y)
                        game.building.flyingBlock.x, game.building.flyingBlock.y = (game.building.width+1+2*i, 0)
                        game.building.holdings[i], game.building.flyingBlock = (game.building.flyingBlock, game.building.holdings[i])
                        if game.building.flyingBlock == None:
                            game.building.newBlock()
                if event.key == pygame.K_RETURN:
                    game.building.flyingBlock=None
                    game.building.rate()
                    game.building = None
                    game.mode="r"
                    game.money+=48
                    ok_button.text="I recieve $"+str(48) # ska kunna få olika mycket. inte bara 48 dollar
                    ok_button.rebuild()

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            
                #buttons
                if event.ui_element in back_buttons:
                    game.mode=""
                if event.ui_element == shop_button:
                    game.mode="s"
                if event.ui_element == exit_button:
                    jump_out = True
                if event.ui_element == build_button:
                    game.mode="b"
                    game.start()
                if event.ui_element == ok_button:
                    game.mode=""
                    menu_textbox.html_text="Yo though <br>$"+str(game.money)
                    menu_textbox.rebuild()
                    shop_textbox.html_text="Yo though <br>$"+str(game.money)
                    shop_textbox.rebuild()
                if event.ui_element == basket_button:
                    if game.money>=100:
                        game.money-=100
                        game.baskets += 1
                    menu_textbox.html_text="Yo though <br>$"+str(game.money)
                    menu_textbox.rebuild()
                    shop_textbox.html_text="Yo though <br>$"+str(game.money)
                    shop_textbox.rebuild()
        manager.process_events(event)

    manager.update(time_delta)



    game_display.fill((100,100,200))
    manager.draw_ui(game_display)
    
    game.draw()

    pygame.display.flip()


pygame.quit()
quit()
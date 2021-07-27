import pygame
import pygame_gui
import random

resolution = (1200,700)
gridSize = 64
topLeft = (20,20+gridSize)
difficulty= 1 # 0-1 but can go to 9

pygame.init()
clock = pygame.time.Clock()
game_display = pygame.display.set_mode(resolution)#, pygame.FULLSCREEN)
pygame.display.set_caption('HouseReview!')
pygame.display.set_icon(pygame.image.load("data/house/window.png"))

managers={
    "":pygame_gui.UIManager(resolution), #Main menu
    "b":pygame_gui.UIManager(resolution), #Build
    "r":pygame_gui.UIManager(resolution), #Review
    "p":pygame_gui.UIManager(resolution), #Payment
    "s":pygame_gui.UIManager(resolution), #Shop
}

def loadImage(name,r,r2=None):
    if not r2:
        r2=r
    image = pygame.image.load("data/"+name)
    image = pygame.transform.scale(image, (r, r2))
    return image

def outOfTen(rating):
    rating = round(rating*10,2)
    if rating == int(rating):
        rating = int(rating)
    return str(rating)+"/10"

class Sound():
    v=1
    pygame.mixer.init(buffer=32)
    hitSound = pygame.mixer.Sound("data/sound/soundeffect2.wav")
    lickSound = pygame.mixer.Sound("data/sound/lickeffect.wav")
    lickSound.set_volume(v*0.3)
    
    pygame.mixer.music.load("data/sound/music.wav") #must be wav 16bit and stuff?
    pygame.mixer.music.set_volume(v*0.1)
    pygame.mixer.music.play(-1)

class Block():

    def __init__(self, x, y, name, image):
        self.x = x
        self.y = y
        self.name = name
        self.image = image

    def land(self):
        Sound.hitSound.play()
        game.money-=game.building.blockPrice
        game.updateMoneyTextboxes()
        highest = game.building.height
        for i in game.building.blocks:
            if i.x == self.x:
                highest = min(i.y, highest)
        self.y = highest - 1
        game.building.blocks.append(self)
        game.building.grid[self.y][self.x]=self
        game.building.newBlock(self.x)
        print(game.building.grid)

    def draw(self):
        game_display.blit(self.image, (self.x*gridSize+topLeft[0], self.y*gridSize+topLeft[1]))

class Game():

    wind_image = loadImage("characters/mrwind.png", resolution[1])
    rain_image = loadImage("characters/prec.png", resolution[1])
    design_image=loadImage("characters/designer.png", resolution[1])

    wind_quotes = [
        ("Looks good!", 6,8),
        ("Too much wind!", 3,5),
        ("This is really bad.", 2,4),
        ("Uh...", -1,5),
        ("Okay...", 3,7),
        ("Doesn't handle wind very well.", 3,6),
        ("Good wind protection.", 7,10),
        ("This is good.", 7,9),
    ]
    rain_quotes = [
        ("Precipitation check clear!", 9,10),
        ("Subpar :(", 2,5),
        ("Okay moisture level.", 5,7),
        ("Too much rain!", 3,5),
        ("Could not handle a light drizzle!", 2,4),
        ("You forgot the roof...", -1,4),
        ("I'm drowning!", 0,4),
        ("Oh no...", 1,5),
        ("Decent", 6,8),
        ("Good waterproofing.", 8,10),
        ("Could withstand a moonsoon!", 9,10),
        ("This is a house not a swimming pool", 2,4),
    ]
    design_quotes = [
        ("This line of work is not for you.", 0,4),
        ("Is this even a building?", -1,4),
        ("A tremendous waste of resources.", 0,5.5),
        ("Awful.", 1,5),
        ("Not connected enough!", 2,4),
        ("Cheaply constructed.", 3,6),
        ("Could use improvements.", 4,7),
        ("At least you tried… ", 4,6),
        ("Not quite my taste.", 3,6),
        ("Good design.", 7,8),
        ("You have keen eyes.", 7,8),
        ("More colour, more everything.", 6.5,7),
        ("Excellent connections.", 8,9),
        ("Competent craftsmanship.", 7,8),
        ("Wonderfully innovative.", 8.5,10),
        ("A masterclass in interior design!", 9.3,9.7),
        ("Can I buy it?", 9.5,10),

    ]

    def __init__(self):
        self.money = 100
        self.mode = ""
        self.review_stage = 0
        self.baskets = 0
        self.bucketPrice = 100
        self.building = None

    def start(self):
        self.building = House(random.randint(6,10), random.randint(6,9), baskets=self.baskets)

    def updateMoneyTextboxes(self):
        menu_textbox.html_text="Yo though <br>$"+str(game.money)
        menu_textbox.rebuild()
        build_textbox.html_text="Yo though <br>$"+str(game.money)
        build_textbox.rebuild()
        shop_textbox.html_text="Yo though <br>$"+str(game.money)
        shop_textbox.rebuild()

    def speak(self, quotes, rating):
        available = [quote[0] for quote in quotes if (quote[1]<rating*10 and rating*10<=quote[2])]
        print("i can say ",len(available))
        return " ".join(random.sample(available, random.randint(1,random.randint(1,len(available)))))

    def draw(self):
        if self.building:
            self.building.draw()
        if self.mode=="r":
            image = [self.wind_image, self.rain_image, self.design_image][self.review_stage]
            game_display.blit(image, (resolution[0]-(resolution[1]*3)//4, topLeft[1]))

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
        for i in self.blockNames:
            image = loadImage(self.pathName+"/"+i+".png", gridSize)
            self.images[i] = image
        self.newBlock(starter=True)

    def newBlock(self, x=3, starter=False):
        if starter:
            name = random.choice(self.starters)
        else:
            name = random.choices(self.blockNames, weights = self.blockWeights, k = 1)[0]
        img = self.images[name]
        self.flyingBlock = Block(x,-1, name, img)



    def draw(self):
        for i in range(self.height+1):
            pygame.draw.line(game_display, (200,200,200), (topLeft[0],topLeft[1]+gridSize*i), (topLeft[0]+self.width*gridSize, topLeft[1]+gridSize*i), 1)
        for i in range(self.width+1):
            pygame.draw.line(game_display, (200,200,200), (topLeft[0]+gridSize*i,topLeft[1]), (topLeft[0]+gridSize*i, topLeft[1]+self.height*gridSize), 1)
        if self.flyingBlock:
            self.flyingBlock.draw()
        for block in self.blocks:
            block.draw()
        if(game.mode=="b"):
            for i in range(len(self.holdings)):
                d = gridSize//4
                pygame.draw.rect(game_display, (100,100,100), (topLeft[0]+(self.width+1+2*i)*gridSize-d, topLeft[1]-d, 2*d+gridSize,2*d+gridSize), 0)
                if not self.holdings[i] == None:
                    self.holdings[i].draw()

class House(Building):
    blockPrice = 1
    pathName="house"
    starters = ["wall","leftwall","rightwall","door1"]
    blockNames = ["wall","leftwall","rightwall","window","door0","door1","leftroof","rightroof","roof","plateau"]
    blockWeights = [2,1,1,1,0.8,0.8,1,1,2,1]

    def __init__(self, w,h, baskets=0):
        super(House, self).__init__(w,h,baskets)

    def rate(self):

        # WIND RATING
        wind_rating = 0
        wind_total = 0
        for x in range(self.width):
            for y in range(len(self.grid)):
                if self.grid[y][x]:
                    if x==0 or not self.grid[y][x-1]:
                        if (self.grid[y][x].name in ["leftwall","leftroof"]):
                            wind_rating+=1
                        elif self.grid[y][x].name in ["roof","rightroof"]:
                            wind_rating+=0.5
                        else:
                            pass
                        wind_total+=1
                    if x==self.width-1 or not self.grid[y][x+1]:
                        if (self.grid[y][x].name in ["rightwall","rightroof"]):
                            wind_rating+=1
                        elif self.grid[y][x].name in ["roof","leftroof"]:
                            wind_rating+=0.5
                        else:
                            pass
                        wind_total+=1
        self.wind_rating=0.5
        if wind_total>0:
            self.wind_rating = wind_rating/wind_total
        print(self.wind_rating)

        # PRECIPATION RATING
        rain_rating = 0
        rain_total = 0
        for x in range(self.width):
            for y in range(self.height):
                if(self.grid[y][x]==None):
                    continue
                if(self.grid[y][x].name in ["roof","plateau"]):
                    rain_rating+=1
                elif self.grid[y][x].name=="rightroof":
                    if x<self.width-1 and self.grid[y][x+1]:
                        rain_rating+=0.5
                    else:
                        rain_rating+=1
                elif self.grid[y][x].name=="leftroof":
                    if x>0 and self.grid[y][x-1]:
                        rain_rating+=0.5
                    else:
                        rain_rating+=1
                rain_total+=1
                break
                    
        self.rain_rating=0.5
        if rain_total>0:
            self.rain_rating = rain_rating/rain_total
        print(self.rain_rating)

        # DESIGNER RATING
        def cccf(bad=[],okay=[],good=[],fallback=1): #createCheckConnectionFunction
            def checkConnection(block):
                if(block==None):
                    blockType="air"
                else:
                    blockType=block.name
                if blockType in good:
                    return 1
                elif blockType in okay:
                    return 0.5
                elif blockType in bad:
                    return 0
                else:
                    return fallback
            return checkConnection
        
        roofDown=cccf(bad=["door1","air","leftroof","rightroof"])
        roofRight=cccf(good=["rightroof","roof","air"],fallback=0.5)
        wallRight=cccf(bad=["leftroof","leftwall"],okay=["roof","rightroof"])
        wallDown=cccf(bad=["door1","leftroof","rightroof","leftwall","rightwall"])
        leftwallDown=cccf(good=["air","leftwall","plateau","roof"],fallback=0)
        rightwallDown=cccf(good=["air","rightwall","plateau","roof"],fallback=0)
        rightRight=cccf(good=["leftwall","leftroof","air"],fallback=0)
        windowDown=cccf(bad=["door1","leftroof","rightroof","leftwall","rightwall"],okay=["air"])
        doorheadDown=cccf(good=["door1"],okay=["air","plateau"],fallback=0)
        doorDown=cccf(good=["door1","air","plateau"],okay=["roof"],fallback=0)
        connectionHash={
            "wall":[wallRight, wallDown], # Tile: [Right, Down] 
            "leftwall":[wallRight, leftwallDown],
            "rightwall":[rightRight,rightwallDown],
            "window":[wallRight,windowDown],
            "door0":[wallRight,doorheadDown],
            "door1":[wallRight,doorDown],
            "leftroof":[roofRight,roofDown],
            "rightroof":[rightRight,roofDown],
            "roof":[roofRight,roofDown],
            "plateau":[wallRight,wallDown],
        }
        design_total=0
        design_rating=0
        for x in range(self.width-1):
            for y in range(self.height):
                if(self.grid[y][x]):
                    if(y==self.height-1):
                        down=None
                    else:
                        down=self.grid[y+1][x]
                    design_rating+=connectionHash[self.grid[y][x].name][1](down)
                    design_total+=1

                    right=self.grid[y][x+1]
                    if(right):
                        design_rating+=connectionHash[self.grid[y][x].name][0](right)
                        design_total+=1
        self.design_rating=0.8
        if design_total>0:
            self.design_rating = design_rating/design_total
        self.design_rating=self.design_rating**4   
        print(self.design_rating)
        self.price=int((10**(self.design_rating*self.rain_rating*self.wind_rating)-difficulty)*len(self.blocks))
        print("$"+str(self.price))
class Castle(Building):
    blockPrice = 2
    pathName="castle"
    starters = ["wall","door1"]
    blockNames = ["wall","door0","door1","roofwall","roof","window"]
    blockWeights = [2,0.8,0.8,0.5,2,1]

    def __init__(self, w,h, baskets=0):
        super(Castle, self).__init__(w,h,baskets)

    def rate(self):

        # WIND RATING
        wind_rating = 0
        wind_total = 0
        for x in range(self.width):
            for y in range(len(self.grid)):
                if self.grid[y][x]:
                    if x==0 or not self.grid[y][x-1]:
                        if (self.grid[y][x].name in ["door1","door0"]):
                            pass
                        elif self.grid[y][x].name in []:
                            wind_rating+=0.5
                        else:
                            wind_rating+=1
                        wind_total+=1
                    if x==self.width-1 or not self.grid[y][x+1]:
                        if (self.grid[y][x].name in ["door1","door0"]):
                            pass
                        elif self.grid[y][x].name in []:
                            wind_rating+=0.5
                        else:
                            wind_rating+=1
                        wind_total+=1
        self.wind_rating=0.5
        if wind_total>0:
            self.wind_rating = wind_rating/wind_total
        print(self.wind_rating)

        # PRECIPATION RATING
        rain_rating = 0
        rain_total = 0
        for x in range(self.width):
            for y in range(self.height):
                if(self.grid[y][x]==None):
                    continue
                if(self.grid[y][x].name in ["roof"]):
                    rain_rating+=1
                rain_total+=1
                break
                    
        self.rain_rating=0.5
        if rain_total>0:
            self.rain_rating = rain_rating/rain_total
        print(self.rain_rating)

        # DESIGNER RATING
        def cccf(bad=[],okay=[],good=[],fallback=1): #createCheckConnectionFunction
            def checkConnection(block):
                if(block==None):
                    blockType="air"
                else:
                    blockType=block.name
                if blockType in good:
                    return 1
                elif blockType in okay:
                    return 0.5
                elif blockType in bad:
                    return 0
                else:
                    return fallback
            return checkConnection
        
        roofRight=cccf(good=["roofwall","roof","air"],okay=["wall","window"],fallback=0)
        roofwallRight=cccf(good=["roofwall","roof"],okay=["air"],fallback=0)
        roofDown=cccf(bad=["door1","roof","air"])
        windowDown=cccf(bad=["door1","roof"],okay=["air"])
        wallRight=cccf(bad=["wallroof"],okay=["roof"])
        wallDown=cccf(bad=["door1","roof"])

        doorheadRight=cccf(good=["door0","air","window","wall"],fallback=0)
        doorRight=cccf(good=["door1","air","window","wall"],fallback=0)
        doorheadDown=cccf(good=["door1"],okay=["air"],fallback=0)
        doorDown=cccf(good=["door1","air"],fallback=0)
        connectionHash={
            "wall":[wallRight, wallDown], # Tile: [Right, Down]
            "window":[wallRight,windowDown],
            "door0":[doorheadRight,doorheadDown],
            "door1":[doorRight,doorDown],
            "roofwall":[roofwallRight,windowDown],
            "roof":[roofRight,windowDown],
        }
        design_total=0
        design_rating=0
        for x in range(self.width-1):
            for y in range(self.height):
                if(self.grid[y][x]):
                    if(y==self.height-1):
                        down=None
                    else:
                        down=self.grid[y+1][x]
                    design_rating+=connectionHash[self.grid[y][x].name][1](down)
                    design_total+=1

                    right=self.grid[y][x+1]
                    if(right):
                        design_rating+=connectionHash[self.grid[y][x].name][0](right)
                        design_total+=1
        self.design_rating=0.8
        if design_total>0:
            self.design_rating = design_rating/design_total
        self.design_rating=self.design_rating**4   
        print(self.design_rating)
        self.price=int((10**(self.design_rating*self.rain_rating*self.wind_rating)-difficulty)*len(self.blocks))
        print("$"+str(self.price))



# Main Menu
menu_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((20, 25), (200, 75)),html_text="Yo though <br>$100",manager=managers[""])
build_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (200, 50)),text='Build Buildings',manager=managers[""])
shop_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 350), (200, 50)),text='Buy Baskets',manager=managers[""])
exit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 425), (200, 50)),text='Bye Bye',manager=managers[""])

back_buttons = [
    pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 50), (100, 50)),text='Back',manager=managers["s"]),
]

# Building
build_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((700, 125), (200, 75)),html_text="Yo though <br>$100",manager=managers["b"])
done_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((720, 305), (400, 300)),text='Is good now',manager=managers["b"])

# Shop
shop_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((200, 125), (200, 75)),html_text="Yo though <br>$100",manager=managers["s"])
basket_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (200, 50)),text='Buy Bucket ($100)',manager=managers["s"])

# Review
review_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((700, 25), (300, 175)),html_text="This house is horrendous! I can barely accept this work.",manager=managers["r"])
rating_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((720, 305), (100, 50)),html_text="huh",manager=managers["r"])
ok_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((650, 450), (200, 100)),text='You recieved $X money.',manager=managers["r"])

# Payment
payment_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((resolution[0]//4, resolution[1]//4), (resolution[0]//2, resolution[1]//2)),text='You recieved $X money.',manager=managers["p"])

game = Game()

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
                        Sound.lickSound.play()
                        game.building.flyingBlock.x+=1
                if event.key == pygame.K_LEFT:
                    if game.building.flyingBlock.x>0:
                        Sound.lickSound.play()
                        game.building.flyingBlock.x-=1
                if event.key == pygame.K_DOWN:
                    if game.money>=1 and not game.building.grid[0][game.building.flyingBlock.x]: #blockPrice
                        game.building.flyingBlock.land()
                for i in range(len(game.building.holdings)):
                    if event.key == getattr(pygame,"K_"+str(i+1)):
                        Sound.lickSound.play()
                        if game.building.holdings[i]:
                            game.building.holdings[i].x, game.building.holdings[i].y = (game.building.flyingBlock.x, game.building.flyingBlock.y)
                        game.building.flyingBlock.x, game.building.flyingBlock.y = (game.building.width+1+2*i, 0)
                        game.building.holdings[i], game.building.flyingBlock = (game.building.flyingBlock, game.building.holdings[i])
                        if game.building.flyingBlock == None:
                            game.building.newBlock()
                
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                
                Sound.hitSound.play()
                #buttons
                if event.ui_element in back_buttons:
                    game.mode=""
                if event.ui_element == shop_button:
                    game.mode="s"
                if event.ui_element == exit_button:
                    jump_out = True
                if event.ui_element == build_button:
                    if game.money:
                        game.mode="b"
                        game.start()
                if event.ui_element == done_button:
                    game.building.flyingBlock=None
                    game.building.rate()
                    payment_button.text="Recieve $"+str(game.building.price)+"!"
                    payment_button.rebuild()
                    game.money+=game.building.price
                    game.mode = "r"
                    game.review_stage = 0
                    ok_button.text="OK"
                    ok_button.rebuild()
                    review_textbox.html_text=game.speak(game.wind_quotes, game.building.wind_rating)
                    review_textbox.rebuild()
                    rating_textbox.html_text=outOfTen(game.building.wind_rating)
                    rating_textbox.rebuild()

                if event.ui_element == payment_button:
                    game.mode=""
                    game.updateMoneyTextboxes()
                if event.ui_element == ok_button:
                    if game.review_stage==2:
                        game.mode="p"
                        game.building=None
                    else:
                        game.review_stage+=1
                        if game.review_stage==1:
                            rating = game.building.rain_rating
                            quotes = game.rain_quotes
                        else:
                            rating = game.building.design_rating
                            quotes = game.design_quotes
                        review_textbox.html_text=game.speak(quotes, rating)
                        review_textbox.rebuild()
                        rating_textbox.html_text=outOfTen(rating)
                        rating_textbox.rebuild()
                if event.ui_element == basket_button:
                    if game.money>=game.bucketPrice:
                        game.money-=game.bucketPrice
                        game.bucketPrice+=100
                        game.baskets += 1
                    basket_button.text='Buy Bucket ($'+str(game.bucketPrice)+')'
                    basket_button.rebuild()
                    game.updateMoneyTextboxes()
        manager.process_events(event)

    manager.update(time_delta)



    game_display.fill((100,100,200))
    manager.draw_ui(game_display)
    
    game.draw()

    pygame.display.flip()


pygame.quit()
quit()
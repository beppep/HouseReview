import pygame
import pygame_gui
import random
import math # for prod lmao

resolution = (1300,700)
gridSize = 64
topLeft = (20,20+gridSize)
difficulty= 1 # 0-1 but can go to 9 (even above with ads?)
rating_decimals = 0

pygame.init()
clock = pygame.time.Clock()
game_display = pygame.display.set_mode(resolution)#, pygame.FULLSCREEN)
pygame.display.set_caption('House Review!')
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

def outOfTen(rating, outOfWhat=10):
    rating = round(rating*outOfWhat,rating_decimals)
    if rating == int(rating):
        rating = int(rating)
    return str(rating)+"/"+str(outOfWhat)

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
        #print(game.building.grid)

    def draw(self):
        game_display.blit(self.image, (self.x*gridSize+topLeft[0], self.y*gridSize+topLeft[1]))

class Game():

    rater_images = {
        "wind":[loadImage("characters/mrwind.png", resolution[1]),loadImage("characters/wind2.png", resolution[1])],
        "rain":loadImage("characters/prec.png", resolution[1]),
        "design":loadImage("characters/designer.png", resolution[1]),
        "dice":loadImage("characters/dicer.png", resolution[1]),
    }

    rater_quotes = {
        "wind":[
            ("Looks good!", 6,9),
            ("Too much wind!", 1,5),
            ("This is really bad.", 0,4),
            ("Uh...", 0,5),
            ("Okay...", 3,7),
            ("Doesn't handle wind very well.", 3,6),
            ("Good wind protection.", 7,10),
            ("This is good.", 7,10),
            ("No walls!?", 0,3),
        ],
        "rain":[
            ("Precipitation check clear!", 9,10),
            ("Subpar :(", 2,5),
            ("Okay moisture level.", 5,7),
            ("Too much rain!", 3,5),
            ("Could not handle a light drizzle!", 1,4),
            ("You forgot the roof...", 0,4),
            ("I'm drowning!", 0,4),
            ("Oh no...", 1,5),
            ("Decent", 6,8),
            ("Good waterproofing.", 8,10),
            ("Could withstand a moonsoon!", 9,10),
            ("This is a house not a swimming pool", 0,4),
        ],
        "design":[
            ("This line of work is not for you.", 1,4),
            ("Is this even a building?", 0,4),
            ("A tremendous waste of resources.", 1,4.5),
            ("Awful.", 1,5),
            ("Not connected enough!", 2,4),
            ("Cheaply constructed.", 3,6),
            ("Could use improvements.", 4,7),
            ("At least you tried… ", 2,5),
            ("Not quite my taste.", 5,8),
            ("Good design.", 6,9.5),
            ("You have keen eyes.", 7,9),
            ("More colour, more everything.", 6,7),
            ("Excellent connections.", 7,9),
            ("Competent craftsmanship.", 6,8),
            ("Wonderfully innovative.", 8.5,10),
            ("A masterclass in interior design!", 9.3,10),
            ("Can I buy it?", 9.5,10),
        ],
        "dice":[
            ("Lmao.", 1,6),
            ("I dont know what im doing.", 1,6),
            ("I dont care.", 1,6),
            ("Not my problem.", 1,2),
            ("Its your lucky day.", 5,6),
            ("Whoops...", 1,3),
            ("I didnt even look at the house lol.", 1,6),
            ("haha...", 1,6),
            ("I dont want this job.",1,6),
            ("Im just gonna roll a die.",1,6),
        ]
    }

    def __init__(self):
        self.money = 69
        self.mode = ""
        self.review_stage = 0
        self.baskets = 0
        self.bucketPrice = 100
        self.building = None
        self.ads = 0

    def start(self, buildingType):
        self.building = buildingType(random.randint(6,10), random.randint(6,9), baskets=self.baskets)

    def start_rating(self):
        self.building.flyingBlock=None
        self.building.rate()
        self.current_rater_images = []
        #select rater images
        for i in self.building.raters:
            image = self.rater_images[i]
            if type(image)==list:
                image = random.choice(image)
            self.current_rater_images.append(image)
        self.mode = "r"
        self.review_stage = 0
        self.show_rating()
        ok_button.text="OK"
        ok_button.rebuild()

    def ok_rating(self): # when ok pressed on rating screen
        if self.review_stage==2:
            self.mode="p"
            payment_button.text="Recieve $"+str(self.building.price)+"!"
            payment_button.rebuild()
            game.money+=game.building.price
            game.building = None
        else:
            self.review_stage+=1
            self.show_rating()

    def show_rating(self):
        rating = self.building.ratings[self.review_stage]
        rating_max = self.building.ratings_max[self.review_stage]
        quotes = self.rater_quotes[self.building.raters[self.review_stage]]
        review_textbox.html_text=game.speak(quotes, rating, rating_max)
        review_textbox.rebuild()
        rating_textbox.html_text=outOfTen(rating, outOfWhat=rating_max)
        rating_textbox.rebuild()

    def updateMoneyTextboxes(self):
        menu_textbox.html_text="Yo though <br>$"+str(game.money)
        menu_textbox.rebuild()
        build_textbox.html_text="Yo though <br>$"+str(game.money)
        build_textbox.rebuild()
        shop_textbox.html_text="Yo though <br>$"+str(game.money)
        shop_textbox.rebuild()

    def speak(self, quotes, rating, rating_max):
        available = [quote[0] for quote in quotes if (quote[1]<=rating*rating_max<=quote[2])]
        print("i can say ",len(available))
        return " ".join(random.sample(available, random.randint(1,random.randint(1,len(available)))))

    def draw(self):
        if self.building:
            self.building.draw()
        if self.mode=="r":
            image = self.current_rater_images[self.review_stage]
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

    def rate(self):

        # choose raters
        self.raters = []
        self.raters.append("wind")
        self.raters.append("rain")
        self.raters.append("design")
        if random.random()<0.1:
            self.raters[random.randint(0,len(self.raters)-1)] = "dice"

        # rate
        self.ratings = []
        self.ratings_max = []
        for rater in self.raters:
            a,b = getattr(self, "rate_"+rater)()
            self.ratings.append(a)
            self.ratings_max.append(b)

        # calculate price
        self.price=int((10**(math.prod(self.ratings))-difficulty+game.ads)*len(self.blocks))*self.blockPrice
        game.ads = 0
        ads_button.enable()
        print("$"+str(self.price))

    def rate_dice(self):
        return random.randint(1,6)/6, 6

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
    blockNames = ["wall","leftwall","rightwall","window","door0","door1","leftroof","rightroof","roof"]
    blockWeights = [2,1,1,1,0.8,0.8,1,1,2]

    def __init__(self, w,h, baskets=0):
        super(House, self).__init__(w,h,baskets)

    def rate_wind(self):
        wind_rating = 0
        wind_total = 0
        for x in range(self.width):
            for y in range(len(self.grid)):
                if self.grid[y][x]:
                    if x==0 or not self.grid[y][x-1]:
                        if (self.grid[y][x].name in ["leftwall","leftroof"]):
                            wind_rating+=1
                        elif self.grid[y][x].name in ["roofwindow","roof","rightroof"]:
                            wind_rating+=0.5
                        else:
                            pass
                        wind_total+=1
                    if x==self.width-1 or not self.grid[y][x+1]:
                        if (self.grid[y][x].name in ["rightwall","rightroof"]):
                            wind_rating+=1
                        elif self.grid[y][x].name in ["roofwindow","roof","leftroof"]:
                            wind_rating+=0.5
                        else:
                            pass
                        wind_total+=1
        return wind_rating/wind_total, 10

    def rate_rain(self):
        rain_rating = 0
        rain_total = 0
        for x in range(self.width):
            for y in range(self.height):
                if(self.grid[y][x]==None):
                    continue
                if(self.grid[y][x].name in ["roof","roofwindow","plateau"]):
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
                    
        return rain_rating/rain_total, 10

    def rate_design(self):
        def cccf(bad=[],okay=[],good=[],fallback=1): #createCheckConnectionFunction
            def checkConnection(block):
                if(block==None):
                    blockType="air"
                else:
                    blockType=block.name
                    if blockType == "roofwindow":
                        blockType = "roof"
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
            "roofwindow":[roofRight,roofDown],
            "plateau":[wallRight,wallDown],
        }
        design_total=0
        design_rating=0
        for x in range(self.width):
            for y in range(self.height):
                if(self.grid[y][x]):
                    if(y==self.height-1):
                        down=None
                    else:
                        down=self.grid[y+1][x]
                    design_rating+=connectionHash[self.grid[y][x].name][1](down)
                    design_total+=1

                    if(x==self.width-1):
                        right=None
                    else:
                        right=self.grid[y][x+1]
                    design_rating+=connectionHash[self.grid[y][x].name][0](right)
                    design_total+=1
        design_rating = design_rating/design_total
        return design_rating**4, 10+random.randint(-1,1)*(random.random()<0.5)
class Castle(Building):
    blockPrice = 2
    pathName="castle"
    starters = ["wall","door1","leftwall","rightwall"]
    blockNames = ["wall","leftwall","rightwall","door0","door1","roofwall","window","roof"]
    blockWeights = [2,1,1,0.8,0.8,1,1,2]

    def __init__(self, w,h, baskets=0):
        super(Castle, self).__init__(w,h,baskets)

    def rate_wind(self):
        wind_rating = 0
        wind_total = 0
        for x in range(self.width):
            for y in range(len(self.grid)):
                if self.grid[y][x]:
                    if x==0 or not self.grid[y][x-1]:
                        if (self.grid[y][x].name in ["leftwall","roof","flag"]):
                            wind_rating+=1
                        elif self.grid[y][x].name in ["door0","door1"]:
                            pass
                        else:
                            wind_rating+=0.5
                        wind_total+=1
                    if x==self.width-1 or not self.grid[y][x+1]:
                        if (self.grid[y][x].name in ["rightwall","roof","flag"]):
                            wind_rating+=1
                        elif self.grid[y][x].name in ["door1","door0"]:
                            pass
                        else:
                            wind_rating+=0.5
                        wind_total+=1
        return wind_rating/wind_total, 10

    def rate_rain(self):
        rain_rating = 0
        rain_total = 0
        for x in range(self.width):
            for y in range(self.height):
                if(self.grid[y][x]==None):
                    continue
                if(self.grid[y][x].name in ["roof","flag"]):
                    rain_rating+=1
                rain_total+=1
                break
                    
        return rain_rating/rain_total, 10

    def rate_design(self):
        def cccf(bad=[],okay=[],good=[],fallback=1): #createCheckConnectionFunction
            def checkConnection(block):
                if(block==None):
                    blockType="air"
                else:
                    blockType=block.name
                    if blockType == "flag":
                        blockType = "roof"
                if blockType in good:
                    return 1
                elif blockType in okay:
                    return 0.5
                elif blockType in bad:
                    return 0
                else:
                    return fallback
            return checkConnection
        
        roofRight=cccf(good=["roofwall","roof","air","leftwall"],okay=["wall","window","rightwall"],fallback=0)
        roofwallRight=cccf(good=["roofwall","roof","air"],okay=["wall","window","rightwall"],fallback=0)
        roofDown=cccf(bad=["door1","roof"],okay=["air"])
        windowDown=cccf(bad=["door1","roof"],okay=["air","leftwall","rightwall"])
        wallRight=cccf(okay=["roof","roofwall","leftwall","air"])
        wallDown=cccf(bad=["door1","roof"],okay=["leftwall","rightwall"])
        rightwallDown=cccf(good=["rightwall","air"],okay=["wall","dindow","door0"],fallback=0)
        leftwallDown=cccf(good=["leftwall","air"],okay=["wall","dindow","door0"],fallback=0)

        doorheadRight=cccf(good=["door0","air","window","wall","wallright"],okay=["roofwall"],fallback=0)
        doorRight=cccf(good=["door1","air","window","wall","wallright"],okay=["roofwall"],fallback=0)
        doorheadDown=cccf(good=["door1"],okay=["air"],fallback=0)
        doorDown=cccf(good=["door1","air"],fallback=0)
        connectionHash={
            "wall":[wallRight, wallDown], # Tile: [Right, Down]
            "rightwall":[roofRight, rightwallDown],
            "leftwall":[wallRight, leftwallDown],
            "window":[wallRight,windowDown],
            "door0":[doorheadRight,doorheadDown],
            "door1":[doorRight,doorDown],
            "roofwall":[roofwallRight,roofDown],
            "roof":[roofRight,roofDown],
            "flag":[roofRight,roofDown],
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

                    if(x==self.width-1):
                        right=None
                    else:
                        right=self.grid[y][x+1]
                    design_rating+=connectionHash[self.grid[y][x].name][0](right)
                    design_total+=1
        design_rating = design_rating/design_total
        return design_rating**4, 10+random.randint(-1,1)*(random.random()<0.5)



# Main Menu
menu_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((20, 25), (200, 75)),html_text="Yo though <br>$69",manager=managers[""])
difficulty_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((1000, 125), (200, 50)),html_text=str(int(100*difficulty))+'% difficulty.',manager=managers[""])
difficulty_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((1000, 200), (200, 50)),start_value=100, value_range=(0,100), manager=managers[""])
difficulty_slider.enable_arrow_buttons=0
build_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (200, 50)),text='Build Buildings ('+str(House.blockPrice)+"$)",manager=managers[""])
castle_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((575, 275), (200, 50)),text='Build Castle ('+str(Castle.blockPrice)+"$)",manager=managers[""]) # new manager?
castle_button.disable()
shop_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 350), (200, 50)),text='Buy Things',manager=managers[""])
exit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 425), (200, 50)),text='Bye Bye',manager=managers[""])

back_buttons = [
    pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 50), (100, 50)),text='Back',manager=managers["s"]),
]

# Building
build_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((720, 200), (200, 75)),html_text="Yo though <br>$69",manager=managers["b"])
done_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((720, 300), (400, 300)),text='Is good now',manager=managers["b"])

# Shop
shop_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((200, 125), (200, 75)),html_text="Yo though <br>$69",manager=managers["s"])
basket_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((125, 275), (200, 50)),text='Buy Bucket ($100)',manager=managers["s"])
plateau_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 350), (200, 50)),text='Platform Tiles ($30)',manager=managers["s"])
roofwindow_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 425), (200, 50)),text='Roof Window Tiles ($10)',manager=managers["s"])
unlock_castle_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((575, 275), (200, 50)),text='Unlock Castles ($30)',manager=managers["s"])
flag_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((575, 350), (200, 50)),text='Flag Tiles ($30)',manager=managers["s"])
lottery_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((125, 350), (200, 50)),text='Lottery Ticket ($2)',manager=managers["s"])
ads_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((125, 425), (200, 50)),text='Advertisement ($10)',manager=managers["s"])

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
                if event.key in [pygame.K_RIGHT, pygame.K_d]:
                    if game.building.flyingBlock.x<game.building.width-1:
                        Sound.lickSound.play()
                        game.building.flyingBlock.x+=1
                if event.key in [pygame.K_LEFT, pygame.K_a]:
                    if game.building.flyingBlock.x>0:
                        Sound.lickSound.play()
                        game.building.flyingBlock.x-=1
                if event.key in [pygame.K_DOWN, pygame.K_s, pygame.K_SPACE]:
                    if game.money>=game.building.blockPrice and not game.building.grid[0][game.building.flyingBlock.x]:
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
            if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                difficulty = event.value/100
                difficulty_textbox.html_text=str(event.value)+'% difficulty.'
                difficulty_textbox.rebuild()

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
                    if game.money>=House.blockPrice:
                        game.mode="b"
                        game.start(House)
                if event.ui_element == castle_button:
                    if game.money>=Castle.blockPrice:
                        game.mode="b"
                        game.start(Castle)
                if event.ui_element == done_button and len(game.building.blocks):
                    game.start_rating()

                if event.ui_element == payment_button:
                    game.mode=""
                    game.updateMoneyTextboxes()
                if event.ui_element == ok_button:
                    game.ok_rating()
                if event.ui_element == basket_button:
                    if game.money>=game.bucketPrice:
                        game.money-=game.bucketPrice
                        game.bucketPrice+=100
                        game.baskets += 1
                        if game.baskets<5:
                            basket_button.text='Buy Bucket ($'+str(game.bucketPrice)+')'
                            basket_button.rebuild()
                            game.updateMoneyTextboxes()
                        else:
                            basket_button.disable()
                            #basket_button.kill()
                if event.ui_element == lottery_button:
                    if game.money>=2:
                        game.money-=2
                        if random.random()<0.01:
                            game.money+=100
                        game.updateMoneyTextboxes()
                if event.ui_element == ads_button:
                    if game.money>=10:
                        game.money-=10
                        game.ads = 1
                        ads_button.disable()
                        game.updateMoneyTextboxes()
                if event.ui_element == plateau_button:
                    if game.money>=30:
                        game.money-=30
                        House.starters.append("plateau")
                        House.blockNames.append("plateau")
                        House.blockWeights.append(1)
                        plateau_button.disable()
                        #plateau_button.kill()
                        game.updateMoneyTextboxes()
                if event.ui_element == roofwindow_button:
                    if game.money>=10:
                        game.money-=10
                        House.blockNames.append("roofwindow")
                        House.blockWeights.append(0.5)
                        roofwindow_button.disable()
                        #roofwindow_button.kill()
                        game.updateMoneyTextboxes()
                if event.ui_element == flag_button:
                    if game.money>=30:
                        game.money-=30
                        Castle.blockNames.append("flag")
                        Castle.blockWeights.append(0.5)
                        flag_button.disable()
                        #flag_button.kill()
                        game.updateMoneyTextboxes()
                if event.ui_element == unlock_castle_button:
                    if game.money>=30:
                        game.money-=30
                        castle_button.enable()
                        unlock_castle_button.disable()
                        #unlock_castle_button.kill()
                        game.updateMoneyTextboxes()
        manager.process_events(event)

    manager.update(time_delta)



    game_display.fill((100,100,200))
    manager.draw_ui(game_display)
    
    game.draw()

    pygame.display.flip()


pygame.quit()
quit()


# 193$ arthur 5 buckets diff 1
# 122$ arthur 0 buckets diff 1
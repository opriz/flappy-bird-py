import pygame
import itertools
from typing import Tuple
import random
from PIL import Image
import sys
import os

class PipeSingle(pygame.sprite.Sprite):
    def __init__(self, shapeType: str, delta: int):
        pygame.sprite.Sprite.__init__(self)

        path = "./resources/images/pipe-green.png" 
        image = pygame.image.load(path).convert_alpha()
        if shapeType == "up" :
            self.image = pygame.transform.rotate(image,180) 
        elif shapeType == "down" :
            self.image = image
        self.rect = self.image.get_rect()

        self._delta = delta

    def reset(self,rect):
        self.rect = rect
       
    def update(self):
        self.rect.left = self.rect.left + self._delta

    def is_out(self,leftBoundary) ->bool:
        if self.rect.right <= leftBoundary:
            return True
        return False

class PipePair:
    PIPE_DELTA = -3

    def __init__(self,pipeGroup,gapSize,startLeft,yRange,leftBoundary):
        self._pipeUp = PipeSingle("up",self.PIPE_DELTA)
        self._pipeDown = PipeSingle("down",self.PIPE_DELTA)
        pipeGroup.add(self._pipeUp,self._pipeDown)

        self._gapSize = gapSize
        self._start = startLeft
        self._yRange = yRange
        self._leftBoundary = leftBoundary
        self.isCounted = False

    def init(self,start):
        self.reset(start+self._pipeUp.rect.width)

    def move(self):
        self._pipeUp.update()
        self._pipeDown.update()
        if self._pipeUp.is_out(self._leftBoundary) or self._pipeDown.is_out(self._leftBoundary):
            self.reset(self._start)

    def reset(self,start):
        width = self._pipeUp.rect.width  
        y = random.randint(self._yRange[0],self._yRange[1])

        startLeft = start - width
        newUpButtom = y - self._gapSize//2
        newDownTop = y + self._gapSize//2

        self._pipeUp.rect.left = startLeft
        self._pipeUp.rect.bottom = newUpButtom
        self._pipeDown.rect.left = startLeft
        self._pipeDown.rect.top = newDownTop
        self.isCounted = False
    
    def get_centerx(self):
        return self._pipeUp.rect.left + self._pipeUp.rect.width//2

class Bird(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, v: int, a: int):
        pygame.sprite.Sprite.__init__(self)
        self._init_up_v = -15
        self._v = 0
        self._a = a

        self.images = itertools.cycle((
            pygame.image.load("./resources/images/bluebird-upflap.png").convert(),
            pygame.image.load("./resources/images/bluebird-midflap.png").convert(),
            pygame.image.load("./resources/images/bluebird-downflap.png").convert(),
        ))

        self.image = pygame.image.load("./resources/images/bluebird-upflap.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y


    def up(self):
        self._v = self._init_up_v

    def down(self):
        pass
    
    def update(self):
        self._v = self._v + self._a
        self.rect.top = self.rect.top + self._v

    def get_position(self):
        return self.rect

class BackGround:
    def __init__(self,path):
        self.image = pygame.image.load(path).convert()
        self.rect = self.image.get_rect()

class Score:
    def __init__(self,midpos: int, top: int):
        resources = {
            "0": os.path.join(os.getcwd(),"resources/images/0.png"),
            "1": os.path.join(os.getcwd(),"resources/images/1.png"),
            "2": os.path.join(os.getcwd(),"resources/images/2.png"),
            "3": os.path.join(os.getcwd(),"resources/images/3.png"),
            "4": os.path.join(os.getcwd(),"resources/images/4.png"),
            "5": os.path.join(os.getcwd(),"resources/images/5.png"),
            "6": os.path.join(os.getcwd(),"resources/images/6.png"),
            "7": os.path.join(os.getcwd(),"resources/images/7.png"),
            "8": os.path.join(os.getcwd(),"resources/images/8.png"),
            "9": os.path.join(os.getcwd(),"resources/images/9.png")
        }
        self._numberImages = dict()
        for k,v in resources.items():
            self._numberImages[k] = pygame.image.load(v)

        self._score = 0
        self.images = [self._numberImages['0']]
        self.rects = [self.images[0].get_rect()]
        
        self._top = top
        self._midpos = midpos
        self._width = self.rects[0].width
        self._height = self.rects[0].height

        self.update_image_position()
    
    def add(self):  
        self._score = self._score + 1
        self.update_image_position()
    
    def update_image_position(self):
        left = self._midpos - self._width//2
        numStr = list(str(int(self._score)))
        
        self.images = []
        self.rects = []
        count = len(numStr)
        totalLen = (self._width+self._width//5)*(count-1) + self._width
        left = self._midpos - totalLen//2
        for s in numStr:
            self.images.append(self._numberImages[s])
            self.rects.append(
                pygame.Rect(left,self._top,self._width,self._height)
            )
            left = left + self._width//5 + self._width

class App:
    def __init__(self):
        self._isRunning = True
        self.sounds = dict()
        soundResources = {
                    "dead": os.path.join(os.getcwd(),"resources/audios/die.wav"),
                    "hit" : os.path.join(os.getcwd(),"resources/audios/hit.wav"),
                    "point" : os.path.join(os.getcwd(),"resources/audios/point.wav"),
                    "swoosh" : os.path.join(os.getcwd(),"resources/audios/swoosh.wav"),
                    "wing" : os.path.join(os.getcwd(),"resources/audios/wing.wav"),
                }
        for k,v in soundResources.items() :
            self.sounds[k] = pygame.mixer.Sound(v)

    def init(self):
        backgroundPath = "./resources/images/background-day.png"
        backgroundImage = Image.open(backgroundPath)
        size = (backgroundImage.size[0],backgroundImage.size[1])
        
        self.screen = pygame.display.set_mode(size)
        self.backgroud = BackGround(backgroundPath)
        self._startImage = pygame.image.load("./resources/images/message.png").convert_alpha()
        self._overImage = pygame.image.load("./resources/images/gameover.png").convert_alpha()

        self.bird = Bird(20,50,-2,1.5)

        interval = size[0]//3*2
        self._pipeGroup = pygame.sprite.Group()
        backgroudHeight = self.backgroud.rect.height
        backgroudWidth = self.backgroud.rect.width
        pipePair1 = PipePair(self._pipeGroup,backgroudHeight//3,backgroudWidth//2*3,(backgroudHeight//4,backgroudHeight//4*3),0)
        pipePair2 = PipePair(self._pipeGroup,backgroudHeight//3,backgroudWidth//2*3,(backgroudHeight//4,backgroudHeight//4*3),0)
        pipePair3 = PipePair(self._pipeGroup,backgroudHeight//3,backgroudWidth//2*3,(backgroudHeight//4,backgroudHeight//4*3),0)

        pipePair1.init(backgroudWidth)
        pipePair2.init(backgroudWidth+backgroudWidth//2)
        pipePair3.init(backgroudWidth+backgroudWidth)
        self.pipePairs = [pipePair1,pipePair2,pipePair3]

        self.score = Score(backgroudWidth//2, backgroudHeight//5)

        self.screen.blit(self.backgroud.image,(0,0))
    
    def on_event(self,event):
        if event.type == pygame.QUIT:
            self._isRunning = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.bird.up()
            self.sounds['wing'].play()

    def erase(self):
        self.screen.blit(self.backgroud.image,(0,0))

    def loop(self):
        self.bird.update()
        if self.bird.rect.bottom > self.backgroud.rect.bottom*2 or self.bird.rect.top < -self.backgroud.rect.bottom//2:
            self._isRunning = False
            return

        for pipePair in self.pipePairs:
            pipePair.move()
            if pipePair.get_centerx() <= self.bird.rect.right and not pipePair.isCounted:
                self.sounds['point'].play()
                pipePair.isCounted = True
                self.score.add()
            

        if len(pygame.sprite.spritecollide(self.bird,self._pipeGroup,0))!=0:
            self._isRunning = False
            self.sounds["hit"].play()
            return
        
    def render(self):
        for sprite in self._pipeGroup.sprites():
            self.screen.blit(sprite.image,sprite.rect)

        self.screen.blit(next(self.bird.images),self.bird.get_position())

        for i,image in enumerate(self.score.images) :
            self.screen.blit(image,self.score.rects[i])

        pygame.display.update()

    # 不用显式调用
    # def cleanup(self):
    #     pygame.quit() 

    def run(self): # 包含主循环
        self.screen.blit(self.backgroud.image,(0,0))
        self.screen.blit(self._startImage,(self.backgroud.rect.width//2 - self._startImage.get_rect().width//2,self.backgroud.rect.width//3))

        flag = False
        control = -1
        while True:    
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    flag = True
                    break
            if flag :
                break
            
            control = control*-1 
            self.show_start(control)

        while self._isRunning: 
            events = pygame.event.get() # 时间获取和处理（状态改变条件获取）
            for event in events:
                self.on_event(event)
            self.erase() # 擦除前一个状态
            self.loop() # 状态修改
            self.render() # 新状态渲染
            pygame.time.delay(20)
        self.sounds['dead'].play()

        self.show_over()
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.time.delay(1000)
                    return

    def show_start(self,control):
        self.screen.blit(self.backgroud.image,self.bird.rect,self.bird.rect)
        self.bird.rect.top = self.bird.rect.top + 5*control
        self.screen.blit(self.bird.image,self.bird.rect,self.bird.rect)
        pygame.display.update()

    def show_over(self):
        self.screen.blit(self._overImage,
            (self.backgroud.rect.width//2-self._overImage.get_rect().width//2,self.backgroud.rect.height//3)
        )
        pygame.display.update()

        
if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()

    app = App()
    app.init()
    app.run()

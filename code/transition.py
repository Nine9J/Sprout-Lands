from email import charset
from numpy import place
import pygame
from settings import *
from timer import Timer

class Transition:
    def __init__(self,reset,player):
        # 基础设置
        self.display_surface = pygame.display.get_surface()
        self.reset = reset
        self.player = player

        # overlay image
        self.image = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.color = 255
        self.speed = -2

    def play(self):

        self.color += self.speed
        if self.color < 0:
            self.speed *= -1
            self.color = 0
            self.reset()
        if self.color > 255:
            self.color = 255
            self.player.sleep = False
            self.speed = -2

        self.image.fill((self.color,self.color,self.color))
        self.display_surface.blit(self.image,(0,0),special_flags=pygame.BLEND_RGBA_MULT)

class Info:
    def __init__(self,player,info):
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.info = info
        self.f = pygame.font.Font('../font/ZiTiGuanJiaFangMeng-2.ttf',50)

        self.info_surf = self.f.render(info,True,(255,255,255))
        self.info_rect = self.info_surf.get_rect(midbottom  = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2))
        self.time = 200
    
    def display(self):
        self.time -= 2
        if self.time < 0:
            self.player.info_flag = '0'
            self.time = 250
        self.display_surface.blit(self.info_surf,self.info_rect)

class End:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.background_surf = pygame.image.load('../graphics/ui/Background.png')
        self.background_surf = pygame.transform.scale(self.background_surf,(590,680))
        self.background_rect = self.background_surf.get_rect(midbottom = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2+340))
        self.background_surf.set_colorkey((255,255,255))
        
        self.f = pygame.font.Font('../font/ZiTiGuanJiaFangMeng-2.ttf',30)
        self.file = open('../graphics/ui/text/end.txt','r',encoding='utf-8')
        self.txt = self.file.readlines()
        self.txt_surf = []
        self.txt_rect = []
        height = 30
        
        for index,line in enumerate(self.txt):
            i = index % 19
            self.txt_surf.append(self.f.render(line,True,(0,0,0)))
            self.txt_rect.append(self.txt_surf[index].get_rect(topleft = (SCREEN_WIDTH//2 - 270,SCREEN_HEIGHT//2 - 315 + height*i)))
        self.size = len(self.txt_surf)
        self.page  = self.size // 19 + 1
        self.last = self.size % 19
        self.txt_index = 1

        # timer
        self.timer = Timer(80,self.turn)
        self.turn_index = ''

        self.up_info = self.f.render('按A向上翻页',True,(255,255,255))
        self.down_info = self.f.render('按D向下翻页',True,(255,255,255))
        self.up_rect = self.up_info.get_rect(midbottom = (SCREEN_WIDTH//2 - 190,SCREEN_HEIGHT//2 + 315))
        self.down_rect = self.down_info.get_rect(midbottom = (SCREEN_WIDTH//2 + 190,SCREEN_HEIGHT//2 + 315))

        

    def input(self):
        keys=pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.timer.activate()
            self.turn_index = 'up'
        elif keys[pygame.K_d]:
            self.timer.activate()
            self.turn_index = 'down'
    
    def turn(self):
        if self.turn_index == 'down':
            if self.txt_index < self.page:
                self.txt_index+=1
        elif self.turn_index == 'up':
            if self.txt_index > 1:
                self.txt_index-=1

    def display(self):
        self.display_surface.blit(self.background_surf,self.background_rect)
        if self.txt_index == self.page:
            for i in range((self.txt_index - 1) * 19,(self.txt_index - 1) * 19 + self.last):
                self.display_surface.blit(self.txt_surf[i],self.txt_rect[i])
        else:
            for i in range((self.txt_index - 1) * 19,self.txt_index * 19):
                self.display_surface.blit(self.txt_surf[i],self.txt_rect[i])
        
        self.display_surface.blit(self.up_info,self.up_rect)
        self.display_surface.blit(self.down_info,self.down_rect)
        self.input()
        self.timer.update()
        page = self.f.render('- '+str(self.txt_index)+' -',True,(255,255,255))
        page_rect = page.get_rect(midbottom = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2 + 315))
        self.display_surface.blit(page,page_rect)

        
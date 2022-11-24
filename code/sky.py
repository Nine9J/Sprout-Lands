import operator
import pygame
from settings import *
from support import import_folder
from sprites import Generic
import random

class Drops(Generic):
    def __init__(self,surf,pos,moving,groups,z):
        super().__init__(pos,surf,groups,z)

        self.lifetime = random.randint(400,500)
        self.start_time = pygame.time.get_ticks()

        # moving
        self.moving  = moving
        if self.moving:
            self.pos = pygame.Vector2(self.rect.topleft)
            self.direction = pygame.Vector2(-2,4)
            self.speed = random.randint(200,250)
    
    def update(self,dt):
        # movement
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = (round(self.pos.x),round(self.pos.y))

        # timer
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()


class Rain:
    def __init__(self,all_sprites):
        self.all_sprites = all_sprites
        # 获取雨点图像
        self.drops = import_folder('../graphics/rain/drops/')
        self.floor = import_folder('../graphics/rain/floor/')

        # 获取地图大小
        self.floor_w , self.floor_h = pygame.image.load('../graphics/world/ground.png').get_size()
    
    def create_drops(self):
        Drops(
            surf = random.choice(self.drops),
            pos = (random.randint(0,self.floor_w),random.randint(0,self.floor_h)),
            moving = True,
            groups = self.all_sprites,
            z = LAYERS['rain drops'])

    def create_floor(self):
        Drops(
            surf = random.choice(self.floor),
            pos = (random.randint(0,self.floor_w),random.randint(0,self.floor_h)),
            moving = False,
            groups = self.all_sprites,
            z = LAYERS['rain floor'])
    
    def update(self):
        self.create_drops()
        self.create_floor()

class Sky:
    def __init__(self):
        self.display_surf = pygame.display.get_surface()
        self.full_surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.start_color = [255,255,255]
        self.mid_color = (239,127,156)
        self.end_color = (120,101,155)
        self.daytime = 0

        self.weather_surfs = import_folder('../graphics/ui/weather/')
            
        self.weather = 'daytime'
        self.daytime_index = 0

    def display(self,dt,raining):
        if self.daytime <= 4000:
            self.daytime +=1
        else:
            self.daytime += 1
            # 首先转换成 黄昏 再转换为 晚上
            for index,value in enumerate(self.mid_color):
                if self.start_color[index] > value:
                    self.start_color[index] -= 3*dt
                    self.daytime_index = 1

            if self.start_color[0]<=self.mid_color[0] and self.start_color[1]<=self.mid_color[1] and self.start_color[2]<=self.mid_color[2]:
                self.daytime_index =2
                for index,value in enumerate(self.end_color):
                    if self.start_color[index] > value:
                        self.start_color[index] -= 20*dt

        self.full_surf.fill(self.start_color)
        self.display_surf.blit(self.full_surf,(0,0),special_flags=pygame.BLEND_RGBA_MULT)

        # 根据时间情况更换天气图标
        if self.daytime_index == 0:
            if raining:
                self.display_surf.blit(self.weather_surfs[3],(364,64))
            else:
                self.display_surf.blit(self.weather_surfs[0],(364,64))
        elif self.daytime_index == 1:
            self.display_surf.blit(self.weather_surfs[1],(364,64))
        else:
            self.display_surf.blit(self.weather_surfs[2],(364,64))


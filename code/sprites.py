from random import randint
import pygame
from settings import *

class Generic(pygame.sprite.Sprite):
    def __init__(self , pos , surf , groups , z = LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2 , -self.rect.height * 0.75)

class Interaction(Generic):
    def __init__(self,pos ,size,groups,name):
        surf = pygame.Surface(size)
        super().__init__(pos,surf,groups)
        self.name = name

# 房顶
# 实现进入房间后房顶淡出，走出房间后房顶淡入
class HouseTop(Generic):
    def __init__(self, pos, surf, groups,z,inzone):
        super().__init__(pos, surf, groups,z)
        self.inzone = inzone
        self.image = self.image.convert_alpha()
        self.transparency = 255
    
    def update(self,dt):
        if self.inzone[0]:
            if self.transparency>0:
                self.transparency-=15
                self.image.set_alpha(self.transparency)
        else:
            if self.transparency<255:
                self.transparency+=15
                self.image.set_alpha(self.transparency)
    

class Water(Generic):
    def __init__(self, pos, frames, groups):
        # 激活设置，用于循环更换水的图片
        # animation setup
        self.frames = frames
        self.frame_index = 0

        # sprite setup
        super().__init__(
            pos = pos,
            surf = self.frames[self.frame_index],
            groups = groups,
            z = LAYERS['water']
        )

    def animate(self,dt):
        self.frame_index += 5*dt
        if self.frame_index >= len(self.frames):
            self.frame_index=0
        
        self.image = self.frames[int(self.frame_index)]

    
    def update(self,dt):
        self.animate(dt)

class WildFlower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox  = self.rect.copy().inflate(-20,-self.rect.height * 0.95)

# 粒子效果
class Particle(Generic):
    def __init__(self,pos,surf,groups,z,duration=200):
        super().__init__(pos,surf,groups,z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration

        # white surface
        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface()
        new_surf.set_colorkey((0,0,0))
        self.image = new_surf

    def update(self,dt):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()


class Tree(Generic):
    def __init__(self, pos, surf, groups,name):
        super().__init__(pos, surf, groups)

        # apples
        self.apple_surf = pygame.image.load('../graphics/fruit/apple.png')
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_apple()

    # 创建苹果
    def create_apple(self):
        for pos in self.apple_pos:
            if randint(0,10)<1:
                x = pos[0] + self.rect.left
                y = pos[1] + self.rect.top
                Generic((x,y),self.apple_surf,[self.apple_sprites,self.groups()[0]],LAYERS['fruit'])

    # 在玩家使用axe，并且target_pos触碰到树时调用
    def get_apple(self,package):
        self.package = package
        if self.apple_sprites:
            for apple in self.apple_sprites.sprites():
                Particle(
                    pos = apple.rect.topleft,
                    surf = apple.image,
                    groups = self.groups()[0],
                    z = LAYERS['fruit'])
                self.package['apple']+=1
                apple.kill()
                break
    
    # 在每天结束时删除所有苹果，在一天开始时重新创建苹果
    def remove_apple(self):
        for apple in self.apple_sprites.sprites():
            apple.kill()
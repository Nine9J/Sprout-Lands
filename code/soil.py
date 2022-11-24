import pygame
from settings import *
from pytmx import load_pygame
import random
from sprites import Particle

from support import import_folder, import_folder_dict

class SoilTile(pygame.sprite.Sprite):
    def __init__(self,pos,surf,groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil']

class WaterTile(pygame.sprite.Sprite):
    def __init__(self,pos,surf,groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil water']

class RipenTip(pygame.sprite.Sprite):
    def __init__(self,pos,surf,groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['rain drops']

class Plant(pygame.sprite.Sprite):
    def __init__(self,plant_type,groups,soil,check_watered):
        super().__init__(groups)
        # 基础设置
        self.all_sprites = groups[0]
        self.plant_type = plant_type
        self.frames = import_folder(f'../graphics/fruit/{plant_type}/')
        self.soil = soil

        # 植物生长设置
        self.age = 0
        self.max_age = len(self.frames)  - 1
        self.grow_speed = GROW_SPEED[self.plant_type]
        # 判断是否已经浇水的函数
        self.check_watered = check_watered

        # sprites 设置
        self.image = self.frames[self.age]
        self.y_offset = -12 if self.plant_type == 'corn' else -6
        self.rect = self.image.get_rect(midbottom = self.soil.rect.midbottom + pygame.math.Vector2(0,self.y_offset))
        self.z = LAYERS['ground plant']

        self.havestable = False

        self.ripen_tip = pygame.image.load('../graphics/ui/ripen.png')
        self.ripen_tip.convert_alpha()
        pos = self.soil.rect.midbottom + pygame.math.Vector2(-16,-100)
        self.ripentip = RipenTip(pos,self.ripen_tip,self.all_sprites)
        self.ripentip.image.set_alpha(0)


    # 控制生长速度，如果浇水则生长。否则不生长
    def grow(self):
        # 如果已经浇过水
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed  # 增加生长时间 age，用于改对应的植物图片

            if int(self.age) > 0:
                self.z = LAYERS['main']
                # 如果过了种子阶段，就创建碰撞箱
                self.hitbox = self.rect.copy().inflate(- 26, -self.rect.height * 0.4)
            if self.age >=3:  # 如果已经成熟
                self.havestable = True
                self.age = self.max_age
            
            # 更换照片
            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(midbottom = self.soil.rect.midbottom + pygame.math.Vector2(0,self.y_offset))

    def tip(self):
        if self.havestable:
            self.ripentip.image.set_alpha(255)
                
    
            
class SoilLayer:
    def __init__(self,all_sprites,collision_sprites):
        # sprite group
        self.all_sprites = all_sprites
        self.soil_sprites  = pygame.sprite.Group()
        self.water_sprites  = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()
        self.collision_sprites = collision_sprites

        # graphics
        self.soil_surf  = pygame.image.load('../graphics/soil/o.png')
        self.soil_surfs = import_folder_dict('../graphics/soil/')
        self.soil_water = import_folder('../graphics/soil_water/')
        
        

        self.create_soil_gird()
        self.create_gethit_rect()

    
    # 获取哪一个tile是可以耕种的
    def create_soil_gird(self):
        ground = pygame.image.load('../graphics/world/ground.png')
        # 获取地图的格子数目
        h_tiles = ground.get_width() // TILE_SIZE
        v_tiles = ground.get_height() // TILE_SIZE

        # 获取哪一个tile是可以耕种的
        self.grid  = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        for x,y,_ in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')

    # 创建可耕种区域的rect
    def create_gethit_rect(self):
        self.hit_rects = []
        for row_index , row in enumerate(self.grid):
            for col_index , cell in enumerate(row):
                if 'F' in cell:   # 判断是否有可耕种
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    rect = pygame.Rect(x,y,TILE_SIZE,TILE_SIZE)   # 创建rect
                    self.hit_rects.append(rect)

    # 使用锄头后执行的操作
    def get_hit(self,point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE
                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()

    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for row_index , row in enumerate(self.grid):
            for col_index , cell in enumerate(row):
                if 'X' in cell:
                    # tile option
                    l = 'X' in row[col_index - 1]
                    r = 'X' in row[col_index + 1]
                    t = 'X' in self.grid[row_index - 1][col_index]
                    b = 'X' in self.grid[row_index + 1][col_index]

                    # 根据上下左右是否是耕地而改变当前soil的图片
                    tile_type = 'soil'
                    if not any((l,t,r,b)):tile_type = 'o'
                    if l and not any((t,r,b)):tile_type = 'r'
                    if t and not any((l,r,b)):tile_type = 'b'
                    if r and not any((t,l,b)):tile_type = 'l'
                    if b and not any((t,r,l)):tile_type = 't'
                    if l and t and not any((r,b)):tile_type = 'br'
                    if l and r and not any((t,b)):tile_type = 'lr'
                    if l and b and not any((r,t)):tile_type = 'tr'
                    if t and r and not any((l,b)):tile_type = 'bl'
                    if t and b and not any((r,l)):tile_type = 'tb'
                    if r and b and not any((l,t)):tile_type = 'tl'
                    if all((l,t,r)) and not b:tile_type = 'lrb'
                    if all((l,t,b)) and not r:tile_type = 'tbl'
                    if all((l,r,b)) and not t:tile_type = 'lrt'
                    if all((t,r,b)) and not l:tile_type = 'tbr'
                    if all((l,t,r,b)):tile_type = 'x'

                    SoilTile(pos = (col_index * TILE_SIZE,row_index * TILE_SIZE),
                    surf = self.soil_surfs[tile_type],
                    groups = [self.all_sprites,self.soil_sprites])

    def water(self,target_pos):
        for sprite in self.soil_sprites.sprites():
            if sprite.rect.collidepoint(target_pos):
                # 1.向grid中加入'W'表示该片土地已经别浇过
                x = sprite.rect.x  // TILE_SIZE
                y = sprite.rect.y // TILE_SIZE
                self.grid[y][x].append('W')

                # 2.创建watertile类
                pos  = sprite.rect.topleft
                surf = random.choice(self.soil_water)
                WaterTile(pos,surf,[self.all_sprites,self.water_sprites])

    def remove_water(self):
        # 删除所有 Watertile
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        # 更新 grid
        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')

    # 下雨时将所有soil更新为watered状态
    def water_all(self):
        for sprite in self.soil_sprites.sprites():
            x = sprite.rect.x  // TILE_SIZE
            y = sprite.rect.y // TILE_SIZE

            if 'W' not in self.grid[y][x]:
                self.grid[y][x].append('W')
                pos  = sprite.rect.topleft
                surf = random.choice(self.soil_water)
                WaterTile(pos,surf,[self.all_sprites,self.water_sprites])

    def check_watered(self,pos):
        x = pos[0]  // TILE_SIZE
        y = pos[1] // TILE_SIZE
        cell = self.grid[y][x]
        is_watered = 'W' in cell
        return is_watered

    def plant_seed(self,target_pos,seed,num):
        if seed=='corn' and num['corn']<=0:
            return
        if seed=='tomato' and num['tomato']<=0:
            return
        for sprite in self.soil_sprites.sprites():
            if sprite.rect.collidepoint(target_pos):
                x = sprite.rect.x  // TILE_SIZE
                y = sprite.rect.y // TILE_SIZE

                if 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')
                    # 创建植物类对象
                    Plant(seed,[self.all_sprites,self.plant_sprites,self.collision_sprites],sprite,self.check_watered)
                    num[seed]-=1

    def update_plant(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()
            plant.tip()
            
    def havest(self,target_pos,package,num):
        self.package = package
        if self.plant_sprites:
            for sprite in self.plant_sprites.sprites():
                if sprite.rect.collidepoint(target_pos):
                    if sprite.havestable:
                        self.package[sprite.plant_type] += 1
                        num[sprite.plant_type] +=2
                    else :
                        num[sprite.plant_type] +=1
                    Particle(
                        pos = sprite.rect.topleft,
                        surf = sprite.image,
                        groups = self.all_sprites,
                        z = LAYERS['main']
                        )
                    sprite.ripentip.kill()
                    sprite.kill()
                    self.grid[sprite.rect.centery // TILE_SIZE][sprite.rect.centerx // TILE_SIZE].remove('P')
                    
                    
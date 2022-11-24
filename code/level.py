import random
import pygame
from player import Player
from overlay  import Overlay
from settings import LAYERS, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE
from soil import SoilLayer
from sprites import Generic, HouseTop, Water, WildFlower,Interaction,Tree
from pytmx.util_pygame import load_pygame
from support import import_folder
from sky import Rain,Sky
from transition import Transition,Info,End

class Level:
    def __init__(self):
        # get display surface        
        self.display_surface=pygame.display.get_surface()

        #sprite group
        self.all_sprite=CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        #setup
        self.soil_layer = SoilLayer(self.all_sprite,self.collision_sprites)
        self.trees = pygame.sprite.Group()
        # 地板
        self.floor_pos = []

        self.setup()

        self.overlay = Overlay(self.player)

        # sky
        self.rain = Rain(self.all_sprite)
        self.raining = False

        # 睡觉转换动画
        self.transition = Transition(self.reset,self.player)

        # 天空，白天黑夜转换
        self.sky = Sky()

        self.days = 0

        self.item = [self.player.package['apple'],self.player.package['corn'],self.player.package['tomato']]

        self.infos = {'1':Info(self.player,'兑换钥匙成功!'),'2':Info(self.player,'需要30个苹果,3个小麦,1个番茄兑换钥匙'),'3':End(),'4':Info(self.player,'需要钥匙!')}
        

    def setup(self):
        # 导入 tiled 的 tmx 文件
        tmx_data = load_pygame('../data/map.tmx')

        # 导入 house 房子
        for layer in ['HouseFloor','HouseFurnitureBottom']:
            for x,y,surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x*TILE_SIZE,y*TILE_SIZE),surf,self.all_sprite,LAYERS['house bottom'])
                if layer=='HouseFloor':
                    self.floor_pos.append((x,y))
        
        for layer in ['HouseWalls','HouseFurnitureTop']:
            for x,y,surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x*TILE_SIZE,y*TILE_SIZE),surf,self.all_sprite,LAYERS['main'])


        # 导入 fence 栅栏
        for x,y,surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x*TILE_SIZE,y*TILE_SIZE),surf,[self.all_sprite,self.collision_sprites],LAYERS['main'])

        for x,y,surf in tmx_data.get_layer_by_name('Hint').tiles():
            Generic((x*TILE_SIZE,y*TILE_SIZE),surf,self.all_sprite,LAYERS['hint'])

        # 水
        water_frame  = import_folder('../graphics/water')
        for x,y,surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x*TILE_SIZE,y*TILE_SIZE),water_frame,self.all_sprite)

        #花
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x,obj.y),obj.image,[self.all_sprite,self.collision_sprites])

        #树
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x,obj.y),obj.image,[self.all_sprite,self.collision_sprites,self.trees],obj.name)

        #导入屏障
        for x,y,surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x*TILE_SIZE,y*TILE_SIZE),pygame.Surface((TILE_SIZE,TILE_SIZE)),self.collision_sprites)

        Generic(
            pos = (0,0),
            surf = pygame.image.load('../graphics/world/ground.png').convert_alpha(),
            groups = self.all_sprite,
            z = LAYERS['ground']
            )

        #创建玩家
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player=Player(
                    pos = (obj.x,obj.y),
                    group = self.all_sprite,
                    collision_sprites = self.collision_sprites,
                    interaction = self.interaction_sprites,
                    soil_layer = self.soil_layer,
                    trees = self.trees,
                    floor_pos = self.floor_pos
                    )
                    
            elif obj.name == 'Bed':
                Interaction((obj.x,obj.y),(obj.width,obj.height),self.interaction_sprites,'Bed')
            elif obj.name == 'Trader':
                Interaction((obj.x,obj.y),(obj.width,obj.height),self.interaction_sprites,'Trader')
            elif obj.name == 'Chest':
                Interaction((obj.x,obj.y),(obj.width,obj.height),self.interaction_sprites,'Chest')
            elif obj.name == 'Picture':
                Interaction((obj.x,obj.y),(obj.width,obj.height),self.interaction_sprites,'Picture')
            

        # 导入房顶
        for x,y,surf in tmx_data.get_layer_by_name('HouseTop').tiles():
            HouseTop((x*TILE_SIZE,y*TILE_SIZE),surf,self.all_sprite,LAYERS['house top'],self.player.inzone)

    def reset(self):
        # 下雨机率
        self.raining = random.randint(0,9) > 4
        self.soil_layer.update_plant()
        self.soil_layer.remove_water()
        for tree in self.trees.sprites():
            tree.remove_apple()
            tree.create_apple()
        
        self.sky.start_color = [255,255,255]
        self.sky.daytime = 0
        self.sky.daytime_index = 0
        self.days += 1

    def run(self,dt):
        self.display_surface.fill('black')
        # self.all_sprite.draw(self.display_surface)
        self.all_sprite.custom_draw(self.player)
        self.all_sprite.update(dt)

        #rain
        if self.raining:
            self.rain.update()
            self.soil_layer.water_all()

        # sky
        self.sky.display(dt,self.raining)


        self.overlay.display(self.days,dt,[self.player.package['apple'],self.player.package['corn'],self.player.package['tomato']],self.player.seed_num,self.player.selected_seed)

        if self.player.sleep:
            self.transition.play()

        self.player.set_tradeable()

        if self.player.info_flag!='0':
            self.infos[self.player.info_flag].display()


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()


    def custom_draw(self , player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites() , key = lambda sprite:sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image,offset_rect)

                    # if sprite == player:
                    #     pygame.draw.rect(self.display_surface,'red',offset_rect,5)
                    #     hitbox_rect = player.hitbox.copy()
                    #     hitbox_rect.center = offset_rect.center
                    #     pygame.draw.rect(self.display_surface,'green',hitbox_rect,5)
                   

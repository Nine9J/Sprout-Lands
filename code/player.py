from tkinter import CENTER
import pygame
from settings import LAYERS,PLAYER_TOOL_OFFSET, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite):

    def __init__(self, pos , group , collision_sprites,interaction,soil_layer,trees,floor_pos):
        super().__init__(group)

        self.import_assets()
        self.status = 'down_idle'
        self.frame_index=0

        # general setup
        self.image=self.animations[self.status][self.frame_index]
        self.rect=self.image.get_rect(center=pos)
        self.z = LAYERS['main']

        # movement
        self.direction=pygame.math.Vector2()
        self.pos=pygame.math.Vector2(self.rect.center)
        self.speed=200

        # 碰撞箱
        self.hitbox  = self.rect.copy().inflate((-126,-70))
        self.collision_sprites = collision_sprites

        # timer
        self.timers={
            'tool use':Timer(350,self.use_tool),
            'tool switch' : Timer(200),
            'seed use':Timer(350,self.use_seed),
            'seed switch' : Timer(200)
        }

        # tools
        self.tools=['axe','hoe','water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        # seeds
        self.seeds=['corn','tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        # 背包
        self.package = {
            'apple':0,
            'corn':0,
            'tomato': 0
        }

        # soil
        self.soil_layer = soil_layer

        # trees
        self.trees = trees

        #interaction
        self.interaction_sprites = interaction
        self.sleep = False

        # 是否在房子内
        self.floor_pos = floor_pos
        self.inzone = [False,0]

        # 设置种子数量
        self.seed_num = {'corn':1,'tomato':1}

        # 设置箱子钥匙
        self.chest_key = False

        # 设置是否可交易
        self.tradeable = False

        self.info_flag = '0'

        # 导入字体
        self.f = pygame.font.Font('../font/ZiTiGuanJiaFangMeng-2.ttf',50)

        self.display_surface = pygame.display.get_surface()

        
    def import_assets(self):
        self.animations={'up': [],'down': [],'left': [],'right': [],
						   'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
						   'right_hoe':[],'left_hoe':[],'up_hoe':[],'down_hoe':[],
						   'right_axe':[],'left_axe':[],'up_axe':[],'down_axe':[],
						   'right_water':[],'left_water':[],'up_water':[],'down_water':[]}

        for animation in self.animations.keys():
            full_path='../graphics/character/' + animation
            self.animations[animation]=import_folder(full_path)

    def animate(self,dt):
        self.frame_index += 4*dt
        if self.frame_index>=len(self.animations[self.status]):
            self.frame_index=0
        
        self.image=self.animations[self.status][int(self.frame_index)]

    def input(self):
        keys=pygame.key.get_pressed()

        if not self.timers['tool use'].active and not self.sleep and self.info_flag == '0':
            #directions
            if keys[pygame.K_w]:
                self.direction.y = -1
                self.status='up'
            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.status='down'
            else :
                self.direction.y = 0
            
            if keys[pygame.K_d]:
                self.direction.x = 1
                self.status='right'
            elif keys[pygame.K_a]:
                self.direction.x = -1
                self.status='left'
            else :
                self.direction.x = 0
            
            # tool use
            if keys[pygame.K_SPACE]:
                self.timers['tool use'].activate()
                self.direction=pygame.math.Vector2()
                self.frame_index=0

            # change tool
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.tool_index += 1
                self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
                self.selected_tool=self.tools[self.tool_index]

            # seed use
            if keys[pygame.K_p]:
                self.timers['seed use'].activate()
                self.direction=pygame.math.Vector2()
                self.frame_index=0

            # change seed
            if keys[pygame.K_e] and not self.timers['seed switch'].active:
                self.timers['seed switch'].activate()
                self.seed_index += 1
                self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
                self.selected_seed=self.seeds[self.seed_index]


            # 交互
            if keys[pygame.K_RETURN]:
                self.direction.x = 0
                self.direction.y = 0
                collided_interaction_sprite = pygame.sprite.spritecollide(self,self.interaction_sprites,False)
                if collided_interaction_sprite:
                    if collided_interaction_sprite[0].name == 'Trader':
                        if self.tradeable:
                            self.info_flag = '1'
                            self.package['apple']-=30
                            self.package['corn']-=3
                            self.package['tomato']-=1
                            self.chest_key = True
                        else:
                            self.info_flag = '2'
                    elif collided_interaction_sprite[0].name == 'Bed':
                        self.status = 'left_idle'
                        self.sleep =True
                    elif collided_interaction_sprite[0].name == 'Picture':
                        pass
                    elif collided_interaction_sprite[0].name == 'Chest':
                        if self.chest_key:
                            self.info_flag = '3'
                        else:
                            self.info_flag = '4'


    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

    def use_tool(self):
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)

        if self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)
        
        if self.selected_tool == 'axe':
            # 收获作物
            self.soil_layer.havest(self.target_pos,self.package,self.seed_num)
            # 收获苹果
            for tree in self.trees.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.get_apple(self.package)
                    
    def use_seed(self):
        self.soil_layer.plant_seed(self.target_pos,self.selected_seed,self.seed_num)

    def get_status(self):
        # if the player is not moving
        # add _idle to status
        if self.direction.magnitude()==0:
            self.status = self.status.split('_')[0]+'_idle'

        # tool use
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' +self.selected_tool

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    #碰撞逻辑
    def collision(self,direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite,'hitbox'):  #判断是否有碰撞箱
                if sprite.hitbox.colliderect(self.hitbox):  #判断是否与player发生碰撞
                    if direction == 'horizontal':  #水平方向
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:
                            self.hitbox.left  = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    if direction == 'vertical':   #垂直方向
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:
                            self.hitbox.top  = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    #移动
    def move(self,dt):
        # normalize the vector
        #（单位化向量，防止斜着走的时候速度过快）
        if self.direction.magnitude()>0:
            self.direction=self.direction.normalize()
        
        # horizontal movement
        # 随direction更新水平方向位置
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx=self.hitbox.centerx
        self.collision('horizontal')

        # vertical movement
        # 随direction更新竖直方向位置
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery  = round(self.pos.y)
        self.rect.centery=self.hitbox.centery
        self.collision('vertical')

    def is_inhouse(self):
        flag = False
        x = self.rect.center[0] // TILE_SIZE
        y = self.rect.center[1] // TILE_SIZE
        for pos in self.floor_pos:
            if x == pos[0] and y == pos[1]:
                self.inzone[0] = True
                flag = True
        if not flag:
            self.inzone[0] = False

    def set_tradeable(self):
        if self.package['apple']>=30 and self.package['corn']>=3 and self.package['tomato']>=1:
            self.tradeable = True
        else:
            self.tradeable = False

    def display_info(self,info):
        info_surf = self.f.render(info,True,(0,0,0))
        info_rect = info_surf.get_rect(midbottom  = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2))
        self.display_surface.blit(info_surf,info_rect)

    def update(self,dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        self.move(dt)
        self.is_inhouse()
        self.animate(dt)


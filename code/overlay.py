import pygame
from settings import *
from support import import_folder,import_folder_dict

class Overlay:
    def __init__(self,player):
        
        # general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player

        # import
        overlay_path = '../graphics/overlay/'
        self.tools_surf = {tool: pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in player.tools}
        self.seeds_surf = {seed: pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha() for seed in player.seeds}

        self.dialog_surf = pygame.image.load('../graphics/ui/dialog.png').convert_alpha()
        self.dialog_surf.set_colorkey((255,255,255))

        # 导入表情图片
        self.emotions = {
            '0':[],'1':[],'2':[],'3':[],'4':[],'5':[],'6':[]
        }
        for emotion in self.emotions.keys():
            full_path='../graphics/ui/emotion/' + emotion
            self.emotions[emotion]=import_folder(full_path)

        self.emotion_index = 0
        self.frame_index = 0

        # 导入工具栏盒子
        self.box_surf = pygame.image.load('../graphics/overlay/box.png').convert_alpha()
        self.box_surf = pygame.transform.scale(self.box_surf,(128,128))

        # 导入展示框
        self.board_surf  =pygame.image.load('../graphics/overlay/board.png').convert_alpha()
        self.board_surf = pygame.transform.scale(self.board_surf,(128,128))

        # 导入物品图片
        self.items = import_folder_dict('../graphics/ui/item')

        # 导入字体
        self.f = pygame.font.Font('../font/ZiTiGuanJiaFangMeng-2.ttf',50)
        self.f2 = pygame.font.Font('../font/LycheeSoda.ttf',30)
        self.f3 = pygame.font.Font('../font/ZiTiGuanJiaFangMeng-2.ttf',25)

        self.tips_surfs = [
            self.f3.render('W A S D 移动',True,(255,255,255)),
            self.f3.render('Q 切换工具',True,(255,255,255)),
            self.f3.render('E 切换种子',True,(255,255,255)),
            self.f3.render('空格 使用工具',True,(255,255,255)),
            self.f3.render('P 播种',True,(255,255,255)),
            self.f3.render('Enter 交互',True,(255,255,255))
        ]

        

    def display(self,days,dt,item,seed_num,seed):
        self.days = days
        # 展示工具栏
        box_rect1 = self.box_surf.get_rect(midbottom = OVERLAY_POSITIONS['box1'])
        box_rect2 = self.box_surf.get_rect(midbottom = OVERLAY_POSITIONS['box2'])
        self.display_surface.blit(self.box_surf,box_rect1)
        self.display_surface.blit(self.box_surf,box_rect2)
        # show tools
        tool_surf = self.tools_surf[self.player.selected_tool]
        tool_rect = tool_surf.get_rect(midbottom = OVERLAY_POSITIONS['tool'])
        self.display_surface.blit(tool_surf , tool_rect)
        # show seeds
        seed_surf = self.seeds_surf[self.player.selected_seed]
        seed_surf = pygame.transform.scale(seed_surf,(64,64))
        seed_rect = seed_surf.get_rect(midbottom = OVERLAY_POSITIONS['seed'])
        self.display_surface.blit( seed_surf, seed_rect)

        # show展示框
        board_rect = self.box_surf.get_rect(midbottom = OVERLAY_POSITIONS['board'])
        self.display_surface.blit(self.board_surf,board_rect)

        # 展示物品数量
        i = 1
        for item_surf in self.items.values():
            item_surf = pygame.transform.scale(item_surf,(20,20))
            item_rect = item_surf.get_rect(midbottom = OVERLAY_POSITIONS['item'+str(i)])
            i+=1
            self.display_surface.blit(item_surf,item_rect)

        i_surf  = self.f2.render(f'{item[0]}  {item[1]}  {item[2]}',True,(0,0,0))
        i_rect = i_surf.get_rect(midbottom = (80,265))
        self.display_surface.blit(i_surf,i_rect)

        #展示种子数量
        seed_num_surf = self.f2.render(f'{seed_num[seed]}',True,(0,0,0))
        seed_num_rect = seed_num_surf.get_rect(midbottom = (175,SCREEN_HEIGHT-20))
        self.display_surface.blit(seed_num_surf,seed_num_rect)

        # 展示对话框
        dialog_surf = pygame.transform.scale(self.dialog_surf,(352,128))
        dialog_rect = self.dialog_surf.get_rect(midbottom = OVERLAY_POSITIONS['dialog'])
        self.display_surface.blit(dialog_surf,dialog_rect)

        # 天数展示
        day_surf  = self.f.render(f'第 {self.days} 天',True,(255,255,255))
        day_rect = day_surf.get_rect(midbottom = (236,115))
        self.display_surface.blit(day_surf,day_rect)
        
        # 不同天展示不同的表情
        self.emotion_index = str(self.days % 7)

        self.frame_index += 4*dt
        if self.frame_index>=len(self.emotions[self.emotion_index]):
            self.frame_index=0
        emotion_surf = self.emotions[self.emotion_index][int(self.frame_index)]
        emotion_surf = pygame.transform.scale(emotion_surf,(64,64))
        emotion_rect = emotion_surf.get_rect(midbottom = OVERLAY_POSITIONS['emotion'])
        self.display_surface.blit(emotion_surf,emotion_rect)

        # 展示提示
        for tip_index,tip_surf in enumerate(self.tips_surfs):
            tip_rect = self.tips_surfs[tip_index].get_rect(topleft = (20,280 + 25 * tip_index))
            self.display_surface.blit(tip_surf,tip_rect)
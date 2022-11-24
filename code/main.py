import sys,pygame
from level import Level
from settings import *

class Game:
    def __init__(self):
        pygame.init()
        # 设置游戏屏幕宽度和高度
        self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        # 获取时间
        self.clock = pygame.time.Clock()
        # 设置游戏名称
        pygame.display.set_caption('Sprout Lands')
        # 导入游戏 icon 图片并设置 icon
        img = pygame.image.load("../graphics/ui/icon.png")
        pygame.display.set_icon(img)

        self.level =Level()

    def run(self):
        while True:
            for event in pygame.event.get():
                # 监测是否点击退出
                if event.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # 获取 增量时间 delta time
            dt=self.clock.tick() / 1000
            # 执行游戏关卡的刷新
            self.level.run(dt)

            pygame.display.update()

if __name__=='__main__':
    game=Game()
    game.run()


from pygame.math import Vector2
# screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 64

# overlay positions 
OVERLAY_POSITIONS = {
	'tool' : (60, SCREEN_HEIGHT-32), 
	'seed': (145, SCREEN_HEIGHT-32),
	'dialog': (100,80),
	'emotion' :(75,110),
	'box1' : (60,SCREEN_HEIGHT),
	'box2':(145,SCREEN_HEIGHT),
	'board':(80,280),
	'item1':(50,200),
	'item2':(80,200),
	'item3':(110,200)
	}

PLAYER_TOOL_OFFSET = {
	'left': Vector2(-40,20),
	'right': Vector2(40,20),
	'up': Vector2(0,-20),
	'down': Vector2(0,50)
}

LAYERS = {
	'water': 0,
	'ground': 1,
	'soil': 2,
	'soil water': 3,
	'rain floor': 4,
	'house bottom': 5,
	'ground plant': 6,
	'main': 7,
	'hint': 8,
	'house top': 9,
	'fruit': 10,
	'rain drops': 11
}

APPLE_POS = {
	'Small': [(18,17), (30,37), (12,50), (30,45), (20,30), (30,10)],
	'Large': [(30,24), (60,65), (50,50), (16,40),(45,50), (42,70)]
}

GROW_SPEED = {
	'corn': 1,
	'tomato': 0.6
}

SALE_PRICES = {
	'wood': 4,
	'apple': 2,
	'corn': 10,
	'tomato': 20
}
PURCHASE_PRICES = {
	'corn': 4,
	'tomato': 5
}
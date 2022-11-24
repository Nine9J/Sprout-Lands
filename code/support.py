from os import walk
import pygame

# 获取图片列表
def import_folder(path):
    
    surface_list=[]

    for _ , __ , img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list

# 获取图片字典
def import_folder_dict(path):
    surf_dict = {}

    for _ , __ , img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surf_dict[image.split('.')[0]] = image_surf
    
    return surf_dict
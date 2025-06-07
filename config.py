#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏配置文件 - 修复版本
包含所有游戏常量和设置
"""


class GameConfig:
    # 屏幕设置
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 768
    FPS = 60

    # 游戏网格设置
    TILE_SIZE = 32
    GRID_OFFSET_X = 50
    GRID_OFFSET_Y = 50

    # 颜色定义
    COLORS = {
        "BLACK": (0, 0, 0),
        "WHITE": (255, 255, 255),
        "RED": (255, 0, 0),
        "GREEN": (0, 255, 0),
        "BLUE": (0, 0, 255),
        "YELLOW": (255, 255, 0),
        "PURPLE": (128, 0, 128),
        "ORANGE": (255, 165, 0),
        "CYAN": (0, 255, 255),
        "GRAY": (128, 128, 128),
        "DARK_GRAY": (64, 64, 64),
        "LIGHT_GRAY": (192, 192, 192),
        "BROWN": (139, 69, 19),
        "DARK_GREEN": (0, 128, 0),
        "PINK": (255, 192, 203),
        "LIME": (0, 255, 0),
        "MAROON": (128, 0, 0),
        "NAVY": (0, 0, 128),
        "OLIVE": (128, 128, 0),
        "TEAL": (0, 128, 128)
    }

    # 游戏元素颜色
    ELEMENT_COLORS = {
        "PLAYER": "BLUE",
        "WALL": "GRAY",
        "GOAL": "GREEN",
        "SWAMP": "BROWN",
        "TRAP": "RED",
        "ENEMY": "PURPLE",
        "POWER_UP_SPEED": "YELLOW",
        "POWER_UP_SCORE": "ORANGE",
        "POWER_UP_INVINCIBLE": "CYAN"
    }

    # 玩家设置 - 修复速度设置
    PLAYER_SPEED = 8.0  # 增加基础速度
    PLAYER_LIVES = 3
    SWAMP_SLOW_FACTOR = 0.5

    # 敌人设置
    ENEMY_SPEED = 2
    ENEMY_CHASE_DISTANCE = 5

    # 道具设置
    POWER_UP_DURATION = {
        "speed": 5000,  # 5秒
        "invincible": 3000  # 3秒
    }

    POWER_UP_EFFECTS = {
        "speed": 2.0,  # 速度加倍
        "score": 100,  # 额外分数
        "invincible": True  # 无敌状态
    }

    # 分数设置
    SCORE_PER_SECOND = 1
    TRAP_PENALTY = 50
    ENEMY_PENALTY = 100
    LEVEL_COMPLETE_BONUS = 500

    # 字体设置
    FONT_SIZES = {
        "SMALL": 16,
        "MEDIUM": 24,
        "LARGE": 32,
        "XLARGE": 48
    }

    # UI设置
    UI_PANEL_HEIGHT = 100
    UI_MARGIN = 10

    # 动画设置
    ANIMATION_SPEED = 8
    BLINK_DURATION = 500  # 闪烁持续时间（毫秒）

    # 文件路径
    LEVELS_DIR = "levels"
    ASSETS_DIR = "assets"
    IMAGES_DIR = "assets/images"
    SOUNDS_DIR = "assets/sounds"
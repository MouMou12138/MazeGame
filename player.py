#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
玩家类 - 修复版本
处理玩家角色的移动、状态和渲染
"""

import pygame
import math
from config import GameConfig


class Player:
    def __init__(self, x, y):
        """初始化玩家"""
        self.start_x = x
        self.start_y = y
        self.x = float(x)  # 确保使用浮点数
        self.y = float(y)  # 确保使用浮点数
        self.speed = GameConfig.PLAYER_SPEED
        self.lives = GameConfig.PLAYER_LIVES
        self.score = 0

        # 状态
        self.is_moving = False
        self.in_swamp = False
        self.invincible = False
        self.speed_boost = False

        # 效果持续时间
        self.invincible_timer = 0
        self.speed_boost_timer = 0

        # 动画
        self.animation_frame = 0
        self.animation_timer = 0

        # 移动方向
        self.direction = "down"  # up, down, left, right

        print(f"Player initialized at ({self.x}, {self.y})")  # 调试信息

    def reset(self):
        """重置玩家状态"""
        self.x = float(self.start_x)
        self.y = float(self.start_y)
        self.is_moving = False
        self.in_swamp = False
        self.invincible = False
        self.speed_boost = False
        self.invincible_timer = 0
        self.speed_boost_timer = 0
        self.animation_frame = 0
        self.animation_timer = 0
        self.direction = "down"
        print(f"Player reset to ({self.x}, {self.y})")  # 调试信息

    def update(self, dt, level_data):
        """更新玩家状态"""
        # 更新效果计时器
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False

        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed_boost = False

        # 更新动画
        if self.is_moving:
            self.animation_timer += dt
            if self.animation_timer >= 1000 / GameConfig.ANIMATION_SPEED:
                self.animation_frame = (self.animation_frame + 1) % 4
                self.animation_timer = 0
        else:
            self.animation_frame = 0

        # 处理输入
        self.handle_input(dt, level_data)

    def handle_input(self, dt, level_data):
        """处理玩家输入 - 修复版本"""
        keys = pygame.key.get_pressed()
        dx = dy = 0
        self.is_moving = False

        # 计算移动速度 - 修复速度计算
        current_speed = self.speed
        if self.speed_boost:
            current_speed *= GameConfig.POWER_UP_EFFECTS["speed"]
        if self.in_swamp:
            current_speed *= GameConfig.SWAMP_SLOW_FACTOR

        # 每帧移动的距离 - 修复移动计算
        move_distance = current_speed * dt / 1000.0  # dt是毫秒，转换为秒

        # WASD控制
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -move_distance
            self.direction = "up"
            self.is_moving = True
            print(f"Moving up: dy={dy}")  # 调试信息
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = move_distance
            self.direction = "down"
            self.is_moving = True
            print(f"Moving down: dy={dy}")  # 调试信息

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -move_distance
            self.direction = "left"
            self.is_moving = True
            print(f"Moving left: dx={dx}")  # 调试信息
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = move_distance
            self.direction = "right"
            self.is_moving = True
            print(f"Moving right: dx={dx}")  # 调试信息

        # 检查碰撞并移动
        if dx != 0:
            new_x = self.x + dx
            if self.can_move_to(new_x, self.y, level_data):
                self.x = new_x
                print(f"Player moved to x={self.x}")  # 调试信息

        if dy != 0:
            new_y = self.y + dy
            if self.can_move_to(self.x, new_y, level_data):
                self.y = new_y
                print(f"Player moved to y={self.y}")  # 调试信息

    def can_move_to(self, x, y, level_data):
        """检查是否可以移动到指定位置"""
        # 检查边界
        if x < 0 or y < 0 or x >= level_data["width"] or y >= level_data["height"]:
            print(f"Boundary check failed: ({x}, {y}) vs ({level_data['width']}, {level_data['height']})")
            return False

        # 检查墙壁碰撞 - 使用网格坐标检查
        grid_x = int(x)
        grid_y = int(y)

        for wall in level_data["walls"]:
            wall_x, wall_y, wall_w, wall_h = wall
            if (wall_x <= grid_x < wall_x + wall_w and
                    wall_y <= grid_y < wall_y + wall_h):
                print(f"Wall collision at ({grid_x}, {grid_y})")
                return False

        return True

    def check_tile_effects(self, level_data):
        """检查当前位置的地形效果"""
        grid_x = int(self.x)
        grid_y = int(self.y)

        # 重置沼泽状态
        self.in_swamp = False

        # 检查沼泽
        for swamp in level_data["swamps"]:
            if grid_x == swamp[0] and grid_y == swamp[1]:
                self.in_swamp = True
                break

        # 检查陷阱
        for trap in level_data["traps"]:
            if grid_x == trap[0] and grid_y == trap[1]:
                self.hit_trap()
                break

    def hit_trap(self):
        """触发陷阱"""
        if not self.invincible:
            self.score = max(0, self.score - GameConfig.TRAP_PENALTY)
            self.lives -= 1
            # 短暂无敌时间
            self.invincible = True
            self.invincible_timer = 1000  # 1秒无敌

    def hit_enemy(self):
        """被敌人击中"""
        if not self.invincible:
            self.score = max(0, self.score - GameConfig.ENEMY_PENALTY)
            self.lives -= 1
            # 短暂无敌时间
            self.invincible = True
            self.invincible_timer = 2000  # 2秒无敌

    def collect_power_up(self, power_up_type):
        """收集道具"""
        if power_up_type == "speed":
            self.speed_boost = True
            self.speed_boost_timer = GameConfig.POWER_UP_DURATION["speed"]
        elif power_up_type == "score":
            self.score += GameConfig.POWER_UP_EFFECTS["score"]
        elif power_up_type == "invincible":
            self.invincible = True
            self.invincible_timer = GameConfig.POWER_UP_DURATION["invincible"]

    def add_score(self, points):
        """增加分数"""
        self.score += points

    def is_at_goal(self, goal_pos):
        """检查是否到达终点"""
        grid_x = int(self.x)
        grid_y = int(self.y)
        return grid_x == goal_pos[0] and grid_y == goal_pos[1]

    def get_rect(self):
        """获取玩家矩形"""
        return pygame.Rect(self.x * GameConfig.TILE_SIZE, self.y * GameConfig.TILE_SIZE,
                           GameConfig.TILE_SIZE, GameConfig.TILE_SIZE)

    def draw(self, screen, offset_x, offset_y):
        """绘制玩家"""
        x = self.x * GameConfig.TILE_SIZE + offset_x
        y = self.y * GameConfig.TILE_SIZE + offset_y

        # 玩家矩形
        player_rect = pygame.Rect(x, y, GameConfig.TILE_SIZE, GameConfig.TILE_SIZE)

        # 根据状态选择颜色
        color = GameConfig.COLORS[GameConfig.ELEMENT_COLORS["PLAYER"]]

        # 无敌状态闪烁效果
        if self.invincible:
            time_ms = pygame.time.get_ticks()
            if (time_ms // 100) % 2:  # 每100ms闪烁一次
                color = GameConfig.COLORS["WHITE"]

        # 速度加成效果
        if self.speed_boost:
            # 添加黄色边框
            pygame.draw.rect(screen, GameConfig.COLORS["YELLOW"],
                             pygame.Rect(x - 2, y - 2, GameConfig.TILE_SIZE + 4, GameConfig.TILE_SIZE + 4))

        # 绘制玩家主体
        pygame.draw.rect(screen, color, player_rect)

        # 绘制简单的像素小人
        # 头部
        head_rect = pygame.Rect(x + 8, y + 4, 16, 12)
        pygame.draw.rect(screen, GameConfig.COLORS["WHITE"], head_rect)

        # 眼睛
        pygame.draw.circle(screen, GameConfig.COLORS["BLACK"], (int(x + 12), int(y + 8)), 2)
        pygame.draw.circle(screen, GameConfig.COLORS["BLACK"], (int(x + 20), int(y + 8)), 2)

        # 身体
        body_rect = pygame.Rect(x + 10, y + 16, 12, 12)
        pygame.draw.rect(screen, color, body_rect)

        # 根据方向绘制不同的姿态
        if self.direction == "up":
            # 向上的箭头
            pygame.draw.polygon(screen, GameConfig.COLORS["WHITE"],
                                [(x + 16, y + 2), (x + 12, y + 6), (x + 20, y + 6)])
        elif self.direction == "down":
            # 向下的箭头
            pygame.draw.polygon(screen, GameConfig.COLORS["WHITE"],
                                [(x + 16, y + 30), (x + 12, y + 26), (x + 20, y + 26)])
        elif self.direction == "left":
            # 向左的箭头
            pygame.draw.polygon(screen, GameConfig.COLORS["WHITE"],
                                [(x + 2, y + 16), (x + 6, y + 12), (x + 6, y + 20)])
        elif self.direction == "right":
            # 向右的箭头
            pygame.draw.polygon(screen, GameConfig.COLORS["WHITE"],
                                [(x + 30, y + 16), (x + 26, y + 12), (x + 26, y + 20)])

        # 移动动画效果
        if self.is_moving and self.animation_frame % 2:
            # 简单的跳跃效果
            offset = 2
            pygame.draw.rect(screen, color,
                             pygame.Rect(x, y - offset, GameConfig.TILE_SIZE, GameConfig.TILE_SIZE))
            pygame.draw.rect(screen, GameConfig.COLORS["WHITE"],
                             pygame.Rect(x + 8, y + 4 - offset, 16, 12))
            pygame.draw.circle(screen, GameConfig.COLORS["BLACK"], (int(x + 12), int(y + 8 - offset)), 2)
            pygame.draw.circle(screen, GameConfig.COLORS["BLACK"], (int(x + 20), int(y + 8 - offset)), 2)
            pygame.draw.rect(screen, color,
                             pygame.Rect(x + 10, y + 16 - offset, 12, 12))
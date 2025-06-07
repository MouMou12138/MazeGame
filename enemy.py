#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
敌人类
处理敌人的AI、移动和渲染
"""

import pygame
import math
from collections import deque
from config import GameConfig


class Enemy:
    def __init__(self, start_pos, path, speed):
        """初始化敌人"""
        self.start_pos = start_pos
        self.x = float(start_pos[0])
        self.y = float(start_pos[1])
        self.path = path
        self.speed = speed
        self.current_target = 0

        # AI状态
        self.mode = "PATROL"  # PATROL, CHASE
        self.chase_target = None
        self.last_player_pos = None

        # 动画
        self.animation_frame = 0
        self.animation_timer = 0

        # 路径查找
        self.path_to_player = []
        self.path_update_timer = 0

    def reset(self):
        """重置敌人状态"""
        self.x = float(self.start_pos[0])
        self.y = float(self.start_pos[1])
        self.current_target = 0
        self.mode = "PATROL"
        self.chase_target = None
        self.last_player_pos = None
        self.path_to_player = []
        self.path_update_timer = 0
        self.animation_frame = 0
        self.animation_timer = 0

    def update(self, dt, player, level_data):
        """更新敌人状态"""
        # 更新动画
        self.animation_timer += dt
        if self.animation_timer >= 1000 / GameConfig.ANIMATION_SPEED:
            self.animation_frame = (self.animation_frame + 1) % 4
            self.animation_timer = 0

        # 检查是否应该追击玩家
        player_distance = self.distance_to_player(player)

        if player_distance <= GameConfig.ENEMY_CHASE_DISTANCE:
            self.mode = "CHASE"
            self.chase_target = (player.x, player.y)
        elif player_distance > GameConfig.ENEMY_CHASE_DISTANCE * 1.5:
            self.mode = "PATROL"
            self.chase_target = None

        # 根据模式更新移动
        if self.mode == "CHASE":
            self.update_chase(dt, player, level_data)
        else:
            self.update_patrol(dt, level_data)

    def update_patrol(self, dt, level_data):
        """更新巡逻移动"""
        if not self.path or len(self.path) == 0:
            return

        # 获取当前目标点
        target = self.path[self.current_target]
        dx = target[0] - self.x
        dy = target[1] - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 0.1:
            # 到达目标点，切换到下一个
            self.current_target = (self.current_target + 1) % len(self.path)
        else:
            # 移动向目标点
            move_distance = self.speed * dt / 1000
            if move_distance > distance:
                move_distance = distance

            # 归一化方向向量
            dx /= distance
            dy /= distance

            new_x = self.x + dx * move_distance
            new_y = self.y + dy * move_distance

            # 检查碰撞
            if self.can_move_to(new_x, new_y, level_data):
                self.x = new_x
                self.y = new_y

    def update_chase(self, dt, player, level_data):
        """更新追击移动"""
        # 定期更新到玩家的路径
        self.path_update_timer += dt
        if self.path_update_timer >= 500:  # 每500ms更新一次路径
            self.path_to_player = self.find_path_to_player(player, level_data)
            self.path_update_timer = 0

        # 如果有路径，沿着路径移动
        if self.path_to_player and len(self.path_to_player) > 1:
            target = self.path_to_player[1]  # 下一个路径点
            dx = target[0] - self.x
            dy = target[1] - self.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < 0.1:
                # 到达路径点，移除它
                self.path_to_player.pop(0)
            else:
                # 移动向目标点
                move_distance = self.speed * 1.5 * dt / 1000  # 追击时速度更快
                if move_distance > distance:
                    move_distance = distance

                # 归一化方向向量
                dx /= distance
                dy /= distance

                new_x = self.x + dx * move_distance
                new_y = self.y + dy * move_distance

                # 检查碰撞
                if self.can_move_to(new_x, new_y, level_data):
                    self.x = new_x
                    self.y = new_y
        else:
            # 没有路径时，直接向玩家移动
            dx = player.x - self.x
            dy = player.y - self.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance > 0.1:
                move_distance = self.speed * dt / 1000
                if move_distance > distance:
                    move_distance = distance

                dx /= distance
                dy /= distance

                new_x = self.x + dx * move_distance
                new_y = self.y + dy * move_distance

                if self.can_move_to(new_x, new_y, level_data):
                    self.x = new_x
                    self.y = new_y

    def find_path_to_player(self, player, level_data):
        """使用BFS算法找到通往玩家的路径"""
        start = (int(self.x), int(self.y))
        goal = (int(player.x), int(player.y))

        if start == goal:
            return [start]

        # BFS搜索
        queue = deque([(start, [start])])
        visited = {start}

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        max_search_depth = 20  # 限制搜索深度

        while queue and len(visited) < max_search_depth * max_search_depth:
            (x, y), path = queue.popleft()

            if (x, y) == goal:
                return path

            for dx, dy in directions:
                nx, ny = x + dx, y + dy

                if (nx, ny) not in visited and self.can_move_to(nx, ny, level_data):
                    visited.add((nx, ny))
                    new_path = path + [(nx, ny)]
                    queue.append(((nx, ny), new_path))

        return []  # 没有找到路径

    def can_move_to(self, x, y, level_data):
        """检查是否可以移动到指定位置"""
        # 检查边界
        if x < 0 or y < 0 or x >= level_data["width"] or y >= level_data["height"]:
            return False

        # 检查墙壁碰撞
        enemy_rect = pygame.Rect(x * GameConfig.TILE_SIZE, y * GameConfig.TILE_SIZE,
                                 GameConfig.TILE_SIZE, GameConfig.TILE_SIZE)

        for wall in level_data["walls"]:
            wall_rect = pygame.Rect(wall[0] * GameConfig.TILE_SIZE, wall[1] * GameConfig.TILE_SIZE,
                                    wall[2] * GameConfig.TILE_SIZE, wall[3] * GameConfig.TILE_SIZE)
            if enemy_rect.colliderect(wall_rect):
                return False

        return True

    def distance_to_player(self, player):
        """计算到玩家的距离"""
        dx = self.x - player.x
        dy = self.y - player.y
        return math.sqrt(dx * dx + dy * dy)

    def collides_with_player(self, player):
        """检查是否与玩家碰撞"""
        dx = abs(self.x - player.x)
        dy = abs(self.y - player.y)
        return dx < 0.8 and dy < 0.8  # 允许一些重叠

    def get_rect(self):
        """获取敌人矩形"""
        return pygame.Rect(self.x * GameConfig.TILE_SIZE, self.y * GameConfig.TILE_SIZE,
                           GameConfig.TILE_SIZE, GameConfig.TILE_SIZE)

    def draw(self, screen, offset_x, offset_y):
        """绘制敌人"""
        x = self.x * GameConfig.TILE_SIZE + offset_x
        y = self.y * GameConfig.TILE_SIZE + offset_y

        # 敌人矩形
        enemy_rect = pygame.Rect(x, y, GameConfig.TILE_SIZE, GameConfig.TILE_SIZE)

        # 根据模式选择颜色
        if self.mode == "CHASE":
            color = GameConfig.COLORS["RED"]
            border_color = GameConfig.COLORS["YELLOW"]
        else:
            color = GameConfig.COLORS[GameConfig.ELEMENT_COLORS["ENEMY"]]
            border_color = GameConfig.COLORS["BLACK"]

        # 绘制敌人主体
        pygame.draw.rect(screen, color, enemy_rect)
        pygame.draw.rect(screen, border_color, enemy_rect, 2)

        # 绘制简单的怪物形象
        # 身体
        body_rect = pygame.Rect(x + 4, y + 8, 24, 16)
        pygame.draw.ellipse(screen, color, body_rect)

        # 眼睛
        if self.mode == "CHASE":
            eye_color = GameConfig.COLORS["YELLOW"]
        else:
            eye_color = GameConfig.COLORS["RED"]

        pygame.draw.circle(screen, eye_color, (int(x + 10), int(y + 12)), 3)
        pygame.draw.circle(screen, eye_color, (int(x + 22), int(y + 12)), 3)

        # 瞳孔
        pygame.draw.circle(screen, GameConfig.COLORS["BLACK"], (int(x + 10), int(y + 12)), 1)
        pygame.draw.circle(screen, GameConfig.COLORS["BLACK"], (int(x + 22), int(y + 12)), 1)

        # 嘴巴
        mouth_points = [(x + 8, y + 20), (x + 16, y + 24), (x + 24, y + 20)]
        pygame.draw.polygon(screen, GameConfig.COLORS["BLACK"], mouth_points)

        # 移动动画效果
        if self.animation_frame % 2:
            # 简单的摆动效果
            offset = 1
            pygame.draw.rect(screen, color,
                             pygame.Rect(x + offset, y, GameConfig.TILE_SIZE, GameConfig.TILE_SIZE))
            pygame.draw.rect(screen, border_color,
                             pygame.Rect(x + offset, y, GameConfig.TILE_SIZE, GameConfig.TILE_SIZE), 2)

        # 追击模式时的警告标志
        if self.mode == "CHASE":
            # 绘制感叹号
            pygame.draw.circle(screen, GameConfig.COLORS["YELLOW"],
                               (int(x + 16), int(y - 8)), 8)
            pygame.draw.circle(screen, GameConfig.COLORS["RED"],
                               (int(x + 16), int(y - 8)), 6)

            # 感叹号
            font = pygame.font.Font(None, 16)
            text = font.render("!", True, GameConfig.COLORS["WHITE"])
            text_rect = text.get_rect(center=(x + 16, y - 8))
            screen.blit(text, text_rect)
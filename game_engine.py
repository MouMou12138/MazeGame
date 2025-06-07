#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏引擎
处理游戏逻辑、碰撞检测和渲染
"""

import pygame
import math
from player import Player
from enemy import Enemy
from config import GameConfig


class PowerUp:
    def __init__(self, power_type, position):
        """初始化道具"""
        self.type = power_type
        self.x = position[0]
        self.y = position[1]
        self.collected = False
        self.animation_frame = 0
        self.animation_timer = 0
        self.float_offset = 0
        self.float_direction = 1

    def update(self, dt):
        """更新道具动画"""
        # 旋转动画
        self.animation_timer += dt
        if self.animation_timer >= 1000 / GameConfig.ANIMATION_SPEED:
            self.animation_frame = (self.animation_frame + 1) % 8
            self.animation_timer = 0

        # 浮动效果
        self.float_offset += self.float_direction * dt * 0.002
        if abs(self.float_offset) > 3:
            self.float_direction *= -1

    def draw(self, screen, offset_x, offset_y):
        """绘制道具"""
        if self.collected:
            return

        x = self.x * GameConfig.TILE_SIZE + offset_x
        y = self.y * GameConfig.TILE_SIZE + offset_y + self.float_offset

        # 根据类型选择颜色和形状
        if self.type == "speed":
            color = GameConfig.COLORS[GameConfig.ELEMENT_COLORS["POWER_UP_SPEED"]]
            # 绘制闪电符号
            points = [
                (x + 10, y + 5), (x + 15, y + 12), (x + 12, y + 15),
                (x + 22, y + 27), (x + 17, y + 20), (x + 20, y + 17), (x + 10, y + 5)
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, GameConfig.COLORS["WHITE"], points, 2)

        elif self.type == "score":
            color = GameConfig.COLORS[GameConfig.ELEMENT_COLORS["POWER_UP_SCORE"]]
            # 绘制钻石
            center_x, center_y = x + 16, y + 16
            points = [
                (center_x, center_y - 8),
                (center_x + 8, center_y),
                (center_x, center_y + 8),
                (center_x - 8, center_y)
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, GameConfig.COLORS["WHITE"], points, 2)

        elif self.type == "invincible":
            color = GameConfig.COLORS[GameConfig.ELEMENT_COLORS["POWER_UP_INVINCIBLE"]]
            # 绘制盾牌
            center_x, center_y = x + 16, y + 16
            pygame.draw.circle(screen, color, (center_x, center_y), 12)
            pygame.draw.circle(screen, GameConfig.COLORS["WHITE"], (center_x, center_y), 12, 3)
            pygame.draw.circle(screen, GameConfig.COLORS["WHITE"], (center_x, center_y), 6)

        # 发光效果
        if self.animation_frame < 4:
            glow_surface = pygame.Surface((GameConfig.TILE_SIZE + 8, GameConfig.TILE_SIZE + 8))
            glow_surface.set_alpha(50)
            glow_surface.fill(color)
            screen.blit(glow_surface, (x - 4, y - 4))


class GameEngine:
    def __init__(self, screen, level_manager, ui_manager):
        """初始化游戏引擎"""
        self.screen = screen
        self.level_manager = level_manager
        self.ui_manager = ui_manager

        # 游戏对象
        self.player = None
        self.enemies = []
        self.power_ups = []

        # 游戏状态
        self.game_time = 0
        self.score_timer = 0

        # 渲染偏移
        self.camera_x = 0
        self.camera_y = 0

        # 粒子效果
        self.particles = []

        # 音效（如果有的话）
        self.sound_enabled = False

    def reset(self):
        """重置游戏状态"""
        level_data = self.level_manager.get_current_level()
        if not level_data:
            return

        # 重置玩家
        start_pos = level_data["player_start"]
        self.player = Player(start_pos[0], start_pos[1])

        # 重置敌人
        self.enemies = []
        for enemy_data in level_data["enemies"]:
            enemy = Enemy(enemy_data["start"], enemy_data["path"], enemy_data["speed"])
            self.enemies.append(enemy)

        # 重置道具
        self.power_ups = []
        for power_up_data in level_data["power_ups"]:
            power_up = PowerUp(power_up_data["type"], power_up_data["position"])
            self.power_ups.append(power_up)

        # 重置游戏状态
        self.game_time = 0
        self.score_timer = 0
        self.particles = []

        # 重置摄像机
        self.update_camera()

    def update(self):
        """更新游戏逻辑"""
        if not self.player:
            return "GAME_OVER"

        # 获取时间增量
        dt = 1000 / GameConfig.FPS  # 固定时间步长

        # 更新游戏时间
        self.game_time += dt / 1000

        # 更新分数计时器
        self.score_timer += dt
        if self.score_timer >= 1000:  # 每秒增加分数
            self.player.add_score(GameConfig.SCORE_PER_SECOND)
            self.score_timer = 0

        # 获取关卡数据
        level_data = self.level_manager.get_current_level()
        if not level_data:
            return "GAME_OVER"

        # 更新玩家
        self.player.update(dt, level_data)

        # 检查地形效果
        self.player.check_tile_effects(level_data)

        # 更新敌人
        for enemy in self.enemies:
            enemy.update(dt, self.player, level_data)

        # 更新道具
        for power_up in self.power_ups:
            power_up.update(dt)

        # 更新粒子效果
        self.update_particles(dt)

        # 检查碰撞
        self.check_collisions()

        # 更新摄像机
        self.update_camera()

        # 检查游戏结束条件
        if self.player.lives <= 0:
            return "GAME_OVER"

        # 检查胜利条件
        if self.player.is_at_goal(level_data["goal"]):
            # 关卡完成奖励
            self.player.add_score(GameConfig.LEVEL_COMPLETE_BONUS)
            return "VICTORY"

        return "PLAYING"

    def check_collisions(self):
        """检查所有碰撞"""
        # 检查玩家与敌人的碰撞
        for enemy in self.enemies:
            if enemy.collides_with_player(self.player):
                self.player.hit_enemy()
                # 创建碰撞粒子效果
                self.create_particles(self.player.x, self.player.y, GameConfig.COLORS["RED"])
                break

        # 检查玩家与道具的碰撞
        for power_up in self.power_ups:
            if not power_up.collected:
                player_grid_x = int(self.player.x)
                player_grid_y = int(self.player.y)

                if player_grid_x == power_up.x and player_grid_y == power_up.y:
                    power_up.collected = True
                    self.player.collect_power_up(power_up.type)
                    # 创建收集粒子效果
                    color = GameConfig.COLORS[GameConfig.ELEMENT_COLORS[f"POWER_UP_{power_up.type.upper()}"]]
                    self.create_particles(power_up.x, power_up.y, color)

    def create_particles(self, x, y, color, count=10):
        """创建粒子效果"""
        import random
        for _ in range(count):
            particle = {
                "x": x * GameConfig.TILE_SIZE + GameConfig.TILE_SIZE // 2,
                "y": y * GameConfig.TILE_SIZE + GameConfig.TILE_SIZE // 2,
                "vx": random.uniform(-2, 2),
                "vy": random.uniform(-2, 2),
                "color": color,
                "life": 1000,  # 1秒生命周期
                "size": random.randint(2, 6)
            }
            self.particles.append(particle)

    def update_particles(self, dt):
        """更新粒子效果"""
        for particle in self.particles[:]:  # 创建副本以便安全删除
            particle["x"] += particle["vx"] * dt / 16
            particle["y"] += particle["vy"] * dt / 16
            particle["life"] -= dt
            particle["size"] = max(1, particle["size"] - dt / 200)

            if particle["life"] <= 0:
                self.particles.remove(particle)

    def update_camera(self):
        """更新摄像机位置"""
        if not self.player:
            return

        level_data = self.level_manager.get_current_level()
        if not level_data:
            return

        # 计算可视区域大小
        view_width = (self.screen.get_width() - GameConfig.GRID_OFFSET_X * 2) // GameConfig.TILE_SIZE
        view_height = (
                                  self.screen.get_height() - GameConfig.GRID_OFFSET_Y * 2 - GameConfig.UI_PANEL_HEIGHT) // GameConfig.TILE_SIZE

        # 摄像机跟随玩家
        target_x = self.player.x - view_width // 2
        target_y = self.player.y - view_height // 2

        # 限制摄像机边界
        max_x = max(0, level_data["width"] - view_width)
        max_y = max(0, level_data["height"] - view_height)

        self.camera_x = max(0, min(target_x, max_x))
        self.camera_y = max(0, min(target_y, max_y))

    def render(self):
        """渲染游戏画面"""
        level_data = self.level_manager.get_current_level()
        if not level_data or not self.player:
            return

        # 计算渲染偏移
        offset_x = GameConfig.GRID_OFFSET_X - self.camera_x * GameConfig.TILE_SIZE
        offset_y = GameConfig.GRID_OFFSET_Y + GameConfig.UI_PANEL_HEIGHT - self.camera_y * GameConfig.TILE_SIZE

        # 绘制背景
        self.draw_background(offset_x, offset_y, level_data)

        # 绘制地形元素
        self.draw_terrain(offset_x, offset_y, level_data)

        # 绘制道具
        for power_up in self.power_ups:
            power_up.draw(self.screen, offset_x, offset_y)

        # 绘制敌人
        for enemy in self.enemies:
            enemy.draw(self.screen, offset_x, offset_y)

        # 绘制玩家
        self.player.draw(self.screen, offset_x, offset_y)

        # 绘制粒子效果
        self.draw_particles(offset_x, offset_y)

        # 绘制HUD
        level_name = self.level_manager.get_level_name()
        self.ui_manager.draw_game_hud(self.player, level_name, self.game_time, self.level_manager.current_level_num)

        # 绘制小地图
        self.ui_manager.draw_mini_map(level_data, self.player, self.enemies, offset_x, offset_y)

    def draw_background(self, offset_x, offset_y, level_data):
        """绘制背景"""
        # 计算可见区域
        start_x = max(0, int(self.camera_x))
        start_y = max(0, int(self.camera_y))
        end_x = min(level_data["width"], int(self.camera_x) + 50)
        end_y = min(level_data["height"], int(self.camera_y) + 50)

        # 绘制地面瓦片
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_x = x * GameConfig.TILE_SIZE + offset_x
                tile_y = y * GameConfig.TILE_SIZE + offset_y

                # 棋盘格背景
                if (x + y) % 2 == 0:
                    color = (40, 40, 40)
                else:
                    color = (50, 50, 50)

                tile_rect = pygame.Rect(tile_x, tile_y, GameConfig.TILE_SIZE, GameConfig.TILE_SIZE)
                pygame.draw.rect(self.screen, color, tile_rect)

    def draw_terrain(self, offset_x, offset_y, level_data):
        """绘制地形元素"""
        # 绘制沼泽
        for swamp in level_data["swamps"]:
            x = swamp[0] * GameConfig.TILE_SIZE + offset_x
            y = swamp[1] * GameConfig.TILE_SIZE + offset_y
            swamp_rect = pygame.Rect(x, y, GameConfig.TILE_SIZE, GameConfig.TILE_SIZE)

            # 沼泽底色
            pygame.draw.rect(self.screen, GameConfig.COLORS[GameConfig.ELEMENT_COLORS["SWAMP"]], swamp_rect)

            # 沼泽纹理
            for i in range(0, GameConfig.TILE_SIZE, 8):
                for j in range(0, GameConfig.TILE_SIZE, 8):
                    if (i + j) % 16 == 0:
                        bubble_rect = pygame.Rect(x + i, y + j, 4, 4)
                        pygame.draw.ellipse(self.screen, GameConfig.COLORS["DARK_GREEN"], bubble_rect)

        # 绘制陷阱
        for trap in level_data["traps"]:
            x = trap[0] * GameConfig.TILE_SIZE + offset_x
            y = trap[1] * GameConfig.TILE_SIZE + offset_y
            trap_rect = pygame.Rect(x, y, GameConfig.TILE_SIZE, GameConfig.TILE_SIZE)

            # 陷阱动画
            current_time = pygame.time.get_ticks()
            if (current_time // 500) % 2:  # 每500ms闪烁
                pygame.draw.rect(self.screen, GameConfig.COLORS[GameConfig.ELEMENT_COLORS["TRAP"]], trap_rect)
            else:
                pygame.draw.rect(self.screen, GameConfig.COLORS["DARK_GRAY"], trap_rect)

            # 陷阱标志
            center_x = x + GameConfig.TILE_SIZE // 2
            center_y = y + GameConfig.TILE_SIZE // 2
            points = [
                (center_x, center_y - 8),
                (center_x - 6, center_y + 6),
                (center_x + 6, center_y + 6)
            ]
            pygame.draw.polygon(self.screen, GameConfig.COLORS["BLACK"], points)
            pygame.draw.polygon(self.screen, GameConfig.COLORS["WHITE"], points, 2)

        # 绘制墙壁
        for wall in level_data["walls"]:
            x = wall[0] * GameConfig.TILE_SIZE + offset_x
            y = wall[1] * GameConfig.TILE_SIZE + offset_y
            w = wall[2] * GameConfig.TILE_SIZE
            h = wall[3] * GameConfig.TILE_SIZE
            wall_rect = pygame.Rect(x, y, w, h)

            # 墙壁主体
            pygame.draw.rect(self.screen, GameConfig.COLORS[GameConfig.ELEMENT_COLORS["WALL"]], wall_rect)

            # 墙壁纹理
            for i in range(0, w, GameConfig.TILE_SIZE):
                for j in range(0, h, GameConfig.TILE_SIZE):
                    # 砖块纹理
                    brick_x = x + i
                    brick_y = y + j
                    brick_rect = pygame.Rect(brick_x, brick_y, GameConfig.TILE_SIZE, GameConfig.TILE_SIZE)
                    pygame.draw.rect(self.screen, GameConfig.COLORS["DARK_GRAY"], brick_rect, 2)

                    # 砖块接缝
                    pygame.draw.line(self.screen, GameConfig.COLORS["BLACK"],
                                     (brick_x, brick_y + GameConfig.TILE_SIZE // 2),
                                     (brick_x + GameConfig.TILE_SIZE, brick_y + GameConfig.TILE_SIZE // 2))

        # 绘制终点
        goal = level_data["goal"]
        x = goal[0] * GameConfig.TILE_SIZE + offset_x
        y = goal[1] * GameConfig.TILE_SIZE + offset_y
        goal_rect = pygame.Rect(x, y, GameConfig.TILE_SIZE, GameConfig.TILE_SIZE)

        # 终点动画
        current_time = pygame.time.get_ticks()
        pulse = abs(math.sin(current_time / 500.0))
        goal_color = (
            int(GameConfig.COLORS[GameConfig.ELEMENT_COLORS["GOAL"]][0] * (0.7 + pulse * 0.3)),
            int(GameConfig.COLORS[GameConfig.ELEMENT_COLORS["GOAL"]][1] * (0.7 + pulse * 0.3)),
            int(GameConfig.COLORS[GameConfig.ELEMENT_COLORS["GOAL"]][2] * (0.7 + pulse * 0.3))
        )
        pygame.draw.rect(self.screen, goal_color, goal_rect)

        # 终点标志
        center_x = x + GameConfig.TILE_SIZE // 2
        center_y = y + GameConfig.TILE_SIZE // 2
        pygame.draw.circle(self.screen, GameConfig.COLORS["WHITE"], (center_x, center_y), 8)
        pygame.draw.circle(self.screen, GameConfig.COLORS["BLACK"], (center_x, center_y), 6)
        pygame.draw.circle(self.screen, GameConfig.COLORS["WHITE"], (center_x, center_y), 3)

    def draw_particles(self, offset_x, offset_y):
        """绘制粒子效果"""
        for particle in self.particles:
            x = int(particle["x"] + offset_x)
            y = int(particle["y"] + offset_y)
            size = max(1, int(particle["size"]))

            # 根据生命周期调整透明度
            alpha = int(255 * (particle["life"] / 1000))

            # 创建带透明度的表面
            particle_surface = pygame.Surface((size * 2, size * 2))
            particle_surface.set_alpha(alpha)
            particle_surface.fill(particle["color"])

            self.screen.blit(particle_surface, (x - size, y - size))

    def get_visible_bounds(self):
        """获取可见区域边界"""
        level_data = self.level_manager.get_current_level()
        if not level_data:
            return 0, 0, 0, 0

        view_width = (self.screen.get_width() - GameConfig.GRID_OFFSET_X * 2) // GameConfig.TILE_SIZE
        view_height = (
                                  self.screen.get_height() - GameConfig.GRID_OFFSET_Y * 2 - GameConfig.UI_PANEL_HEIGHT) // GameConfig.TILE_SIZE

        start_x = max(0, int(self.camera_x))
        start_y = max(0, int(self.camera_y))
        end_x = min(level_data["width"], start_x + view_width)
        end_y = min(level_data["height"], start_y + view_height)

        return start_x, start_y, end_x, end_y
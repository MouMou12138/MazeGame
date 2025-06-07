#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI管理器 - 修复版本
处理游戏界面、菜单和HUD显示
"""

import pygame
import sys
from config import GameConfig


class UIManager:
    def __init__(self, screen):
        """初始化UI管理器"""
        self.screen = screen
        self.screen_width = GameConfig.SCREEN_WIDTH
        self.screen_height = GameConfig.SCREEN_HEIGHT

        # 初始化字体 - 修复字体加载问题
        pygame.font.init()

        # 尝试加载系统字体，如果失败则使用默认字体
        try:
            # 尝试加载中文字体
            font_name = None
            if sys.platform.startswith('win'):
                font_name = 'microsoftyaheui'  # Windows中文字体
            elif sys.platform.startswith('darwin'):
                font_name = 'pingfangsc'  # macOS中文字体
            else:
                font_name = 'notosanscjk'  # Linux中文字体

            self.fonts = {
                "small": pygame.font.SysFont(font_name, GameConfig.FONT_SIZES["SMALL"]) or pygame.font.Font(None,
                                                                                                            GameConfig.FONT_SIZES[
                                                                                                                "SMALL"]),
                "medium": pygame.font.SysFont(font_name, GameConfig.FONT_SIZES["MEDIUM"]) or pygame.font.Font(None,
                                                                                                              GameConfig.FONT_SIZES[
                                                                                                                  "MEDIUM"]),
                "large": pygame.font.SysFont(font_name, GameConfig.FONT_SIZES["LARGE"]) or pygame.font.Font(None,
                                                                                                            GameConfig.FONT_SIZES[
                                                                                                                "LARGE"]),
                "xlarge": pygame.font.SysFont(font_name, GameConfig.FONT_SIZES["XLARGE"]) or pygame.font.Font(None,
                                                                                                              GameConfig.FONT_SIZES[
                                                                                                                  "XLARGE"])
            }
        except:
            # 如果系统字体加载失败，使用默认字体
            self.fonts = {
                "small": pygame.font.Font(None, GameConfig.FONT_SIZES["SMALL"]),
                "medium": pygame.font.Font(None, GameConfig.FONT_SIZES["MEDIUM"]),
                "large": pygame.font.Font(None, GameConfig.FONT_SIZES["LARGE"]),
                "xlarge": pygame.font.Font(None, GameConfig.FONT_SIZES["XLARGE"])
            }

        # 动画相关
        self.menu_animation_offset = 0
        self.menu_animation_direction = 1
        self.last_time = pygame.time.get_ticks()

    def update_animations(self):
        """更新动画效果"""
        current_time = pygame.time.get_ticks()
        dt = current_time - self.last_time
        self.last_time = current_time

        # 菜单浮动动画
        self.menu_animation_offset += self.menu_animation_direction * dt * 0.002
        if abs(self.menu_animation_offset) > 10:
            self.menu_animation_direction *= -1

    def draw_menu(self):
        """绘制主菜单"""
        self.update_animations()

        # 背景渐变
        self.draw_gradient_background()

        # 游戏标题 - 使用英文避免字体问题
        title_text = "Maze Adventure Game"
        title_surface = self.fonts["xlarge"].render(title_text, True, GameConfig.COLORS["WHITE"])
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 150 + self.menu_animation_offset))

        # 标题阴影效果
        shadow_surface = self.fonts["xlarge"].render(title_text, True, GameConfig.COLORS["DARK_GRAY"])
        shadow_rect = shadow_surface.get_rect(center=(self.screen_width // 2 + 3, 153 + self.menu_animation_offset))
        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(title_surface, title_rect)

        # 菜单选项 - 使用英文
        menu_items = [
            ("Press SPACE to Start Game", GameConfig.COLORS["YELLOW"]),
            ("WASD to Move", GameConfig.COLORS["WHITE"]),
            ("Reach Green Goal to Win", GameConfig.COLORS["GREEN"]),
            ("Avoid Purple Enemies", GameConfig.COLORS["PURPLE"]),
            ("Beware of Red Traps", GameConfig.COLORS["RED"]),
            ("Brown Swamps Slow You Down", GameConfig.COLORS["BROWN"]),
            ("Collect Power-ups", GameConfig.COLORS["CYAN"]),
            ("Press Q to Quit", GameConfig.COLORS["LIGHT_GRAY"])
        ]

        y_start = 250
        for i, (text, color) in enumerate(menu_items):
            surface = self.fonts["medium"].render(text, True, color)
            rect = surface.get_rect(center=(self.screen_width // 2, y_start + i * 40))

            # 为主要按钮添加边框
            if i == 0:  # 开始游戏按钮
                border_rect = pygame.Rect(rect.x - 20, rect.y - 10, rect.width + 40, rect.height + 20)
                pygame.draw.rect(self.screen, GameConfig.COLORS["YELLOW"], border_rect, 3)
                pygame.draw.rect(self.screen, GameConfig.COLORS["BLACK"], border_rect)

            self.screen.blit(surface, rect)

        # 版本信息
        version_text = "v1.0 - AI Made"
        version_surface = self.fonts["small"].render(version_text, True, GameConfig.COLORS["GRAY"])
        version_rect = version_surface.get_rect(bottomright=(self.screen_width - 10, self.screen_height - 10))
        self.screen.blit(version_surface, version_rect)

    # ... 其他方法保持不变，但将中文文本改为英文 ...

    def draw_game_hud(self, player, level_name, game_time, level_num):
        """绘制游戏HUD"""
        # HUD背景
        hud_rect = pygame.Rect(0, 0, self.screen_width, GameConfig.UI_PANEL_HEIGHT)
        pygame.draw.rect(self.screen, GameConfig.COLORS["BLACK"], hud_rect)
        pygame.draw.rect(self.screen, GameConfig.COLORS["GRAY"], hud_rect, 2)

        margin = GameConfig.UI_MARGIN
        y_pos = margin

        # 关卡信息
        level_text = f"Level {level_num}: {level_name}"
        level_surface = self.fonts["medium"].render(level_text, True, GameConfig.COLORS["WHITE"])
        self.screen.blit(level_surface, (margin, y_pos))

        # 生命值
        lives_text = f"Lives: {player.lives}"
        lives_surface = self.fonts["medium"].render(lives_text, True, GameConfig.COLORS["RED"])
        self.screen.blit(lives_surface, (margin, y_pos + 30))

        # 分数
        score_text = f"Score: {player.score}"
        score_surface = self.fonts["medium"].render(score_text, True, GameConfig.COLORS["YELLOW"])
        score_rect = score_surface.get_rect()
        self.screen.blit(score_surface, (self.screen_width // 2 - score_rect.width // 2, y_pos))

        # 时间
        minutes = int(game_time // 60)
        seconds = int(game_time % 60)
        time_text = f"Time: {minutes:02d}:{seconds:02d}"
        time_surface = self.fonts["medium"].render(time_text, True, GameConfig.COLORS["CYAN"])
        time_rect = time_surface.get_rect()
        self.screen.blit(time_surface, (self.screen_width - time_rect.width - margin, y_pos))

        # 状态指示器
        status_y = y_pos + 30
        status_x = self.screen_width - 200

        if player.speed_boost:
            speed_text = "Speed Boost!"
            speed_surface = self.fonts["small"].render(speed_text, True, GameConfig.COLORS["YELLOW"])
            self.screen.blit(speed_surface, (status_x, status_y))
            status_x -= 80

        if player.invincible:
            invincible_text = "Invincible!"
            invincible_surface = self.fonts["small"].render(invincible_text, True, GameConfig.COLORS["CYAN"])
            self.screen.blit(invincible_surface, (status_x, status_y))

        # 控制提示
        controls_text = "ESC: Pause | R: Restart"
        controls_surface = self.fonts["small"].render(controls_text, True, GameConfig.COLORS["LIGHT_GRAY"])
        controls_rect = controls_surface.get_rect()
        self.screen.blit(controls_surface, (self.screen_width // 2 - controls_rect.width // 2, y_pos + 60))

    def draw_gradient_background(self):
        """绘制渐变背景"""
        # 简单的垂直渐变效果
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            color_r = int(20 * (1 - ratio) + 5 * ratio)
            color_g = int(30 * (1 - ratio) + 10 * ratio)
            color_b = int(60 * (1 - ratio) + 20 * ratio)
            color = (color_r, color_g, color_b)
            pygame.draw.line(self.screen, color, (0, y), (self.screen_width, y))

    def draw_pause_menu(self):
        """绘制暂停菜单"""
        # 半透明覆盖层
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill(GameConfig.COLORS["BLACK"])
        self.screen.blit(overlay, (0, 0))

        # 暂停文字
        pause_text = "GAME PAUSED"
        pause_surface = self.fonts["xlarge"].render(pause_text, True, GameConfig.COLORS["WHITE"])
        pause_rect = pause_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
        self.screen.blit(pause_surface, pause_rect)

        # 菜单选项
        menu_items = [
            "ESC - Continue Game",
            "R - Restart Level",
            "Q - Return to Menu"
        ]

        y_start = self.screen_height // 2 - 20
        for i, text in enumerate(menu_items):
            surface = self.fonts["medium"].render(text, True, GameConfig.COLORS["WHITE"])
            rect = surface.get_rect(center=(self.screen_width // 2, y_start + i * 40))
            self.screen.blit(surface, rect)

    def draw_game_over(self):
        """绘制游戏结束界面"""
        # 半透明覆盖层
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill(GameConfig.COLORS["RED"])
        self.screen.blit(overlay, (0, 0))

        # 游戏结束文字
        game_over_text = "GAME OVER"
        game_over_surface = self.fonts["xlarge"].render(game_over_text, True, GameConfig.COLORS["WHITE"])
        game_over_rect = game_over_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
        self.screen.blit(game_over_surface, game_over_rect)

        # 失败原因
        reason_text = "You ran out of lives!"
        reason_surface = self.fonts["medium"].render(reason_text, True, GameConfig.COLORS["YELLOW"])
        reason_rect = reason_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(reason_surface, reason_rect)

        # 菜单选项
        menu_items = [
            "R - Restart Level",
            "Q - Return to Menu"
        ]

        y_start = self.screen_height // 2 + 20
        for i, text in enumerate(menu_items):
            surface = self.fonts["medium"].render(text, True, GameConfig.COLORS["WHITE"])
            rect = surface.get_rect(center=(self.screen_width // 2, y_start + i * 40))
            self.screen.blit(surface, rect)

    def draw_victory(self, has_next_level=False):
        """绘制胜利界面"""
        # 半透明覆盖层
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill(GameConfig.COLORS["GREEN"])
        self.screen.blit(overlay, (0, 0))

        # 胜利文字
        victory_text = "LEVEL COMPLETE!"
        victory_surface = self.fonts["xlarge"].render(victory_text, True, GameConfig.COLORS["WHITE"])
        victory_rect = victory_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
        self.screen.blit(victory_surface, victory_rect)

        # 祝贺文字
        congrats_text = "Congratulations!"
        congrats_surface = self.fonts["medium"].render(congrats_text, True, GameConfig.COLORS["YELLOW"])
        congrats_rect = congrats_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(congrats_surface, congrats_rect)

        # 菜单选项
        menu_items = []
        if has_next_level:
            menu_items.append("N - Next Level")
        menu_items.extend([
            "R - Restart Level",
            "Q - Return to Menu"
        ])

        y_start = self.screen_height // 2 + 20
        for i, text in enumerate(menu_items):
            surface = self.fonts["medium"].render(text, True, GameConfig.COLORS["WHITE"])
            rect = surface.get_rect(center=(self.screen_width // 2, y_start + i * 40))
            self.screen.blit(surface, rect)

        # 绘制星星动画效果
        self.draw_victory_stars()

    def draw_victory_stars(self):
        """绘制胜利星星动画"""
        import math
        current_time = pygame.time.get_ticks()

        for i in range(10):
            angle = (current_time / 1000.0 + i * 0.5) * 2
            x = self.screen_width // 2 + math.cos(angle) * (100 + i * 20)
            y = self.screen_height // 2 + math.sin(angle) * (80 + i * 15)

            # 绘制星星
            star_points = []
            for j in range(5):
                outer_angle = j * 2 * math.pi / 5 - math.pi / 2
                inner_angle = (j + 0.5) * 2 * math.pi / 5 - math.pi / 2

                outer_x = x + math.cos(outer_angle) * 8
                outer_y = y + math.sin(outer_angle) * 8
                inner_x = x + math.cos(inner_angle) * 4
                inner_y = y + math.sin(inner_angle) * 4

                star_points.extend([(outer_x, outer_y), (inner_x, inner_y)])

            if len(star_points) >= 6:  # 确保有足够的点
                pygame.draw.polygon(self.screen, GameConfig.COLORS["YELLOW"], star_points)

    def draw_mini_map(self, level_data, player, enemies, offset_x, offset_y):
        """绘制小地图"""
        if not level_data:
            return

        # 小地图设置
        mini_map_size = 150
        mini_map_x = self.screen_width - mini_map_size - 10
        mini_map_y = GameConfig.UI_PANEL_HEIGHT + 10

        # 计算缩放比例
        scale_x = mini_map_size / level_data["width"]
        scale_y = mini_map_size / level_data["height"]
        scale = min(scale_x, scale_y)

        # 小地图背景
        mini_map_rect = pygame.Rect(mini_map_x, mini_map_y, mini_map_size, mini_map_size)
        pygame.draw.rect(self.screen, GameConfig.COLORS["BLACK"], mini_map_rect)
        pygame.draw.rect(self.screen, GameConfig.COLORS["WHITE"], mini_map_rect, 2)

        # 绘制墙壁
        for wall in level_data["walls"]:
            wall_x = mini_map_x + wall[0] * scale
            wall_y = mini_map_y + wall[1] * scale
            wall_w = wall[2] * scale
            wall_h = wall[3] * scale
            wall_rect = pygame.Rect(wall_x, wall_y, wall_w, wall_h)
            pygame.draw.rect(self.screen, GameConfig.COLORS["GRAY"], wall_rect)

        # 绘制终点
        goal = level_data["goal"]
        goal_x = mini_map_x + goal[0] * scale
        goal_y = mini_map_y + goal[1] * scale
        pygame.draw.circle(self.screen, GameConfig.COLORS["GREEN"],
                           (int(goal_x), int(goal_y)), max(2, int(scale // 2)))

        # 绘制敌人
        for enemy in enemies:
            enemy_x = mini_map_x + enemy.x * scale
            enemy_y = mini_map_y + enemy.y * scale
            color = GameConfig.COLORS["RED"] if enemy.mode == "CHASE" else GameConfig.COLORS["PURPLE"]
            pygame.draw.circle(self.screen, color,
                               (int(enemy_x), int(enemy_y)), max(1, int(scale // 3)))

        # 绘制玩家
        player_x = mini_map_x + player.x * scale
        player_y = mini_map_y + player.y * scale
        pygame.draw.circle(self.screen, GameConfig.COLORS["BLUE"],
                           (int(player_x), int(player_y)), max(2, int(scale // 2)))

        # 小地图标题
        title_text = "Mini Map"
        title_surface = self.fonts["small"].render(title_text, True, GameConfig.COLORS["WHITE"])
        self.screen.blit(title_surface, (mini_map_x, mini_map_y - 20))
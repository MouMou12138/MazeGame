#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迷宫探险游戏 - 主文件
作者: LY
日期: 2025年6月
"""

import pygame
import sys
import json
from pathlib import Path
from game_engine import GameEngine
from level_manager import LevelManager
from ui_manager import UIManager
from config import GameConfig


class MazeGame:
    def __init__(self):
        """初始化游戏"""
        pygame.init()
        pygame.mixer.init()

        # 设置显示模式
        self.screen = pygame.display.set_mode((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
        pygame.display.set_caption("迷宫探险游戏")

        # 游戏时钟
        self.clock = pygame.time.Clock()

        # 初始化各个管理器
        self.level_manager = LevelManager()
        self.ui_manager = UIManager(self.screen)
        self.game_engine = GameEngine(self.screen, self.level_manager, self.ui_manager)

        # 游戏状态
        self.running = True
        self.game_state = "MENU"  # MENU, PLAYING, PAUSED, GAME_OVER, VICTORY

        # 加载资源
        self.load_resources()

    def load_resources(self):
        """加载游戏资源"""
        try:
            # 创建资源文件夹
            Path("assets/images").mkdir(parents=True, exist_ok=True)
            Path("assets/sounds").mkdir(parents=True, exist_ok=True)
            Path("levels").mkdir(parents=True, exist_ok=True)

            # 创建默认关卡文件
            self.create_default_levels()

        except Exception as e:
            print(f"资源加载错误: {e}")

    def create_default_levels(self):
        """创建默认关卡"""
        # 关卡1 - 简单关卡
        level1 = {
            "name": "新手村",
            "width": 15,
            "height": 15,
            "player_start": [1, 1],
            "goal": [13, 13],
            "walls": [
                [0, 0, 15, 1], [0, 0, 1, 15], [14, 0, 1, 15], [0, 14, 15, 1],
                [3, 3, 5, 1], [3, 5, 1, 3], [10, 2, 1, 5], [7, 8, 3, 1]
            ],
            "swamps": [[5, 5], [6, 5], [5, 6], [11, 11], [12, 11]],
            "traps": [[4, 8], [9, 4], [12, 7]],
            "enemies": [
                {"start": [8, 2], "path": [[8, 2], [8, 5], [11, 5], [11, 2]], "speed": 1},
                {"start": [2, 10], "path": [[2, 10], [6, 10], [6, 12], [2, 12]], "speed": 1.5}
            ],
            "power_ups": [
                {"type": "speed", "position": [7, 3]},
                {"type": "score", "position": [10, 10]}
            ]
        }

        # 关卡2 - 中等难度
        level2 = {
            "name": "森林迷宫",
            "width": 20,
            "height": 20,
            "player_start": [1, 1],
            "goal": [18, 18],
            "walls": [
                [0, 0, 20, 1], [0, 0, 1, 20], [19, 0, 1, 20], [0, 19, 20, 1],
                [5, 2, 1, 8], [2, 5, 8, 1], [12, 3, 1, 6], [15, 8, 1, 5],
                [8, 12, 6, 1], [3, 15, 10, 1]
            ],
            "swamps": [
                [3, 3], [4, 3], [3, 4], [16, 6], [17, 6], [16, 7],
                [7, 14], [8, 14], [9, 14]
            ],
            "traps": [[6, 7], [14, 4], [11, 16], [17, 12], [5, 18]],
            "enemies": [
                {"start": [10, 5], "path": [[10, 5], [10, 10], [15, 10], [15, 5]], "speed": 1.2},
                {"start": [4, 12], "path": [[4, 12], [4, 17], [12, 17], [12, 12]], "speed": 1},
                {"start": [16, 14], "path": [[16, 14], [18, 14], [18, 16], [16, 16]], "speed": 2}
            ],
            "power_ups": [
                {"type": "speed", "position": [9, 7]},
                {"type": "score", "position": [14, 15]},
                {"type": "invincible", "position": [6, 11]}
            ]
        }

        # 保存关卡文件
        with open("levels/level1.json", "w", encoding="utf-8") as f:
            json.dump(level1, f, indent=2, ensure_ascii=False)

        with open("levels/level2.json", "w", encoding="utf-8") as f:
            json.dump(level2, f, indent=2, ensure_ascii=False)

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if self.game_state == "MENU":
                    if event.key == pygame.K_SPACE:
                        self.start_game()
                    elif event.key == pygame.K_q:
                        self.running = False

                elif self.game_state == "PLAYING":
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "PAUSED"
                    elif event.key == pygame.K_r:
                        self.restart_level()

                elif self.game_state == "PAUSED":
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "PLAYING"
                    elif event.key == pygame.K_r:
                        self.restart_level()
                    elif event.key == pygame.K_q:
                        self.game_state = "MENU"

                elif self.game_state in ["GAME_OVER", "VICTORY"]:
                    if event.key == pygame.K_r:
                        self.restart_level()
                    elif event.key == pygame.K_n and self.game_state == "VICTORY":
                        self.next_level()
                    elif event.key == pygame.K_q:
                        self.game_state = "MENU"

    def start_game(self):
        """开始游戏"""
        self.level_manager.load_level(1)
        self.game_engine.reset()
        self.game_state = "PLAYING"

    def restart_level(self):
        """重新开始当前关卡"""
        self.game_engine.reset()
        self.game_state = "PLAYING"

    def next_level(self):
        """下一关"""
        current_level = self.level_manager.current_level_num
        if self.level_manager.load_level(current_level + 1):
            self.game_engine.reset()
            self.game_state = "PLAYING"
        else:
            # 所有关卡完成
            self.game_state = "MENU"

    def update(self):
        """更新游戏状态"""
        if self.game_state == "PLAYING":
            result = self.game_engine.update()

            if result == "GAME_OVER":
                self.game_state = "GAME_OVER"
            elif result == "VICTORY":
                self.game_state = "VICTORY"

    def render(self):
        """渲染游戏画面"""
        self.screen.fill(GameConfig.COLORS["BLACK"])

        if self.game_state == "MENU":
            self.ui_manager.draw_menu()

        elif self.game_state == "PLAYING":
            self.game_engine.render()

        elif self.game_state == "PAUSED":
            self.game_engine.render()
            self.ui_manager.draw_pause_menu()

        elif self.game_state == "GAME_OVER":
            self.game_engine.render()
            self.ui_manager.draw_game_over()

        elif self.game_state == "VICTORY":
            self.game_engine.render()
            current_level = self.level_manager.current_level_num
            has_next = self.level_manager.has_next_level(current_level)
            self.ui_manager.draw_victory(has_next)

        pygame.display.flip()

    def run(self):
        """运行游戏主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(GameConfig.FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = MazeGame()
    game.run()
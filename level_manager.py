#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关卡管理器
处理关卡加载、地图生成和关卡数据管理
"""

import json
import random
import os
from pathlib import Path
from config import GameConfig


class LevelManager:
    def __init__(self):
        """初始化关卡管理器"""
        self.current_level = None
        self.current_level_num = 1
        self.levels_dir = Path(GameConfig.LEVELS_DIR)

        # 确保关卡目录存在
        self.levels_dir.mkdir(exist_ok=True)

    def load_level(self, level_num):
        """加载指定关卡"""
        level_file = self.levels_dir / f"level{level_num}.json"

        if level_file.exists():
            try:
                with open(level_file, "r", encoding="utf-8") as f:
                    self.current_level = json.load(f)
                    self.current_level_num = level_num
                    return True
            except Exception as e:
                print(f"加载关卡 {level_num} 失败: {e}")
                return False
        else:
            # 如果文件不存在，生成随机关卡
            self.current_level = self.generate_random_level(level_num)
            self.current_level_num = level_num
            # 保存生成的关卡
            self.save_level(level_num, self.current_level)
            return True

    def save_level(self, level_num, level_data):
        """保存关卡数据"""
        level_file = self.levels_dir / f"level{level_num}.json"
        try:
            with open(level_file, "w", encoding="utf-8") as f:
                json.dump(level_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存关卡 {level_num} 失败: {e}")

    def has_next_level(self, current_level_num):
        """检查是否有下一关"""
        next_level_file = self.levels_dir / f"level{current_level_num + 1}.json"
        return next_level_file.exists() or current_level_num < 10  # 最多生成10关

    def generate_random_level(self, level_num):
        """生成随机关卡"""
        # 根据关卡数调整难度
        base_size = 15
        size_increase = min(level_num - 1, 10)  # 最大增加10
        width = height = base_size + size_increase

        level_data = {
            "name": f"随机关卡 {level_num}",
            "width": width,
            "height": height,
            "player_start": [1, 1],
            "goal": [width - 2, height - 2],
            "walls": [],
            "swamps": [],
            "traps": [],
            "enemies": [],
            "power_ups": []
        }

        # 生成边界墙
        level_data["walls"] = self.generate_border_walls(width, height)

        # 生成内部墙壁
        level_data["walls"].extend(self.generate_internal_walls(width, height, level_num))

        # 生成沼泽
        level_data["swamps"] = self.generate_swamps(width, height, level_num)

        # 生成陷阱
        level_data["traps"] = self.generate_traps(width, height, level_num)

        # 生成敌人
        level_data["enemies"] = self.generate_enemies(width, height, level_num)

        # 生成道具
        level_data["power_ups"] = self.generate_power_ups(width, height, level_num)

        return level_data

    def generate_border_walls(self, width, height):
        """生成边界墙"""
        walls = []
        # 上边界
        walls.append([0, 0, width, 1])
        # 下边界
        walls.append([0, height - 1, width, 1])
        # 左边界
        walls.append([0, 0, 1, height])
        # 右边界
        walls.append([width - 1, 0, 1, height])
        return walls

    def generate_internal_walls(self, width, height, level_num):
        """生成内部墙壁"""
        walls = []
        wall_count = min(5 + level_num, 15)  # 墙壁数量随关卡增加

        for _ in range(wall_count):
            # 随机生成墙壁
            wall_type = random.choice(["horizontal", "vertical", "block"])

            if wall_type == "horizontal":
                # 水平墙
                wall_length = random.randint(2, min(8, width // 3))
                x = random.randint(2, width - wall_length - 2)
                y = random.randint(2, height - 3)
                walls.append([x, y, wall_length, 1])

            elif wall_type == "vertical":
                # 垂直墙
                wall_length = random.randint(2, min(8, height // 3))
                x = random.randint(2, width - 3)
                y = random.randint(2, height - wall_length - 2)
                walls.append([x, y, 1, wall_length])

            else:  # block
                # 方块墙
                size = random.randint(2, 4)
                x = random.randint(2, width - size - 2)
                y = random.randint(2, height - size - 2)
                walls.append([x, y, size, size])

        return walls

    def generate_swamps(self, width, height, level_num):
        """生成沼泽"""
        swamps = []
        swamp_count = min(3 + level_num // 2, 12)

        for _ in range(swamp_count):
            x = random.randint(2, width - 3)
            y = random.randint(2, height - 3)
            # 避免在起点和终点附近生成
            if (abs(x - 1) > 2 or abs(y - 1) > 2) and \
                    (abs(x - (width - 2)) > 2 or abs(y - (height - 2)) > 2):
                swamps.append([x, y])
                # 可能生成相邻的沼泽
                if random.random() < 0.3:
                    for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                        nx, ny = x + dx, y + dy
                        if 2 <= nx < width - 2 and 2 <= ny < height - 2:
                            if random.random() < 0.5:
                                swamps.append([nx, ny])

        return swamps

    def generate_traps(self, width, height, level_num):
        """生成陷阱"""
        traps = []
        trap_count = min(2 + level_num // 3, 8)

        for _ in range(trap_count):
            x = random.randint(2, width - 3)
            y = random.randint(2, height - 3)
            # 避免在起点和终点附近生成
            if (abs(x - 1) > 2 or abs(y - 1) > 2) and \
                    (abs(x - (width - 2)) > 2 or abs(y - (height - 2)) > 2):
                traps.append([x, y])

        return traps

    def generate_enemies(self, width, height, level_num):
        """生成敌人"""
        enemies = []
        enemy_count = min(1 + level_num // 2, 5)

        for i in range(enemy_count):
            # 随机起始位置
            start_x = random.randint(3, width - 4)
            start_y = random.randint(3, height - 4)

            # 生成巡逻路径
            path_length = random.randint(3, 6)
            path = [[start_x, start_y]]

            current_x, current_y = start_x, start_y
            for _ in range(path_length - 1):
                # 随机选择方向
                directions = []
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nx, ny = current_x + dx, current_y + dy
                    if 2 <= nx < width - 2 and 2 <= ny < height - 2:
                        directions.append((nx, ny))

                if directions:
                    next_pos = random.choice(directions)
                    path.append(list(next_pos))
                    current_x, current_y = next_pos
                else:
                    break

            # 敌人速度随关卡增加
            speed = 1.0 + level_num * 0.2

            enemies.append({
                "start": [start_x, start_y],
                "path": path,
                "speed": min(speed, 3.0)  # 最大速度限制
            })

        return enemies

    def generate_power_ups(self, width, height, level_num):
        """生成道具"""
        power_ups = []
        power_up_count = min(2 + level_num // 4, 6)

        power_up_types = ["speed", "score", "invincible"]

        for _ in range(power_up_count):
            x = random.randint(2, width - 3)
            y = random.randint(2, height - 3)
            # 避免在起点和终点附近生成
            if (abs(x - 1) > 2 or abs(y - 1) > 2) and \
                    (abs(x - (width - 2)) > 2 or abs(y - (height - 2)) > 2):
                power_type = random.choice(power_up_types)
                power_ups.append({
                    "type": power_type,
                    "position": [x, y]
                })

        return power_ups

    def is_position_blocked(self, x, y, level_data):
        """检查位置是否被阻挡"""
        # 检查边界
        if x < 0 or y < 0 or x >= level_data["width"] or y >= level_data["height"]:
            return True

        # 检查墙壁
        for wall in level_data["walls"]:
            if (wall[0] <= x < wall[0] + wall[2] and
                    wall[1] <= y < wall[1] + wall[3]):
                return True

        return False

    def get_current_level(self):
        """获取当前关卡数据"""
        return self.current_level

    def get_level_name(self):
        """获取当前关卡名称"""
        if self.current_level:
            return self.current_level.get("name", f"关卡 {self.current_level_num}")
        return "未知关卡"
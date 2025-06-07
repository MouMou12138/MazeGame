# MazeGame
期末大作业啦
# 🎮 迷宫探险游戏 (Maze Adventure Game)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/yourusername/maze-adventure-game)

一个基于 Python Pygame 开发的 2D 迷宫探险游戏，采用模块化设计，包含丰富的游戏元素和现代化的用户界面。

![游戏截图](screenshots/gameplay.png)

## ✨ 特性

### 🎯 核心功能
- **完整的游戏循环**：从主菜单到游戏结束的完整流程
- **智能敌人AI**：基于状态机的敌人行为系统
- **物理碰撞检测**：高效的网格碰撞检测算法
- **道具系统**：速度加成、无敌、分数奖励等多种道具
- **关卡管理**：支持JSON格式的可扩展关卡系统

### 🌍 地形元素
- **墙壁**：阻挡移动的障碍物
- **沼泽**：减缓移动速度的地形
- **陷阱**：触发后扣分并减少生命值
- **道具**：提供各种增益效果

### 💻 用户界面
- **主菜单**：游戏开始和控制说明
- **游戏HUD**：实时显示生命值、分数、时间等信息
- **小地图**：显示玩家位置和敌人分布
- **暂停菜单**：游戏暂停和重启选项
- **胜利/失败界面**：游戏结果展示

### 🎨 视觉效果
- **动画系统**：角色移动动画和状态效果
- **粒子效果**：道具收集和特殊效果
- **摄像机跟随**：平滑的视角跟随系统
- **状态指示**：无敌闪烁、速度加成光环等

## 🚀 快速开始

### 系统要求
- Python 3.8 或更高版本
- Pygame 2.0 或更高版本
- 支持的操作系统：Windows、macOS、Linux

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/yourusername/maze-adventure-game.git
   cd maze-adventure-game

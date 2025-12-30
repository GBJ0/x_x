# -*- coding: utf-8 -*-
# 主程序：使用拆分后的模块（碰撞判定、排行榜、页面）
import pygame
import time
import random
import os
from datetime import datetime
import collision
import pages
import leaderboard

# 全局配置常量
snake_speed = 30
window_x = 720
window_y = 480

black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)
yellow = pygame.Color(255, 255, 0)
gray = pygame.Color(100, 100, 100)
light_gray = pygame.Color(170, 170, 170)

pygame.init()
pygame.display.set_caption('贪吃蛇 - Pavan Ananth Sharma')
game_window = pygame.display.set_mode((window_x, window_y))
fps = pygame.time.Clock()

try:
    BASE_DIR = os.path.dirname(__file__)
except NameError:
    BASE_DIR = os.path.abspath(os.curdir)

# 字体查找与获取（保持原逻辑）
def find_chinese_font():
    candidates = ['msyh', 'msyhui', 'simhei', 'simsun', 'noto', 'noto sans cjk', 'arialunicode', 'wqy-zenhei', 'wqy-microhei']
    for name in candidates:
        f = pygame.font.match_font(name)
        if f:
            return f
    fonts_dir = os.path.join(BASE_DIR, 'fonts')
    if os.path.isdir(fonts_dir):
        for fname in os.listdir(fonts_dir):
            if fname.lower().endswith(('.ttf', '.ttc', '.otf')):
                return os.path.join(fonts_dir, fname)
    return None

FONT_PATH = find_chinese_font()

def get_font(size, bold=False):
    try:
        if FONT_PATH:
            return pygame.font.Font(FONT_PATH, size)
    except Exception:
        pass
    return pygame.font.SysFont('arial', size, bold=bold)

# 游戏配置
RED_PROBABILITY = 0.2
MAX_FRUITS = 20
FRUIT_LIFETIME_MS = 30 * 1000

LEADERBOARD_LOCK_SECONDS = 1.0
CENTER_BLOCK_HALF = 100
CENTER_X = window_x // 2
CENTER_Y = window_y // 2

# 排行榜模块配置
LEADERBOARD_FILE = os.path.join(BASE_DIR, "leaderboard.json")
leaderboard.configure(LEADERBOARD_FILE, size=10)

# 可重置状态
snake_position = None
snake_body = None
fruits = None
move_count = None
pending_growth = None
direction = None
change_to = None
score = None
obstacles = []
difficulty = None

# 生成果实与障碍（保留原逻辑，但使用 collision.in_center_block）
def spawn_fruit(fruits_list, fruit_type=None):
    if len(fruits_list) >= MAX_FRUITS:
        return
    attempts = 0
    while attempts < 1000:
        pos = [random.randrange(1, (window_x // 10)) * 10,
               random.randrange(1, (window_y // 10)) * 10]
        collision_with_snake = any(pos[0] == b[0] and pos[1] == b[1] for b in snake_body)
        collision_with_fruits = any(pos[0] == f['pos'][0] and pos[1] == f['pos'][1] for f in fruits_list)
        collision_with_obstacles = any(pos[0] == o[0] and pos[1] == o[1] for o in obstacles)
        if not (collision_with_snake or collision_with_fruits or collision_with_obstacles or collision.in_center_block(pos[0], pos[1], CENTER_X, CENTER_Y, CENTER_BLOCK_HALF)):
            local_type = fruit_type if fruit_type is not None else ('red' if random.random() < RED_PROBABILITY else 'white')
            fruits_list.append({'pos': pos, 'type': local_type, 'spawn_time': pygame.time.get_ticks()})
            return
        attempts += 1

def spawn_obstacles(count):
    attempts = 0
    created = 0
    grid_w = window_x // 10
    grid_h = window_y // 10
    while created < count and attempts < count * 200:
        pos = [random.randrange(0, grid_w) * 10,
               random.randrange(0, grid_h) * 10]
        if collision.in_center_block(pos[0], pos[1], CENTER_X, CENTER_Y, CENTER_BLOCK_HALF):
            attempts += 1
            continue
        collision_with_snake = any(pos[0] == b[0] and pos[1] == b[1] for b in snake_body)
        collision_with_fruits = any(pos[0] == f['pos'][0] and pos[1] == f['pos'][1] for f in fruits)
        collision_with_obstacles = any(pos[0] == o[0] and pos[1] == o[1] for o in obstacles)
        if not (collision_with_snake or collision_with_fruits or collision_with_obstacles):
            obstacles.append(pos)
            created += 1
        attempts += 1

def spawn_large_obstacles(num, w=3, h=3):
    # 声明使用全局的 obstacles 变量
    global obstacles
    
    grid_w = window_x // 10
    grid_h = window_y // 10
    w = max(1, min(w, grid_w))
    h = max(1, min(h, grid_h))
    created = 0
    attempts = 0
    max_attempts = 2000
    
    while created < num and attempts < max_attempts:
        # 随机选择一个起始位置
        tl_x = random.randint(0, grid_w - w)
        tl_y = random.randint(0, grid_h - h)
        
        # 检查是否会与中心区域重叠
        would_hit_center = False
        for gx in range(tl_x, tl_x + w):
            for gy in range(tl_y, tl_y + h):
                px, py = gx * 10, gy * 10
                if collision.in_center_block(px, py, CENTER_X, CENTER_Y, CENTER_BLOCK_HALF):
                    would_hit_center = True
                    break
            if would_hit_center:
                break
        
        if would_hit_center:
            attempts += 1
            continue
        
        # 检查是否与蛇身重叠
        overlap_with_snake = False
        for gx in range(tl_x, tl_x + w):
            for gy in range(tl_y, tl_y + h):
                px, py = gx * 10, gy * 10
                if any(px == b[0] and py == b[1] for b in snake_body):
                    overlap_with_snake = True
                    break
            if overlap_with_snake:
                break
        
        if overlap_with_snake:
            attempts += 1
            continue
        
        # 检查是否与现有障碍物重叠
        overlap_with_obstacles = False
        for gx in range(tl_x, tl_x + w):
            for gy in range(tl_y, tl_y + h):
                px, py = gx * 10, gy * 10
                if any(px == o[0] and py == o[1] for o in obstacles):
                    overlap_with_obstacles = True
                    break
            if overlap_with_obstacles:
                break
        
        if overlap_with_obstacles:
            attempts += 1
            continue
        
        # 检查是否与果实重叠
        overlap_with_fruits = False
        for gx in range(tl_x, tl_x + w):
            for gy in range(tl_y, tl_y + h):
                px, py = gx * 10, gy * 10
                if any(px == f['pos'][0] and py == f['pos'][1] for f in fruits):
                    overlap_with_fruits = True
                    break
            if overlap_with_fruits:
                break
        
        if overlap_with_fruits:
            attempts += 1
            continue
        
        # 如果所有检查都通过，生成障碍物
        for gx in range(tl_x, tl_x + w):
            for gy in range(tl_y, tl_y + h):
                obstacles.append([gx * 10, gy * 10])
        created += 1
        
        attempts += 1
    
    print(f"Generated {created} large obstacles out of {num} requested")

def reset_game():
    global snake_position, snake_body, fruits, move_count, pending_growth, direction, change_to, score, obstacles
    cx = (window_x // 2 // 10) * 10
    cy = (window_y // 2 // 10) * 10
    snake_position = [cx, cy]
    snake_body = [[cx, cy],
                  [cx - 10, cy],
                  [cx - 20, cy],
                  [cx - 30, cy]]
    fruits = []
    move_count = 0
    pending_growth = 0
    direction = 'RIGHT'
    change_to = direction
    score = 0
    obstacles = []  # 清空障碍物列表
    spawn_fruit(fruits, 'white')
    # 只在困难模式下生成障碍物
    if difficulty == 'hard':
        # 尝试生成更多但更小的障碍物
        spawn_large_obstacles(6, w=3, h=3)

def show_score(choice, color, font_name, size):
    score_font = get_font(size)
    score_surface = score_font.render('分数：' + str(score), True, color)
    score_rect = score_surface.get_rect()
    game_window.blit(score_surface, score_rect)

# 初始化流程：使用 pages 模块的页面函数
pages.show_start_screen(game_window, get_font, fps, window_x, window_y)

# 修改：将难度选择放在一个函数中，确保全局变量被正确更新
def select_difficulty():
    global difficulty, snake_speed, RED_PROBABILITY
    difficulty, snake_speed, RED_PROBABILITY = pages.show_difficulty_screen(game_window, get_font, fps, window_x, window_y)

select_difficulty()
reset_game()

# 主循环
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                change_to = 'UP'
            if event.key == pygame.K_DOWN:
                change_to = 'DOWN'
            if event.key == pygame.K_LEFT:
                change_to = 'LEFT'
            if event.key == pygame.K_RIGHT:
                change_to = 'RIGHT'
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit

    # 移除过期果实
    now_ms = pygame.time.get_ticks()
    before_count = len(fruits)
    fruits[:] = [f for f in fruits if now_ms - f.get('spawn_time', now_ms) < FRUIT_LIFETIME_MS]
    removed = before_count - len(fruits)
    for _ in range(removed):
        if len(fruits) < MAX_FRUITS:
            spawn_fruit(fruits)

    # 防止反向
    if change_to == 'UP' and direction != 'DOWN':
        direction = 'UP'
    if change_to == 'DOWN' and direction != 'UP':
        direction = 'DOWN'
    if change_to == 'LEFT' and direction != 'RIGHT':
        direction = 'LEFT'
    if change_to == 'RIGHT' and direction != 'LEFT':
        direction = 'RIGHT'

    # 移动蛇头
    if direction == 'UP':
        snake_position[1] -= 10
    if direction == 'DOWN':
        snake_position[1] += 10
    if direction == 'LEFT':
        snake_position[0] -= 10
    if direction == 'RIGHT':
        snake_position[0] += 10

    move_count += 1
    if move_count % 20 == 0 and len(fruits) < MAX_FRUITS:
        spawn_fruit(fruits)

    snake_body.insert(0, list(snake_position))

    eaten_index = None
    for i, f in enumerate(fruits):
        if snake_position[0] == f['pos'][0] and snake_position[1] == f['pos'][1]:
            eaten_index = i
            if f['type'] == 'white':
                score += 10
                pending_growth += 1
            else:
                score += 20
                pending_growth += 2
            break

    if eaten_index is not None:
        fruits.pop(eaten_index)
        if len(fruits) == 0:
            spawn_fruit(fruits)
    else:
        if pending_growth > 0:
            pending_growth -= 1
        else:
            snake_body.pop()

    game_window.fill(black)

    for o in obstacles:
        pygame.draw.rect(game_window, yellow, pygame.Rect(o[0], o[1], 10, 10))

    for pos in snake_body:
        pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))

    for f in fruits:
        col = red if f['type'] == 'red' else white
        pygame.draw.rect(game_window, col, pygame.Rect(f['pos'][0], f['pos'][1], 10, 10))

    # 撞墙 / 障碍 / 自身 碰撞判定 使用 collision 模块
    if collision.hit_wall(snake_position, window_x, window_y):
        pages.show_game_over_screen(game_window, get_font, fps, window_x, window_y, leaderboard.add_score_to_leaderboard, lambda idx: pages.show_leaderboard_screen(game_window, get_font, fps, window_x, window_y, leaderboard.load_leaderboard, idx, LEADERBOARD_LOCK_SECONDS), select_difficulty, reset_game, score, difficulty)
    if collision.hit_obstacle(snake_position, obstacles):
        pages.show_game_over_screen(game_window, get_font, fps, window_x, window_y, leaderboard.add_score_to_leaderboard, lambda idx: pages.show_leaderboard_screen(game_window, get_font, fps, window_x, window_y, leaderboard.load_leaderboard, idx, LEADERBOARD_LOCK_SECONDS), select_difficulty, reset_game, score, difficulty)
    if collision.hit_self(snake_position, snake_body):
        pages.show_game_over_screen(game_window, get_font, fps, window_x, window_y, leaderboard.add_score_to_leaderboard, lambda idx: pages.show_leaderboard_screen(game_window, get_font, fps, window_x, window_y, leaderboard.load_leaderboard, idx, LEADERBOARD_LOCK_SECONDS), select_difficulty, reset_game, score, difficulty)

    show_score(1, white, 'times new roman', 20)

    pygame.display.update()
    fps.tick(snake_speed)
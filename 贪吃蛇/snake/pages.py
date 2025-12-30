# 页面（UI）功能模块：接收所需资源与回调，由主程序传入以避免循环依赖
import pygame
from typing import Callable

# 难度名映射
DIFF_MAP = {
    'easy': '简单',
    'normal': '普通',
    'hard': '困难',
    'unknown': '未知'
}

def draw_center_text(game_window, get_font: Callable, text: str, size: int = 36, color=None, y_offset: int = 0, window_x: int = 720, window_y: int = 480):
    font = get_font(size)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(window_x // 2, window_y // 2 + y_offset))
    game_window.blit(surf, rect)

def show_start_screen(game_window, get_font, fps, window_x, window_y):
    while True:
        game_window.fill((0,0,0))
        draw_center_text(game_window, get_font, '贪吃蛇', size=64, color=pygame.Color(255,0,0), y_offset=-50, window_x=window_x, window_y=window_y)
        draw_center_text(game_window, get_font, '按 空格 开始', size=28, color=pygame.Color(255,0,0), y_offset=30, window_x=window_x, window_y=window_y)
        draw_center_text(game_window, get_font, '使用方向键移动', size=20, color=pygame.Color(255,255,255), y_offset=60, window_x=window_x, window_y=window_y)
        draw_center_text(game_window, get_font, '按 ESC 退出', size=18, color=pygame.Color(255,255,255), y_offset=100, window_x=window_x, window_y=window_y)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            return
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            raise SystemExit
        fps.tick(10)

def show_difficulty_screen(game_window, get_font, fps, window_x, window_y):
    btn_w, btn_h = 360, 60
    center_x = window_x // 2
    start_y = window_y // 2 - 10
    easy_rect = pygame.Rect(center_x - btn_w // 2, start_y - 70, btn_w, btn_h)
    normal_rect = pygame.Rect(center_x - btn_w // 2, start_y, btn_w, btn_h)
    hard_rect = pygame.Rect(center_x - btn_w // 2, start_y + 70, btn_w, btn_h)

    def draw_button(rect, text, hover=False):
        color = pygame.Color(170,170,170) if hover else pygame.Color(100,100,100)
        pygame.draw.rect(game_window, color, rect, border_radius=6)
        font = get_font(24)
        surf = font.render(text, True, pygame.Color(255,255,255))
        srect = surf.get_rect(center=rect.center)
        game_window.blit(surf, srect)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        game_window.fill((0,0,0))
        draw_center_text(game_window, get_font, '选择难度', size=48, color=pygame.Color(255,255,255), y_offset=-120, window_x=window_x, window_y=window_y)
        draw_button(easy_rect, '简单（点击）', easy_rect.collidepoint(mouse_pos))
        draw_button(normal_rect, '普通（点击）', normal_rect.collidepoint(mouse_pos))
        draw_button(hard_rect, '困难（点击）', hard_rect.collidepoint(mouse_pos))
        draw_center_text(game_window, get_font, '点击选择难度', size=18, color=pygame.Color(255,255,255), y_offset=150, window_x=window_x, window_y=window_y)
        draw_center_text(game_window, get_font, '按 ESC 退出', size=14, color=pygame.Color(255,255,255), y_offset=180, window_x=window_x, window_y=window_y)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if easy_rect.collidepoint(event.pos):
                    return 'easy', 20, 0.3
                if normal_rect.collidepoint(event.pos):
                    return 'normal', 30, 0.2
                if hard_rect.collidepoint(event.pos):
                    return 'hard', 40, 0.2
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            raise SystemExit

        fps.tick(30)

def show_leaderboard_screen(game_window, get_font, fps, window_x, window_y, load_leaderboard_cb, highlight_index=None, lock_seconds=1.0):
    # 加载并排序
    entries = load_leaderboard_cb() or []
    entries.sort(key=lambda e: e.get('score', 0), reverse=True)

    lock_end = pygame.time.get_ticks() + int(lock_seconds * 1000)
    font = get_font(22)
    start_y = 110
    center_x = window_x // 2
    start_x = center_x - 220
    col_rank_x = start_x
    col_score_x = start_x + 60
    col_diff_x = start_x + 150
    col_time_x = start_x + 240
    col_tag_x = start_x + 460

    while True:
        game_window.fill((0,0,0))
        draw_center_text(game_window, get_font, '排行榜', size=48, color=pygame.Color(255,255,255), y_offset=-180, window_x=window_x, window_y=window_y)
        if not entries:
            no_surf = font.render("暂无分数。", True, pygame.Color(255,255,255))
            game_window.blit(no_surf, (center_x - no_surf.get_width() // 2, start_y))
        else:
            for i, e in enumerate(entries):
                y = start_y + i * 28
                is_highlight = (highlight_index is not None and i == highlight_index)
                color = pygame.Color(255,0,0) if is_highlight else pygame.Color(255,255,255)
                rank_surf = font.render(f"{i+1}.", True, color)
                score_surf = font.render(str(e.get('score', 0)), True, color)
                diff_text = DIFF_MAP.get(e.get('difficulty', 'unknown'), '未知')
                diff_surf = font.render(diff_text, True, color)
                time_text = e.get('time', '')[:19].replace('T', ' ')
                time_surf = font.render(time_text, True, color)
                game_window.blit(rank_surf, (col_rank_x, y))
                game_window.blit(score_surf, (col_score_x, y))
                game_window.blit(diff_surf, (col_diff_x, y))
                game_window.blit(time_surf, (col_time_x, y))
                if is_highlight:
                    tag = get_font(18).render("（NEW）", True, pygame.Color(255,0,0))
                    game_window.blit(tag, (col_tag_x, y))

        now = pygame.time.get_ticks()
        if now < lock_end:
            remaining = max(0, (lock_end - now) // 1000)
            hint = f'按 空格 返回（{remaining+1}秒后可返回），按 ESC 退出'
        else:
            hint = '按 空格 返回，按 ESC 退出'
        draw_center_text(game_window, get_font, hint, size=18, color=pygame.Color(255,255,255), y_offset=200, window_x=window_x, window_y=window_y)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and pygame.time.get_ticks() >= lock_end:
                    pygame.time.wait(150)
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and pygame.time.get_ticks() >= lock_end:
            pygame.time.wait(150)
            return
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            raise SystemExit

        fps.tick(15)

def show_game_over_screen(game_window, get_font, fps, window_x, window_y, add_score_cb, show_leaderboard_cb: Callable, show_difficulty_cb: Callable, reset_game_cb: Callable, score, difficulty):
    try:
        new_rank = add_score_cb(score, difficulty)
    except Exception:
        new_rank = None

    while True:
        game_window.fill((0,0,0))
        draw_center_text(game_window, get_font, '游戏结束', size=64, color=pygame.Color(255,0,0), y_offset=-60, window_x=window_x, window_y=window_y)
        draw_center_text(game_window, get_font, f'分数：{score}', size=32, color=pygame.Color(255,0,0), y_offset=0, window_x=window_x, window_y=window_y)
        draw_center_text(game_window, get_font, '按 空格 查看排行榜    按 ESC 退出', size=18, color=pygame.Color(255,255,255), y_offset=60, window_x=window_x, window_y=window_y)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    show_leaderboard_cb(new_rank)
                    # 重新选择难度并重置（页面函数返回新设置）
                    show_difficulty_cb()
                    reset_game_cb()
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            pygame.time.wait(150)
            show_leaderboard_cb(new_rank)
            show_difficulty_cb()
            reset_game_cb()
            return
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            raise SystemExit

        fps.tick(10)
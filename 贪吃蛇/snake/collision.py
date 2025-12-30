# 碰撞逻辑
def in_center_block(px: int, py: int, center_x: int, center_y: int, half: int) -> bool:
    return abs(px - center_x) < half and abs(py - center_y) < half

def hit_wall(snake_position: list[int], window_x: int, window_y: int) -> bool:
    return snake_position[0] < 0 or snake_position[0] > window_x - 10 or snake_position[1] < 0 or snake_position[1] > window_y - 10

def hit_self(snake_position: list[int], snake_body: list[list[int]]) -> bool:
    for block in snake_body[1:]:
        if snake_position[0] == block[0] and snake_position[1] == block[1]:
            return True
    return False

def hit_obstacle(snake_position: list[int], obstacles: list[list[int]]) -> bool:
    return any(snake_position[0] == o[0] and snake_position[1] == o[1] for o in obstacles)
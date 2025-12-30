# 排行榜持久化模块
import json
import os
from datetime import datetime

LEADERBOARD_FILE = None
LEADERBOARD_SIZE = 10

def configure(path: str, size: int = 10):
    global LEADERBOARD_FILE, LEADERBOARD_SIZE
    LEADERBOARD_FILE = path
    LEADERBOARD_SIZE = size

def load_leaderboard():
    if not LEADERBOARD_FILE:
        return []
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []

def save_leaderboard(entries):
    if not LEADERBOARD_FILE:
        return
    try:
        with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def add_score_to_leaderboard(score_value, diff):
    """
    将分数添加到排行榜，并确保排行榜最多包含 LEADERBOARD_SIZE 条记录，
    如果新分数在排序后的排行榜中，返回其排名（0-based index），否则返回 None。
    """
    entries = load_leaderboard()
    entry = {
        "score": int(score_value),
        "difficulty": diff if diff is not None else "unknown",
        "time": datetime.utcnow().isoformat() + "Z"
    }
    entries.append(entry)
    entries.sort(key=lambda e: e.get("score", 0), reverse=True)
    entries = entries[:LEADERBOARD_SIZE]
    save_leaderboard(entries)
    # 在排序后的列表中查找新添加的条目
    for idx, e in enumerate(entries):
        if e.get("time") == entry["time"] and e.get("score") == entry["score"]:
            return idx
    return None
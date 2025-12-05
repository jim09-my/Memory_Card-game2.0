"""
通用数据管理器
负责读取和写入 data 目录下的 json 文件
"""
import json
import os
from typing import Any

from config import DataConfig, AchievementConfig, ItemConfig


def _ensure_dir(path: str):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def load_json(path: str, default: Any):
    _ensure_dir(path)
    if not os.path.exists(path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(default, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        return default

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception:
        return default


def save_json(path: str, data: Any):
    _ensure_dir(path)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ----------------- players -----------------
def load_players():
    """Load account-only players mapping from players.json"""
    return load_json(DataConfig.PLAYERS_FILE, {})


def save_players(players_dict):
    save_json(DataConfig.PLAYERS_FILE, players_dict)


def save_player(player):
    """Save account-only info for a player to players.json.

    This writes minimal account fields (username, password, created_at, last_login).
    Runtime data (points/items/records/achievements) should be stored in player_profiles.json.
    """
    players = load_players()
    acct = {
        'username': player.username,
        'password': getattr(player, 'password', ''),
        'created_at': getattr(player, 'created_at', None),
        'last_login': getattr(player, 'last_login', None)
    }
    # 写入账号+运行态（兼容旧版逻辑：把运行态存回 players.json）
    try:
        # 如果 player 对象有 to_dict 方法，保存完整数据（包含 points/items/game_records 等）
        player_data = player.to_dict() if hasattr(player, 'to_dict') else acct
    except Exception:
        player_data = acct

    players[player.username] = player_data
    save_players(players)

# ----------------- player profiles (runtime state) -----------------
PROFILES_FILE = os.path.join(os.path.dirname(DataConfig.PLAYERS_FILE), 'player_profiles.json')


def load_player_profiles():
    return load_json(PROFILES_FILE, {})


def save_player_profiles(profiles_dict):
    save_json(PROFILES_FILE, profiles_dict)


def load_player_profile(username):
    profiles = load_player_profiles()
    return profiles.get(username, {})


def save_player_profile(player):
    # 向后兼容：将运行态保存到 players.json（不再使用单独的 player_profiles.json）
    try:
        save_player(player)
    except Exception:
        pass

    # 如果旧的 player_profiles.json 文件存在，删除它（用户不需要该文件）
    try:
        if os.path.exists(PROFILES_FILE):
            os.remove(PROFILES_FILE)
    except Exception:
        pass


# ----------------- achievements -----------------
def load_achievements():
    # default to config definitions (ids and metadata)
    # We store achievements file as a dict with definitions and unlocked mapping
    default = {
        'definitions': AchievementConfig.ACHIEVEMENTS if hasattr(AchievementConfig, 'ACHIEVEMENTS') else [],
        'unlocked': {}
    }
    return load_json(DataConfig.ACHIEVEMENTS_FILE, default)


def save_achievements(data):
    save_json(DataConfig.ACHIEVEMENTS_FILE, data)


def get_unlocked_achievements_for_user(username):
    data = load_achievements()
    unlocked = data.get('unlocked', {})
    return unlocked.get(username, [])


def add_unlocked_achievement(username, achievement_id):
    data = load_achievements()
    unlocked = data.get('unlocked', {})
    user_list = unlocked.get(username, [])
    if achievement_id not in user_list:
        user_list.append(achievement_id)
        unlocked[username] = user_list
        data['unlocked'] = unlocked
        save_achievements(data)


# ----------------- records -----------------
def load_records():
    return load_json(DataConfig.RECORDS_FILE, [])


def save_records(data):
    save_json(DataConfig.RECORDS_FILE, data)


def append_record(record):
    # Ensure record contains timestamp and username for consistency
    try:
        if 'timestamp' not in record:
            import time as _time
            record['timestamp'] = int(_time.time())
    except Exception:
        pass
    try:
        if 'username' not in record:
            # leave username as None if not provided
            record['username'] = None
    except Exception:
        pass

    records = load_records()
    records.append(record)
    save_records(records)


# ----------------- shop items -----------------
def load_shop_items():
    # default to ItemConfig.ITEMS structure
    default = ItemConfig.ITEMS if hasattr(ItemConfig, 'ITEMS') else {}
    # 如果文件存在则读取，否则直接返回代码内默认配置但不创建文件（用户不需要 shop_items.json）
    _ensure_dir(DataConfig.SHOP_FILE)
    if os.path.exists(DataConfig.SHOP_FILE):
        try:
            with open(DataConfig.SHOP_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_shop_items(data):
    save_json(DataConfig.SHOP_FILE, data)


# ----------------- settings -----------------
def load_settings():
    return load_json(DataConfig.SETTINGS_FILE, {})


def save_settings(data):
    save_json(DataConfig.SETTINGS_FILE, data)

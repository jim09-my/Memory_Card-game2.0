"""
游戏配置文件
包含所有游戏参数和常量定义
"""
import os

# ============== 路径配置 ==============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')

# 确保目录存在
for dir_path in [DATA_DIR, ASSETS_DIR, IMAGES_DIR, SOUNDS_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


# ============== 游戏配置 ==============
class GameConfig:
    """游戏基础配置"""
    NORMAL_GRID = 4  # 普通模式网格大小
    ULTIMATE_GRID = 7  # 终极模式网格大小
    ULTIMATE_TIME_LIMIT = 480  # 终极模式时间限制（秒）

    CARD_SIZE = 20  # 卡牌大小
    CARD_PADDING = 10  # 卡牌间距

    FLIP_ANIMATION_TIME = 300  # 翻牌动画时间（毫秒）
    MATCH_DELAY = 1000  # 配对成功延迟（毫秒）
    MISMATCH_DELAY = 1500  # 配对失败延迟（毫秒）


# ============== 积分配置 ==============
class PointsConfig:
    """积分奖励配置"""
    # 通关奖励
    NORMAL_MODE_REWARD = 200
    ULTIMATE_MODE_REWARD = 1200

    # 成就奖励
    RECORD_BREAK_REWARD = 300
    FIRST_WIN_REWARD = 800
    PERFECT_GAME_REWARD = 500  # 零失误

    # 每日奖励
    DAILY_LOGIN_REWARD = 100
    CONSECUTIVE_3_DAYS_REWARD = 200
    CONSECUTIVE_7_DAYS_REWARD = 500

    # 新手奖励
    NEW_PLAYER_BONUS = 500
    FIRST_GAME_BONUS = 100


# ============== 道具配置 ==============
class ItemConfig:
    """道具配置"""
    ITEMS = {
        'hint': {
            'name': '提示道具',
            'description': '显示一对卡牌的位置',
            'price': 200,
            'icon': '💡',
            'effect_value': 1
        },
        'time_extend': {
            'name': '延时道具',
            'description': '延长30秒游戏时间',
            'price': 300,
            'icon': '⏰',
            'effect_value': 30
        },
        'shuffle_prevent': {
            'name': '防洗牌道具',
            'description': '防止触发洗牌机制',
            'price': 400,
            'icon': '🛡️',
            'effect_value': 1
        },
        'undo': {
            'name': '撤销道具',
            'description': '撤销上一步操作',
            'price': 250,
            'icon': '↩️',
            'effect_value': 1
        }
    }


# ============== 成就配置 ==============
class AchievementConfig:
    """成就配置"""
    ACHIEVEMENTS = [
        # 入门成就
        {
            'id': 'first_game',
            'name': '初次尝试',
            'description': '完成第一场游戏',
            'category': '入门',
            'reward': 100,
            'icon': '🎮',
            'condition': lambda player: len(player.game_records) >= 1
        },
        {
            'id': 'normal_master',
            'name': '普通大师',
            'description': '普通模式通关10次',
            'category': '入门',
            'reward': 300,
            'icon': '🏆',
            'condition': lambda player: sum(1 for r in player.game_records
                                            if r['mode'] == 'normal' and r['completed']) >= 10
        },
        {
            'id': 'perfect_memory',
            'name': '完美记忆',
            'description': '普通模式零失误通关',
            'category': '入门',
            'reward': 500,
            'icon': '💎',
            'condition': lambda player: any(r['mode'] == 'normal' and r['moves'] == 8
                                            for r in player.game_records)
        },

        # 挑战成就
        {
            'id': 'ultimate_challenger',
            'name': '终极挑战者',
            'description': '完成终极模式',
            'category': '挑战',
            'reward': 800,
            'icon': '⚡',
            'condition': lambda player: any(r['mode'] == 'ultimate' and r['completed']
                                            for r in player.game_records)
        },
        {
            'id': 'speed_king',
            'name': '速度之王',
            'description': '2分钟内完成普通模式',
            'category': '挑战',
            'reward': 600,
            'icon': '🚀',
            'condition': lambda player: any(r['mode'] == 'normal' and r['time_used'] <= 120
                                            for r in player.game_records)
        },
        {
            'id': 'memory_master',
            'name': '记忆大师',
            'description': '终极模式零失误通关',
            'category': '挑战',
            'reward': 1000,
            'icon': '🧠',
            'condition': lambda player: any(r['mode'] == 'ultimate' and r['moves'] == 24.5
                                            for r in player.game_records)
        },

        # 持久成就
        {
            'id': 'persistent',
            'name': '坚持不懈',
            'description': '连续登录7天',
            'category': '持久',
            'reward': 700,
            'icon': '📅',
            'condition': lambda player: player.consecutive_days >= 7
        },
        {
            'id': 'game_expert',
            'name': '游戏达人',
            'description': '完成100场游戏',
            'category': '持久',
            'reward': 1500,
            'icon': '🎯',
            'condition': lambda player: len(player.game_records) >= 100
        },
        {
            'id': 'rich_player',
            'name': '积分富翁',
            'description': '累计获得10000积分',
            'category': '持久',
            'reward': 2000,
            'icon': '💰',
            'condition': lambda player: player.total_points_earned >= 10000
        }
    ]


# ============== 界面配置 ==============
class UIConfig:
    """界面配置"""
    # 窗口尺寸
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800

    # 颜色配置
    COLORS = {
        'primary': '#4A90E2',
        'success': '#5CB85C',
        'warning': '#F0AD4E',
        'danger': '#D9534F',
        'bg_dark': '#2C3E50',
        'bg_light': '#ECF0F1',
        'text_dark': '#34495E',
        'text_light': '#FFFFFF',
        'card_back': '#3498DB',
        'card_front': '#FFFFFF'
    }

    # 字体配置
    FONTS = {
        'title': ('Arial', 24, 'bold'),
        'heading': ('Arial', 18, 'bold'),
        'normal': ('Arial', 12),
        'small': ('Arial', 10),
        'button': ('Arial', 14, 'bold')
    }


# ============== 数据文件配置 ==============
class DataConfig:
    """数据文件路径配置"""
    PLAYERS_FILE = os.path.join(DATA_DIR, 'players.json')
    RECORDS_FILE = os.path.join(DATA_DIR, 'records.json')
    ACHIEVEMENTS_FILE = os.path.join(DATA_DIR, 'achievements.json')
    SHOP_FILE = os.path.join(DATA_DIR, 'shop_items.json')
    SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')

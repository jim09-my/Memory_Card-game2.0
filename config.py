import os

# ============== 路径配置 ==============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')

for dir_path in [DATA_DIR, ASSETS_DIR, IMAGES_DIR, SOUNDS_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# ============== 游戏配置 ==============
class GameConfig:
    NORMAL_GRID = 4
    ULTIMATE_GRID = 6
    NORMAL_TIME_LIMIT = None
    ULTIMATE_TIME_LIMIT = 120
    ULTIMATE_SHUFFLE_TIME_LIMIT = 180
    
    # 这里只做逻辑参考，实际尺寸由UI动态计算
    CARD_SIZE = 80 
    CARD_PADDING = 15

    FLIP_ANIMATION_TIME = 300
    MATCH_DELAY = 1000
    MISMATCH_DELAY = 1500

# ============== 积分配置 ==============
class PointsConfig:
    NORMAL_MODE_REWARD = 200
    ULTIMATE_MODE_REWARD = 1200
    RECORD_BREAK_REWARD = 300
    FIRST_WIN_REWARD = 800
    PERFECT_GAME_REWARD = 500
    DAILY_LOGIN_REWARD = 100
    CONSECUTIVE_3_DAYS_REWARD = 200
    CONSECUTIVE_7_DAYS_REWARD = 500
    NEW_PLAYER_BONUS = 500
    FIRST_GAME_BONUS = 100

# ============== 道具配置 ==============
class ItemConfig:
    ITEMS = {
        'hint': {'name': '提示道具', 'description': '显示一对卡牌', 'price': 200, 'icon': '💡', 'effect_value': 1},
        'time_extend': {'name': '延时道具', 'description': '延长30秒', 'price': 300, 'icon': '⏰', 'effect_value': 30},
        'shuffle_prevent': {'name': '防洗牌', 'description': '防止洗牌', 'price': 400, 'icon': '🛡️', 'effect_value': 1},
        'undo': {'name': '撤销道具', 'description': '撤销一步', 'price': 250, 'icon': '↩️', 'effect_value': 1}
    }

# ============== 成就配置 (保持原样) ==============
class AchievementConfig:
    ACHIEVEMENTS = [
        {'id': 'first_game', 'name': '初次尝试', 'description': '完成第一场游戏', 'category': '入门', 'reward': 100, 'icon': '🎮', 'condition': lambda p: len(p.game_records) >= 1},
        {'id': 'normal_master', 'name': '普通大师', 'description': '普通模式通关10次', 'category': '入门', 'reward': 300, 'icon': '🏆', 'condition': lambda p: sum(1 for r in p.game_records if r['mode'] == 'normal' and r['completed']) >= 10},
        # ... 其他成就保持不变 ...
    ]

# ============== 界面配置 (核心修改) ==============
class UIConfig:
    """界面配置 - 仿截图风格"""
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800

    # 颜色配置
    COLORS = {
        'primary': '#009688',      # 背景：青绿色 (Teal)
        'primary_dark': '#00796B', # 背景纹理深色
        'success': '#2ECC71',
        'warning': '#F1C40F',
        'danger': '#E74C3C',
        'bg_dark': '#263238',
        'text_dark': '#2C3E50',
        'text_light': '#FFFFFF',
        
        # 卡牌样式
        'card_back': '#FFC107',    # 卡背：亮黄色/琥珀色
        'card_front': '#FFFFFF',   # 卡面：白色
        'card_border': '#FFFFFF',  # 卡背内圈颜色
        'glow_color': '#00E676',   # 选中发光：荧光绿
        'text_red': '#E74C3C',     # 红桃/方块文字颜色
        'text_black': '#2C3E50'    # 黑桃/梅花文字颜色
    }

    FONTS = {
        'title': ('Helvetica', 24, 'bold'),
        'heading': ('Helvetica', 18, 'bold'),
        'normal': ('Helvetica', 12),
        'card_main': ('Times New Roman', 24, 'bold'),
        'card_corner': ('Arial', 10, 'bold'),
        'button': ('Helvetica', 12, 'bold')
    }

# ============== 扑克牌配置 ==============
class PokerConfig:
    SUITS = ['♠', '♥', '♦', '♣']
    RANKS = ['A'] + [str(i) for i in range(2, 11)]

    @classmethod
    def build_deck(cls):
        return [(r, s) for s in cls.SUITS for r in cls.RANKS]

    @classmethod
    def sample_faces(cls, count):
        import random
        deck = cls.build_deck()
        random.shuffle(deck)
        return deck[:count]

    @staticmethod
    def suit_color(suit:str):
        return UIConfig.COLORS['text_red'] if suit in ('♥','♦') else UIConfig.COLORS['text_black']

# ============== 数据文件配置 (保持原样) ==============
class DataConfig:
    PLAYERS_FILE = os.path.join(DATA_DIR, 'players.json')
    RECORDS_FILE = os.path.join(DATA_DIR, 'records.json')
    ACHIEVEMENTS_FILE = os.path.join(DATA_DIR, 'achievements.json')
    SHOP_FILE = os.path.join(DATA_DIR, 'shop_items.json')
    SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')

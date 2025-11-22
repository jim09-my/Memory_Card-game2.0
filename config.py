import os

# ============== 路径配置 (保持不变) ==============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')

for dir_path in [DATA_DIR, ASSETS_DIR, IMAGES_DIR, SOUNDS_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# ============== 游戏配置 (保持不变) ==============
class GameConfig:
    NORMAL_GRID = 4
    ULTIMATE_GRID = 6
    NORMAL_TIME_LIMIT = None
    ULTIMATE_TIME_LIMIT = 120
    ULTIMATE_SHUFFLE_TIME_LIMIT = 180
    
    CARD_SIZE = 80 
    CARD_PADDING = 15

    FLIP_ANIMATION_TIME = 250 # 稍微加快一点动画让手感更脆
    MATCH_DELAY = 800
    MISMATCH_DELAY = 1000

# ============== 积分/道具/成就配置 (保持不变) ==============
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

class ItemConfig:
    ITEMS = {
        'hint': {'name': '透视眼', 'description': '偷看一对卡牌', 'price': 200, 'icon': '👁️', 'effect_value': 1},
        'time_extend': {'name': '时间胶囊', 'description': '延长30秒', 'price': 300, 'icon': '⏳', 'effect_value': 30},
        'shuffle_prevent': {'name': '定身术', 'description': '防止洗牌', 'price': 400, 'icon': '🛡️', 'effect_value': 1},
        'undo': {'name': '时光倒流', 'description': '撤销一步', 'price': 250, 'icon': '↩️', 'effect_value': 1}
    }

class AchievementConfig:
    ACHIEVEMENTS = [
        {'id': 'first_game', 'name': '初次尝试', 'description': '完成第一场游戏', 'category': '入门', 'reward': 100, 'icon': '🎮', 'condition': lambda p: len(p.game_records) >= 1},
        {'id': 'normal_master', 'name': '普通大师', 'description': '普通模式通关10次', 'category': '入门', 'reward': 300, 'icon': '🏆', 'condition': lambda p: sum(1 for r in p.game_records if r['mode'] == 'normal' and r['completed']) >= 10},
    ]

# ============== 界面配置 (核心视觉修改) ==============
class UIConfig:
    """界面配置 - 1:1 复刻截图风格"""
    WINDOW_WIDTH = 1100
    WINDOW_HEIGHT = 850

    # 颜色配置 (Teal & Yellow Theme)
    COLORS = {
        'primary': '#2896A0',      # 核心背景色：截图中的青绿色
        'primary_dark': '#1E7882', # 深色装饰
        
        'bg_light': '#E0F7FA',     # 浅色区域
        'text_dark': '#263238',    # 深灰色文字
        'text_light': '#FFFFFF',   # 白色文字
        
        # 卡牌视觉
        'card_back_bg': '#FFCD3C', # 卡背：截图中的芥末黄
        'card_back_icon': '#FFF5E0', # 卡背图标：奶油色
        'card_front': '#FFFFFF',   # 卡面：纯白
        'card_border_white': '#FFFFFF', # 未翻开时的白边
        
        'success_glow': '#32FF64', # 配对成功光效：荧光绿 (Neon Green)
        'danger': '#FF5252',
        
        'text_red': '#E74C3C',     # 扑克花色红
        'text_black': '#2C3E50'    # 扑克花色黑
    }

    # 字体配置 (尽量使用圆体)
    FONTS = {
        'title': ('Arial Rounded MT Bold', 28, 'bold'), # 如果系统没有，会自动回退
        'heading': ('Arial Rounded MT Bold', 18, 'bold'),
        'normal': ('Arial', 12),
        'card_main': ('Times New Roman', 32, 'bold'),
        'card_corner': ('Arial', 11, 'bold'),
        'button': ('Arial Rounded MT Bold', 13)
    }

# ============== 扑克牌配置 (保持不变) ==============
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

# ============== 数据文件配置 (保持不变) ==============
class DataConfig:
    PLAYERS_FILE = os.path.join(DATA_DIR, 'players.json')
    RECORDS_FILE = os.path.join(DATA_DIR, 'records.json')
    ACHIEVEMENTS_FILE = os.path.join(DATA_DIR, 'achievements.json')
    SHOP_FILE = os.path.join(DATA_DIR, 'shop_items.json')
    SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
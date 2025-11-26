import os
import sys
import random
from datetime import datetime


# ============== 路径配置（支持打包） ==============

def get_base_path():
    """获取数据目录（支持打包和开发环境）"""
    if getattr(sys, 'frozen', False):
        # 打包后：使用用户文档目录
        if sys.platform == 'win32':
            base = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'MemoryCardGame')
        elif sys.platform == 'darwin':  # macOS
            base = os.path.expanduser('~/Library/Application Support/MemoryCardGame')
        else:  # Linux
            base = os.path.expanduser('~/.memory_card_game')
    else:
        # 开发环境：使用项目根目录下的 data 文件夹
        base = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    # 确保目录存在
    os.makedirs(base, exist_ok=True)
    return base
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
        'hint': {'name': '透视眼', 'description': '偷看一对卡牌', 'price': 200, 'icon': '\U0001f441\ufe0f', 'effect_value': 1},
        'time_extend': {'name': '时间胶囊', 'description': '延长30秒', 'price': 300, 'icon': '\u23f3', 'effect_value': 30},
        'shuffle_prevent': {'name': '防洗牌护盾', 'description': '阻止一次洗牌（仅洗牌模式）', 'price': 400, 'icon': '\U0001f6e1\ufe0f', 'effect_value': 1},
        # 将原“时光倒流”替换为“时间静止”道具，键名保持为 undo 以兼容现有数据与成就逻辑
        'undo': {'name': '时间静止', 'description': '在终极模式中冻结时间10秒（仍可翻牌配对）', 'price': 250, 'icon': '\u23f8\ufe0f', 'effect_value': 10}
    }

class AchievementConfig:
    @staticmethod
    def current_win_streak(p):
        streak = 0
        for r in sorted(p.game_records, key=lambda x: x.get('timestamp',0), reverse=True):
            if r.get('completed'):
                streak += 1
            else:
                break
        return streak
    @staticmethod
    def current_win_streak_by_mode(p, mode):
        streak = 0
        for r in sorted(p.game_records, key=lambda x: x.get('timestamp',0), reverse=True):
            if r.get('completed') and r.get('mode') == mode:
                streak += 1
            else:
                break
        return streak
    @staticmethod
    def current_win_streak_no_item(p):
        streak = 0
        for r in sorted(p.game_records, key=lambda x: x.get('timestamp',0), reverse=True):
            iu = r.get('items_used', {})
            if r.get('completed') and all((iu.get(k,0)==0) for k in ['hint','time_extend','shuffle_prevent','undo']):
                streak += 1
            else:
                break
        return streak
    @staticmethod
    def _day_key(ts):
        try:
            return datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        except Exception:
            return None
    @staticmethod
    def last_day(p):
        if not p.game_records:
            return None
        ts = p.game_records[-1].get('timestamp', None)
        return AchievementConfig._day_key(ts) if ts else None
    @staticmethod
    def count_plays_on_day(p, day_key):
        if not day_key:
            return 0
        return sum(1 for r in p.game_records if AchievementConfig._day_key(r.get('timestamp',0)) == day_key)
    @staticmethod
    def tools_variety_on_day(p, day_key):
        if not day_key:
            return False
        used = {'hint':0,'time_extend':0,'shuffle_prevent':0,'undo':0}
        for r in p.game_records:
            if AchievementConfig._day_key(r.get('timestamp',0)) != day_key:
                continue
            iu = r.get('items_used', {})
            for k in list(used.keys()):
                used[k] += iu.get(k,0)
        return all(v >= 1 for v in used.values())
    ACHIEVEMENTS = [
        {'id': 'first_game', 'name': '初次尝试', 'description': '完成第一场游戏', 'category': '入门', 'reward': 100, 'icon': '🎮', 'condition': lambda p: len(p.game_records) >= 1},
        {'id': 'normal_master', 'name': '普通大师', 'description': '普通模式通关10次', 'category': '入门', 'reward': 300, 'icon': '🏆', 'condition': lambda p: sum(1 for r in p.game_records if r.get('mode') == 'normal' and r.get('completed')) >= 10},
        {'id': 'ultimate_conqueror', 'name': '终极征服者', 'description': '终极模式通关5次', 'category': '挑战', 'reward': 800, 'icon': '👑', 'condition': lambda p: sum(1 for r in p.game_records if r.get('mode') == 'ultimate' and r.get('completed')) >= 5},
        {'id': 'persistent_50', 'name': '毅力十足', 'description': '累计游玩50局', 'category': '成长', 'reward': 200, 'icon': '🔁', 'condition': lambda p: len(p.game_records) >= 50},
        {'id': 'item_user_10', 'name': '工具达人', 'description': '累计使用道具10次', 'category': '活跃', 'reward': 150, 'icon': '🧰', 'condition': lambda p: sum((sum(r.get('items_used', {}).values()) if isinstance(r.get('items_used', {}), dict) else 0) for r in p.game_records) >= 10},
        {'id': 'no_item_10', 'name': '清心寡欲', 'description': '无道具通关10次', 'category': '技术', 'reward': 500, 'icon': '🚫', 'condition': lambda p: sum(1 for r in p.game_records if r.get('completed') and all((r.get('items_used',{}).get(k,0)==0) for k in ['hint','time_extend','shuffle_prevent','undo'])) >= 10},
        {'id': 'win_streak_3', 'name': '连胜三场', 'description': '连续通关3场', 'category': '连胜', 'reward': 200, 'icon': '💥', 'condition': lambda p: AchievementConfig.current_win_streak(p) >= 3},
        {'id': 'win_streak_5', 'name': '势不可挡', 'description': '连续通关5场', 'category': '连胜', 'reward': 400, 'icon': '⚡', 'condition': lambda p: AchievementConfig.current_win_streak(p) >= 5},
        {'id': 'login_streak_3', 'name': '活跃签到·3', 'description': '连续登录3天', 'category': '活跃', 'reward': 200, 'icon': '📅', 'condition': lambda p: p.consecutive_days >= 3},
        {'id': 'login_streak_7', 'name': '活跃签到·7', 'description': '连续登录7天', 'category': '活跃', 'reward': 500, 'icon': '📆', 'condition': lambda p: p.consecutive_days >= 7},
        {'id': 'first_win', 'name': '首胜加冕', 'description': '首次通关任意模式', 'category': '入门', 'reward': 50, 'icon': '🥇', 'condition': lambda p: p.completed_games >= 1},
        {'id': 'first_ultimate_win', 'name': '初试终极', 'description': '首次通关终极模式', 'category': '入门', 'reward': 75, 'icon': '🧗', 'condition': lambda p: sum(1 for r in p.game_records if r.get('mode')=='ultimate' and r.get('completed')) >= 1},
        {'id': 'first_item_use', 'name': '初用道具', 'description': '首次使用任意道具', 'category': '入门', 'reward': 10, 'icon': '🧰', 'condition': lambda p: any(((sum(r.get('items_used', {}).values()) if isinstance(r.get('items_used', {}), dict) else 0) > 0) for r in p.game_records)},
        {'id': 'record_break_normal', 'name': '打破个人纪录', 'description': '刷新普通模式个人最佳用时', 'category': '入门', 'reward': 100, 'icon': '⏱️', 'condition': lambda p: p.best_time_normal is not None},
        {'id': 'persistent_100', 'name': '百战不殆', 'description': '累计游玩100局', 'category': '成长', 'reward': 300, 'icon': '📈', 'condition': lambda p: len(p.game_records) >= 100},
        {'id': 'points_5000', 'name': '千分达人', 'description': '累计获得积分达到5000', 'category': '成长', 'reward': 500, 'icon': '💎', 'condition': lambda p: getattr(p, 'total_points_earned', 0) >= 5000},
        {'id': 'normal_master_30', 'name': '普通老练', 'description': '普通模式通关30次', 'category': '成长', 'reward': 300, 'icon': '🏆', 'condition': lambda p: sum(1 for r in p.game_records if r.get('mode')=='normal' and r.get('completed')) >= 30},
        {'id': 'ultimate_conqueror_30', 'name': '终极精进', 'description': '终极模式通关30次', 'category': '成长', 'reward': 1000, 'icon': '👑', 'condition': lambda p: sum(1 for r in p.game_records if r.get('mode')=='ultimate' and r.get('completed')) >= 30},
        {'id': 'login_total_30', 'name': '常回家看看', 'description': '累计登录天数30（非连续）', 'category': '成长', 'reward': 300, 'icon': '📅', 'condition': lambda p: (datetime.fromtimestamp(getattr(p,'last_login',0)).date() - datetime.fromtimestamp(getattr(p,'created_at',0)).date()).days >= 30},
        {'id': 'item_user_50', 'name': '道具达人', 'description': '累计使用道具50次', 'category': '成长', 'reward': 500, 'icon': '🧰', 'condition': lambda p: sum((sum(r.get('items_used', {}).values()) if isinstance(r.get('items_used', {}), dict) else 0) for r in p.game_records) >= 50},
        {'id': 'flawless_normal', 'name': '零失误·普通', 'description': '普通模式失误数为0通关', 'category': '技术', 'reward': 666, 'icon': '🧠', 'condition': lambda p: any(r.get('completed') and r.get('mode')=='normal' and r.get('mistakes',0)==0 for r in p.game_records)},
        {'id': 'flawless_ultimate', 'name': '零失误·终极', 'description': '终极模式失误数为0通关', 'category': '技术', 'reward': 6666, 'icon': '🧠', 'condition': lambda p: any(r.get('completed') and r.get('mode')=='ultimate' and r.get('mistakes',0)==0 for r in p.game_records)},
        {'id': 'speedrunner_normal_45', 'name': '速通·普通', 'description': '普通模式45秒内通关', 'category': '技术', 'reward': 300, 'icon': '⚡', 'condition': lambda p: any(r.get('completed') and r.get('mode')=='normal' and r.get('time_used',1e9) <= 45 for r in p.game_records)},
        {'id': 'speedrunner_ultimate_80', 'name': '速通·终极', 'description': '终极模式80秒内通关', 'category': '技术', 'reward': 600, 'icon': '⚡', 'condition': lambda p: any(r.get('completed') and r.get('mode')=='ultimate' and r.get('time_used',1e9) <= 80 for r in p.game_records)},
        {'id': 'low_moves_normal_32', 'name': '省步高手', 'description': '普通模式通关步数<=32', 'category': '技术', 'reward': 320, 'icon': '🪜', 'condition': lambda p: any(r.get('completed') and r.get('mode')=='normal' and r.get('moves',1e9) <= 32 for r in p.game_records)},
        {'id': 'no_undo_20', 'name': '撤销？没什么用', 'description': '累计20次在不用撤销的情况下通关', 'category': '技术', 'reward': 400, 'icon': '↩️', 'condition': lambda p: sum(1 for r in p.game_records if r.get('completed') and (r.get('items_used',{}).get('undo',0)==0)) >= 20},
        {'id': 'perfect_combo_normal_50', 'name': '无双·普通', 'description': '普通模式零失误且≤50秒通关', 'category': '技术', 'reward': 666, 'icon': '🎯', 'condition': lambda p: any(r.get('completed') and r.get('mode')=='normal' and r.get('mistakes',0)==0 and r.get('time_used',1e9) <= 50 for r in p.game_records)},
        {'id': 'perfect_combo_ultimate_100', 'name': '无双·终极', 'description': '终极模式零失误且≤100秒通关', 'category': '技术', 'reward': 6666, 'icon': '🎯', 'condition': lambda p: any(r.get('completed') and r.get('mode')=='ultimate' and r.get('mistakes',0)==0 and r.get('time_used',1e9) <= 100 for r in p.game_records)},
        {'id': 'ultimate_no_item_5', 'name': '终极无道具5', 'description': '终极模式无道具通关5次', 'category': '技术', 'reward': 1200, 'icon': '🏅', 'condition': lambda p: sum(1 for r in p.game_records if r.get('completed') and r.get('mode')=='ultimate' and all((r.get('items_used',{}).get(k,0)==0) for k in ['hint','time_extend','shuffle_prevent','undo'])) >= 5},
        {'id': 'win_streak_7', 'name': '七连胜', 'description': '连续通关7场', 'category': '连胜', 'reward': 600, 'icon': '💥', 'condition': lambda p: AchievementConfig.current_win_streak(p) >= 7},
        {'id': 'win_streak_10', 'name': '十连胜', 'description': '连续通关10场', 'category': '连胜', 'reward': 1000, 'icon': '🔥', 'condition': lambda p: AchievementConfig.current_win_streak(p) >= 10},
        {'id': 'ultimate_streak_10', 'name': '终极十连', 'description': '终极模式连续通关10场', 'category': '连胜', 'reward': 800, 'icon': '⚡', 'condition': lambda p: AchievementConfig.current_win_streak_by_mode(p, 'ultimate') >= 10},
        {'id': 'no_item_streak_10', 'name': '无道具十连', 'description': '无道具连续通关10场', 'category': '连胜', 'reward': 500, 'icon': '🛡️', 'condition': lambda p: AchievementConfig.current_win_streak_no_item(p) >= 10},
        {'id': 'login_streak_14', 'name': '活跃签到·14', 'description': '连续登录14天', 'category': '活跃', 'reward': 600, 'icon': '📅', 'condition': lambda p: p.consecutive_days >= 14},
        {'id': 'login_streak_30', 'name': '活跃签到·30', 'description': '连续登录30天', 'category': '活跃', 'reward': 1200, 'icon': '📆', 'condition': lambda p: p.consecutive_days >= 30},
        {'id': 'daily_ten_plays', 'name': '每日十局', 'description': '单日完成10局', 'category': '活跃', 'reward': 200, 'icon': '📈', 'condition': lambda p: AchievementConfig.count_plays_on_day(p, AchievementConfig.last_day(p)) >= 10},
        {'id': 'tool_variety_day_4', 'name': '工具全能', 'description': '单日四种道具各至少使用一次', 'category': '活跃', 'reward': 50, 'icon': '🧩', 'condition': lambda p: AchievementConfig.tools_variety_on_day(p, AchievementConfig.last_day(p))},
        {'id': 'dev_mode_admin', 'name': '误闯天家', 'description': '进入开发者模式', 'category': None, 'reward': 0, 'hidden': True, 'icon': '🗝️'},
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
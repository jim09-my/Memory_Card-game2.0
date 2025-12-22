import os
import sys
import random
from datetime import datetime

# ============== 1. 路径处理工具函数 ==============

def get_app_data_path():
    r"""
    获取跨平台的用户数据存储路径 (用于存放 json 存档)
    Windows: C:\Users\用户名\AppData\Roaming\MemoryCardGame
    """
    app_name = "MemoryCardGame"
    
    if sys.platform == 'win32':
        base_path = os.environ.get('APPDATA')
    else:
        base_path = os.path.expanduser('~/.local/share')
    
    full_path = os.path.join(base_path, app_name)
    
    # 确保目录存在
    if not os.path.exists(full_path):
        try:
            os.makedirs(full_path)
        except Exception as e:
            print(f"Error creating data dir: {e}")
            
    return full_path

def get_resource_path(relative_path):
    """
    获取静态资源绝对路径
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        
    return os.path.join(base_path, relative_path)

# ============== 2. 全局目录配置 ==============
BASE_DATA_DIR = get_app_data_path()
_GLOBAL_DATA_DIR = os.path.join(BASE_DATA_DIR, 'data') 

if not os.path.exists(_GLOBAL_DATA_DIR):
    try: os.makedirs(_GLOBAL_DATA_DIR)
    except: pass

ASSETS_DIR = get_resource_path('assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')

# ============== 3. 游戏参数配置 ==============
class GameConfig:
    NORMAL_GRID = 4
    ULTIMATE_GRID = 6
    NORMAL_TIME_LIMIT = None
    ULTIMATE_TIME_LIMIT = 120
    ULTIMATE_SHUFFLE_TIME_LIMIT = 180
    
    CARD_SIZE = 80 
    CARD_PADDING = 15

    FLIP_ANIMATION_TIME = 250
    MATCH_DELAY = 800
    MISMATCH_DELAY = 1000

# ============== 4. 积分/道具配置 ==============
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
        'undo': {'name': '时间静止', 'description': '在终极模式中冻结时间10秒（仍可翻牌配对）', 'price': 250, 'icon': '\u23f8\ufe0f', 'effect_value': 10}
    }

# ============== 5. 成就配置 ==============
class AchievementConfig:
    @staticmethod
    def current_win_streak(p):
        streak = 0
        records = p.get_all_records() if hasattr(p, 'get_all_records') else list(p.game_records)
        for r in sorted(records, key=lambda x: x.get('timestamp',0), reverse=True):
            if r.get('completed'): streak += 1
            else: break
        return streak
    @staticmethod
    def current_win_streak_by_mode(p, mode):
        streak = 0
        records = p.get_all_records() if hasattr(p, 'get_all_records') else list(p.game_records)
        for r in sorted(records, key=lambda x: x.get('timestamp',0), reverse=True):
            if r.get('completed') and r.get('mode') == mode: streak += 1
            else: break
        return streak
    @staticmethod
    def current_win_streak_by_ultimate(p):
        streak = 0
        records = p.get_all_records() if hasattr(p, 'get_all_records') else list(p.game_records)
        for r in sorted(records, key=lambda x: x.get('timestamp',0), reverse=True):
            if r.get('completed') and r.get('mode') in ('ultimate','ultimate_shuffle'):
                streak += 1
            else:
                break
        return streak
    @staticmethod
    def current_win_streak_no_item(p):
        streak = 0
        records = p.get_all_records() if hasattr(p, 'get_all_records') else list(p.game_records)
        for r in sorted(records, key=lambda x: x.get('timestamp',0), reverse=True):
            iu = r.get('items_used', {})
            if r.get('completed') and all((iu.get(k,0)==0) for k in ['hint','time_extend','shuffle_prevent','undo']):
                streak += 1
            else: break
        return streak
    @staticmethod
    def count_completed_by_mode(p, mode):
        records = p.get_all_records() if hasattr(p, 'get_all_records') else list(p.game_records)
        return sum(1 for r in records if r.get('completed') and r.get('mode') == mode)
    @staticmethod
    def sum_items_used_total(p):
        total = 0
        records = p.get_all_records() if hasattr(p, 'get_all_records') else list(p.game_records)
        for r in records:
            iu = r.get('items_used', {})
            if isinstance(iu, dict):
                total += sum(iu.values())
        return total
    @staticmethod
    def count_no_item_completions(p):
        records = p.get_all_records() if hasattr(p, 'get_all_records') else list(p.game_records)
        return sum(1 for r in records if r.get('completed') and all((r.get('items_used',{}).get(k,0)==0) for k in ['hint','time_extend','shuffle_prevent','undo']))
    @staticmethod
    def has_first_ultimate_win(p):
        records = p.get_all_records() if hasattr(p, 'get_all_records') else list(p.game_records)
        return any(r.get('completed') and r.get('mode') in ('ultimate','ultimate_shuffle') for r in records)
    @staticmethod
    def has_first_item_use(p):
        return AchievementConfig.sum_items_used_total(p) >= 1
    @staticmethod
    def did_break_normal_record(p):
        records = p.get_all_records() if hasattr(p, 'get_all_records') else list(p.game_records)
        if not records:
            return False
        last = records[-1]
        if not last.get('completed') or last.get('mode') != 'normal':
            return False
        last_time = last.get('time_used', 0)
        prev_times = [r.get('time_used', 0) for r in records[:-1] if r.get('completed') and r.get('mode') == 'normal' and r.get('time_used', 0) > 0]
        if not prev_times:
            return False
        return last_time > 0 and last_time < min(prev_times)
    @staticmethod
    def last_record(p):
        records = p.get_all_records() if hasattr(p, 'get_all_records') else list(p.game_records)
        return records[-1] if records else None
    @staticmethod
    def speedrunner_normal_45(p):
        last = AchievementConfig.last_record(p)
        return bool(last and last.get('completed') and last.get('mode') == 'normal' and last.get('time_used', 9999) <= 45)
    @staticmethod
    def speedrunner_ultimate_80(p):
        last = AchievementConfig.last_record(p)
        return bool(last and last.get('completed') and last.get('mode') in ('ultimate','ultimate_shuffle') and last.get('time_used', 9999) <= 80)
    @staticmethod
    def low_moves_normal_32(p):
        last = AchievementConfig.last_record(p)
        return bool(last and last.get('completed') and last.get('mode') == 'normal' and last.get('moves', 9999) <= 32)
    @staticmethod
    def perfect_combo_normal_50(p):
        last = AchievementConfig.last_record(p)
        return bool(last and last.get('completed') and last.get('mode') == 'normal' and last.get('mistakes', 1) == 0 and last.get('time_used', 9999) <= 50)
    @staticmethod
    def perfect_combo_ultimate_100(p):
        last = AchievementConfig.last_record(p)
        return bool(last and last.get('completed') and last.get('mode') in ('ultimate','ultimate_shuffle') and last.get('mistakes', 1) == 0 and last.get('time_used', 9999) <= 100)
    @staticmethod
    def ultimate_no_item_5(p):
        records = p.get_all_records() if hasattr(p, 'get_all_records') else list(p.game_records)
        def no_item(r):
            iu = r.get('items_used', {})
            return isinstance(iu, dict) and sum(iu.values()) == 0
        return sum(1 for r in records if r.get('completed') and r.get('mode') in ('ultimate','ultimate_shuffle') and no_item(r)) >= 5
    @staticmethod
    def total_login_days(p):
        days = getattr(p, 'login_days', None)
        if isinstance(days, (set, list)):
            return len(days)
        return 0
    @staticmethod
    def _day_key(ts):
        try: return datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        except: return None
    @staticmethod
    def last_day(p):
        records = p.get_all_records() if hasattr(p, 'get_all_records') else list(p.game_records)
        if not records: return None
        ts = records[-1].get('timestamp', None)
        return AchievementConfig._day_key(ts) if ts else None
    @staticmethod
    def count_plays_on_day(p, day_key):
        if not day_key: return 0
        records = p.get_all_records() if hasattr(p, 'get_all_records') else list(p.game_records)
        return sum(1 for r in records if AchievementConfig._day_key(r.get('timestamp',0)) == day_key)
    @staticmethod
    def tools_variety_on_day(p, day_key):
        if not day_key: return False
        used = {'hint':0,'time_extend':0,'shuffle_prevent':0,'undo':0}
        records = p.get_all_records() if hasattr(p, 'get_all_records') else list(p.game_records)
        for r in records:
            if AchievementConfig._day_key(r.get('timestamp',0)) != day_key: continue
            iu = r.get('items_used', {})
            for k in list(used.keys()): used[k] += iu.get(k,0)
        return all(v >= 1 for v in used.values())
        
    ACHIEVEMENTS = [
        {'id': 'first_game', 'name': '初次尝试', 'description': '完成第一场游戏', 'category': '入门', 'reward': 100, 'icon': '🎮', 'condition': lambda p: getattr(p, 'total_games', 0) >= 1},
        {'id': 'normal_master', 'name': '普通大师', 'description': '普通模式通关10次', 'category': '入门', 'reward': 300, 'icon': '🏆', 'condition': lambda p: AchievementConfig.count_completed_by_mode(p, 'normal') >= 10},
        {'id': 'ultimate_conqueror', 'name': '终极征服者', 'description': '终极模式通关5次', 'category': '挑战', 'reward': 800, 'icon': '👑', 'condition': lambda p: AchievementConfig.count_completed_by_mode(p, 'ultimate') + AchievementConfig.count_completed_by_mode(p, 'ultimate_shuffle') >= 5},
        {'id': 'persistent_50', 'name': '毅力十足', 'description': '累计游玩50局', 'category': '成长', 'reward': 200, 'icon': '🔁', 'condition': lambda p: getattr(p, 'total_games', 0) >= 50},
        {'id': 'item_user_10', 'name': '工具达人', 'description': '累计使用道具10次', 'category': '活跃', 'reward': 150, 'icon': '🧰', 'condition': lambda p: AchievementConfig.sum_items_used_total(p) >= 10},
        {'id': 'no_item_10', 'name': '清心寡欲', 'description': '无道具通关10次', 'category': '技术', 'reward': 500, 'icon': '🚫', 'condition': lambda p: AchievementConfig.count_no_item_completions(p) >= 10},
        {'id': 'win_streak_3', 'name': '连胜三场', 'description': '连续通关3场', 'category': '连胜', 'reward': 200, 'icon': '💥', 'condition': lambda p: AchievementConfig.current_win_streak(p) >= 3},
        {'id': 'win_streak_5', 'name': '势不可挡', 'description': '连续通关5场', 'category': '连胜', 'reward': 400, 'icon': '⚡', 'condition': lambda p: AchievementConfig.current_win_streak(p) >= 5},
        {'id': 'login_streak_3', 'name': '活跃签到·3', 'description': '连续登录3天', 'category': '活跃', 'reward': 200, 'icon': '📅', 'condition': lambda p: p.consecutive_days >= 3},
        {'id': 'login_streak_7', 'name': '活跃签到·7', 'description': '连续登录7天', 'category': '活跃', 'reward': 500, 'icon': '📆', 'condition': lambda p: p.consecutive_days >= 7},
        {'id': 'first_win', 'name': '首胜加冕', 'description': '首次通关任意模式', 'category': '入门', 'reward': 50, 'icon': '🥇', 'condition': lambda p: p.completed_games >= 1},
        {'id': 'first_ultimate_win', 'name': '初试终极', 'description': '首次通关终极模式', 'category': '入门', 'reward': 75, 'icon': '🧗', 'condition': lambda p: AchievementConfig.has_first_ultimate_win(p)},
        {'id': 'first_item_use', 'name': '初用道具', 'description': '首次使用任意道具', 'category': '入门', 'reward': 10, 'icon': '🧰', 'condition': lambda p: AchievementConfig.has_first_item_use(p)},
        {'id': 'record_break_normal', 'name': '打破个人纪录', 'description': '刷新普通模式个人最佳用时', 'category': '入门', 'reward': 100, 'icon': '⏱️', 'condition': lambda p: AchievementConfig.did_break_normal_record(p)},
        {'id': 'persistent_100', 'name': '百战不殆', 'description': '累计游玩100局', 'category': '成长', 'reward': 300, 'icon': '📈', 'condition': lambda p: getattr(p, 'total_games', 0) >= 100},
        {'id': 'points_5000', 'name': '千分达人', 'description': '累计获得积分达到5000', 'category': '成长', 'reward': 500, 'icon': '💎', 'condition': lambda p: getattr(p, 'total_points_earned', 0) >= 5000},
        {'id': 'normal_master_30', 'name': '普通老练', 'description': '普通模式通关30次', 'category': '成长', 'reward': 300, 'icon': '🏆', 'condition': lambda p: AchievementConfig.count_completed_by_mode(p, 'normal') >= 30},
        {'id': 'ultimate_conqueror_30', 'name': '终极精进', 'description': '终极模式通关30次', 'category': '成长', 'reward': 1000, 'icon': '👑', 'condition': lambda p: AchievementConfig.count_completed_by_mode(p, 'ultimate') + AchievementConfig.count_completed_by_mode(p, 'ultimate_shuffle') >= 30},
        {'id': 'login_total_30', 'name': '常回家看看', 'description': '累计登录天数30（非连续）', 'category': '成长', 'reward': 300, 'icon': '📅', 'condition': lambda p: AchievementConfig.total_login_days(p) >= 30},
        {'id': 'item_user_50', 'name': '道具达人', 'description': '累计使用道具50次', 'category': '成长', 'reward': 500, 'icon': '🧰', 'condition': lambda p: AchievementConfig.sum_items_used_total(p) >= 50},
        {'id': 'flawless_normal', 'name': '零失误·普通', 'description': '普通模式失误数为0通关', 'category': '技术', 'reward': 666, 'icon': '🧠', 'condition': lambda p: any(r.get('completed') and r.get('mode')=='normal' and r.get('mistakes',1)==0 for r in (p.get_all_records() if hasattr(p,'get_all_records') else list(p.game_records)))},
        {'id': 'flawless_ultimate', 'name': '零失误·终极', 'description': '终极模式失误数为0通关', 'category': '技术', 'reward': 6666, 'icon': '🧠', 'condition': lambda p: any(r.get('completed') and r.get('mode') in ('ultimate','ultimate_shuffle') and r.get('mistakes',1)==0 for r in (p.get_all_records() if hasattr(p,'get_all_records') else list(p.game_records)))},
        {'id': 'speedrunner_normal_45', 'name': '速通·普通', 'description': '普通模式45秒内通关', 'category': '技术', 'reward': 300, 'icon': '⚡', 'condition': lambda p: AchievementConfig.speedrunner_normal_45(p)},
        {'id': 'speedrunner_ultimate_80', 'name': '速通·终极', 'description': '终极模式80秒内通关', 'category': '技术', 'reward': 600, 'icon': '⚡', 'condition': lambda p: AchievementConfig.speedrunner_ultimate_80(p)},
        {'id': 'low_moves_normal_32', 'name': '省步高手', 'description': '普通模式通关步数<=32', 'category': '技术', 'reward': 320, 'icon': '🪜', 'condition': lambda p: AchievementConfig.low_moves_normal_32(p)},
        {'id': 'perfect_combo_normal_50', 'name': '无双·普通', 'description': '普通模式零失误且≤50秒通关', 'category': '技术', 'reward': 666, 'icon': '🎯', 'condition': lambda p: AchievementConfig.perfect_combo_normal_50(p)},
        {'id': 'perfect_combo_ultimate_100', 'name': '无双·终极', 'description': '终极模式零失误且≤100秒通关', 'category': '技术', 'reward': 6666, 'icon': '🎯', 'condition': lambda p: AchievementConfig.perfect_combo_ultimate_100(p)},
        {'id': 'ultimate_no_item_5', 'name': '终极无道具5', 'description': '终极模式无道具通关5次', 'category': '技术', 'reward': 1200, 'icon': '🏅', 'condition': lambda p: AchievementConfig.ultimate_no_item_5(p)},
        {'id': 'win_streak_7', 'name': '七连胜', 'description': '连续通关7场', 'category': '连胜', 'reward': 600, 'icon': '💥', 'condition': lambda p: AchievementConfig.current_win_streak(p) >= 7},
        {'id': 'win_streak_10', 'name': '十连胜', 'description': '连续通关10场', 'category': '连胜', 'reward': 1000, 'icon': '🔥', 'condition': lambda p: AchievementConfig.current_win_streak(p) >= 10},
        {'id': 'ultimate_streak_10', 'name': '终极十连', 'description': '终极模式连续通关10场', 'category': '连胜', 'reward': 800, 'icon': '⚡', 'condition': lambda p: AchievementConfig.current_win_streak_by_ultimate(p) >= 10},
        {'id': 'no_item_streak_10', 'name': '无道具十连', 'description': '无道具连续通关10场', 'category': '连胜', 'reward': 500, 'icon': '🛡️', 'condition': lambda p: AchievementConfig.current_win_streak_no_item(p) >= 10},
        {'id': 'login_streak_14', 'name': '活跃签到·14', 'description': '连续登录14天', 'category': '活跃', 'reward': 600, 'icon': '📅', 'condition': lambda p: p.consecutive_days >= 14},
        {'id': 'login_streak_30', 'name': '活跃签到·30', 'description': '连续登录30天', 'category': '活跃', 'reward': 1200, 'icon': '📆', 'condition': lambda p: p.consecutive_days >= 30},
        {'id': 'daily_ten_plays', 'name': '每日十局', 'description': '单日完成10局', 'category': '活跃', 'reward': 200, 'icon': '📈', 'condition': lambda p: AchievementConfig.count_plays_on_day(p, AchievementConfig.last_day(p)) >= 10},
        {'id': 'tool_variety_day_4', 'name': '工具全能', 'description': '单日四种道具各至少使用一次', 'category': '活跃', 'reward': 50, 'icon': '🧩', 'condition': lambda p: AchievementConfig.tools_variety_on_day(p, AchievementConfig.last_day(p))},
        {'id': 'dev_mode_admin', 'name': '误闯天家', 'description': '进入开发者模式', 'category': None, 'reward': 0, 'hidden': True, 'icon': '🗝️'},
    ]

# ============== 6. 界面配置 ==============
class UIConfig:
    WINDOW_WIDTH = 1100
    WINDOW_HEIGHT = 850

    COLORS = {
        'primary': '#2896A0',      
        'primary_dark': '#1E7882', 
        
        'bg_light': '#E0F7FA',     
        'text_dark': '#263238',    
        'text_light': '#FFFFFF',   
        
        'card_back_bg': '#FFCD3C', 
        'card_back_icon': '#FFF5E0', 
        'card_front': '#FFFFFF',   
        'card_border_white': '#FFFFFF', 
        
        'success_glow': '#32FF64', 
        'danger': '#FF5252',
        
        'text_red': '#E74C3C',     
        'text_black': '#2C3E50'    
    }

    FONTS = {
        'title': ('Arial Rounded MT Bold', 28, 'bold'),
        'heading': ('Arial Rounded MT Bold', 18, 'bold'),
        'normal': ('Arial', 12),
        'card_main': ('Times New Roman', 32, 'bold'),
        'card_corner': ('Arial', 11, 'bold'),
        'button': ('Arial Rounded MT Bold', 13)
    }

# ============== 7. 扑克牌配置 ==============
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

# ============== 8. 数据文件路径定义 ==============
class DataConfig:
    DATA_DIR = _GLOBAL_DATA_DIR 
    
    PLAYERS_FILE = os.path.join(DATA_DIR, 'players.json')
    RECORDS_FILE = os.path.join(DATA_DIR, 'records.json')
    ACHIEVEMENTS_FILE = os.path.join(DATA_DIR, 'achievements.json')
    SHOP_FILE = os.path.join(DATA_DIR, 'shop_items.json')
    SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')

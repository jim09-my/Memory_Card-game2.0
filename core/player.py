"""
玩家类 - 完整数据结构版
使用：Queue（游戏记录）、HashTable（道具库存）、Heap（最佳成绩 Top N）
"""

import json
import time
from datetime import datetime, timedelta

# === 导入自定义数据结构 ===
from data_structures.queue import Queue
from data_structures.hash_table import ItemInventory
from data_structures.heap import TopNRecords  # <--- 新增：使用堆来管理最佳记录

class Player:
    """玩家类"""

    def __init__(self, username, password=''):
        """
        初始化玩家（邮箱字段已移除）
        :param username: 用户名
        :param password: 登录密码
        """
        self.username = username
        self.password = password
        self.points = 500  # 初始积分
        self.level = 1
        self.experience = 0
        self.total_points_earned = 0  # 累计获得的积分

        # 游戏统计
        self.total_games = 0
        self.completed_games = 0
        self.total_moves = 0
        self.total_time = 0
        
        # === 使用 Heap (TopNRecords) 管理最佳成绩 (Top 5) ===
        # 以前只是 best_time_normal = None，现在我们用最小堆保留前5个最快时间
        self.best_records_normal = TopNRecords(n=5, mode='min')
        self.best_records_ultimate = TopNRecords(n=5, mode='min')

        # === 使用 Queue 管理游戏记录 ===
        self.game_records = Queue(max_size=50)

        # === 使用 HashTable 管理道具库存 ===
        self.items = ItemInventory()

        # 成就列表
        self.achievements = []

        # 福利状态
        self.benefits = {
            'free_hint_redeemed': False
        }

        # 登录信息
        self.created_at = time.time()
        self.last_login = time.time()
        self.consecutive_days = 1
        # 新增：登录历史（用于非连续累计登录判定）
        try:
            today_key = datetime.now().strftime('%Y-%m-%d')
        except Exception:
            today_key = None
        self.login_days = set([today_key]) if today_key else set()

        # 监听器（用于 UI 更新等）
        self._listeners = []

    def add_game_record(self, record):
        """添加游戏记录（使用 Queue 和 Heap）"""
        record['timestamp'] = time.time()
        
        # 1. 入队 (Queue)
        self.game_records.enqueue(record)

        # 更新统计
        self.total_games += 1
        if record.get('completed'):
            self.completed_games += 1

        self.total_moves += record.get('moves', 0)
        self.total_time += record.get('time_used', 0)

        # 2. 更新最佳成绩 (Heap)
        if record.get('completed'):
            mode = record.get('mode')
            time_used = record.get('time_used', 0)
            
            # 只有当时间有效时才记录
            if time_used > 0:
                if mode == 'normal':
                    # 将时间作为 key 插入堆中，记录本身作为 data
                    self.best_records_normal.add_record(time_used, record)
                elif mode == 'ultimate' or mode == 'ultimate_shuffle':
                    self.best_records_ultimate.add_record(time_used, record)

        try:
            self._notify_listeners()
        except Exception:
            pass

    def get_all_records(self):
        """获取所有游戏记录（返回列表）"""
        # Queue 对象不可迭代，必须调用 to_list()
        return self.game_records.to_list()

    def add_points(self, amount):
        self.points += amount
        self.total_points_earned += amount
        self._update_level()
        print(f"{self.username} 获得 {amount} 积分，当前: {self.points}")
        try:
            self._notify_listeners()
        except Exception:
            pass

    def deduct_points(self, amount):
        if self.points >= amount:
            self.points -= amount
            print(f"{self.username} 消耗 {amount} 积分，剩余: {self.points}")
            try:
                self._notify_listeners()
            except Exception:
                pass
            return True
        else:
            print(f"{self.username} 积分不足！需要 {amount}，当前 {self.points}")
            return False

    def _update_level(self):
        new_level = self.total_points_earned // 1000 + 1
        if new_level > self.level:
            old_level = self.level
            self.level = new_level
            print(f"🎉 恭喜升级！{old_level} -> {self.level}")

    def add_item(self, item_id, quantity=1):
        """添加道具（使用 HashTable）"""
        self.items.add_item(item_id, quantity)
        try:
            self._notify_listeners()
        except Exception:
            pass

    def use_item(self, item_id, quantity=1):
        """使用道具（使用 HashTable）"""
        success = self.items.use_item(item_id, quantity)
        if success:
            try:
                self._notify_listeners()
            except Exception:
                pass
        return success

    def get_item_count(self, item_id):
        """获取道具数量（使用 HashTable）"""
        return self.items.get_item_count(item_id)

    def has_item(self, item_id, quantity=1):
        """检查是否拥有道具（使用 HashTable）"""
        return self.items.has_item(item_id, quantity)

    def add_change_listener(self, callback):
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_change_listener(self, callback):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_listeners(self):
        for cb in list(self._listeners):
            try:
                cb()
            except Exception as e:
                print(f"Listener error: {e}")

    def can_claim_free_hint(self):
        if self.benefits.get('free_hint_redeemed'):
            return False
        seven_days = 7 * 24 * 60 * 60
        return (time.time() - self.created_at) <= seven_days

    def mark_free_hint_redeemed(self):
        self.benefits['free_hint_redeemed'] = True

    def unlock_achievement(self, achievement_id):
        if achievement_id not in self.achievements:
            self.achievements.append(achievement_id)
            print(f"🏆 {self.username} 解锁成就: {achievement_id}")
            try:
                self._notify_listeners()
            except Exception:
                pass
            return True
        return False

    def has_achievement(self, achievement_id):
        return achievement_id in self.achievements

    def get_win_rate(self):
        if self.total_games == 0:
            return 0
        return self.completed_games / self.total_games * 100

    def get_average_time(self):
        if self.completed_games == 0:
            return 0
        # 修正：调用 get_all_records() 而不是直接访问 queue
        records_list = self.get_all_records()
        total_completed_time = sum(r.get('time_used', 0) for r in records_list if r.get('completed'))
        return total_completed_time / self.completed_games

    def get_average_moves(self):
        if self.total_games == 0:
            return 0
        return self.total_moves / self.total_games

    def update_login(self):
        now = time.time()
        last_login_date = datetime.fromtimestamp(self.last_login).date()
        today = datetime.now().date()

        days_diff = (today - last_login_date).days

        if days_diff == 1:
            self.consecutive_days += 1
            print(f"连续登录 {self.consecutive_days} 天")
        elif days_diff > 1:
            self.consecutive_days = 1
            print("连续登录已重置")

        self.last_login = now
        # 记录登录日期到历史集合
        try:
            self.login_days.add(today.strftime('%Y-%m-%d'))
        except Exception:
            pass

    def get_statistics(self):
        # 从堆中获取最佳记录
        best_normal_record = self.best_records_normal.get_best()
        best_normal_time = best_normal_record[0] if best_normal_record else None
        
        best_ultimate_record = self.best_records_ultimate.get_best()
        best_ultimate_time = best_ultimate_record[0] if best_ultimate_record else None

        return {
            'username': self.username,
            'level': self.level,
            'points': self.points,
            'total_points_earned': self.total_points_earned,
            'total_games': self.total_games,
            'completed_games': self.completed_games,
            'win_rate': self.get_win_rate(),
            'average_time': self.get_average_time(),
            'average_moves': self.get_average_moves(),
            'best_time_normal': best_normal_time,
            'best_time_ultimate': best_ultimate_time,
            'consecutive_days': self.consecutive_days,
            'achievement_count': len(self.achievements)
        }

    def to_dict(self):
        """序列化（将数据结构转为 JSON 兼容格式）"""
        return {
            'username': self.username,
            'password': self.password,
            'points': self.points,
            'level': self.level,
            'experience': self.experience,
            'total_points_earned': self.total_points_earned,
            'total_games': self.total_games,
            'completed_games': self.completed_games,
            'total_moves': self.total_moves,
            'total_time': self.total_time,
            # 保存堆数据 (TopNRecords -> List)
            'best_records_normal': self.best_records_normal.get_top_n(), 
            'best_records_ultimate': self.best_records_ultimate.get_top_n(),
            'items': dict(self.items.get_all_items()),  # HashTable -> dict
            'achievements': self.achievements,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'consecutive_days': self.consecutive_days,
            'game_records': self.game_records.to_list(),  # Queue -> list
            'benefits': self.benefits
            , 'login_days': sorted(list(self.login_days))
        }

    @classmethod
    def from_dict(cls, data):
        """反序列化（从 dict 恢复数据结构）"""
        # 兼容旧数据：旧数据可能包含 'email' 字段，但构造函数已移除该参数
        player = cls(data['username'], data.get('password', ''))
        player.points = data.get('points', 500)
        player.level = data.get('level', 1)
        player.experience = data.get('experience', 0)
        player.total_points_earned = data.get('total_points_earned', 0)
        player.total_games = data.get('total_games', 0)
        player.completed_games = data.get('completed_games', 0)
        player.total_moves = data.get('total_moves', 0)
        player.total_time = data.get('total_time', 0)

        # 恢复最佳记录堆
        # 注意：JSON中保存的是 [(time, record), ...] 列表
        best_normal_list = data.get('best_records_normal', [])
        for val, rec in best_normal_list:
            player.best_records_normal.add_record(val, rec)
            
        best_ultimate_list = data.get('best_records_ultimate', [])
        for val, rec in best_ultimate_list:
            player.best_records_ultimate.add_record(val, rec)
            
        # 兼容旧数据：如果堆为空但有旧的 best_time 字段
        if player.best_records_normal.heap.is_empty() and data.get('best_time_normal'):
            player.best_records_normal.add_record(data['best_time_normal'], {})
        if player.best_records_ultimate.heap.is_empty() and data.get('best_time_ultimate'):
             player.best_records_ultimate.add_record(data['best_time_ultimate'], {})

        # 恢复道具（dict -> HashTable）
        items_dict = data.get('items', {})
        player.items = ItemInventory()
        for item_id, quantity in items_dict.items():
            player.items.add_item(item_id, quantity)
        
        player.achievements = data.get('achievements', [])
        player.created_at = data.get('created_at', time.time())
        player.last_login = data.get('last_login', time.time())
        player.consecutive_days = data.get('consecutive_days', 1)
        try:
            player.login_days = set(data.get('login_days', []))
        except Exception:
            player.login_days = set()
        
        # 恢复游戏记录（list -> Queue）
        records_list = data.get('game_records', [])
        player.game_records = Queue(max_size=50)
        for record in records_list:
            player.game_records.enqueue(record)
        
        player.benefits = data.get('benefits', {'free_hint_redeemed': False})
        return player

    def save_to_file(self, filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"玩家数据已保存: {filepath}")

    @classmethod
    def load_from_file(cls, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"玩家数据已加载: {filepath}")
        return cls.from_dict(data)

    def __str__(self):
        return f"Player({self.username}, Lv.{self.level}, {self.points}分)"

    def __repr__(self):
        return self.__str__()

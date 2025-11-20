"""
玩家类
管理玩家数据和状态
"""

import json
import time
from datetime import datetime, timedelta


class Player:
    """玩家类"""

    def __init__(self, username, password='', email=''):
        """
        初始化玩家
        :param username: 用户名
        :param password: 登录密码
        :param email: 邮箱（兼容旧数据）
        """
        self.username = username
        self.password = password
        self.email = email
        self.points = 500  # 初始积分
        self.level = 1
        self.experience = 0
        self.total_points_earned = 0  # 累计获得的积分

        # 游戏统计
        self.total_games = 0
        self.completed_games = 0
        self.total_moves = 0
        self.total_time = 0
        self.best_time_normal = None
        self.best_time_ultimate = None

        # 道具库存
        self.items = {}

        # 成就
        self.achievements = []

        # 福利状态
        self.benefits = {
            'free_hint_redeemed': False
        }

        # 登录信息
        self.created_at = time.time()
        self.last_login = time.time()
        self.consecutive_days = 1

        # 游戏记录
        self.game_records = []

        # 监听器（用于 UI 更新等）
        self._listeners = []
    def add_points(self, amount):
        """
        增加积分
        :param amount: 积分数量
        """
        self.points += amount
        self.total_points_earned += amount
        self._update_level()
        print(f"{self.username} 获得 {amount} 积分，当前: {self.points}")
        # 通知监听器（例如界面或持久化）
        try:
            self._notify_listeners()
        except Exception:
            pass

    def deduct_points(self, amount):
        """
        扣除积分
        :param amount: 积分数量
        :return: 是否成功
        """
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
        """更新等级（基于经验值）"""
        # 每1000积分提升1级
        new_level = self.total_points_earned // 1000 + 1
        if new_level > self.level:
            old_level = self.level
            self.level = new_level
            print(f"🎉 恭喜升级！{old_level} -> {self.level}")

    def add_item(self, item_id, quantity=1):
        """
        添加道具
        :param item_id: 道具ID
        :param quantity: 数量
        """
        if item_id in self.items:
            self.items[item_id] += quantity
        else:
            self.items[item_id] = quantity
        print(f"{self.username} 获得道具 {item_id} x{quantity}")
        # 通知监听器（例如界面）更新
        try:
            self._notify_listeners()
        except Exception:
            pass

    def use_item(self, item_id, quantity=1):
        """
        使用道具
        :param item_id: 道具ID
        :param quantity: 数量
        :return: 是否成功
        """
        if item_id not in self.items or self.items[item_id] < quantity:
            print(f"{self.username} 道具 {item_id} 不足")
            return False

        self.items[item_id] -= quantity
        if self.items[item_id] == 0:
            del self.items[item_id]

        print(f"{self.username} 使用道具 {item_id} x{quantity}")
        # 通知监听器（例如界面）更新
        try:
            self._notify_listeners()
        except Exception:
            pass
        return True

    # ----------------- 监听器接口 -----------------
    def add_change_listener(self, callback):
        """注册变更监听器，callback 不带参数。"""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_change_listener(self, callback):
        """移除已注册的监听器。"""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_listeners(self):
        """通知所有监听器（安全调用）。"""
        for cb in list(self._listeners):
            try:
                cb()
            except Exception as e:
                print(f"Listener error: {e}")

    def can_claim_free_hint(self):
        """检查新手免费提示是否可用（注册7天内且未领取）"""
        if self.benefits.get('free_hint_redeemed'):
            return False
        seven_days = 7 * 24 * 60 * 60
        return (time.time() - self.created_at) <= seven_days

    def mark_free_hint_redeemed(self):
        """标记已领取新手免费提示"""
        self.benefits['free_hint_redeemed'] = True

    def get_item_count(self, item_id):
        """获取道具数量"""
        return self.items.get(item_id, 0)

    def has_item(self, item_id, quantity=1):
        """检查是否拥有道具"""
        return self.get_item_count(item_id) >= quantity

    def unlock_achievement(self, achievement_id):
        """
        解锁成就
        :param achievement_id: 成就ID
        """
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
        """检查是否拥有成就"""
        return achievement_id in self.achievements

    def add_game_record(self, record):
        """
        添加游戏记录
        :param record: 游戏记录字典
        """
        record['timestamp'] = time.time()
        self.game_records.append(record)

        # 更新统计
        self.total_games += 1
        if record.get('completed'):
            self.completed_games += 1

        self.total_moves += record.get('moves', 0)
        self.total_time += record.get('time_used', 0)

        # 更新最佳成绩
        if record.get('completed'):
            mode = record.get('mode')
            time_used = record.get('time_used', 0)

            if mode == 'normal':
                if self.best_time_normal is None or time_used < self.best_time_normal:
                    self.best_time_normal = time_used
                    print(f"🎉 打破普通模式记录: {time_used}秒")
            elif mode == 'ultimate':
                if self.best_time_ultimate is None or time_used < self.best_time_ultimate:
                    self.best_time_ultimate = time_used
                    print(f"🎉 打破终极模式记录: {time_used}秒")

        # 保持最近50条记录
        if len(self.game_records) > 50:
            self.game_records = self.game_records[-50:]
        # 通知监听器并尝试持久化
        try:
            self._notify_listeners()
        except Exception:
            pass

    def get_win_rate(self):
        """获取胜率"""
        if self.total_games == 0:
            return 0
        return self.completed_games / self.total_games * 100

    def get_average_time(self):
        """获取平均用时"""
        if self.completed_games == 0:
            return 0
        return self.total_time / self.completed_games

    def get_average_moves(self):
        """获取平均步数"""
        if self.total_games == 0:
            return 0
        return self.total_moves / self.total_games

    def update_login(self):
        """更新登录信息"""
        now = time.time()
        last_login_date = datetime.fromtimestamp(self.last_login).date()
        today = datetime.now().date()

        days_diff = (today - last_login_date).days

        if days_diff == 1:
            # 连续登录
            self.consecutive_days += 1
            print(f"连续登录 {self.consecutive_days} 天")
        elif days_diff > 1:
            # 断签
            self.consecutive_days = 1
            print("连续登录已重置")

        self.last_login = now

    def get_statistics(self):
        """获取统计信息"""
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
            'best_time_normal': self.best_time_normal,
            'best_time_ultimate': self.best_time_ultimate,
            'consecutive_days': self.consecutive_days,
            'achievement_count': len(self.achievements)
        }

    def to_dict(self):
        """转换为字典"""
        return {
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'points': self.points,
            'level': self.level,
            'experience': self.experience,
            'total_points_earned': self.total_points_earned,
            'total_games': self.total_games,
            'completed_games': self.completed_games,
            'total_moves': self.total_moves,
            'total_time': self.total_time,
            'best_time_normal': self.best_time_normal,
            'best_time_ultimate': self.best_time_ultimate,
            'items': self.items,
            'achievements': self.achievements,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'consecutive_days': self.consecutive_days,
            'game_records': self.game_records,
            'benefits': self.benefits
        }

    @classmethod
    def from_dict(cls, data):
        """从字典创建玩家"""
        player = cls(data['username'], data.get('password', ''), data.get('email', ''))
        player.points = data.get('points', 500)
        player.level = data.get('level', 1)
        player.experience = data.get('experience', 0)
        player.total_points_earned = data.get('total_points_earned', 0)
        player.total_games = data.get('total_games', 0)
        player.completed_games = data.get('completed_games', 0)
        player.total_moves = data.get('total_moves', 0)
        player.total_time = data.get('total_time', 0)
        player.best_time_normal = data.get('best_time_normal')
        player.best_time_ultimate = data.get('best_time_ultimate')
        player.items = data.get('items', {})
        player.achievements = data.get('achievements', [])
        player.created_at = data.get('created_at', time.time())
        player.last_login = data.get('last_login', time.time())
        player.consecutive_days = data.get('consecutive_days', 1)
        player.game_records = data.get('game_records', [])
        player.benefits = data.get('benefits', {'free_hint_redeemed': False})
        return player

    def save_to_file(self, filepath):
        """保存到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"玩家数据已保存: {filepath}")

    @classmethod
    def load_from_file(cls, filepath):
        """从文件加载"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"玩家数据已加载: {filepath}")
        return cls.from_dict(data)

    def __str__(self):
        """字符串表示"""
        return f"Player({self.username}, Lv.{self.level}, {self.points}分)"

    def __repr__(self):
        return self.__str__()


# ============== 测试代码 ==============
if __name__ == '__main__':
    print("=" * 50)
    print("玩家类测试")
    print("=" * 50)

    # 创建玩家
    player = Player("TestPlayer", "test@example.com")

    print(f"\n1. 玩家信息: {player}")

    # 测试积分
    print("\n2. 积分测试：")
    player.add_points(500)
    player.deduct_points(200)

    # 测试道具
    print("\n3. 道具测试：")
    player.add_item('hint', 5)
    player.add_item('time_extend', 3)
    player.use_item('hint', 2)
    print(f"   提示道具剩余: {player.get_item_count('hint')}")

    # 测试成就
    print("\n4. 成就测试：")
    player.unlock_achievement('first_win')
    player.unlock_achievement('speed_king')
    print(f"   成就数量: {len(player.achievements)}")

    # 测试游戏记录
    print("\n5. 游戏记录测试：")
    for i in range(5):
        record = {
            'mode': 'normal' if i % 2 == 0 else 'ultimate',
            'completed': i % 3 != 0,
            'time_used': 60 + i * 10,
            'moves': 20 + i * 2
        }
        player.add_game_record(record)

    # 统计信息
    print("\n6. 统计信息：")
    stats = player.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # 保存和加载
    print("\n7. 保存和加载测试：")
    import os

    test_file = 'test_player.json'
    player.save_to_file(test_file)

    loaded_player = Player.load_from_file(test_file)
    print(f"   加载的玩家: {loaded_player}")
    print(f"   积分: {loaded_player.points}")

    # 清理测试文件
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"   已删除测试文件")

"""
哈希表数据结构实现
用于：玩家信息快速查找、道具管理、成就系统
"""


class HashNode:
    """哈希表节点"""

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None  # 用于链地址法解决冲突


class HashTable:
    """
    哈希表实现
    """

    def __init__(self, capacity=100):
        """
        初始化哈希表
        """
        self.capacity = capacity
        self.size = 0
        self.table = [None] * capacity
        self.load_factor_threshold = 0.75

    def _hash(self, key):
        """
        哈希函数
        """
        if isinstance(key, int):
            return key % self.capacity
        elif isinstance(key, str):
            # 字符串哈希：使用多项式滚动哈希
            hash_value = 0
            for i, char in enumerate(key):
                hash_value += ord(char) * (31 ** i)
            return hash_value % self.capacity
        else:
            # 其他类型：使用Python内置hash
            return hash(key) % self.capacity

    def _rehash(self):
        """
        重新哈希（扩容）
        """
        print(f"重新哈希：容量从 {self.capacity} 扩大到 {self.capacity * 2}")

        old_table = self.table
        self.capacity *= 2
        self.table = [None] * self.capacity
        self.size = 0

        # 重新插入所有元素
        for head in old_table:
            current = head
            while current:
                self.put(current.key, current.value)
                current = current.next

    def get_load_factor(self):
        """获取负载因子"""
        return self.size / self.capacity

    def put(self, key, value):
        """
        插入或更新键值对
        """
        # 检查是否需要扩容
        if self.get_load_factor() > self.load_factor_threshold:
            self._rehash()

        index = self._hash(key)
        head = self.table[index]

        # 检查键是否已存在（更新）
        current = head
        while current:
            if current.key == key:
                current.value = value
                return
            current = current.next

        # 键不存在，插入新节点（头插法）
        new_node = HashNode(key, value)
        new_node.next = head
        self.table[index] = new_node
        self.size += 1

    def get(self, key):
        """
        获取值
        """
        index = self._hash(key)
        current = self.table[index]

        while current:
            if current.key == key:
                return current.value
            current = current.next

        return None

    def contains(self, key):
        """
        检查键是否存在
        """
        return self.get(key) is not None

    def remove(self, key):
        """
        删除键值对
        """
        index = self._hash(key)
        head = self.table[index]

        if head is None:
            return False

        # 删除头节点
        if head.key == key:
            self.table[index] = head.next
            self.size -= 1
            return True

        # 删除其他节点
        current = head
        while current.next:
            if current.next.key == key:
                current.next = current.next.next
                self.size -= 1
                return True
            current = current.next

        return False

    def keys(self):
        """
        获取所有键
        """
        result = []
        for head in self.table:
            current = head
            while current:
                result.append(current.key)
                current = current.next
        return result

    def values(self):
        """
        获取所有值
        """
        result = []
        for head in self.table:
            current = head
            while current:
                result.append(current.value)
                current = current.next
        return result

    def items(self):
        """
        获取所有键值对
        """
        result = []
        for head in self.table:
            current = head
            while current:
                result.append((current.key, current.value))
                current = current.next
        return result

    def clear(self):
        """清空哈希表"""
        self.table = [None] * self.capacity
        self.size = 0

    def get_size(self):
        """获取元素数量"""
        return self.size

    def is_empty(self):
        """检查是否为空"""
        return self.size == 0

    def get_statistics(self):
        """
        获取哈希表统计信息
        """
        # 计算链长度分布
        chain_lengths = []
        max_chain_length = 0
        empty_buckets = 0

        for head in self.table:
            length = 0
            current = head
            while current:
                length += 1
                current = current.next

            chain_lengths.append(length)
            max_chain_length = max(max_chain_length, length)
            if length == 0:
                empty_buckets += 1

        avg_chain_length = sum(chain_lengths) / len(chain_lengths)

        return {
            'capacity': self.capacity,
            'size': self.size,
            'load_factor': self.get_load_factor(),
            'empty_buckets': empty_buckets,
            'max_chain_length': max_chain_length,
            'avg_chain_length': avg_chain_length
        }

    def __str__(self):
        """字符串表示"""
        if self.is_empty():
            return "HashTable(empty)"
        return f"HashTable(size={self.size}, capacity={self.capacity}, load_factor={self.get_load_factor():.2f})"

    def __len__(self):
        return self.size

    def __getitem__(self, key):
        value = self.get(key)
        if value is None:
            raise KeyError(f"Key '{key}' not found")
        return value

    def __setitem__(self, key, value):
        self.put(key, value)

    def __delitem__(self, key):
        if not self.remove(key):
            raise KeyError(f"Key '{key}' not found")

    def __contains__(self, key):
        return self.contains(key)


# ============== 应用示例类 ==============

class PlayerDatabase:
    """
    玩家数据库
    使用哈希表快速存储和查找玩家信息
    """

    def __init__(self):
        self.players = HashTable(capacity=50)

    def add_player(self, username, player_data):
        """
        添加玩家
        :param username: 用户名
        :param player_data: 玩家数据字典
        """
        if self.players.contains(username):
            print(f"玩家 {username} 已存在，将更新数据")

        self.players.put(username, player_data)
        print(f"添加玩家: {username}")

    def get_player(self, username):
        """
        获取玩家信息
        :param username: 用户名
        :return: 玩家数据，不存在返回None
        """
        return self.players.get(username)

    def update_player(self, username, updates):
        """
        更新玩家信息
        :param username: 用户名
        :param updates: 更新的字段字典
        :return: 成功返回True，失败返回False
        """
        player = self.players.get(username)
        if player is None:
            print(f"玩家 {username} 不存在")
            return False

        player.update(updates)
        self.players.put(username, player)
        print(f"更新玩家 {username}: {updates}")
        return True

    def remove_player(self, username):
        """
        删除玩家
        :param username: 用户名
        :return: 成功返回True，失败返回False
        """
        if self.players.remove(username):
            print(f"删除玩家: {username}")
            return True
        else:
            print(f"玩家 {username} 不存在")
            return False

    def player_exists(self, username):
        """检查玩家是否存在"""
        return self.players.contains(username)

    def get_all_players(self):
        """获取所有玩家"""
        return self.players.items()

    def get_player_count(self):
        """获取玩家数量"""
        return self.players.get_size()

    def search_by_points(self, min_points):
        """
        按积分搜索玩家
        :param min_points: 最小积分
        :return: 符合条件的玩家列表
        """
        result = []
        for username, data in self.players.items():
            if data.get('points', 0) >= min_points:
                result.append((username, data))
        return result

    def get_top_players(self, n=10):
        """
        获取积分最高的N个玩家
        :param n: 数量
        :return: 玩家列表（已排序）
        """
        all_players = self.players.items()
        sorted_players = sorted(all_players,
                                key=lambda x: x[1].get('points', 0),
                                reverse=True)
        return sorted_players[:n]


class ItemInventory:
    """
    道具库存管理
    使用哈希表管理玩家道具
    """

    def __init__(self):
        self.inventory = HashTable(capacity=20)

    def add_item(self, item_id, quantity=1):
        """
        添加道具
        :param item_id: 道具ID
        :param quantity: 数量
        """
        current_quantity = self.inventory.get(item_id)
        if current_quantity is None:
            self.inventory.put(item_id, quantity)
            print(f"获得道具 {item_id} x{quantity}")
        else:
            self.inventory.put(item_id, current_quantity + quantity)
            print(f"道具 {item_id} 数量增加 {quantity}，当前: {current_quantity + quantity}")

    def use_item(self, item_id, quantity=1):
        """
        使用道具
        :param item_id: 道具ID
        :param quantity: 数量
        :return: 成功返回True，失败返回False
        """
        current_quantity = self.inventory.get(item_id)
        if current_quantity is None or current_quantity < quantity:
            print(f"道具 {item_id} 不足")
            return False

        new_quantity = current_quantity - quantity
        if new_quantity == 0:
            self.inventory.remove(item_id)
            print(f"使用道具 {item_id} x{quantity}，已用完")
        else:
            self.inventory.put(item_id, new_quantity)
            print(f"使用道具 {item_id} x{quantity}，剩余: {new_quantity}")

        return True

    def get_item_count(self, item_id):
        """
        获取道具数量
        :param item_id: 道具ID
        :return: 数量
        """
        quantity = self.inventory.get(item_id)
        return quantity if quantity is not None else 0

    def has_item(self, item_id, quantity=1):
        """
        检查是否拥有足够的道具
        :param item_id: 道具ID
        :param quantity: 数量
        :return: 是否拥有
        """
        return self.get_item_count(item_id) >= quantity

    def get_all_items(self):
        """获取所有道具"""
        return self.inventory.items()

    def clear_inventory(self):
        """清空库存"""
        self.inventory.clear()
        print("库存已清空")


class AchievementManager:
    """
    成就管理器
    使用哈希表管理玩家成就
    """

    def __init__(self):
        self.achievements = HashTable(capacity=30)
        self.unlocked = HashTable(capacity=30)  # 已解锁的成就

    def register_achievement(self, achievement_id, achievement_data):
        """
        注册成就
        :param achievement_id: 成就ID
        :param achievement_data: 成就数据
        """
        self.achievements.put(achievement_id, achievement_data)
        print(f"注册成就: {achievement_data.get('name')}")

    def unlock_achievement(self, achievement_id):
        """
        解锁成就
        :param achievement_id: 成就ID
        :return: 成就数据，失败返回None
        """
        if self.is_unlocked(achievement_id):
            print(f"成就 {achievement_id} 已解锁")
            return None

        achievement = self.achievements.get(achievement_id)
        if achievement is None:
            print(f"成就 {achievement_id} 不存在")
            return None

        import time
        unlock_data = {
            'achievement_id': achievement_id,
            'unlocked_at': time.time(),
            **achievement
        }
        self.unlocked.put(achievement_id, unlock_data)

        print(f"🏆 解锁成就: {achievement.get('name')}")
        return achievement

    def is_unlocked(self, achievement_id):
        """检查成就是否已解锁"""
        return self.unlocked.contains(achievement_id)

    def get_achievement(self, achievement_id):
        """获取成就信息"""
        return self.achievements.get(achievement_id)

    def get_unlocked_achievements(self):
        """获取所有已解锁的成就"""
        return self.unlocked.items()

    def get_locked_achievements(self):
        """获取所有未解锁的成就"""
        locked = []
        for ach_id, ach_data in self.achievements.items():
            if not self.is_unlocked(ach_id):
                locked.append((ach_id, ach_data))
        return locked

    def get_progress(self):
        """
        获取成就进度
        :return: (已解锁数量, 总数量, 完成度)
        """
        total = self.achievements.get_size()
        unlocked = self.unlocked.get_size()
        percentage = (unlocked / total * 100) if total > 0 else 0

        return unlocked, total, percentage

    def get_achievement_stats(self):
        """获取成就统计"""
        unlocked, total, percentage = self.get_progress()

        # 按类别统计
        categories = {}
        for ach_id, ach_data in self.achievements.items():
            category = ach_data.get('category', '未分类')
            if category not in categories:
                categories[category] = {'total': 0, 'unlocked': 0}
            categories[category]['total'] += 1
            if self.is_unlocked(ach_id):
                categories[category]['unlocked'] += 1

        return {
            'total': total,
            'unlocked': unlocked,
            'percentage': percentage,
            'categories': categories
        }


# ============== 测试代码 ==============
if __name__ == '__main__':
    print("=" * 50)
    print("哈希表测试")
    print("=" * 50)

    ht = HashTable(capacity=10)

    print("\n1. 插入键值对：")
    data = [
        ('apple', 5),
        ('banana', 3),
        ('orange', 8),
        ('grape', 2),
        ('melon', 6)
    ]

    for key, value in data:
        ht.put(key, value)
        print(f"   插入 {key}: {value}")

    print(f"\n2. 哈希表信息：")
    print(f"   {ht}")

    print(f"\n3. 获取值：")
    print(f"   apple: {ht.get('apple')}")
    print(f"   banana: {ht.get('banana')}")
    print(f"   watermelon: {ht.get('watermelon')}")

    print(f"\n4. 删除键：")
    ht.remove('banana')
    print(f"   删除 banana 后: {ht.get('banana')}")

    print(f"\n5. 所有键值对：")
    for key, value in ht.items():
        print(f"   {key}: {value}")

    print(f"\n6. 统计信息：")
    stats = ht.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # 测试玩家数据库
    print("\n" + "=" * 50)
    print("玩家数据库测试")
    print("=" * 50)

    player_db = PlayerDatabase()

    print("\n1. 添加玩家：")
    players = [
        ('Alice', {'points': 1500, 'level': 5, 'wins': 20}),
        ('Bob', {'points': 2200, 'level': 8, 'wins': 35}),
        ('Charlie', {'points': 800, 'level': 3, 'wins': 10}),
        ('David', {'points': 3000, 'level': 10, 'wins': 50})
    ]

    for username, data in players:
        player_db.add_player(username, data)

    print(f"\n2. 查询玩家：")
    alice = player_db.get_player('Alice')
    print(f"   Alice: {alice}")

    print(f"\n3. 更新玩家：")
    player_db.update_player('Alice', {'points': 1800, 'wins': 25})

    print(f"\n4. TOP玩家：")
    for i, (username, data) in enumerate(player_db.get_top_players(3), 1):
        print(f"   {i}. {username}: {data['points']}分")

    # 测试道具库存
    print("\n" + "=" * 50)
    print("道具库存测试")
    print("=" * 50)

    inventory = ItemInventory()

    print("\n1. 添加道具：")
    inventory.add_item('hint', 5)
    inventory.add_item('time_extend', 3)
    inventory.add_item('hint', 2)  # 再次添加

    print(f"\n2. 使用道具：")
    inventory.use_item('hint', 3)

    print(f"\n3. 检查道具：")
    print(f"   提示道具数量: {inventory.get_item_count('hint')}")
    print(f"   是否有延时道具: {inventory.has_item('time_extend', 2)}")

    print(f"\n4. 所有道具：")
    for item_id, quantity in inventory.get_all_items():
        print(f"   {item_id}: {quantity}")

    # 测试成就管理
    print("\n" + "=" * 50)
    print("成就管理测试")
    print("=" * 50)

    ach_mgr = AchievementManager()

    print("\n1. 注册成就：")
    achievements = [
        ('first_win', {'name': '首胜', 'category': '入门', 'points': 100}),
        ('speed_king', {'name': '速度之王', 'category': '挑战', 'points': 500}),
        ('persistent', {'name': '坚持不懈', 'category': '持久', 'points': 300})
    ]

    for ach_id, ach_data in achievements:
        ach_mgr.register_achievement(ach_id, ach_data)

    print(f"\n2. 解锁成就：")
    ach_mgr.unlock_achievement('first_win')
    ach_mgr.unlock_achievement('persistent')

    print(f"\n3. 成就进度：")
    unlocked, total, percentage = ach_mgr.get_progress()
    print(f"   进度: {unlocked}/{total} ({percentage:.1f}%)")

    print(f"\n4. 统计信息：")
    stats = ach_mgr.get_achievement_stats()
    print(f"   总成就数: {stats['total']}")
    print(f"   已解锁: {stats['unlocked']}")
    print(f"   完成度: {stats['percentage']:.1f}%")

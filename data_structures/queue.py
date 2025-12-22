"""
队列数据结构实现
用于：游戏历史记录、事件队列
"""


class Node:
    """队列节点"""

    def __init__(self, data):
        self.data = data
        self.next = None


class Queue:
    """
    队列的实现（基于链表）
    FIFO (First In First Out) 先进先出
    """

    def __init__(self, max_size=None):
        """
        初始化队列
        """
        self.front = None
        self.rear = None
        self.size = 0
        self.max_size = max_size

    def is_empty(self):
        """检查队列是否为空"""
        return self.front is None

    def is_full(self):
        """检查队列是否已满"""
        if self.max_size is None:
            return False
        return self.size >= self.max_size

    def enqueue(self, data):
        """
        入队操作
        """
        # 如果队列已满，删除最前面的元素（FIFO覆盖）
        if self.is_full():
            self.dequeue()
            print(f"队列已满，自动删除最旧记录")

        new_node = Node(data)

        if self.is_empty():
            self.front = new_node
            self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node

        self.size += 1
        return True

    def dequeue(self):
        """
        出队操作
        """
        if self.is_empty():
            print("队列为空，无法出队！")
            return None

        data = self.front.data
        self.front = self.front.next

        if self.front is None:
            self.rear = None

        self.size -= 1
        return data

    def peek(self):
        """
        查看队首元素但不删除
        """
        if self.is_empty():
            return None
        return self.front.data

    def get_size(self):
        """获取队列大小"""
        return self.size

    def clear(self):
        """清空队列"""
        self.front = None
        self.rear = None
        self.size = 0

    def to_list(self):
        """将队列转换为列表（从队首到队尾）"""
        result = []
        current = self.front
        while current:
            result.append(current.data)
            current = current.next
        return result

    def __str__(self):
        """字符串表示"""
        if self.is_empty():
            return "Queue(empty)"
        return f"Queue(size={self.size}, front={self.front.data})"

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return self.size


# ============== 循环队列实现 ==============

class CircularQueue:
    """
    循环队列实现（基于数组）
    """

    def __init__(self, max_size):
        """
        初始化循环队列
        """
        self.max_size = max_size
        self.queue = [None] * max_size
        self.front = 0
        self.rear = 0
        self.size = 0

    def is_empty(self):
        """检查队列是否为空"""
        return self.size == 0

    def is_full(self):
        """检查队列是否已满"""
        return self.size == self.max_size

    def enqueue(self, data):
        """入队操作"""
        if self.is_full():
            print("循环队列已满！")
            return False

        self.queue[self.rear] = data
        self.rear = (self.rear + 1) % self.max_size
        self.size += 1
        return True

    def dequeue(self):
        """出队操作"""
        if self.is_empty():
            print("循环队列为空！")
            return None

        data = self.queue[self.front]
        self.queue[self.front] = None
        self.front = (self.front + 1) % self.max_size
        self.size -= 1
        return data

    def peek(self):
        """查看队首元素"""
        if self.is_empty():
            return None
        return self.queue[self.front]

    def to_list(self):
        """转换为列表"""
        if self.is_empty():
            return []

        result = []
        index = self.front
        for _ in range(self.size):
            result.append(self.queue[index])
            index = (index + 1) % self.max_size
        return result


# ============== 应用示例类 ==============

class GameRecordQueue:
    """
    游戏记录队列
    保存最近N场游戏记录
    """

    def __init__(self, max_records=50):
        self.records = Queue(max_size=max_records)

    def add_record(self, game_record):
        """
        添加游戏记录
        """
        self.records.enqueue(game_record)
        print(f"记录已添加，当前记录数：{self.records.get_size()}")

    def get_all_records(self):
        """获取所有记录（列表形式）"""
        return self.records.to_list()

    def get_recent_records(self, n=10):
        """
        获取最近N条记录
        """
        all_records = self.records.to_list()
        return all_records[-n:] if len(all_records) > n else all_records

    def get_best_score(self, mode='normal'):
        """
        获取指定模式的最佳成绩
        """
        records = [r for r in self.records.to_list()
                   if r.get('mode') == mode and r.get('completed')]

        if not records:
            return None

        # 按时间排序，返回最快的
        return min(records, key=lambda x: x.get('time_used', float('inf')))

    def get_statistics(self):
        """获取统计信息"""
        all_records = self.records.to_list()

        if not all_records:
            return {
                'total_games': 0,
                'completed_games': 0,
                'win_rate': 0,
                'total_time': 0
            }

        completed = [r for r in all_records if r.get('completed')]
        total_time = sum(r.get('time_used', 0) for r in completed)

        return {
            'total_games': len(all_records),
            'completed_games': len(completed),
            'win_rate': len(completed) / len(all_records) * 100,
            'total_time': total_time,
            'avg_time': total_time / len(completed) if completed else 0
        }


# ============== 测试代码 ==============
if __name__ == '__main__':
    print("=" * 50)
    print("队列数据结构测试")
    print("=" * 50)

    # 测试基本队列操作
    queue = Queue(max_size=5)

    print("\n1. 测试入队操作：")
    for i in range(1, 6):
        queue.enqueue(f"记录{i}")
        print(f"   入队 记录{i}，队列大小：{queue.get_size()}")

    print(f"\n2. 队列满测试（自动覆盖）：")
    queue.enqueue("记录6")

    print(f"\n3. 查看队首：{queue.peek()}")

    print(f"\n4. 队列内容：{queue.to_list()}")

    print(f"\n5. 测试出队操作：")
    for i in range(3):
        data = queue.dequeue()
        print(f"   出队 {data}，剩余大小：{queue.get_size()}")

    # 测试游戏记录队列
    print("\n" + "=" * 50)
    print("游戏记录队列测试")
    print("=" * 50)

    record_queue = GameRecordQueue(max_records=5)

    # 添加模拟记录
    for i in range(1, 8):
        record = {
            'game_id': i,
            'mode': 'normal' if i % 2 else 'ultimate',
            'time_used': 60 + i * 10,
            'moves': 20 + i,
            'completed': i % 3 != 0
        }
        record_queue.add_record(record)

    print(f"\n最近3条记录：")
    for record in record_queue.get_recent_records(3):
        print(f"   {record}")

    print(f"\n统计信息：")
    stats = record_queue.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

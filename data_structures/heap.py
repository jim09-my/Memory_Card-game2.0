"""
堆数据结构实现
用于：获取TOP N成绩、优先级队列
"""


class MinHeap:
    """
    最小堆实现
    """

    def __init__(self):
        self.heap = []
        self.size = 0

    def parent(self, i):
        """获取父节点索引"""
        return (i - 1) // 2

    def left_child(self, i):
        """获取左子节点索引"""
        return 2 * i + 1

    def right_child(self, i):
        """获取右子节点索引"""
        return 2 * i + 2

    def is_empty(self):
        """检查堆是否为空"""
        return self.size == 0

    def get_min(self):
        """获取最小值（不删除）"""
        if self.is_empty():
            return None
        return self.heap[0]

    def insert(self, item):
        """
        插入元素
        """
        self.heap.append(item)
        self.size += 1
        self._heapify_up(self.size - 1)

    def _heapify_up(self, i):
        """向上调整堆"""
        parent = self.parent(i)

        if i > 0 and self._compare(self.heap[i], self.heap[parent]) < 0:
            self.heap[i], self.heap[parent] = self.heap[parent], self.heap[i]
            self._heapify_up(parent)

    def extract_min(self):
        """
        删除并返回最小值
        """
        if self.is_empty():
            return None

        if self.size == 1:
            self.size -= 1
            return self.heap.pop()

        min_item = self.heap[0]
        self.heap[0] = self.heap.pop()
        self.size -= 1
        self._heapify_down(0)

        return min_item

    def _heapify_down(self, i):
        """向下调整堆"""
        min_index = i
        left = self.left_child(i)
        right = self.right_child(i)

        if left < self.size and self._compare(self.heap[left], self.heap[min_index]) < 0:
            min_index = left

        if right < self.size and self._compare(self.heap[right], self.heap[min_index]) < 0:
            min_index = right

        if min_index != i:
            self.heap[i], self.heap[min_index] = self.heap[min_index], self.heap[i]
            self._heapify_down(min_index)

    def _compare(self, item1, item2):
        """
        比较两个元素
        如果是元组，比较第一个元素（key）
        """
        if isinstance(item1, tuple):
            return -1 if item1[0] < item2[0] else (1 if item1[0] > item2[0] else 0)
        return -1 if item1 < item2 else (1 if item1 > item2 else 0)

    def build_heap(self, items):
        """
        从数组构建堆
        """
        self.heap = items.copy()
        self.size = len(items)

        # 从最后一个非叶子节点开始向下调整
        for i in range(self.size // 2 - 1, -1, -1):
            self._heapify_down(i)

    def heap_sort(self, items):
        """
        堆排序
        """
        self.build_heap(items)
        sorted_list = []

        while not self.is_empty():
            sorted_list.append(self.extract_min())

        return sorted_list

    def get_size(self):
        """获取堆大小"""
        return self.size

    def to_list(self):
        """转换为列表"""
        return self.heap.copy()

    def clear(self):
        """清空堆"""
        self.heap = []
        self.size = 0

    def __str__(self):
        """字符串表示"""
        if self.is_empty():
            return "MinHeap(empty)"
        return f"MinHeap(size={self.size}, min={self.get_min()})"

    def __len__(self):
        return self.size


class MaxHeap(MinHeap):
    """
    最大堆实现
    父节点总是大于或等于子节点
    """

    def _compare(self, item1, item2):
        """
        比较两个元素（反向比较实现最大堆）
        """
        if isinstance(item1, tuple):
            return 1 if item1[0] < item2[0] else (-1 if item1[0] > item2[0] else 0)
        return 1 if item1 < item2 else (-1 if item1 > item2 else 0)

    def get_max(self):
        """获取最大值"""
        return self.get_min()

    def extract_max(self):
        """删除并返回最大值"""
        return self.extract_min()

    def __str__(self):
        """字符串表示"""
        if self.is_empty():
            return "MaxHeap(empty)"
        return f"MaxHeap(size={self.size}, max={self.get_max()})"


# ============== 优先级队列 ==============

class PriorityQueue:
    """
    优先级队列
    基于最小堆实现
    """

    def __init__(self):
        self.heap = MinHeap()

    def enqueue(self, item, priority):
        """
        入队
        """
        self.heap.insert((priority, item))

    def dequeue(self):
        """
        出队（返回优先级最高的元素）
        """
        result = self.heap.extract_min()
        return result[1] if result else None

    def peek(self):
        """查看队首元素"""
        result = self.heap.get_min()
        return result[1] if result else None

    def is_empty(self):
        """检查队列是否为空"""
        return self.heap.is_empty()

    def get_size(self):
        """获取队列大小"""
        return self.heap.get_size()

    def __len__(self):
        return self.heap.get_size()


# ============== 应用示例类 ==============

class TopNRecords:
    """
    TOP N 记录管理
    使用堆高效维护最佳N个记录
    """

    def __init__(self, n=10, mode='min'):
        """
        初始化TOP N管理器
        """
        self.n = n
        self.mode = mode

        # 保留最小的N个：使用最大堆
        # 保留最大的N个：使用最小堆
        self.heap = MaxHeap() if mode == 'min' else MinHeap()

    def add_record(self, value, data):
        """
        添加记录
        """
        if self.heap.get_size() < self.n:
            # 未满，直接插入
            self.heap.insert((value, data))
            print(f"添加记录: {value}，当前记录数: {self.heap.get_size()}")
        else:
            # 已满，比较后决定是否替换
            top = self.heap.get_min() if self.mode == 'max' else self.heap.get_max()

            if self.mode == 'min' and value < top[0]:
                # 保留最小的N个，新值更小则替换
                self.heap.extract_max()
                self.heap.insert((value, data))
                print(f"替换记录: {value} 替换了 {top[0]}")
            elif self.mode == 'max' and value > top[0]:
                # 保留最大的N个，新值更大则替换
                self.heap.extract_min()
                self.heap.insert((value, data))
                print(f"替换记录: {value} 替换了 {top[0]}")
            else:
                print(f"记录 {value} 未进入TOP {self.n}")

    def get_top_n(self):
        """
        获取TOP N记录
        """
        records = self.heap.to_list()

        # 排序
        if self.mode == 'min':
            records.sort(key=lambda x: x[0])  # 升序
        else:
            records.sort(key=lambda x: x[0], reverse=True)  # 降序

        return [(value, data) for value, data in records]

    def get_best(self):
        """
        获取最佳记录
        """
        records = self.get_top_n()
        return records[0] if records else None

    def clear(self):
        """清空记录"""
        self.heap.clear()


class GameEventQueue:
    """
    游戏事件队列
    使用优先级队列管理游戏事件
    """

    def __init__(self):
        self.queue = PriorityQueue()
        self.event_id = 0

    def add_event(self, event_type, priority, data=None):
        """
        添加事件
        """
        self.event_id += 1
        event = {
            'id': self.event_id,
            'type': event_type,
            'data': data
        }
        self.queue.enqueue(event, priority)
        print(f"添加事件: {event_type} (优先级: {priority})")

    def process_next_event(self):
        """
        处理下一个事件
        """
        event = self.queue.dequeue()
        if event:
            print(f"处理事件: {event['type']} (ID: {event['id']})")
        return event

    def peek_next_event(self):
        """查看下一个事件"""
        return self.queue.peek()

    def has_events(self):
        """检查是否有待处理事件"""
        return not self.queue.is_empty()


# ============== 测试代码 ==============
if __name__ == '__main__':
    print("=" * 50)
    print("最小堆测试")
    print("=" * 50)

    min_heap = MinHeap()

    print("\n1. 插入元素：")
    values = [15, 10, 20, 8, 25, 5, 30]
    for val in values:
        min_heap.insert(val)
        print(f"   插入 {val}，当前最小值: {min_heap.get_min()}")

    print(f"\n2. 堆内容: {min_heap.to_list()}")

    print(f"\n3. 依次取出最小值：")
    while not min_heap.is_empty():
        print(f"   取出: {min_heap.extract_min()}")

    # 测试最大堆
    print("\n" + "=" * 50)
    print("最大堆测试")
    print("=" * 50)

    max_heap = MaxHeap()

    print("\n1. 构建堆：")
    values = [15, 10, 20, 8, 25, 5, 30]
    max_heap.build_heap(values)
    print(f"   堆内容: {max_heap.to_list()}")
    print(f"   最大值: {max_heap.get_max()}")

    # 测试TOP N记录
    print("\n" + "=" * 50)
    print("TOP N 记录测试")
    print("=" * 50)

    top5_times = TopNRecords(n=5, mode='min')

    print("\n1. 添加时间记录（保留最快的5个）：")
    times = [120, 95, 150, 88, 110, 200, 85, 105, 90, 180]
    for i, time in enumerate(times):
        top5_times.add_record(time, f"游戏{i + 1}")

    print(f"\n2. TOP 5 最快时间：")
    for i, (time, game) in enumerate(top5_times.get_top_n(), 1):
        print(f"   {i}. {game}: {time}秒")

    print(f"\n3. 最佳记录: {top5_times.get_best()}")

    # 测试优先级队列
    print("\n" + "=" * 50)
    print("优先级队列测试")
    print("=" * 50)

    pq = PriorityQueue()

    print("\n1. 添加任务：")
    tasks = [
        ("渲染画面", 1),
        ("保存数据", 3),
        ("播放音效", 2),
        ("更新UI", 1),
        ("检查网络", 5)
    ]

    for task, priority in tasks:
        pq.enqueue(task, priority)

    print(f"\n2. 按优先级处理任务：")
    while not pq.is_empty():
        print(f"   处理: {pq.dequeue()}")

    # 测试堆排序
    print("\n" + "=" * 50)
    print("堆排序测试")
    print("=" * 50)

    unsorted = [64, 34, 25, 12, 22, 11, 90]
    print(f"\n排序前: {unsorted}")

    heap_sorter = MinHeap()
    sorted_list = heap_sorter.heap_sort(unsorted)
    print(f"排序后: {sorted_list}")

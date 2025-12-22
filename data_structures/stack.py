"""
栈数据结构实现
用于：撤销操作、游戏状态历史记录
"""


class Node:
    """栈节点"""

    def __init__(self, data):
        self.data = data
        self.next = None


class Stack:
    """
    栈的实现（基于链表）
    LIFO (Last In First Out) 后进先出
    """

    def __init__(self, max_size=None):
        """
        初始化栈
        """
        self.top = None
        self.size = 0
        self.max_size = max_size

    def is_empty(self):
        """检查栈是否为空"""
        return self.top is None

    def is_full(self):
        """检查栈是否已满"""
        if self.max_size is None:
            return False
        return self.size >= self.max_size

    def push(self, data):
        """
        入栈操作
        """
        if self.is_full():
            print(f"栈已满，无法压入数据！当前大小：{self.size}")
            return False

        new_node = Node(data)
        new_node.next = self.top
        self.top = new_node
        self.size += 1
        return True

    def pop(self):
        """
        出栈操作
        """
        if self.is_empty():
            print("栈为空，无法弹出数据！")
            return None

        data = self.top.data
        self.top = self.top.next
        self.size -= 1
        return data

    def peek(self):
        """
        查看栈顶元素但不删除
        """
        if self.is_empty():
            return None
        return self.top.data

    def get_size(self):
        """获取栈的大小"""
        return self.size

    def clear(self):
        """清空栈"""
        self.top = None
        self.size = 0

    def to_list(self):
        """将栈转换为列表（从栈顶到栈底）"""
        result = []
        current = self.top
        while current:
            result.append(current.data)
            current = current.next
        return result

    def __str__(self):
        """字符串表示"""
        if self.is_empty():
            return "Stack(empty)"
        items = self.to_list()
        return f"Stack(size={self.size}, top={items[0]})"

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return self.size


# ============== 应用示例类 ==============

class GameStateStack:
    """
    游戏状态栈
    用于实现撤销功能
    """

    def __init__(self, max_undo=10):
        self.states = Stack(max_size=max_undo)

    def save_state(self, game_state):
        """
        保存游戏状态
        """
        state_copy = game_state.copy()
        self.states.push(state_copy)
        print(f"状态已保存，当前可撤销步数：{self.states.get_size()}")

    def undo(self):
        """
        撤销到上一个状态
        """
        if self.states.is_empty():
            print("没有可撤销的操作！")
            return None

        previous_state = self.states.pop()
        print(f"已撤销，剩余可撤销步数：{self.states.get_size()}")
        return previous_state

    def can_undo(self):
        """检查是否可以撤销"""
        return not self.states.is_empty()

    def clear_history(self):
        """清空历史记录"""
        self.states.clear()
        print("撤销历史已清空")


# ============== 测试代码 ==============
if __name__ == '__main__':
    print("=" * 50)
    print("栈数据结构测试")
    print("=" * 50)

    # 测试基本栈操作
    stack = Stack(max_size=5)

    print("\n1. 测试入栈操作：")
    for i in range(1, 6):
        stack.push(i * 10)
        print(f"   压入 {i * 10}，栈大小：{stack.get_size()}")

    print(f"\n2. 栈满测试：")
    stack.push(60) 

    print(f"\n3. 查看栈顶：{stack.peek()}")

    print(f"\n4. 测试出栈操作：")
    while not stack.is_empty():
        data = stack.pop()
        print(f"   弹出 {data}，剩余大小：{stack.get_size()}")

    print(f"\n5. 空栈测试：")
    stack.pop()

    # 测试游戏状态栈
    print("\n" + "=" * 50)
    print("游戏状态栈测试")
    print("=" * 50)

    game_stack = GameStateStack(max_undo=3)

    # 模拟游戏状态
    for step in range(1, 5):
        state = {
            'step': step,
            'score': step * 100,
            'moves': step * 2
        }
        game_stack.save_state(state)

    print(f"\n撤销测试：")
    for i in range(4):
        state = game_stack.undo()
        if state:
            print(f"   恢复到状态：{state}")

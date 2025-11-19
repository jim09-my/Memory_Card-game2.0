"""
链表数据结构实现
用于：卡牌序列管理、动态数据存储
"""

class Node:
    """链表节点"""
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None  # 用于双向链表

class LinkedList:
    """
    单向链表实现
    """
    def __init__(self):
        self.head = None
        self.size = 0

    def is_empty(self):
        """检查链表是否为空"""
        return self.head is None

    def get_size(self):
        """获取链表大小"""
        return self.size

    def append(self, data):
        """
        在链表末尾添加节点
        :param data: 节点数据
        """
        new_node = Node(data)

        if self.is_empty():
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

        self.size += 1

    def prepend(self, data):
        """
        在链表开头添加节点
        :param data: 节点数据
        """
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self.size += 1

    def insert(self, index, data):
        """
        在指定位置插入节点
        :param index: 插入位置
        :param data: 节点数据
        """
        if index < 0 or index > self.size:
            print(f"索引 {index} 超出范围")
            return False

        if index == 0:
            self.prepend(data)
            return True

        new_node = Node(data)
        current = self.head

        for i in range(index - 1):
            current = current.next

        new_node.next = current.next
        current.next = new_node
        self.size += 1
        return True

    def delete(self, data):
        """
        删除第一个匹配的节点
        :param data: 要删除的数据
        :return: 成功返回True，失败返回False
        """
        if self.is_empty():
            return False

        # 删除头节点
        if self.head.data == data:
            self.head = self.head.next
            self.size -= 1
            return True

        # 删除其他节点
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                self.size -= 1
                return True
            current = current.next

        return False

    def delete_at(self, index):
        """
        删除指定位置的节点
        :param index: 节点位置
        :return: 删除的数据，失败返回None
        """
        if index < 0 or index >= self.size:
            print(f"索引 {index} 超出范围")
            return None

        if index == 0:
            data = self.head.data
            self.head = self.head.next
            self.size -= 1
            return data

        current = self.head
        for i in range(index - 1):
            current = current.next

        data = current.next.data
        current.next = current.next.next
        self.size -= 1
        return data

    def search(self, data):
        """
        查找节点
        :param data: 要查找的数据
        :return: 节点索引，未找到返回-1
        """
        current = self.head
        index = 0

        while current:
            if current.data == data:
                return index
            current = current.next
            index += 1

        return -1

    def get(self, index):
        """
        获取指定位置的数据
        :param index: 节点位置
        :return: 节点数据，失败返回None
        """
        if index < 0 or index >= self.size:
            return None

        current = self.head
        for i in range(index):
            current = current.next

        return current.data

    def update(self, index, data):
        """
        更新指定位置的数据
        :param index: 节点位置
        :param data: 新数据
        :return: 成功返回True，失败返回False
        """
        if index < 0 or index >= self.size:
            return False

        current = self.head
        for i in range(index):
            current = current.next

        current.data = data
        return True

    def reverse(self):
        """反转链表"""
        prev = None
        current = self.head

        while current:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node

        self.head = prev

    def to_list(self):
        """转换为Python列表"""
        result = []
        current = self.head

        while current:
            result.append(current.data)
            current = current.next

        return result

    def clear(self):
        """清空链表"""
        self.head = None
        self.size = 0

    def __str__(self):
        """字符串表示"""
        if self.is_empty():
            return "LinkedList(empty)"
        return f"LinkedList(size={self.size}, data={self.to_list()})"

    def __len__(self):
        return self.size

    def __iter__(self):
        """使链表可迭代"""
        current = self.head
        while current:
            yield current.data
            current = current.next


# ============== 双向链表 ==============

class DoublyLinkedList:
    """
    双向链表实现
    支持向前和向后遍历
    """
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def is_empty(self):
        return self.head is None

    def append(self, data):
        """在末尾添加节点"""
        new_node = Node(data)

        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node

        self.size += 1

    def prepend(self, data):
        """在开头添加节点"""
        new_node = Node(data)

        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node

        self.size += 1

    def delete(self, data):
        """删除节点"""
        if self.is_empty():
            return False

        current = self.head

        while current:
            if current.data == data:
                # 删除头节点
                if current == self.head:
                    self.head = current.next
                    if self.head:
                        self.head.prev = None
                    else:
                        self.tail = None
                # 删除尾节点
                elif current == self.tail:
                    self.tail = current.prev
                    self.tail.next = None
                # 删除中间节点
                else:
                    current.prev.next = current.next
                    current.next.prev = current.prev

                self.size -= 1
                return True

            current = current.next

        return False

    def to_list(self):
        """转换为列表"""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

    def to_list_reverse(self):
        """反向转换为列表"""
        result = []
        current = self.tail
        while current:
            result.append(current.data)
            current = current.prev
        return result


# ============== 应用示例类 ==============

class CardList:
    """
    卡牌列表
    使用链表管理游戏卡牌
    """
    def __init__(self):
        self.cards = LinkedList()

    def add_card(self, card):
        """添加卡牌"""
        self.cards.append(card)

    def remove_card(self, card_id):
        """移除卡牌"""
        for i, card in enumerate(self.cards):
            if card.get('id') == card_id:
                self.cards.delete_at(i)
                return True
        return False

    def get_card(self, index):
        """获取指定位置的卡牌"""
        return self.cards.get(index)

    def find_card_by_value(self, value):
        """查找指定值的卡牌"""
        matches = []
        for i, card in enumerate(self.cards):
            if card.get('value') == value:
                matches.append((i, card))
        return matches

    def shuffle(self):
        """洗牌"""
        import random
        cards_list = self.cards.to_list()
        random.shuffle(cards_list)

        self.cards.clear()
        for card in cards_list:
            self.cards.append(card)

    def flip_card(self, index):
        """翻转卡牌"""
        card = self.cards.get(index)
        if card:
            card['is_flipped'] = not card.get('is_flipped', False)
            self.cards.update(index, card)
            return True
        return False

    def get_flipped_cards(self):
        """获取所有已翻转的卡牌"""
        flipped = []
        for i, card in enumerate(self.cards):
            if card.get('is_flipped'):
                flipped.append((i, card))
        return flipped

    def get_all_cards(self):
        """获取所有卡牌"""
        return self.cards.to_list()

    def get_size(self):
        """获取卡牌数量"""
        return self.cards.get_size()


# ============== 测试代码 ==============
if __name__ == '__main__':
    print("="*50)
    print("链表数据结构测试")
    print("="*50)

    # 测试单向链表
    ll = LinkedList()

    print("\n1. 测试添加操作：")
    for i in range(1, 6):
        ll.append(i * 10)
    print(f"   链表内容：{ll.to_list()}")

    print("\n2. 测试插入操作：")
    ll.insert(2, 25)
    print(f"   在位置2插入25：{ll.to_list()}")

    print("\n3. 测试删除操作：")
    ll.delete(30)
    print(f"   删除30后：{ll.to_list()}")

    print("\n4. 测试查找操作：")
    index = ll.search(40)
    print(f"   40的位置：{index}")

    print("\n5. 测试反转操作：")
    ll.reverse()
    print(f"   反转后：{ll.to_list()}")

    # 测试卡牌列表
    print("\n" + "="*50)
    print("卡牌列表测试")
    print("="*50)

    card_list = CardList()

    print("\n1. 添加卡牌：")
    for i in range(1, 9):
        card = {
            'id': i,
            'value': (i - 1) // 2 + 1,
            'is_flipped': False,
            'is_matched': False
        }
        card_list.add_card(card)

    print(f"   卡牌数量：{card_list.get_size()}")

    print("\n2. 查找值为2的卡牌：")
    matches = card_list.find_card_by_value(2)
    for idx, card in matches:
        print(f"   位置{idx}: {card}")

    print("\n3. 洗牌测试：")
    print(f"   洗牌前：{[c['value'] for c in card_list.get_all_cards()]}")
    card_list.shuffle()
    print(f"   洗牌后：{[c['value'] for c in card_list.get_all_cards()]}")

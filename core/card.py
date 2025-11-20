"""
卡牌类
表示游戏中的单个卡牌
"""


class Card:
    """游戏卡牌类"""

    def __init__(self, card_id, value, position=None):
        """
        初始化卡牌
        :param card_id: 卡牌ID（唯一标识）
        :param value: 卡牌值（用于配对）
        :param position: 卡牌位置 (row, col)
        """
        self.id = card_id
        self.value = value
        self.position = position
        self.is_flipped = False  # 是否翻开
        self.is_matched = False  # 是否已配对
        self.is_revealed = False  # 是否被提示显示

    def flip(self):
        """翻转卡牌"""
        if not self.is_matched:
            self.is_flipped = not self.is_flipped
            return True
        return False

    def flip_up(self):
        """翻开卡牌"""
        if not self.is_matched:
            self.is_flipped = True
            return True
        return False

    def flip_down(self):
        """翻回卡牌"""
        if not self.is_matched:
            self.is_flipped = False
            return True
        return False

    def match(self):
        """标记为已配对"""
        self.is_matched = True
        self.is_flipped = True

    def reveal(self):
        """提示显示"""
        self.is_revealed = True

    def hide_reveal(self):
        """隐藏提示"""
        self.is_revealed = False

    def reset(self):
        """重置卡牌状态"""
        self.is_flipped = False
        self.is_matched = False
        self.is_revealed = False

    def can_flip(self):
        """检查是否可以翻转"""
        return not self.is_matched and not self.is_flipped

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'value': self.value,
            'position': self.position,
            'is_flipped': self.is_flipped,
            'is_matched': self.is_matched,
            'is_revealed': self.is_revealed
        }

    @classmethod
    def from_dict(cls, data):
        """从字典创建卡牌"""
        card = cls(data['id'], data['value'], data.get('position'))
        card.is_flipped = data.get('is_flipped', False)
        card.is_matched = data.get('is_matched', False)
        card.is_revealed = data.get('is_revealed', False)
        return card

    def __str__(self):
        """字符串表示"""
        status = "已配对" if self.is_matched else ("翻开" if self.is_flipped else "背面")
        return f"Card(id={self.id}, value={self.value}, status={status})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        """比较卡牌值是否相等"""
        if isinstance(other, Card):
            return self.value == other.value
        return False


# ============== 卡牌工厂 ==============

class CardFactory:
    """卡牌工厂类"""

    @staticmethod
    def create_card_deck(grid_size):
        """
        创建一副卡牌
        :param grid_size: 网格大小（如4表示4x4）
        :return: 卡牌列表
        """
        import random
        from config import PokerConfig

        total_cards = grid_size * grid_size
        total_pairs = total_cards // 2

        # 生成扑克牌卡面作为配对值
        faces = PokerConfig.sample_faces(total_pairs)
        values = faces * 2
        random.shuffle(values)

        # 创建卡牌
        cards = []
        card_id = 0
        for row in range(grid_size):
            for col in range(grid_size):
                card = Card(
                    card_id=card_id,
                    value=values[card_id],
                    position=(row, col)
                )
                cards.append(card)
                card_id += 1

        return cards

    @staticmethod
    def create_custom_deck(values):
        """
        创建自定义卡牌组
        :param values: 值列表
        :return: 卡牌列表
        """
        cards = []
        for i, value in enumerate(values):
            card = Card(card_id=i, value=value)
            cards.append(card)
        return cards

    @staticmethod
    def shuffle_deck(cards):
        """
        洗牌
        :param cards: 卡牌列表
        :return: 洗牌后的卡牌列表
        """
        import random
        shuffled = cards.copy()
        random.shuffle(shuffled)

        # 更新位置
        grid_size = int(len(shuffled) ** 0.5)
        for i, card in enumerate(shuffled):
            row = i // grid_size
            col = i % grid_size
            card.position = (row, col)

        return shuffled


# ============== 测试代码 ==============
if __name__ == '__main__':
    print("=" * 50)
    print("卡牌类测试")
    print("=" * 50)

    # 测试单个卡牌
    print("\n1. 创建卡牌：")
    card = Card(card_id=1, value=5, position=(0, 0))
    print(f"   {card}")

    print("\n2. 翻转卡牌：")
    card.flip()
    print(f"   {card}")

    print("\n3. 配对卡牌：")
    card.match()
    print(f"   {card}")

    # 测试卡牌工厂
    print("\n" + "=" * 50)
    print("卡牌工厂测试")
    print("=" * 50)

    print("\n1. 创建4x4卡牌组：")
    deck = CardFactory.create_card_deck(4)
    print(f"   卡牌数量: {len(deck)}")

    print("\n2. 显示卡牌值分布：")
    values = [card.value for card in deck]
    for i in range(0, len(values), 4):
        print(f"   {values[i:i + 4]}")

    print("\n3. 洗牌：")
    shuffled_deck = CardFactory.shuffle_deck(deck)
    values = [card.value for card in shuffled_deck]
    for i in range(0, len(values), 4):
        print(f"   {values[i:i + 4]}")

    print("\n4. 检查配对：")
    from collections import Counter

    value_counts = Counter(values)
    print(f"   每个值出现次数: {dict(value_counts)}")
    all_pairs = all(count == 2 for count in value_counts.values())
    print(f"   所有值都成对: {all_pairs}")

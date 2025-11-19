"""
二叉搜索树实现
用于：排行榜系统、玩家成绩排序
"""

class TreeNode:
    """二叉树节点"""
    def __init__(self, key, data=None):
        self.key = key          # 用于比较的键（如分数、时间）
        self.data = data        # 节点存储的数据
        self.left = None        # 左子节点
        self.right = None       # 右子节点
        self.height = 1         # 节点高度（用于AVL树）

class BinarySearchTree:
    """
    二叉搜索树实现
    左子树所有节点 < 根节点 < 右子树所有节点
    """
    def __init__(self):
        self.root = None
        self.size = 0

    def is_empty(self):
        """检查树是否为空"""
        return self.root is None

    def get_size(self):
        """获取节点数量"""
        return self.size

    def insert(self, key, data=None):
        """
        插入节点
        :param key: 键值（用于排序）
        :param data: 节点数据
        """
        if self.root is None:
            self.root = TreeNode(key, data)
            self.size += 1
        else:
            self._insert_recursive(self.root, key, data)

    def _insert_recursive(self, node, key, data):
        """递归插入"""
        if key < node.key:
            if node.left is None:
                node.left = TreeNode(key, data)
                self.size += 1
            else:
                self._insert_recursive(node.left, key, data)
        elif key > node.key:
            if node.right is None:
                node.right = TreeNode(key, data)
                self.size += 1
            else:
                self._insert_recursive(node.right, key, data)
        else:
            # 键值相同，更新数据
            node.data = data

    def search(self, key):
        """
        查找节点
        :param key: 要查找的键
        :return: 节点数据，未找到返回None
        """
        return self._search_recursive(self.root, key)

    def _search_recursive(self, node, key):
        """递归查找"""
        if node is None:
            return None

        if key == node.key:
            return node.data
        elif key < node.key:
            return self._search_recursive(node.left, key)
        else:
            return self._search_recursive(node.right, key)

    def delete(self, key):
        """
        删除节点
        :param key: 要删除的键
        :return: 成功返回True，失败返回False
        """
        if self.root is None:
            return False

        self.root, deleted = self._delete_recursive(self.root, key)
        if deleted:
            self.size -= 1
        return deleted

    def _delete_recursive(self, node, key):
        """递归删除"""
        if node is None:
            return None, False

        deleted = False

        if key < node.key:
            node.left, deleted = self._delete_recursive(node.left, key)
        elif key > node.key:
            node.right, deleted = self._delete_recursive(node.right, key)
        else:
            # 找到要删除的节点
            deleted = True

            # 情况1：叶子节点
            if node.left is None and node.right is None:
                return None, deleted

            # 情况2：只有一个子节点
            if node.left is None:
                return node.right, deleted
            if node.right is None:
                return node.left, deleted

            # 情况3：有两个子节点
            # 找到右子树的最小节点（后继节点）
            min_node = self._find_min(node.right)
            node.key = min_node.key
            node.data = min_node.data
            node.right, _ = self._delete_recursive(node.right, min_node.key)

        return node, deleted

    def _find_min(self, node):
        """找到子树的最小节点"""
        while node.left:
            node = node.left
        return node

    def _find_max(self, node):
        """找到子树的最大节点"""
        while node.right:
            node = node.right
        return node

    def get_min(self):
        """获取最小值"""
        if self.root is None:
            return None
        return self._find_min(self.root).data

    def get_max(self):
        """获取最大值"""
        if self.root is None:
            return None
        return self._find_max(self.root).data

    # ============== 遍历方法 ==============

    def inorder_traversal(self):
        """中序遍历（升序）"""
        result = []
        self._inorder_recursive(self.root, result)
        return result

    def _inorder_recursive(self, node, result):
        """中序遍历递归"""
        if node:
            self._inorder_recursive(node.left, result)
            result.append((node.key, node.data))
            self._inorder_recursive(node.right, result)

    def preorder_traversal(self):
        """前序遍历"""
        result = []
        self._preorder_recursive(self.root, result)
        return result

    def _preorder_recursive(self, node, result):
        """前序遍历递归"""
        if node:
            result.append((node.key, node.data))
            self._preorder_recursive(node.left, result)
            self._preorder_recursive(node.right, result)

    def postorder_traversal(self):
        """后序遍历"""
        result = []
        self._postorder_recursive(self.root, result)
        return result

    def _postorder_recursive(self, node, result):
        """后序遍历递归"""
        if node:
            self._postorder_recursive(node.left, result)
            self._postorder_recursive(node.right, result)
            result.append((node.key, node.data))

    def level_order_traversal(self):
        """层序遍历（广度优先）"""
        if self.root is None:
            return []

        result = []
        queue = [self.root]

        while queue:
            node = queue.pop(0)
            result.append((node.key, node.data))

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        return result

    def get_height(self):
        """获取树的高度"""
        return self._get_height_recursive(self.root)

    def _get_height_recursive(self, node):
        """递归获取高度"""
        if node is None:
            return 0

        left_height = self._get_height_recursive(node.left)
        right_height = self._get_height_recursive(node.right)

        return max(left_height, right_height) + 1

    def is_balanced(self):
        """检查树是否平衡"""
        return self._is_balanced_recursive(self.root)[0]

    def _is_balanced_recursive(self, node):
        """递归检查平衡"""
        if node is None:
            return True, 0

        left_balanced, left_height = self._is_balanced_recursive(node.left)
        right_balanced, right_height = self._is_balanced_recursive(node.right)

        balanced = (left_balanced and right_balanced and
                   abs(left_height - right_height) <= 1)
        height = max(left_height, right_height) + 1

        return balanced, height

    def clear(self):
        """清空树"""
        self.root = None
        self.size = 0

    def __str__(self):
        """字符串表示"""
        if self.is_empty():
            return "BST(empty)"
        return f"BST(size={self.size}, height={self.get_height()})"


# ============== AVL树实现（自平衡二叉搜索树） ==============

class AVLTree(BinarySearchTree):
    """
    AVL树实现
    自平衡的二叉搜索树，保证查找效率
    """

    def _get_height(self, node):
        """获取节点高度"""
        if node is None:
            return 0
        return node.height

    def _get_balance_factor(self, node):
        """获取平衡因子"""
        if node is None:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _update_height(self, node):
        """更新节点高度"""
        if node:
            node.height = max(self._get_height(node.left),
                            self._get_height(node.right)) + 1

    def _rotate_left(self, z):
        """左旋转"""
        y = z.right
        T2 = y.left

        y.left = z
        z.right = T2

        self._update_height(z)
        self._update_height(y)

        return y

    def _rotate_right(self, z):
        """右旋转"""
        y = z.left
        T3 = y.right

        y.right = z
        z.left = T3

        self._update_height(z)
        self._update_height(y)

        return y

    def insert(self, key, data=None):
        """插入节点并保持平衡"""
        self.root = self._insert_avl(self.root, key, data)

    def _insert_avl(self, node, key, data):
        """AVL插入"""
        # 1. 执行标准BST插入
        if node is None:
            self.size += 1
            return TreeNode(key, data)

        if key < node.key:
            node.left = self._insert_avl(node.left, key, data)
        elif key > node.key:
            node.right = self._insert_avl(node.right, key, data)
        else:
            node.data = data
            return node

        # 2. 更新高度
        self._update_height(node)

        # 3. 获取平衡因子
        balance = self._get_balance_factor(node)

        # 4. 如果不平衡，进行旋转
        # Left-Left情况
        if balance > 1 and key < node.left.key:
            return self._rotate_right(node)

        # Right-Right情况
        if balance < -1 and key > node.right.key:
            return self._rotate_left(node)

        # Left-Right情况
        if balance > 1 and key > node.left.key:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Right-Left情况
        if balance < -1 and key < node.right.key:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def delete(self, key):
        """删除节点并保持平衡"""
        self.root, deleted = self._delete_avl(self.root, key)
        if deleted:
            self.size -= 1
        return deleted

    def _delete_avl(self, node, key):
        """AVL删除"""
        if node is None:
            return None, False

        deleted = False

        # 1. 执行标准BST删除
        if key < node.key:
            node.left, deleted = self._delete_avl(node.left, key)
        elif key > node.key:
            node.right, deleted = self._delete_avl(node.right, key)
        else:
            deleted = True

            if node.left is None:
                return node.right, deleted
            elif node.right is None:
                return node.left, deleted

            min_node = self._find_min(node.right)
            node.key = min_node.key
            node.data = min_node.data
            node.right, _ = self._delete_avl(node.right, min_node.key)

        if node is None:
            return node, deleted

        # 2. 更新高度
        self._update_height(node)

        # 3. 获取平衡因子
        balance = self._get_balance_factor(node)

        # 4. 如果不平衡，进行旋转
        # Left-Left情况
        if balance > 1 and self._get_balance_factor(node.left) >= 0:
            return self._rotate_right(node), deleted

        # Left-Right情况
        if balance > 1 and self._get_balance_factor(node.left) < 0:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node), deleted

        # Right-Right情况
        if balance < -1 and self._get_balance_factor(node.right) <= 0:
            return self._rotate_left(node), deleted

        # Right-Left情况
        if balance < -1 and self._get_balance_factor(node.right) > 0:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node), deleted

        return node, deleted


# ============== 应用示例类 ==============

class Leaderboard:
    """
    排行榜系统
    使用AVL树实现高效的排行榜管理
    """
    def __init__(self, mode='time'):
        """
        初始化排行榜
        :param mode: 排序模式 'time'(时间越少越好) 或 'score'(分数越高越好)
        """
        self.tree = AVLTree()
        self.mode = mode
        self.records = {}  # 存储完整记录 {key: record}

    def add_record(self, player_name, value, **kwargs):
        """
        添加记录
        :param player_name: 玩家名称
        :param value: 排序值（时间或分数）
        :param kwargs: 其他记录信息
        """
        record = {
            'player_name': player_name,
            'value': value,
            **kwargs
        }

        # 生成唯一键（避免重复）
        import time
        key = value + time.time() / 1000000

        self.tree.insert(key, record)
        self.records[key] = record

        print(f"添加记录：{player_name} - {value}")

    def get_top_n(self, n=10):
        """
        获取前N名
        :param n: 数量
        :return: 记录列表
        """
        all_records = self.tree.inorder_traversal()

        if self.mode == 'time':
            # 时间模式：升序（时间越少排名越高）
            top_records = all_records[:n]
        else:
            # 分数模式：降序（分数越高排名越高）
            top_records = all_records[-n:]
            top_records.reverse()

        return [data for key, data in top_records]

    def get_rank(self, player_name):
        """
        获取玩家排名
        :param player_name: 玩家名称
        :return: 排名（从1开始），未找到返回-1
        """
        all_records = self.tree.inorder_traversal()

        if self.mode == 'score':
            all_records.reverse()

        for rank, (key, data) in enumerate(all_records, 1):
            if data['player_name'] == player_name:
                return rank

        return -1

    def get_player_best(self, player_name):
        """
        获取玩家最佳成绩
        :param player_name: 玩家名称
        :return: 最佳记录，未找到返回None
        """
        player_records = [
            (key, data) for key, data in self.tree.inorder_traversal()
            if data['player_name'] == player_name
        ]

        if not player_records:
            return None

        if self.mode == 'time':
            # 返回时间最少的
            return min(player_records, key=lambda x: x[1]['value'])[1]
        else:
            # 返回分数最高的
            return max(player_records, key=lambda x: x[1]['value'])[1]

    def get_all_records(self):
        """获取所有记录（已排序）"""
        all_records = self.tree.inorder_traversal()

        if self.mode == 'score':
            all_records.reverse()

        return [data for key, data in all_records]

    def clear(self):
        """清空排行榜"""
        self.tree.clear()
        self.records.clear()

    def get_statistics(self):
        """获取统计信息"""
        all_records = self.tree.inorder_traversal()

        if not all_records:
            return {
                'total_records': 0,
                'best_value': None,
                'worst_value': None,
                'average_value': 0
            }

        values = [data['value'] for key, data in all_records]

        return {
            'total_records': len(values),
            'best_value': min(values) if self.mode == 'time' else max(values),
            'worst_value': max(values) if self.mode == 'time' else min(values),
            'average_value': sum(values) / len(values)
        }


# ============== 测试代码 ==============
if __name__ == '__main__':
    print("="*50)
    print("二叉搜索树测试")
    print("="*50)

    bst = BinarySearchTree()

    print("\n1. 插入节点：")
    values = [50, 30, 70, 20, 40, 60, 80]
    for val in values:
        bst.insert(val, f"数据{val}")
        print(f"   插入 {val}")

    print(f"\n2. 树的信息：")
    print(f"   大小：{bst.get_size()}")
    print(f"   高度：{bst.get_height()}")
    print(f"   是否平衡：{bst.is_balanced()}")

    print(f"\n3. 遍历：")
    print(f"   中序遍历：{[k for k, d in bst.inorder_traversal()]}")
    print(f"   前序遍历：{[k for k, d in bst.preorder_traversal()]}")
    print(f"   层序遍历：{[k for k, d in bst.level_order_traversal()]}")

    print(f"\n4. 查找：")
    print(f"   查找40：{bst.search(40)}")
    print(f"   最小值：{bst.get_min()}")
    print(f"   最大值：{bst.get_max()}")

    print(f"\n5. 删除：")
    bst.delete(20)
    print(f"   删除20后：{[k for k, d in bst.inorder_traversal()]}")

    # 测试AVL树
    print("\n" + "="*50)
    print("AVL树测试")
    print("="*50)

    avl = AVLTree()

    print("\n1. 插入节点（会自动平衡）：")
    values = [10, 20, 30, 40, 50, 25]
    for val in values:
        avl.insert(val, f"数据{val}")
        print(f"   插入 {val}，高度：{avl.get_height()}")

    print(f"\n2. AVL树信息：")
    print(f"   大小：{avl.get_size()}")
    print(f"   高度：{avl.get_height()}")
    print(f"   是否平衡：{avl.is_balanced()}")
    print(f"   中序遍历：{[k for k, d in avl.inorder_traversal()]}")

    # 测试排行榜
    print("\n" + "="*50)
    print("排行榜系统测试")
    print("="*50)

    leaderboard = Leaderboard(mode='time')

    print("\n1. 添加记录：")
    players = [
        ('Alice', 120, {'moves': 20}),
        ('Bob', 95, {'moves': 18}),
        ('Charlie', 150, {'moves': 25}),
        ('David', 88, {'moves': 16}),
        ('Eve', 110, {'moves': 22})
    ]

    for name, time, extra in players:
        leaderboard.add_record(name, time, **extra)

    print("\n2. 前3名：")
    for i, record in enumerate(leaderboard.get_top_n(3), 1):
        print(f"   {i}. {record['player_name']} - {record['value']}秒")

    print("\n3. 玩家排名：")
    print(f"   Bob的排名：第{leaderboard.get_rank('Bob')}名")
    print(f"   Charlie的排名：第{leaderboard.get_rank('Charlie')}名")

    print("\n4. 统计信息：")
    stats = leaderboard.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

"""
Trie (字典树/前缀树) 实现
用于：成就系统的高效搜索/自动补全
"""

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.data = None  # 存储关联的数据（例如成就对象）

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, data):
        """
        插入单词及其关联数据
        :param word: 关键词（如成就名称）
        :param data: 完整数据对象
        """
        node = self.root
        # 统一转小写以支持不区分大小写搜索
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.data = data

    def search_prefix(self, prefix):
        """
        查找所有以 prefix 为前缀的词关联的数据
        :return: 数据列表
        """
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        
        # 找到前缀对应的节点后，收集该节点下所有子树的单词数据
        results = []
        self._collect_data(node, results)
        return results

    def _collect_data(self, node, results):
        if node.is_end_of_word:
            results.append(node.data)
        
        for char in node.children:
            self._collect_data(node.children[char], results)
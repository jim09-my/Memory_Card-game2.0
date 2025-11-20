"""
简易成就管理器
如果 data/achievements.json 为空，会用 config 中的默认成就初始化。
提供简单的查询/解锁接口。
"""
from managers.data_manager import load_achievements, save_achievements
from config import AchievementConfig


class AchievementManager:
    def __init__(self):
        self._achievements = None
        self.load()

    def load(self):
        data = load_achievements()
        # 支持两种格式：旧版直接是列表，新版是 {definitions: [], unlocked: {}}
        if not data:
            defs = AchievementConfig.ACHIEVEMENTS if hasattr(AchievementConfig, 'ACHIEVEMENTS') else []
            # 写入标准化格式
            save_achievements({'definitions': defs, 'unlocked': {}})
            self._achievements = defs
            return self._achievements

        if isinstance(data, dict):
            defs = data.get('definitions', [])
            self._achievements = defs
            return self._achievements

        # 兼容旧版 list 格式
        self._achievements = data
        return self._achievements

    def get_all(self):
        return self._achievements

    def find_by_id(self, ach_id):
        for a in self._achievements:
            if a.get('id') == ach_id:
                return a
        return None

    def save(self):
        # 保存为标准化结构：{definitions: [...], unlocked: {...}}
        try:
            existing = load_achievements()
            unlocked = {}
            if isinstance(existing, dict):
                unlocked = existing.get('unlocked', {})
        except Exception:
            unlocked = {}
        save_achievements({'definitions': self._achievements, 'unlocked': unlocked})

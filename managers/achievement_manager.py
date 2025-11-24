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
        if not data:
            defs = AchievementConfig.ACHIEVEMENTS if hasattr(AchievementConfig, 'ACHIEVEMENTS') else []
            serializable_defs = [{k: v for k, v in a.items() if k != 'condition'} for a in defs]
            save_achievements({'definitions': serializable_defs, 'unlocked': {}})
            self._achievements = defs
            return self._achievements

        if isinstance(data, dict):
            defs = data.get('definitions', [])
            if not defs:
                defs = AchievementConfig.ACHIEVEMENTS if hasattr(AchievementConfig, 'ACHIEVEMENTS') else []
                serializable_defs = [{k: v for k, v in a.items() if k != 'condition'} for a in defs]
                save_achievements({'definitions': serializable_defs, 'unlocked': data.get('unlocked', {})})
            else:
                serializable_defs = [{k: v for k, v in a.items() if k != 'condition'} for a in defs]
                try:
                    save_achievements({'definitions': serializable_defs, 'unlocked': data.get('unlocked', {})})
                except Exception:
                    pass
            self._achievements = defs
            return self._achievements

        self._achievements = data
        try:
            serializable_defs = [{k: v for k, v in a.items() if k != 'condition'} for a in data]
            save_achievements({'definitions': serializable_defs, 'unlocked': {}})
        except Exception:
            pass
        return self._achievements

    def get_all(self):
        return self._achievements

    def find_by_id(self, ach_id):
        for a in self._achievements:
            if a.get('id') == ach_id:
                return a
        return None

    def save(self):
        try:
            existing = load_achievements()
            unlocked = {}
            if isinstance(existing, dict):
                unlocked = existing.get('unlocked', {})
        except Exception:
            unlocked = {}
        serializable_defs = [{k: v for k, v in a.items() if k != 'condition'} for a in (self._achievements or [])]
        save_achievements({'definitions': serializable_defs, 'unlocked': unlocked})

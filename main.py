"""
程序入口
"""

import json
import os

from config import DataConfig
from gui.login_window import LoginWindow
from gui.main_window import MainWindow


def ensure_data_files():
    """确保基础数据文件存在"""
    # 仅创建必须的全局文件；用户已选择不需要 player_profiles.json, settings.json, shop_items.json
    defaults = {
        DataConfig.PLAYERS_FILE: {},
        DataConfig.RECORDS_FILE: [],
        DataConfig.ACHIEVEMENTS_FILE: []
    }

    data_dir = os.path.dirname(DataConfig.PLAYERS_FILE)
    os.makedirs(data_dir, exist_ok=True)
                               
    for path, default_content in defaults.items():
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(default_content, f, indent=2, ensure_ascii=False)

    # 删除不需要的旧文件（如果存在）: player_profiles.json, settings.json, shop_items.json
    try:
        profiles_file = os.path.join(os.path.dirname(DataConfig.PLAYERS_FILE), 'player_profiles.json')
        for p in [profiles_file, DataConfig.SETTINGS_FILE, DataConfig.SHOP_FILE]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
    except Exception:
        pass


def run_application():
    """启动应用"""
    ensure_data_files()

    # 初始化管理器数据（如果文件为空则写入默认配置）
    try:
        from managers.achievement_manager import AchievementManager
        from managers.shop_manager import ShopManager

        AchievementManager().load()
        ShopManager().load()
    except Exception:
        # 如果管理器不可用则继续（保持向后兼容）
        pass

    def handle_login_success(player):
        main_window = MainWindow(player)
        main_window.run()

    login_window = LoginWindow(handle_login_success)
    login_window.run()


if __name__ == '__main__':
    run_application()

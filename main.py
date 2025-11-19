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
    defaults = {
        DataConfig.PLAYERS_FILE: {},
        DataConfig.RECORDS_FILE: [],
        DataConfig.ACHIEVEMENTS_FILE: [],
        DataConfig.SHOP_FILE: {},
        DataConfig.SETTINGS_FILE: {}
    }

    data_dir = os.path.dirname(DataConfig.PLAYERS_FILE)
    os.makedirs(data_dir, exist_ok=True)

    for path, default_content in defaults.items():
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(default_content, f, indent=2, ensure_ascii=False)


def run_application():
    """启动应用"""
    ensure_data_files()

    def handle_login_success(player):
        main_window = MainWindow(player)
        main_window.run()

    login_window = LoginWindow(handle_login_success)
    login_window.run()


if __name__ == '__main__':
    run_application()

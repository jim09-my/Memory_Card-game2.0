"""
程序入口
"""
import json
import os
import sys
import shutil 

if getattr(sys, 'frozen', False):
    sys.path.append(os.path.dirname(sys.executable))
else:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import DataConfig
from gui.login_window import LoginWindow
from gui.main_window import MainWindow

def get_bundled_data_path(filename):

    if getattr(sys, 'frozen', False):
        base_path = os.path.join(sys._MEIPASS, 'initial_data')
    else:
        base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    return os.path.join(base_path, filename)

def ensure_data_files():
    """
    初始化数据文件
    """
    # 目标目录 (AppData)
    target_dir = DataConfig.DATA_DIR
    
    # 1. 确保目标目录存在
    if not os.path.exists(target_dir):
        try:
            os.makedirs(target_dir)
            print(f"已创建数据目录: {target_dir}")
        except Exception as e:
            print(f"创建目录失败: {e}")

    # 2. 定义需要管理的文件列表
    files_to_check = {
        DataConfig.PLAYERS_FILE: {},
        DataConfig.RECORDS_FILE: [],
        DataConfig.ACHIEVEMENTS_FILE: {'definitions': [], 'unlocked': {}},
        DataConfig.SHOP_FILE: None # 商点文件如果不存，ShopManager会自动处理，这里设None
    }
                               
    # 3. 循环检查
    for target_path, default_content in files_to_check.items():
        if os.path.exists(target_path):
            continue

        filename = os.path.basename(target_path)
        
        # 获取打包在 exe 里的旧数据路径
        bundled_source = get_bundled_data_path(filename)

        try:
            if os.path.exists(bundled_source):
                shutil.copy2(bundled_source, target_path)
                print(f"✨ 已从安装包恢复数据: {filename}")
            
            elif default_content is not None:
                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump(default_content, f, indent=2, ensure_ascii=False)
                print(f"已初始化空文件: {filename}")
                
        except Exception as e:
            print(f"初始化文件失败 {filename}: {e}")

    # 4. 清理旧垃圾文件
    try:
        old_profiles = os.path.join(os.path.dirname(DataConfig.PLAYERS_FILE), 'player_profiles.json')
        if os.path.exists(old_profiles):
            os.remove(old_profiles)
    except Exception:
        pass


def run_application():
    """启动应用"""
    ensure_data_files()

    try:
        from managers.achievement_manager import AchievementManager
        from managers.shop_manager import ShopManager
        AchievementManager().load()
        ShopManager().load()
    except Exception as e:
        print(f"管理器加载警告: {e}")

    def handle_login_success(player):
        main_window = MainWindow(player)
        main_window.run()

    login_window = LoginWindow(handle_login_success)
    login_window.run()


if __name__ == '__main__':
    try:
        run_application()
    except Exception as e:
        print(f"程序崩溃: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")
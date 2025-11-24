"""
测试洗牌触发逻辑（不启动 GUI）
用法：在项目根目录运行 `python test_shuffle.py` 查看输出
"""
from core.game import Game

print('创建终极洗牌模式游戏（ultimate_shuffle）')
g = Game(mode='ultimate_shuffle')
g.start_game()

# 打印初始状态
print('初始状态：', 'moves=', g.moves, 'consecutive_failures=', g.consecutive_failures)

# 模拟若干次失败，直到达到阈值附近
# 我们直接设置 moves 和 consecutive_failures 来模拟场景
from core.game import Game as GClass

# 读取当前阈值逻辑：调用内部方法前先修改状态以便观察
# 模拟不同组合以测试触发条件
scenarios = [
    {'moves': 3, 'fails': 3},
    {'moves': 4, 'fails': 3},
    {'moves': 5, 'fails': 4},
    {'moves': 6, 'fails': 4},
    {'moves': 7, 'fails': 5}
]

for s in scenarios:
    print('\n--- 场景:', s)
    g.moves = s['moves']
    g.consecutive_failures = s['fails']
    triggered = g._check_shuffle_trigger()
    print('触发结果:', triggered)
    print('shuffle_status:', getattr(g, 'shuffle_status', None))

print('\n测试结束')
print('\n测试防洗牌护盾使用后清零连续失败')
from core.player import Player
p = Player('tester')
p.add_item('shuffle_prevent', 1)
g = Game(mode='ultimate_shuffle', player=p)
g.start_game()
g.consecutive_failures = 5
print('使用前:', 'consecutive_failures=', g.consecutive_failures)
activated = g.activate_shuffle_prevent()
print('激活结果:', activated)
print('使用后:', 'consecutive_failures=', g.consecutive_failures, 'shield_active=', g.shuffle_prevent_active, 'items_used=', g.items_used['shuffle_prevent'])
g.consecutive_failures = 7
blocked = g._check_shuffle_trigger()
print('下一次洗牌是否被阻止:', not blocked, 'shield_active_now=', g.shuffle_prevent_active)

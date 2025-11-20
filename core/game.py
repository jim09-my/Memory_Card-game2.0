"""
游戏核心逻辑
管理游戏状态和规则
"""

import random
import time
from core.card import Card, CardFactory
from core.timer import Timer
from data_structures.stack import Stack
from data_structures.queue import Queue
from config import AchievementConfig
from managers.data_manager import append_record, add_unlocked_achievement, save_player

class Game:
    """记忆翻牌游戏核心类"""

    def __init__(self, mode='normal', player=None):
        """
        初始化游戏
        :param mode: 游戏模式 ('normal' 或 'ultimate')
        :param player: 玩家对象
        """
        self.mode = mode
        self.player = player

        # 游戏配置
        if mode == 'normal':
            self.grid_size = 4
            self.time_limit = None
            self.shuffle_enabled = False
        elif mode == 'ultimate':
            self.grid_size = 6
            self.time_limit = 120  # 2分钟
            self.shuffle_enabled = False
        elif mode == 'ultimate_shuffle':
            self.grid_size = 6
            self.time_limit = 180  # 3分钟
            self.shuffle_enabled = True
        else:
            raise ValueError(f"未知的游戏模式：{mode}")

        self.shuffle_failures = 0
        self.shuffle_status = None
        self.pending_shuffle_prevention = False
        self.last_pair = None
        self.last_match = None
        self.flipped_cards = []
        self.matched_pairs = 0
        self.moves = 0
        self.score = 0
        self.mistakes = 0
        self.resolving_pair = False

        # 计时器
        self.timer = Timer(time_limit=self.time_limit)

        # 游戏状态
        self.is_started = False
        self.is_paused = False
        self.is_completed = False
        self.is_failed = False

        # 历史记录（用于撤销）
        self.move_history = Stack(max_size=10)

        # 道具使用记录
        self.items_used = {
            'hint': 0,
            'time_extend': 0,
            'shuffle_prevent': 0,
            'undo': 0
        }

        # 提示显示的卡牌
        self.hint_cards = []

    def start_game(self):
        """开始游戏"""
        if self.is_started:
            print("游戏已经开始")
            return False

        # 创建卡牌
        self.cards = CardFactory.create_card_deck(self.grid_size)

        # 重置状态
        self.flipped_cards = []
        self.matched_pairs = 0
        self.moves = 0
        self.score = 0
        self.mistakes = 0
        self.is_started = True
        self.is_completed = False
        self.is_failed = False

        # 启动计时器
        self.timer.start()

        print(f"游戏开始 - {self.mode}模式 ({self.grid_size}x{self.grid_size})")
        return True

    def flip_card(self, card_index):
        """
        翻牌
        :param card_index: 卡牌索引
        :return: 是否成功
        """
        if not self.is_started or self.is_paused or self.is_completed:
            return False

        # 检查超时
        if self.timer.is_time_up():
            self.fail_game()
            return False

        # 检查索引
        if card_index < 0 or card_index >= len(self.cards):
            print("无效的卡牌索引")
            return False

        card = self.cards[card_index]

        # 检查是否可以翻转
        if not card.can_flip():
            print("该卡牌无法翻转")
            return False

        # 已经有两张翻开的卡牌或正在处理上一对
        if self.resolving_pair or len(self.flipped_cards) >= 2:
            print("已有两张卡牌翻开，请先处理")
            return False

        # 翻牌
        card.flip_up()
        self.flipped_cards.append(card_index)

        print(f"翻开卡牌 {card_index}: 值={card.value}")

        # 如果翻开了两张卡牌，检查是否匹配并标记等待决议
        if len(self.flipped_cards) == 2:
            self._check_match()
            self.resolving_pair = True

        return True

    def _check_match(self):
        """检查两张卡牌是否匹配"""
        if len(self.flipped_cards) != 2:
            return

        idx1, idx2 = self.flipped_cards
        card1 = self.cards[idx1]
        card2 = self.cards[idx2]

        self.moves += 1

        # 保存状态（用于撤销）
        self._save_state()

        pair = (idx1, idx2)
        match = card1.value == card2.value
        if match:
            # 匹配成功
            card1.match()
            card2.match()
            self.matched_pairs += 1
            self.score += 10

            print(f"OK 配对成功！已完成 {self.matched_pairs}/{self.get_total_pairs()}")
            
            # 检查是否完成
            if self.matched_pairs == self.get_total_pairs():
                self.complete_game()
        else:
            # 匹配失败
            self.mistakes += 1
            self.score = max(0, self.score - 1)
            print(f"X 配对失败")

        self.last_pair = pair
        self.last_match = match

    def flip_back_cards(self, pair=None):
        """将未匹配的卡牌翻回"""
        targets = pair if pair is not None else self.flipped_cards
        for idx in targets:
            card = self.cards[idx]
            if not card.is_matched:
                card.flip_down()

    def clear_flipped_cards(self):
        self.flipped_cards = []

    def _save_state(self):
        """保存当前状态（用于撤销）"""
        state = {
            'cards': [card.to_dict() for card in self.cards],
            'flipped_cards': self.flipped_cards.copy(),
            'matched_pairs': self.matched_pairs,
            'moves': self.moves,
            'score': self.score,
            'mistakes': self.mistakes
        }
        self.move_history.push(state)

    def undo_move(self):
        """撤销上一步"""
        if self.move_history.is_empty():
            print("没有可撤销的步骤")
            return False

        # 检查玩家是否有撤销道具
        if self.player and not self.player.has_item('undo'):
            print("没有撤销道具")
            return False

        # 恢复状态
        state = self.move_history.pop()

        # 恢复卡牌
        for i, card_data in enumerate(state['cards']):
            self.cards[i] = Card.from_dict(card_data)

        self.flipped_cards = state['flipped_cards']
        self.matched_pairs = state['matched_pairs']
        self.moves = state['moves']
        self.score = state['score']
        self.mistakes = state['mistakes']

        # 使用道具
        if self.player:
            self.player.use_item('undo')
            self.items_used['undo'] += 1

        print("已撤销上一步")
        return True

    def use_hint(self):
        """使用提示道具"""
        if not self.is_started or self.is_completed:
            return False

        # 检查玩家是否有提示道具
        if self.player and not self.player.has_item('hint'):
            print("没有提示道具")
            return False

        # 找到一对未匹配的卡牌
        unmatched_values = {}
        for i, card in enumerate(self.cards):
            if not card.is_matched:
                if card.value not in unmatched_values:
                    unmatched_values[card.value] = []
                unmatched_values[card.value].append(i)

        # 随机选择一对
        for value, indices in unmatched_values.items():
            if len(indices) >= 2:
                self.hint_cards = indices[:2]

                # 显示提示
                for idx in self.hint_cards:
                    self.cards[idx].reveal()

                # 使用道具
                if self.player:
                    self.player.use_item('hint')
                    self.items_used['hint'] += 1

                print(f"💡 提示：卡牌 {self.hint_cards[0]} 和 {self.hint_cards[1]} 是一对")
                return True

        print("没有可提示的卡牌")
        return False

    def hide_hint(self):
        """隐藏提示"""
        for idx in self.hint_cards:
            if idx < len(self.cards):
                self.cards[idx].hide_reveal()
        self.hint_cards = []

    def extend_time(self, seconds=30):
        """延长时间"""
        if self.timer.time_limit is None:
            print("当前模式无时间限制")
            return False

        # 检查玩家是否有延时道具
        if self.player and not self.player.has_item('time_extend'):
            print("没有延时道具")
            return False

        self.timer.extend_time(seconds)

        # 使用道具
        if self.player:
            self.player.use_item('time_extend')
            self.items_used['time_extend'] += 1

        print(f"⏰ 时间延长 {seconds} 秒")
        return True

    def shuffle_cards(self):
        """洗牌"""
        # 获取未匹配的卡牌
        unmatched_cards = [card for card in self.cards if not card.is_matched]

        if len(unmatched_cards) <= 2:
            print("卡牌太少，无需洗牌")
            return False

        # 提取值并打乱
        values = [card.value for card in unmatched_cards]
        random.shuffle(values)

        # 重新赋值
        for i, card in enumerate(unmatched_cards):
            card.value = values[i]
            card.reset()

        # 清空翻开的卡牌
        self.flipped_cards = []

        print("🔀 卡牌已洗牌")
        return True

    def pause_game(self):
        """暂停游戏"""
        if not self.is_started or self.is_paused or self.is_completed:
            return False

        self.is_paused = True
        self.timer.pause()
        print("游戏已暂停")
        return True

    def resume_game(self):
        """继续游戏"""
        if not self.is_started or not self.is_paused:
            return False

        self.is_paused = False
        self.timer.resume()
        print("游戏已继续")
        return True

    def complete_game(self):
        """完成游戏"""
        if self.is_completed:
            return

        self.is_completed = True
        self.timer.stop()

        time_used = int(self.timer.get_elapsed_time())

        print(f"\n{'='*50}")
        print(f"🎉 恭喜通关！")
        print(f"{'='*50}")
        print(f"用时: {self.timer.format_time(time_used)}")
        print(f"步数: {self.moves}")
        print(f"失误: {self.mistakes}")
        print(f"得分: {self.score}")
        print(f"{'='*50}\n")

        # 计算奖励
        reward = self._calculate_reward(time_used)

        # 保存记录
        if self.player:
            record = {
                'mode': self.mode,
                'grid_size': self.grid_size,
                'username': self.player.username if self.player else None,
                'completed': True,
                'time_used': time_used,
                'moves': self.moves,
                'mistakes': self.mistakes,
                'score': self.score,
                'reward': reward,
                'items_used': self.items_used.copy()
            }
            # 全局追加记录（立即写盘，保证可见性）
            try:
                append_record(record)
            except Exception:
                pass

            # 更新玩家内存状态并通知监听器
            self.player.add_game_record(record)
            self.player.add_points(reward)
            # 检查并解锁成就（基于配置中的条件）
            try:
                for ach in getattr(AchievementConfig, 'ACHIEVEMENTS', []):
                    aid = ach.get('id')
                    if aid and ach.get('condition') and ach.get('condition')(self.player):
                        if not self.player.has_achievement(aid):
                            self.player.unlock_achievement(aid)
                            # 奖励积分（如果配置中定义）
                            reward_amount = ach.get('reward', 0)
                            if reward_amount:
                                self.player.add_points(reward_amount)
                            # 记录到 achievements.json unlocked 映射
                            try:
                                add_unlocked_achievement(self.player.username, aid)
                            except Exception:
                                pass
            except Exception:
                pass
            # 持久化玩家（写入 players.json，包括运行态）
            try:
                save_player(self.player)
            except Exception:
                pass
            # 强制通知监听器，确保 UI 能尽快刷新（增加刷新可靠性）
            try:
                if hasattr(self.player, '_notify_listeners'):
                    self.player._notify_listeners()
            except Exception:
                pass

    def fail_game(self):
        """游戏失败（超时）"""
        if self.is_failed or self.is_completed:
            return

        self.is_failed = True
        self.timer.stop()

        print(f"\n{'='*50}")
        print(f"⏰ 时间到！游戏失败")
        print(f"{'='*50}")
        print(f"已完成: {self.matched_pairs}/{self.get_total_pairs()}")
        print(f"步数: {self.moves}")
        print(f"{'='*50}\n")

        # 保存记录
        if self.player:
            record = {
                'mode': self.mode,
                'grid_size': self.grid_size,
                'username': self.player.username if self.player else None,
                'completed': False,
                'time_used': int(self.timer.get_elapsed_time()),
                'moves': self.moves,
                'mistakes': self.mistakes,
                'score': self.score,
                'reward': 0,
                'items_used': self.items_used.copy()
            }
            # 全局追加记录并立即写盘
            try:
                append_record(record)
            except Exception:
                pass

            self.player.add_game_record(record)

            # 持久化玩家（写入 players.json，包括运行态）
            try:
                save_player(self.player)
            except Exception:
                pass
            try:
                if hasattr(self.player, '_notify_listeners'):
                    self.player._notify_listeners()
            except Exception:
                pass

    def _calculate_reward(self, time_used):
        """
        计算奖励积分
        :param time_used: 用时（秒）
        :return: 奖励积分
        """
        base_reward = 200 if self.mode == 'normal' else 1200

        # 时间奖励（快速完成加分）
        if self.mode == 'normal':
            if time_used < 60:
                base_reward += 100
            elif time_used < 120:
                base_reward += 50
        else:  # ultimate
            if time_used < 240:
                base_reward += 300
            elif time_used < 360:
                base_reward += 150

        # 失误惩罚
        base_reward -= self.mistakes * 5

        # 零失误奖励
        if self.mistakes == 0:
            base_reward += 500

        return max(base_reward, 100)

    def get_last_pair(self):
        return self.last_pair, self.last_match

    def clear_last_pair(self):
        self.last_pair = None
        self.last_match = None

    def resolve_current_pair(self):
        pair, matched = self.get_last_pair()
        if pair is None:
            self.resolving_pair = False
            return False
        if not matched:
            self.flip_back_cards(pair)
        self.clear_last_pair()
        self.clear_flipped_cards()
        self.resolving_pair = False
        if self.matched_pairs == self.get_total_pairs():
            self.complete_game()
        return True

    def get_total_pairs(self):
        """获取总对数"""
        return (self.grid_size * self.grid_size) // 2

    def get_progress(self):
        """
        获取游戏进度
        :return: 进度百分比
        """
        total_pairs = self.get_total_pairs()
        return (self.matched_pairs / total_pairs * 100) if total_pairs > 0 else 0

    def get_card_at(self, row, col):
        """
        获取指定位置的卡牌
        :param row: 行
        :param col: 列
        :return: 卡牌对象
        """
        index = row * self.grid_size + col
        if 0 <= index < len(self.cards):
            return self.cards[index]
        return None

    def get_card_by_index(self, index):
        """获取指定索引的卡牌"""
        if 0 <= index < len(self.cards):
            return self.cards[index]
        return None

    def get_status(self):
        """
        获取游戏状态
        :return: 状态字典
        """
        return {
            'mode': self.mode,
            'grid_size': self.grid_size,
            'is_started': self.is_started,
            'is_paused': self.is_paused,
            'is_completed': self.is_completed,
            'is_failed': self.is_failed,
            'matched_pairs': self.matched_pairs,
            'total_pairs': self.get_total_pairs(),
            'progress': self.get_progress(),
            'moves': self.moves,
            'mistakes': self.mistakes,
            'score': self.score,
            'time_elapsed': self.timer.get_elapsed_time(),
            'time_remaining': self.timer.get_remaining_time(),
            'time_display': self.timer.get_time_display(),
            'items_used': self.items_used.copy()
        }

    def __str__(self):
        """字符串表示"""
        status = "进行中" if self.is_started and not self.is_completed else ("已完成" if self.is_completed else "未开始")
        return f"Game({self.mode}, {status}, {self.matched_pairs}/{self.get_total_pairs()})"


# ============== 测试代码 ==============
if __name__ == '__main__':
    print("="*50)
    print("游戏核心逻辑测试")
    print("="*50)

    from core.player import Player

    # 创建玩家
    player = Player("TestPlayer")
    player.add_item('hint', 3)
    player.add_item('time_extend', 2)
    player.add_item('undo', 2)

    # 创建游戏
    game = Game(mode='normal', player=player)

    print("\n1. 开始游戏：")
    game.start_game()

    print("\n2. 显示卡牌布局：")
    for row in range(game.grid_size):
        line = ""
        for col in range(game.grid_size):
            card = game.get_card_at(row, col)
            line += f"{card.value:2d} "
        print(f"   {line}")

    print("\n3. 模拟游戏流程：")
    # 找到第一对匹配的卡牌
    value_positions = {}
    for i, card in enumerate(game.cards):
        if card.value not in value_positions:
            value_positions[card.value] = []
        value_positions[card.value].append(i)

    # 进行几次翻牌
    for value, positions in list(value_positions.items())[:3]:
        if len(positions) >= 2:
            print(f"\n   翻牌测试 - 值 {value}:")
            idx1, idx2 = positions[:2]

            game.flip_card(idx1)
            print(f"   状态: {game.get_status()}")

            time.sleep(0.5)

            game.flip_card(idx2)
            print(f"   状态: {game.get_status()}")

            time.sleep(0.5)

    print("\n4. 使用提示道具：")
    game.use_hint()

    print("\n5. 游戏状态：")
    status = game.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")

    print("\n6. 玩家统计：")
    stats = player.get_statistics()
    print(f"   总游戏数: {stats['total_games']}")
    print(f"   完成游戏数: {stats['completed_games']}")
    print(f"   当前积分: {stats['points']}")

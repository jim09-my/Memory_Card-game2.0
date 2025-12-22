"""
游戏核心逻辑
管理游戏状态和规则
"""

import random
import time
from core.card import Card, CardFactory
from core.timer import Timer

from data_structures.stack import Stack
from data_structures.linked_list import CardList
from config import AchievementConfig
from managers.data_manager import append_record, add_unlocked_achievement, save_player

class Game:
    """记忆翻牌游戏核心类"""

    def __init__(self, mode='normal', player=None):
        self.mode = mode
        self.player = player

        # 游戏配置
        if mode == 'normal':
            self.grid_size = 4
            self.time_limit = None
            self.shuffle_enabled = False
        elif mode == 'ultimate':
            self.grid_size = 6
            self.time_limit = 120
            self.shuffle_enabled = False
        elif mode == 'ultimate_shuffle':
            self.grid_size = 6
            self.time_limit = 180
            self.shuffle_enabled = True
        else:
            raise ValueError(f"未知的游戏模式：{mode}")

        self.consecutive_failures = 0
        self.shuffle_prevent_active = False
        self.shuffle_warning_shown = False
        self.last_pair = None
        self.last_match = None
        self.flipped_cards = []
        self.matched_pairs = 0
        self.moves = 0
        self.score = 0
        self.mistakes = 0
        self.resolving_pair = False
        
        self.cards = CardList() 

        self.timer = Timer(time_limit=self.time_limit)
        self.is_started = False
        self.is_paused = False
        self.is_completed = False
        self.is_failed = False

        self.move_history = Stack(max_size=10)

        self.items_used = {'hint': 0, 'time_extend': 0, 'shuffle_prevent': 0, 'undo': 0}
        self.hint_cards = []

    def start_game(self):
        if self.is_started:
            return False

        # 创建卡牌 (Factory返回的是list，转存到 CardList 链表中)
        raw_cards = CardFactory.create_card_deck(self.grid_size)
        self.cards = CardList() # 重置链表
        for card in raw_cards:
            self.cards.add_card(card)

        self.flipped_cards = []
        self.matched_pairs = 0
        self.moves = 0
        self.score = 0
        self.mistakes = 0
        self.consecutive_failures = 0
        self.shuffle_prevent_active = False
        self.shuffle_warning_shown = False
        self.is_started = True
        self.is_completed = False
        self.is_failed = False

        self.timer.start()
        print(f"游戏开始 - {self.mode}模式 ({self.grid_size}x{self.grid_size})")
        return True

    def flip_card(self, card_index):
        if not self.is_started or self.is_paused or self.is_completed:
            return False

        if self.timer.is_time_up():
            self.fail_game()
            return False

        if card_index < 0 or card_index >= self.cards.get_size():
            return False

        card = self.cards.get_card(card_index)

        if not card.can_flip():
            return False

        self._save_state()

        if self.resolving_pair or len(self.flipped_cards) >= 2:
            return False

        card.flip_up()
        self.flipped_cards.append(card_index)

        if len(self.flipped_cards) == 2:
            self._check_match()
            self.resolving_pair = True

        return True

    def _check_match(self):
        if len(self.flipped_cards) != 2:
            return

        idx1, idx2 = self.flipped_cards
        card1 = self.cards.get_card(idx1)
        card2 = self.cards.get_card(idx2)

        self.moves += 1
        pair = (idx1, idx2)
        match = card1.value == card2.value
        
        if match:
            card1.match()
            card2.match()
            self.matched_pairs += 1
            self.score += 10
            self.consecutive_failures = 0
            self.shuffle_warning_shown = False
            
            if self.matched_pairs == self.get_total_pairs():
                self.complete_game()
        else:
            self.mistakes += 1
            self.score = max(0, self.score - 1)
            self.consecutive_failures += 1
            
            if self.mode == 'ultimate_shuffle' and self.shuffle_enabled:
                self._check_shuffle_trigger()

        self.last_pair = pair
        self.last_match = match

    def flip_back_cards(self, pair=None):
        targets = pair if pair is not None else self.flipped_cards
        for idx in targets:
            card = self.cards.get_card(idx)
            if not card.is_matched:
                card.flip_down()

    def clear_flipped_cards(self):
        self.flipped_cards = []

    def _save_state(self):
        all_cards_data = [c.to_dict() for c in self.cards.get_all_cards()]
        
        state = {
            'cards': all_cards_data,
            'flipped_cards': self.flipped_cards.copy(),
            'matched_pairs': self.matched_pairs,
            'moves': self.moves,
            'score': self.score,
            'mistakes': self.mistakes,
            'resolving_pair': self.resolving_pair,
            'last_pair': self.last_pair,
            'last_match': self.last_match
        }
        self.move_history.push(state)

    def undo_move(self):
        if self.move_history.is_empty():
            return False
        if self.player and not self.player.has_item('undo'):
            return False

        state = self.move_history.pop()

        self.cards = CardList()
        for card_data in state['cards']:
            self.cards.add_card(Card.from_dict(card_data))

        self.flipped_cards = state['flipped_cards']
        self.matched_pairs = state['matched_pairs']
        self.moves = state['moves']
        self.score = state['score']
        self.mistakes = state['mistakes']
        self.resolving_pair = state.get('resolving_pair', False)
        self.last_pair = state.get('last_pair')
        self.last_match = state.get('last_match')

        if self.player:
            self.player.use_item('undo')
            self.items_used['undo'] += 1
        return True

    def use_hint(self):
        if not self.is_started or self.is_completed:
            return False
        if self.player and not self.player.has_item('hint'):
            return False

        unmatched_values = {}
        all_cards = self.cards.get_all_cards()
        for i, card in enumerate(all_cards):
            if not card.is_matched:
                if card.value not in unmatched_values:
                    unmatched_values[card.value] = []
                unmatched_values[card.value].append(i)

        for value, indices in unmatched_values.items():
            if len(indices) >= 2:
                self.hint_cards = indices[:2]
                for idx in self.hint_cards:
                    self.cards.get_card(idx).reveal()
                
                if self.player:
                    self.player.use_item('hint')
                    self.items_used['hint'] += 1
                return True
        return False

    def hide_hint(self):
        for idx in self.hint_cards:
            if idx < self.cards.get_size():
                self.cards.get_card(idx).hide_reveal()
        self.hint_cards = []

    def extend_time(self, seconds=30):
        if self.timer.time_limit is None: return False
        if self.player and not self.player.has_item('time_extend'): return False
        self.timer.extend_time(seconds)
        if self.player:
            self.player.use_item('time_extend')
            self.items_used['time_extend'] += 1
        return True

    def activate_shuffle_prevent(self):
        if not self.is_started or self.is_completed: return False
        if not self.shuffle_enabled: return False
        if self.player and not self.player.has_item('shuffle_prevent'): return False
        self.shuffle_prevent_active = True
        self.consecutive_failures = 0
        self.shuffle_warning_shown = False
        if self.player:
            self.player.use_item('shuffle_prevent')
            self.items_used['shuffle_prevent'] += 1
        return True

    def _check_shuffle_trigger(self):
        SHUFFLE_THRESHOLD = 7
        if self.shuffle_prevent_active:
            self.shuffle_prevent_active = False
            self.consecutive_failures = 0
            return False
        if self.consecutive_failures >= SHUFFLE_THRESHOLD:
            if self.shuffle_cards():
                self.consecutive_failures = 0
                self.shuffle_warning_shown = False
                return True
        elif self.consecutive_failures == SHUFFLE_THRESHOLD - 1:
            self.shuffle_warning_shown = True
        return False
    
    def shuffle_cards(self):
        if self.shuffle_prevent_active: return False
        
        self.cards.shuffle()
        
        # 重新分配未匹配卡牌的值
        all_cards = self.cards.get_all_cards()
        unmatched_indices = [i for i, c in enumerate(all_cards) if not c.is_matched]
        
        if len(unmatched_indices) <= 2: return False
            
        values = [all_cards[i].value for i in unmatched_indices]
        random.shuffle(values)
        
        for i, idx in enumerate(unmatched_indices):
            card = all_cards[idx]
            card.value = values[i]
            card.reset()

        self.flipped_cards = []
        self.resolving_pair = False
        self.shuffle_status = 'shuffled'
        return True
    
    def get_shuffle_warning(self):
        SHUFFLE_THRESHOLD = 7
        if self.shuffle_enabled and self.consecutive_failures >= SHUFFLE_THRESHOLD - 1:
            remaining = SHUFFLE_THRESHOLD - self.consecutive_failures
            return True, remaining
        return False, 0

    def pause_game(self):
        if not self.is_started or self.is_paused or self.is_completed: return False
        self.is_paused = True
        self.timer.pause()
        return True

    def resume_game(self):
        if not self.is_started or not self.is_paused: return False
        self.is_paused = False
        self.timer.resume()
        return True

    # === 统一的成就检查函数 ===
    def _check_achievements(self):
        if not self.player:
            return
            
        try:
            for ach in getattr(AchievementConfig, 'ACHIEVEMENTS', []):
                aid = ach.get('id')
                if not aid or not ach.get('condition'):
                    continue
                
                if self.player.has_achievement(aid):
                    continue

                if ach['condition'](self.player):
                    self.player.unlock_achievement(aid)
                    
                    # 发放奖励
                    if ach.get('reward'): 
                        self.player.add_points(ach['reward'])
                    
                    # 持久化已解锁成就
                    try: 
                        add_unlocked_achievement(self.player.username, aid)
                    except: pass
        except Exception as e:
            print(f"Achievement check failed: {e}")

    def complete_game(self):
        if self.is_completed: return
        self.is_completed = True
        self.timer.stop()
        time_used = int(self.timer.get_elapsed_time())
        reward = self._calculate_reward(time_used)

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
            try: append_record(record)
            except: pass
            
            self.player.add_game_record(record)
            self.player.add_points(reward)

            self._check_achievements()
            
            try: save_player(self.player)
            except: pass
            
            try: 
                if hasattr(self.player, '_notify_listeners'): self.player._notify_listeners()
            except: pass

    def fail_game(self):
        if self.is_failed or self.is_completed: return
        self.is_failed = True
        self.timer.stop()
        
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
            try: append_record(record)
            except: pass
            
            self.player.add_game_record(record)
            
            self._check_achievements()

            try: save_player(self.player)
            except: pass
            try: 
                if hasattr(self.player, '_notify_listeners'): self.player._notify_listeners()
            except: pass

    def _calculate_reward(self, time_used):
        base_reward = 200 if self.mode == 'normal' else 1200
        if self.mode == 'normal':
            if time_used < 60: base_reward += 100
            elif time_used < 120: base_reward += 50
        elif self.mode == 'ultimate':
            if time_used < 60: base_reward += 300
            elif time_used < 90: base_reward += 150
        else:
            if time_used < 90: base_reward += 300
            elif time_used < 135: base_reward += 150
        base_reward -= self.mistakes * 5
        if self.mistakes == 0: base_reward += 500
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
        return (self.grid_size * self.grid_size) // 2

    def get_progress(self):
        total = self.get_total_pairs()
        return (self.matched_pairs / total * 100) if total > 0 else 0

    def get_card_at(self, row, col):
        index = row * self.grid_size + col
        if 0 <= index < self.cards.get_size():
            return self.cards.get_card(index)
        return None

    def get_card_by_index(self, index):
        if 0 <= index < self.cards.get_size():
            return self.cards.get_card(index)
        return None

    def get_status(self):
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
        status = "进行中" if self.is_started and not self.is_completed else ("已完成" if self.is_completed else "未开始")
        return f"Game({self.mode}, {status}, {self.matched_pairs}/{self.get_total_pairs()})"
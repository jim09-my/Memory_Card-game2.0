"""
简易商店管理器
负责加载商城配置，并提供购买接口。
购买成功会修改玩家数据并保存通过 data_manager.save_player
"""
from config import ItemConfig
from managers.data_manager import load_shop_items, save_shop_items, save_player


class ShopManager:
    def __init__(self):
        self._items = None
        self.load()

    def load(self):
        data = load_shop_items()
        if not data:
            data = ItemConfig.ITEMS if hasattr(ItemConfig, 'ITEMS') else {}
        self._items = data
        return self._items

    def get_items(self):
        return self._items

    def get_item(self, item_id):
        return self._items.get(item_id)

    def purchase_item(self, player, item_id):
        item = self.get_item(item_id)
        if not item:
            return False, '商品不存在'

        # 处理价格
        price = item.get('price', 0)
        if item_id == 'hint' and hasattr(player, 'can_claim_free_hint') and player.can_claim_free_hint():
            price = 0

        # 扣费并发放
        if price > 0:
            if not player.deduct_points(price):
                return False, '积分不足'

        player.add_item(item_id)
        if item_id == 'hint' and price == 0 and hasattr(player, 'mark_free_hint_redeemed'):
            player.mark_free_hint_redeemed()

        # 保存
        try:
            save_player(player)
        except Exception:
            pass

        return True, '购买成功'

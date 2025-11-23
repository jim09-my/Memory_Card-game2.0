"""
计时器类
用于游戏时间管理
"""

import time


class Timer:
    """游戏计时器"""

    def __init__(self, time_limit=None):
        """
        初始化计时器
        :param time_limit: 时间限制（秒），None表示无限制
        """
        self.time_limit = time_limit
        self.start_time = None
        self.pause_time = None
        self.paused_duration = 0
        self.is_running = False
        self.is_paused = False

    def start(self):
        """开始计时"""
        # 如果计时器尚未运行，开始计时；如果此前已停止则重置基准
        if not self.is_running:
            # 如果从未开始或已被停止，重新设置起始时间
            if self.start_time is None or (self.pause_time is not None and not self.is_paused):
                self.start_time = time.time()
                self.paused_duration = 0
            else:
                # 正常从暂停恢复，不重置 start_time
                if self.is_paused and self.pause_time:
                    self.paused_duration += time.time() - self.pause_time
            self.is_running = True
            self.is_paused = False
            print("计时器已启动")

    def pause(self):
        """暂停计时"""
        if self.is_running and not self.is_paused:
            self.pause_time = time.time()
            self.is_paused = True
            print("计时器已暂停")

    def resume(self):
        """继续计时"""
        if self.is_running and self.is_paused:
            self.paused_duration += time.time() - self.pause_time
            self.is_paused = False
            print("计时器已继续")

    def stop(self):
        """停止计时"""
        if self.is_running:
            # 记录停止时间，供 get_elapsed_time 计算
            self.pause_time = time.time()
            self.is_running = False
            self.is_paused = False
            print("计时器已停止")

    def reset(self):
        """重置计时器"""
        self.start_time = None
        self.pause_time = None
        self.paused_duration = 0
        self.is_running = False
        self.is_paused = False
        print("计时器已重置")

    def get_elapsed_time(self):
        """
        获取已用时间（秒）
        :return: 已用时间，未开始返回0
        """
        if self.start_time is None:
            return 0

        if self.is_paused:
            return self.pause_time - self.start_time - self.paused_duration

        if self.is_running:
            return time.time() - self.start_time - self.paused_duration

        # 已停止
        return self.pause_time - self.start_time - self.paused_duration if self.pause_time else 0

    def get_remaining_time(self):
        """
        获取剩余时间（秒）
        :return: 剩余时间，无限制返回None，超时返回0
        """
        if self.time_limit is None:
            return None

        remaining = self.time_limit - self.get_elapsed_time()
        return max(0, remaining)

    def is_time_up(self):
        """
        检查时间是否用完
        :return: 是否超时
        """
        if self.time_limit is None:
            return False

        return self.get_elapsed_time() >= self.time_limit

    def extend_time(self, seconds):
        """
        延长时间
        :param seconds: 延长的秒数
        """
        if self.time_limit is not None:
            self.time_limit += seconds
            print(f"时间已延长 {seconds} 秒")

    def format_time(self, seconds):
        """
        格式化时间显示
        :param seconds: 秒数
        :return: 格式化的时间字符串 (MM:SS)
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def get_time_display(self):
        """
        获取时间显示字符串
        :return: 时间显示
        """
        if self.time_limit is None:
            # 无限制，显示已用时间
            elapsed = self.get_elapsed_time()
            return self.format_time(elapsed)
        else:
            # 有限制，显示剩余时间
            remaining = self.get_remaining_time()
            return self.format_time(remaining)

    def get_status(self):
        """
        获取计时器状态
        :return: 状态字典
        """
        return {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'elapsed_time': self.get_elapsed_time(),
            'remaining_time': self.get_remaining_time(),
            'time_limit': self.time_limit,
            'is_time_up': self.is_time_up()
        }

    def __str__(self):
        """字符串表示"""
        status = "运行中" if self.is_running else ("暂停中" if self.is_paused else "未开始")
        time_info = self.get_time_display()
        return f"Timer({status}, {time_info})"


# ============== 测试代码 ==============
if __name__ == '__main__':
    print("=" * 50)
    print("计时器测试")
    print("=" * 50)

    # 测试无限制计时器
    print("\n1. 无限制计时器：")
    timer1 = Timer()
    timer1.start()

    time.sleep(2)
    print(f"   2秒后: {timer1.get_time_display()}")

    timer1.pause()
    time.sleep(1)  # 暂停期间不计时
    print(f"   暂停1秒")

    timer1.resume()
    time.sleep(1)
    print(f"   继续1秒后: {timer1.get_time_display()}")

    timer1.stop()

    # 测试限时计时器
    print("\n2. 限时计时器（10秒）：")
    timer2 = Timer(time_limit=10)
    timer2.start()

    for i in range(3):
        time.sleep(1)
        print(f"   {i + 1}秒后 - 剩余: {timer2.get_time_display()}, 是否超时: {timer2.is_time_up()}")

    print("\n3. 延长时间：")
    timer2.extend_time(5)
    print(f"   延长5秒后 - 剩余: {timer2.get_time_display()}")

    print("\n4. 计时器状态：")
    status = timer2.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")

    timer2.stop()

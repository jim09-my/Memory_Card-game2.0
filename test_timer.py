import time
from core.timer import Timer

print('测试 Timer 行为')
# 测试开始
t = Timer()
print('初始状态:', t.get_status())
print('start()')
t.start()
print('is_running:', t.is_running, 'is_paused:', t.is_paused)
for i in range(3):
    time.sleep(1)
    print(f'  {i+1}s 后 elapsed:', t.get_elapsed_time(), 'display:', t.get_time_display())

print('pause()')
t.pause()
print('is_running:', t.is_running, 'is_paused:', t.is_paused)
time.sleep(1.5)
print('暂停期间 1.5s 后 elapsed (应不变):', t.get_elapsed_time())

print('resume()')
t.resume()
print('is_running:', t.is_running, 'is_paused:', t.is_paused)
for i in range(2):
    time.sleep(1)
    print(f'  继续 {i+1}s 后 elapsed:', t.get_elapsed_time(), 'display:', t.get_time_display())

print('stop()')
t.stop()
print('停止后 elapsed:', t.get_elapsed_time(), 'is_running:', t.is_running)

# 测试有时间限制的计时器
print('\n测试限时计时器 (time_limit=3s)')
t2 = Timer(time_limit=3)
print('start()')
t2.start()
for i in range(5):
    time.sleep(1)
    print(f'  {i+1}s 后 remaining:', t2.get_remaining_time(), 'is_time_up:', t2.is_time_up())

print('测试完成')

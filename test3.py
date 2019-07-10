# Once the thread’s activity is started, the thread is considered ‘alive’. It stops being alive when its run() method terminates – either normally, or by raising an unhandled exception. The is_alive() method tests whether the thread is alive.

# Other threads can call a thread’s join() method. This blocks the calling thread until the thread whose join() method is called is terminated.

# A thread has a name. The name can be passed to the constructor, and read or changed through the name attribute.


#!/usr/bin/python3

import threading
import time

exitFlag = 0


class myThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + self.name)
        print_time(self.name, self.counter, 5)
        print("Exiting " + self.name)


def print_time(threadName, delay, counter):
    while counter:
        if exitFlag:
            threadName.exit()
        time.sleep(delay)
        print("%s: %s" % (threadName, time.ctime(time.time())))
        counter -= 1


# Create new threads
thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread(2, "Thread-2", 2)

# Start new Threads
thread1.start()
thread2.start()
thread1.join()
thread2.join()
print("Exiting Main Thread")


#!/usr/bin/env python3

#
# import time
# import threading
# from yangvoodoo.sysrepodal import SysrepoDataAbstractionLayer
#
#
# exitFlag = 0
#
#
# class myThread(threading.Thread):
#
#     def __init__(self, threadID, name):
#         threading.Thread.__init__(self)
#         self.threadID = threadID
#         self.name = name
#
#         self.dal = SysrepoDataAbstractionLayer()
#
#     def run(self):
#         print("Starting " + self.name)
#         print('we have a dal', self.dal)
#         time.sleep(5)
#         print("Exiting " + self.name)
#
#
# if __name__ == '__main__':
#     thread1 = myThread(1, "Thread-1")
#     thread1.start()
#     thread1.join()

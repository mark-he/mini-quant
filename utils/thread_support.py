import threading

class Progress(object):

    def __init__(self, total):
        self.cond = threading.Condition()
        self.total = total
        self.pass_count = 0
        self.fail_count = 0

    def is_completed(self):
        return self.total <= self.pass_count + self.fail_count


    def pass_one(self):
        self.cond.acquire()
        self.pass_count += 1
        self.cond.notify()


    def fail_one(self):
        self.cond.acquire()
        self.fail_count += 1
        self.cond.notify()
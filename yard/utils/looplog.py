from yard.utils.log import LoggableMixin


class LoopLogExp(LoggableMixin):
    def __init__(self, comment):
        super(LoopLogExp, self).__init__()
        self.comment = comment
        self.cur_loop = 0
        self.next_target_loop = 1

    def check(self):
        self.cur_loop += 1
        if self.cur_loop < self.next_target_loop:
            return
        else:
            self.info('%s (%d)' % (self.comment, self.cur_loop))
            self.next_target_loop *= 2


class OneTimeLog(LoggableMixin):
    def __init__(self, comment):
        super(OneTimeLog, self).__init__()
        self.comment = comment
        self.cur_loop = 0

    def check(self):
        self.cur_loop += 1
        if self.cur_loop == 1:
            self.info('%s (%d)' % (self.comment, self.cur_loop))

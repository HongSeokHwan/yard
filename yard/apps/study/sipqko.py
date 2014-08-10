from yard.utils.log import LoggableMixin


# This is sipqko study area.
class Sipqko(LoggableMixin):
    def __init__(self):
        super(Sipqko, self).__init__()

    def start(self):
        self.info('Start sipqko study.')

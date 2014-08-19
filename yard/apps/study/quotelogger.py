import time
from yard.utils.log import LoggableMixin


class QuoteLogger(LoggableMixin):
    def __init__(self):
        super(QuoteLogger, self).__init__()
        self.con = None

    def start(self):
        self.info('Start quotlogger in study.')
        self._start_korbit_stream_listener()

        while True:
            self.info('Try collecting quote data.')
            con = self._get_db_connection()

            # TODO
            # collect data
            # insert data

            self.info('Fihish collecting quote data.')
            time.sleep(30)

    def _start_korbit_stream_listener(self):
        # TODO
        # subscribe korbit data
        # insert stream to database
        pass

    def _get_db_connection(self):
        # TODO
        return None

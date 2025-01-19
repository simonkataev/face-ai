from datetime import datetime, timedelta

clock = None
class SysTimer:   
    def __init__(self, now):
        global clock
        clock = now

    @staticmethod
    def now():
        global clock
        return clock

    def timepick(self):
        global clock
        period = timedelta(seconds=1)
        clock = clock + period

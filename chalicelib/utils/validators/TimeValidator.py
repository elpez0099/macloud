from datetime import datetime


class Time24HrsValidator:
    @staticmethod
    def is_valid(time):
        try:
            datetime.strptime(time, '%H:%M:%S')
            return True
        except ValueError:
            return False

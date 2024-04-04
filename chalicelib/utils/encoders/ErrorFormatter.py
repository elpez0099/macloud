import re


class ErrorFormatter:
    @staticmethod
    def prettify(error_message):
        error_message = re.sub(r'\\s+', "", error_message)
        error_message = re.sub(' +', " ", error_message)
        error_message = re.sub(r'\n+', "", error_message)
        return error_message

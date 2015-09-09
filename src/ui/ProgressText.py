__author__ = 'Massimiliano'


class ProgressText:

    def __init__(self, expected_count):
        super().__init__()
        self.expected_count = expected_count
        self.index = 0

    def on_progress(self):
        self.index += 1
        percent = round(100 * self.index / self.expected_count, 2)
        hashes = int(percent)
        print("\r[{}] {}%".format("#" * hashes, percent), end="")



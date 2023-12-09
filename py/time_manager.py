from datetime import datetime
import time



class Timer:
    def __init__(self):
        self.curr_time = datetime.now()
        self.last_time = datetime.now()
        self.stop_time = datetime.now()
        self.stop_end_time = datetime.now()

    def start_timer(self):
        self.curr_time = datetime.now()
        self.last_time = datetime.now()
    def get_elapsed_time(self):
        self.curr_time = datetime.now()
        _elapsed = (self.curr_time - self.last_time - (self.stop_end_time - self.stop_time)) * 60
        self.last_time = self.curr_time
        return _elapsed

    def pause(self):
        self.stop_time = datetime.now()

    def play(self):
        self.stop_end_time = datetime.now()


if __name__ == "__main__":
    timer = Timer()
    timer.start_timer()
    time.sleep(3)
    elapsed = timer.get_elapsed_time()
    print(type(elapsed))
    print(elapsed)

import schedule
import time
import threading

class Scheduler:
    def __init__(self):
        self.running = False
        self.thread = None

    def add_job(self, job, interval):
        schedule.every(interval).seconds.do(job)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _run(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)
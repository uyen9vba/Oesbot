import datetime

import tempora.schedule
import apscheduler.schedulers.background
import apscheduler.triggers.interval


class Scheduler():
    def __init__(self):
        self.scheduler = tempora.schedule.Scheduler()

    def execute(self, method):
        self.scheduler.add(tempora.schedule.InvokeScheduler(method))

    def execute_delayed(self, delay, method):
        self.scheduler.add(tempora.schedule.DelayedCommand.after(delay, method))

    def execute_interval(self, period, method):
        self.scheduler.add(tempora.schedule.PeriodicCommand.after(period, method))


class BackgroundScheduler:
    def __init__(self):
        self.scheduler = apscheduler.schedulers.background.BackgroundScheduler(daemon=True)
        self.scheduler.start()

    @staticmethod
    def execute(self, method, args=[], kwargs={}):
        job = self.scheduler.add_job(
            func=method,
            trigger=datetime.datetime.utcnow(),
            args=args,
            kwargs=kwargs
        )

        return job

    @staticmethod
    def execute_delayed(self, delay, method, args=[], kwargs={}):
        job = self.scheduler.add_job(
            func=method,
            trigger=datetime.datetime.utcnow() + datetime.timedelta(seconds=delay),
            args=args,
            kwargs=kwargs
        )

        return job

    @staticmethod
    def execute_interval(self, interval, method, args=[], kwargs={}, jitter=None):
        job = self.scheduler.add_job(
            func=method,
            trigger=apscheduler.triggers.interval.IntervalTrigger(seconds=interval),
            args=args,
            kwargs=kwargs,
            jitter=jitter
        )

        return job

"""
class ScheduledJob:
    def __init__(self, job):
        self.job = job

    def pause(self, *args, **kwargs):
        if self.job:
            self.job.pause(*args, **kwargs)

    def resume(self, *args, **kwargs):
        if self.job:
            self.job.resume(*args, **kwargs)

    def remove(self, *args, **kwargs):
        if self.job:
            self.job.remove(*args, **kwargs)
"""
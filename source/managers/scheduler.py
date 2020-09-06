import datetime

import tempora.schedule
import apscheduler.schedulers.background
import apscheduler.triggers.interval


class Scheduler():
    scheduler = None

    def init():
        Scheduler.scheduler = tempora.schedule.Scheduler()

    def execute(method):
        Scheduler.scheduler.add(tempora.schedule.InvokeScheduler(method))

    def execute_delayed(delay, method):
        Scheduler.scheduler.add(tempora.schedule.DelayedCommand.after(delay, method))

    def execute_interval(period, method):
        Scheduler.scheduler.add(tempora.schedule.PeriodicCommand.after(period, method))


class BackgroundScheduler:
    scheduler = None

    def init():
        BackgroundScheduler.scheduler = apscheduler.schedulers.background.BackgroundScheduler(daemon=True)
        BackgroundScheduler.scheduler.start()

    @staticmethod
    def execute(method, args=[], kwargs={}):
        job = BackgroundScheduler.scheduler.add_job(
            func=method,
            trigger=datetime.datetime.utcnow(),
            args=args,
            kwargs=kwargs
        )

        return job

    @staticmethod
    def execute_delayed(delay, method, args=[], kwargs={}):
        job = BackgroundScheduler.scheduler.add_job(
            func=method,
            trigger=datetime.datetime.utcnow() + datetime.timedelta(seconds=delay),
            args=args,
            kwargs=kwargs
        )

        return job

    @staticmethod
    def execute_interval(interval, method, args=[], kwargs={}, jitter=None):
        job = BackgroundScheduler.scheduler.add_job(
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
"""
Reset persistent grades for learners.
"""
from datetime import datetime, timedelta
from textwrap import dedent

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils.timezone import now

from ...models import FailedTask


log = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Delete records of FailedTasks that have been resolved
    """
    help = dedent(__doc__).strip()

    def add_arguments(self, parser):
        """
        Add arguments to the command parser.
        """
        parser.add_argument(
            '--task-name', '-t',
            action='store',
            default=None,
            help=u"Restrict cleanup to tasks matching the given task-name.",
        )
        parser.add_argument(
            '--age', '-a',
            action='store_int',
            default=0,
            help=u"Only delete tasks that have been resolved for at least the specified number of days",
        )

    def handle(self, *args, **options):
        tasks = FailedTask.objects.filter(datetime_resolved__lt=now() - timedelta(days=options['age']))
        if options['task_name'] is not None:
            tasks = tasks.filter(task_name=options['task_name'])
        log.info(u'Cleaning up {} tasks'.format(tasks.count()))
        log.debug(u'Tasks to remove: {}'.format(list(tasks)))
        tasks.delete()

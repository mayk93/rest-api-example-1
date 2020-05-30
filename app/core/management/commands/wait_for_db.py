from time import sleep
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Waiting for DB connection ...')

        db_connection = None
        db_connection_attempts = 0
        db_max_connection_attempts = options.get('max_connection_attempts', 5)
        sleep_time = 2

        while not db_connection:
            try:
                db_connection = connections['default']
                if db_connection:
                    self.stdout.write(
                        self.style.SUCCESS('DB connection now available')
                    )
                    return
            except OperationalError:
                self.stdout.write(
                    'DB connection not yet available. Retrying in %s seconds'
                    % sleep_time
                )

            db_connection_attempts += 1
            if db_connection_attempts > db_max_connection_attempts:
                self.stdout.write('DB connection retries maxed out')
                raise OperationalError

            sleep_time *= 2
            sleep(sleep_time)

""" PostgreSQL database connection object using the psycopg2 module. """

import psycopg2
import time


class RetryDecorator:
    """An exponential backoff retry decorator. This helps ensure a database connection is properly
    established if the application container starts before the database container is ready to accept
    connections."""

    def __init__(self, max_attempts=8, delay=0.5):
        self.delay = delay
        self.max_attempts = max_attempts

        self.func = None

    def __call__(self, *args, **kwargs):
        if not self.func:
            self.func = args[0]
            return self

        results = None
        attempts = 1

        while not results:
            try:
                results = self.func(*args, **kwargs)

            except psycopg2.OperationalError:
                if attempts == self.max_attempts:
                    raise

                time.sleep(attempts * self.delay)
                self.delay = self.delay * 2
                attempts += 1

        return results


@RetryDecorator()
def get_connection():
    """Get a connection to the ratestask database."""
    return psycopg2.connect(
        host="database",
        database="postgres",
        user="postgres",
        password="ratestask",
    )

import asyncio
import random

from app.graph.errors import RetryableToolError

MAX_RETRIES = 3
BASE_DELAY_SECONDS = 1.0
MAX_DELAY_SECONDS = 10.0

RETRYABLE_ERRORS = (
    TimeoutError,
    ConnectionError,
)

def is_retryable_error(e: Exception):
    return isinstance(e, RETRYABLE_ERRORS)


def calculate_delay(attempt:int):
    delay = min(BASE_DELAY_SECONDS * (2 ** attempt), MAX_DELAY_SECONDS)

    jiter = random.uniform(0,0.5)

    return delay+jiter

async def execute_with_retry(func,*args,**kwargs):
    for attempt in range(MAX_RETRIES + 1):
        try:
            return await func(*args,**kwargs)

        except Exception as err:

            if not is_retryable_error(err):
                raise
            if attempt >= MAX_RETRIES:
                raise RetryableToolError("Tool failed")


            delay = calculate_delay(attempt)

            await asyncio.sleep(delay)


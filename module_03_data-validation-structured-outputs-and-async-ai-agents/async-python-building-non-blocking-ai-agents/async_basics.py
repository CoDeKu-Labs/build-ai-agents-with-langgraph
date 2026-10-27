"""
Async Python basics (sync vs async)

Install:  nothing. asyncio is part of Python's standard library.
          (Do NOT run `pip install asyncio`: that is an old, unrelated package.)
Run:      python async_basics.py

Three tests with 3 simulated API calls of 2 seconds each:
  1. Synchronous:                    ~6 s
  2. Asynchronous with gather:       ~2 s
  3. Async with a BLOCKING call:     ~6 s   <- the classic mistake
"""

import asyncio
import os
import time

DELAY = float(os.getenv("DEMO_DELAY", "2"))   # seconds per fake API call


# -----------------------------------------------------------
# The three fake API calls
# -----------------------------------------------------------
def sync_api_call(name: str, delay: float) -> str:
    print(f"   [{name}] STARTED (blocking)")
    time.sleep(delay)                      # freezes the whole thread
    print(f"   [{name}] FINISHED")
    return f"{name} result"


async def async_api_call(name: str, delay: float) -> str:
    print(f"   [{name}] STARTED (non-blocking)")
    await asyncio.sleep(delay)             # pauses ONLY this task, others keep running
    print(f"   [{name}] FINISHED")
    return f"{name} result"


async def bad_async_api_call(name: str, delay: float) -> str:
    print(f"   [{name}] STARTED (async def, but...)")
    time.sleep(delay)                      # MISTAKE: a blocking call inside async code
    print(f"   [{name}] FINISHED")
    return f"{name} result"


# -----------------------------------------------------------
# The three runs. Each RETURNS its total time, so we can compare them at the end.
# -----------------------------------------------------------
def run_sync() -> float:
    start = time.perf_counter()
    sync_api_call("Weather API", DELAY)
    sync_api_call("Exchange API", DELAY)
    sync_api_call("LLM call", DELAY)
    return time.perf_counter() - start


async def run_async() -> float:
    start = time.perf_counter()
    await asyncio.gather(                  # start all three, wait until all are done
        async_api_call("Weather API", DELAY),
        async_api_call("Exchange API", DELAY),
        async_api_call("LLM call", DELAY),
    )
    return time.perf_counter() - start


async def run_async_with_mistake() -> float:
    start = time.perf_counter()
    await asyncio.gather(
        bad_async_api_call("Weather API", DELAY),
        bad_async_api_call("Exchange API", DELAY),
        bad_async_api_call("LLM call", DELAY),
    )
    return time.perf_counter() - start


def step(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    input("Press Enter...")


if __name__ == "__main__":
    step("TEST 1: synchronous (the Course 1 pattern)")
    sync_total = run_sync()
    print(f"   TOTAL: {sync_total:.1f}s")

    step("TEST 2: asynchronous with asyncio.gather")
    async_total = asyncio.run(run_async())     # asyncio.run starts the event loop
    print(f"   TOTAL: {async_total:.1f}s")

    step("TEST 3: async def + gather, but with time.sleep inside (the mistake)")
    mistake_total = asyncio.run(run_async_with_mistake())
    print(f"   TOTAL: {mistake_total:.1f}s   <- no speedup at all!")

    print("\n" + "=" * 60)
    print(f"Sync               : {sync_total:.1f}s")
    print(f"Async (correct)    : {async_total:.1f}s   ({sync_total / async_total:.1f}x faster)")
    print(f"Async (with a bug) : {mistake_total:.1f}s")
    print("=" * 60)
    print("Async only helps when EVERYTHING that waits uses `await`.")
    print("A single time.sleep() or a blocking library call stops the other tasks.")

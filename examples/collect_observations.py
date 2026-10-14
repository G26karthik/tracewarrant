"""Real local SQLite work through a stdlib recorder; no model or network."""

import argparse
import asyncio
import sqlite3
from pathlib import Path

from workload_lab.collection import ObservationRecorder
from workload_lab.ir import NodeKind


async def collect():
    recorder = ObservationRecorder()
    pool = recorder.pool(1)
    semaphore = asyncio.Semaphore(1)
    with recorder.run(complete=True) as run:
        # This explicitly closed example has exactly these two serial operations.
        # Do not set complete=True for an arbitrary auto-traced application.
        with run.operation(NodeKind.DATABASE) as first:
            async with first.lease(pool, semaphore.acquire, semaphore.release):
                with sqlite3.connect(":memory:") as database:
                    assert database.execute("select 7").fetchone()[0] == 7
        with run.operation(NodeKind.DATABASE, depends_on=(first,)) as second:
            async with second.lease(pool, semaphore.acquire, semaphore.release):
                with sqlite3.connect(":memory:") as database:
                    assert database.execute("select 11").fetchone()[0] == 11
    return recorder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(collect()).write(args.output)


if __name__ == "__main__":
    main()

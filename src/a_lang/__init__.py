from __future__ import annotations

from queue import Queue
import random
from typing import Any, Callable, Generator, Literal, Sequence, TypeAlias, assert_never


ExecutionMode: TypeAlias = Literal["event-driven", "sequential-style"]


class Task:
    def __init__(self, func: Callable[..., Any]) -> None:
        self.func = func

    def execute(self) -> None | Task:
        result = self.func()
        if callable(result):
            return Task(func=result)
        return None


class Scheduler:
    def __init__(self) -> None:
        self.tasks = Queue[Task]()

    def add_task(self, task: Task) -> None:
        self.tasks.put(task)

    def run(self) -> None:
        while not self.tasks.empty():
            task = self.tasks.get()
            next = task.execute()
            if next is not None:
                self.add_task(task=next)
            self.tasks.task_done()


def print_array_event_driven(array: list[Any], index: int) -> None | Callable[..., Any]:
    if index < len(array):
        print(array[index])
        return lambda: print_array_event_driven(array=array, index=index + 1)


def print_array_secuential(array: list[Any]) -> Generator[None, None, None]:
    for value in array:
        print(value)
        yield


def process_iterator(iterator: Generator) -> None | Callable[..., Any]:
    try:
        next(iterator)
        return lambda: process_iterator(iterator=iterator)
    except StopIteration:
        return None


def _get_mode() -> ExecutionMode:
    modes: Sequence[ExecutionMode] = ["event-driven", "sequential-style"]
    return random.choice(modes)


def main() -> None:
    mode: ExecutionMode = _get_mode()
    scheduler = Scheduler()
    array: list[int] = [
        1,
        2,
        3,
        4,
    ]
    if mode == "event-driven":
        scheduler.add_task(
            task=Task(
                lambda: print_array_event_driven(
                    array=array,
                    index=0,
                )
            )
        )

    elif mode == "sequential-style":
        scheduler.add_task(
            task=Task(
                lambda: process_iterator(iterator=print_array_secuential(array=array))
            )
        )
    else:
        assert_never(mode)

    scheduler.run()

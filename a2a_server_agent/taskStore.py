from a2a.server.tasks import TaskStore
from a2a.server.context import ServerCallContext
from a2a.types import Task
import asyncio

class LocalTaskStore(TaskStore):
    def __init__(self):
        self._store: dict[str, Task] = {}

    async def save(self, task: Task, context: ServerCallContext | None = None) -> None:
        """Saves or updates a task in the store."""
        print(f"TaskStore()->save(): task_id={task.id} status={task.status}")
        self._store[task.id] = task

    async def get(self, task_id: str, context: ServerCallContext | None = None) -> Task | None:
        """Retrieves a task from the store by ID."""
        task = self._store.get(task_id)
        if task:
            print(f"TaskStore()->get(): found task_id={task_id} status={task.status}")
        else:
            print(f"TaskStore()->get(): task_id={task_id} not found")
        return task

    async def delete(self, task_id: str, context: ServerCallContext | None = None) -> None:
        """Deletes a task from the store by ID."""
        if task_id in self._store:
            print(f"TaskStore()->delete(): deleted task_id={task_id}")
            del self._store[task_id]
        else:
            print(f"TaskStore()->delete(): task_id={task_id} not found")

# Global instance to be shared
GLOBAL_TASK_STORE = LocalTaskStore()


from a2a.server.tasks import TaskStore
from a2a.server.context import ServerCallContext
from a2a.types import Task

class LocalTaskStore(TaskStore):

    async def save(self, task: Task, context: ServerCallContext | None = None) -> None:
        """Saves or updates a task in the store."""

        print(f"TaskStore()->save():")
        if context:
            print(f"TaskStore()->get():task: {task},context: {context}")
        else:
            print(f"TaskStore()->get():task: {task},context: empty-context")
            
        pass

    async def get(self, task_id: str, context: ServerCallContext | None = None) -> Task | None:
        """Retrieves a task from the store by ID."""

        print("TaskStore()->get():")
        if context:
            print(f"TaskStore()->get():task_id: {task_id}, context: {context}")
        else:
            print(f"TaskStore()->get():task_id: {task_id}, context: empty-context")

        pass

    async def delete(self, task_id: str, context: ServerCallContext | None = None) -> None:
        """Deletes a task from the store by ID."""

        print("TaskStore()->delete():")
        if context:
            print(f"TaskStore()->get():task_id: {task_id}, context: {context}")
        else:
            print(f"TaskStore()->get():task_id: {task_id}, context: empty-context")

        pass


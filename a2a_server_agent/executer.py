from a2a.server.agent_execution import AgentExecutor
from a2a.types import Message, Part, Role, TextPart, Task, TaskStatus, TaskState
from a2a.server.agent_execution import RequestContext
from a2a.server.events import EventQueue
import logging
import uuid
import asyncio
from taskStore import GLOBAL_TASK_STORE

logger = logging.getLogger("A2A_Server")

class HelloExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Handles requests. Supports two commands:
        1. "Execute": Starts a background task and returns ID.
        2. "Check <task_id>": Checks status of a task.
        """
        if context.message and context.message.parts:
            user_text_part = context.message.parts[0].root
            if isinstance(user_text_part, TextPart):
                user_text = user_text_part.text
            else:
                user_text = str(user_text_part)
        else:
            user_text = ""

        logger.info(f"👉 Executor received: {user_text}")

        response_text = ""

        if user_text.strip().lower() == "execute":
            # 1. Start Async Task
            task_id = str(uuid.uuid4())
            new_task = Task(
                id=task_id,
                status=TaskStatus(state=TaskState.submitted),
                metadata={"original_request": user_text},
                context_id=str(uuid.uuid4()) # Added context_id as it seems required by Task model
            )
            await GLOBAL_TASK_STORE.save(new_task)
            
            # Spawn background worker
            asyncio.create_task(self._background_processing(task_id))
            
            response_text = f"Task Accepted. ID: {task_id}"
            logger.info(f"✅ Created Task {task_id}")

        elif user_text.strip().lower().startswith("check "):
            # 2. Check Status
            parts = user_text.strip().split(" ", 1)
            if len(parts) == 2:
                task_id = parts[1]
                task = await GLOBAL_TASK_STORE.get(task_id)
                if task:
                    if task.status.state == TaskState.completed:
                        # Assuming result is stored in metadata or similar, since Task doesn't have 'output' field in the new types definition I saw?
                        # Wait, I checked Task definition:
                        # artifacts: list[Artifact] | None = None
                        # history: list[Message] | None = None
                        # metadata: dict[str, Any] | None = None
                        # No 'output' field. I should probably use 'metadata' or 'artifacts'.
                        # For now, I'll put the result in 'metadata'.
                        result = task.metadata.get("result") if task.metadata else "No result"
                        response_text = f"COMPLETED: {result}"
                    else:
                        response_text = f"STATUS: {task.status.state.value}"
                else:
                    response_text = "ERROR: Task not found"
            else:
                response_text = "ERROR: Invalid Check command format. Use 'Check <task_id>'"
                
        else:
             response_text = "Unrecognized command. Send 'Execute' to start or 'Check <task_id>' to poll."

        # Send response
        response_message = Message(
            message_id=str(uuid.uuid4()),
            role=Role.agent,
            parts=[Part(root=TextPart(text=response_text))]
        )
        await event_queue.enqueue_event(response_message)

    async def _background_processing(self, task_id: str):
        """Simulates some work and updates the request status."""
        print(f"   [Worker] Starting work on {task_id}...")
        await asyncio.sleep(2) # Simulate work
        
        task = await GLOBAL_TASK_STORE.get(task_id)
        if task:
            task.status = TaskStatus(state=TaskState.completed)
            # Store result in metadata since 'output' field is missing in Task definition
            task.metadata = {"result": "Hello World from Background Worker!"}
            await GLOBAL_TASK_STORE.save(task)
            print(f"   [Worker] Finished work on {task_id}.")

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        logger.warning(f"🛑 CANCEL RECEIVED for Task ID: {context.task_id}")
        pass
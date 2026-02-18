
import asyncio
import logging
import uvicorn
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from uuid import uuid4

# Patch to bypass the check since we know fastapi is installed
import a2a.server.apps.jsonrpc.fastapi_app
a2a.server.apps.jsonrpc.fastapi_app._package_fastapi_installed = True

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps.jsonrpc.fastapi_app import A2AFastAPIApplication
from a2a.server.events import EventQueue, InMemoryQueueManager
from a2a.server.request_handlers.default_request_handler import DefaultRequestHandler
from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore
from a2a.types import (
    AgentCard,
    AgentInterface,
    Message,
    Task,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TextPart,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1. Agent Logic ---

class DemoAgent(AgentExecutor):
    """
    A simple agent that echoes messages and simulates work.
    """

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Executes the agent logic.
        """
        user_message = context.get_user_input()
        logger.info(f"Agent received: {user_message}")

        # Simulate thinking/processing
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(state=TaskState.working),
                final=False
            )
        )
        
        # Simulate a long running process (e.g., 3 steps)
        for i in range(3):
            await asyncio.sleep(1) # Simulate work
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=context.task_id,
                    context_id=context.context_id,
                    status=TaskStatus(state=TaskState.working),
                    final=False
                )
            )

        # Final response
        final_response = f"Echo: {user_message}"
        
        # Mark task as completed with the final response
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(
                    state=TaskState.completed,
                    message=Message(
                        role="agent",
                        message_id=str(uuid4()),
                        parts=[TextPart(text=final_response)]
                    )
                ),
                final=True
            )
        )
        logger.info("Agent finished execution.")


    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Handle cancellation.
        """
        logger.info(f"Cancelling task {context.task_id}")
        # In a real agent, you would signal the running task to stop.
        pass


# --- 2. Server Setup ---

@asynccontextmanager
async def lifespan(app):
    # Startup logic
    logger.info("Server starting up...")
    yield
    # Shutdown logic
    logger.info("Server shutting down...")

def create_app():
    # 1. Infrastructure
    task_store = InMemoryTaskStore()
    queue_manager = InMemoryQueueManager()

    # 2. Agent Definition
    agent = DemoAgent()
    
    # 3. Request Handler (The "Brain")
    request_handler = DefaultRequestHandler(
        agent_executor=agent,
        task_store=task_store,
        queue_manager=queue_manager
    )

    # 4. Agent Card (Metadata)
    agent_card = AgentCard(
        name="Demo Echo Agent",
        description="A simple agent for demonstrating A2A patterns.",
        version="0.0.1",
        url="http://localhost:8000/a2a",
        interfaces=[
            AgentInterface(transport="http", url="http://localhost:8000/a2a")
        ],
        capabilities={
            "streaming": True,
            "history": True
        },
        default_input_modes=[],
        default_output_modes=[],
        skills=[]
    )

    # 5. Application (The "Face")
    a2a_app = A2AFastAPIApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    return a2a_app.build(lifespan=lifespan, rpc_url="/a2a")

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

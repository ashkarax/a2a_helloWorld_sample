
import asyncio
import logging
from uuid import uuid4

from a2a.client.client_factory import ClientFactory
from a2a.types import (
    Message,
    MessageSendConfiguration,
    TaskQueryParams,
    TaskState,
    TextPart
)

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_URL = "http://localhost:8000"

async def run_client_scenarios():
    # 1. Create the Client using the Factory
    # The factory connects to the agent card endpoint and picks the best transport (JSON-RPC)
    logger.info(f"Connecting to agent at {SERVER_URL}...")
    client = await ClientFactory.connect(SERVER_URL)
    
    try:
        # --- Scenario 1: Synchronous (Blocking) ---
        logger.info("\n--- 1. Synchronous Request (Blocking) ---")
        
        sync_message = Message(
            message_id=str(uuid4()),
            role="user",
            parts=[TextPart(text="Hello, Sync World!")],
            context_id="sync-123",
            task_id=None
        )
        
        logger.info(f"Sending message: {sync_message}")
        
        # Send using the client's high-level method
        # We use a context manager (async for) because send_message yields events
        async for event in client.send_message(
            sync_message,
            configuration=MessageSendConfiguration(blocking=True)
        ):
            logger.info(f"Received event: {event}")


        # --- Scenario 2: Asynchronous (Polling) ---
        logger.info("\n--- 2. Asynchronous Request (Polling) ---")
        
        async_message = Message(
            message_id=str(uuid4()),
            role="user",
            parts=[TextPart(text="Hello, Async World!")],
            context_id="async-123",
            task_id=None
        )
        
        logger.info(f"Sending message (non-blocking): {async_message}")
        
        task_id = None
        
        # In non-blocking mode, we expect the first event to be the Task object
        async for event in client.send_message(
            async_message,
            configuration=MessageSendConfiguration(blocking=False)
        ):
            logger.info(f"Initial response: {event}")
            if hasattr(event, 'id'):
                 task_id = event.id

        if task_id:
             logger.info(f"Task started with ID: {task_id}. Polling for completion...")
             
             while True:
                 await asyncio.sleep(1)
                 
                 # Use TaskQueryParams model
                 query = TaskQueryParams(id=task_id)
                 task = await client.get_task(query)
                 
                 logger.info(f"Polled Task State: {task.status.state}")
                 
                 if task.status.state in [TaskState.completed, TaskState.failed, TaskState.canceled]:
                     logger.info("Task Finished!")
                     break

        # --- Scenario 3: Streaming (SSE) ---
        # Note: ClientFactory automatically handles streaming if the agent supports it
        # and we don't force blocking=True. But let's be explicit about expectations.
        logger.info("\n--- 3. Streaming Request ---")
        
        stream_message = Message(
            message_id=str(uuid4()),
            role="user",
            parts=[TextPart(text="Hello, Streaming World!")],
            context_id="stream-123",
            task_id=None
        )
        
        logger.info(f"Sending message: {stream_message}")
        
        # The client automatically handles the stream processing
        async for event in client.send_message(stream_message):
            # The event could be a Message chunk, a Task update, etc.
            logger.info(f"Stream Event: {event}")

    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(run_client_scenarios())

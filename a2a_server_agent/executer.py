from a2a.server.agent_execution import AgentExecutor
from a2a.types import Message, Part, Role,TextPart
from a2a.server.agent_execution import RequestContext
from a2a.server.events import EventQueue
import logging

logger = logging.getLogger("A2A_Server")

class HelloExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        This function is called when a request comes in.
        'context': contains the incoming message/task.
        'event_queue': allows you to stream updates back to the caller.
        """
        if context.call_context:
            print(f"Received request from: {context.call_context.user}")
        else:
            print("No call context available")

        if context.message:
            logger.info("📦 PAYLOAD RECEIVED (Decoded):")
            user_text = context.message.parts[0] if context.message.parts else "[Empty]"
            logger.info(f"   From Role: {context.message.role}")
            logger.info(f"   Content:   {user_text}")
        else:
            logger.warning("   [!] Received request with no message body")
        
        # Create a response message
        response_content = "Hello! I am an A2A agent."
        
        # In A2A, we don't just 'return' strings; we enqueue Events.
        # This allows for streaming, status updates, and partial results.
        response_message = Message(
            message_id="1",
            role=Role.agent,
            parts=[Part(root=TextPart(text=response_content))]
        )

        logger.info(f"📤 SENDING RESPONSE: {response_content}")
        
        # Send the "Message" event back to the client
        await event_queue.enqueue_event(response_message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        # We'll skip cancellation logic for now

        logger.warning(f"🛑 CANCEL RECEIVED for Task ID: {context.task_id}")
        pass
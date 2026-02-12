import asyncio
import uuid
from a2a.client import ClientFactory
from a2a.types import Message, Role, Part, TextPart
from a2a.client.base_client import BaseClient 


async def main():
    agent_url = "http://localhost:8000"
    print(f"🔍 DISCOVERY: Connecting to agent at {agent_url}...")

    # 1. DISCOVERY & CONNECTION PHASE
    # NO 'async with' here. Just await the factory method.
    client = await ClientFactory.connect(agent_url)
    print("✅ CONNECTED!")

    try:
        # 2. CONSTRUCT THE MESSAGE
        request_message = Message(
            message_id=str(uuid.uuid4()),
            role=Role.user,
            parts=[Part(root=TextPart(text="Hello, are you there?"))]
        )

        print("📤 SENDING: 'Hello, are you there?'")

        # 3. EXECUTION PHASE
        async for event in client.send_message(request_message):
            # Print whatever we get back
            print(f"📥 RECEIVED EVENT: {event}")
            
    finally:
        # 4. CLEANUP (Optional but good practice if the client has underlying resources)
        # Check if the client has a close method, though basic Client usage relies on
        # the underlying transport which might need closing.
        if isinstance(client, BaseClient):
            await client.close()

if __name__ == "__main__":
    asyncio.run(main())
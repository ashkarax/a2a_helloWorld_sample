import asyncio
import uuid
import re
from a2a.client import ClientFactory
from a2a.types import Message, Role, Part, TextPart
from a2a.client.base_client import BaseClient 

async def send_text(client, text):
    msg_id = str(uuid.uuid4())
    message = Message(
        message_id=msg_id,
        role=Role.user,
        parts=[Part(root=TextPart(text=text))]
    )
    
    print(f"📤 SENDING: '{text}'")
    response_text = ""
    async for event in client.send_message(message):
         print(f"DEBUG: Event received: {event}")
         
         # Case 1: event is a Message object directly
         if hasattr(event, 'parts') and event.parts:
             part = event.parts[0].root
             if isinstance(part, TextPart):
                 response_text = part.text
             else:
                 response_text = str(part)
             print(f"📥 RECEIVED: {response_text}")
             
         # Case 2: event is a wrapper (e.g. MessageSendSuccessResponse) containing 'result' which is a Message
         elif hasattr(event, 'result') and hasattr(event.result, 'parts'):
              part = event.result.parts[0].root
              if isinstance(part, TextPart):
                 response_text = part.text
              else:
                 response_text = str(part)
              print(f"📥 RECEIVED from result: {response_text}")

         # Case 3: Legacy/Other structure (keeping existing checks just in case, but modified)
         elif hasattr(event, 'message') and event.message and event.message.parts:
             part = event.message.parts[0].root
             if isinstance(part, TextPart):
                 response_text = part.text
             else:
                 response_text = str(part)
             print(f"📥 RECEIVED from message: {response_text}")
             
    if not response_text:
        print("⚠️ DEBUG: No response text extracted.")
    return response_text

async def main():
    agent_url = "http://localhost:8000"
    print(f"🔍 DISCOVERY: Connecting to agent at {agent_url}...")

    # 1. DISCOVERY & CONNECTION PHASE
    client = await ClientFactory.connect(agent_url)
    print("✅ CONNECTED!")

    try:
        # 2. EXECUTION PHASE
        # A. Start the task
        response = await send_text(client, "Execute")
        
        # Parse Task ID (Expected: "Task Accepted. ID: <uuid>")
        match = re.search(r"ID: ([a-f0-9\-]+)", response)
        if not match:
            print("❌ Failed to get Task ID. Exiting.")
            return

        task_id = match.group(1)
        print(f"✅ Task Started: {task_id}")

        # B. Poll for status
        while True:
            await asyncio.sleep(1) 
            print("🔄 Polling status...")
            status_response = await send_text(client, f"Check {task_id}")
            
            if "COMPLETED" in status_response:
                print("🎉 Task Completed Successfully!")
                print(f"Result: {status_response}")
                break
            elif "STATUS" in status_response:
                print(f"⏳ Task is still running: {status_response}")
            else:
                print(f"⚠️ Unexpected response: {status_response}")
                break
            
    finally:
        # 3. CLEANUP 
        if isinstance(client, BaseClient):
            await client.close()

if __name__ == "__main__":
    asyncio.run(main())
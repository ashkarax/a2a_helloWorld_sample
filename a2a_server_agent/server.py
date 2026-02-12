import uvicorn
from a2a.types import AgentCard, AgentSkill,AgentCapabilities


hello_skill=AgentSkill(
    id="say_hello",
    name="Hello_Greeter",
    description="I simply reply with Hello World to anyone who asks.",
    tags=["greet"], #Mandatory
)

agent_card=AgentCard(
    name="HelloAgent",
    description="A beginner's first A2A agent.",
    version="0.1.0",
    url="http://localhost:8000",  # Where you can be found
    skills=[hello_skill],
    capabilities=AgentCapabilities(), #Mandatory
    default_input_modes=["text"], #Mandatory
    default_output_modes=["text"], #Mandatory
)


from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler

from executer import HelloExecutor
from taskStore import LocalTaskStore
from middleware import TrafficLoggerMiddleware


request_handler = DefaultRequestHandler(
    agent_executor=HelloExecutor(),
    task_store=LocalTaskStore() 
)

# Create the application
app_builder = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler
)

if __name__ == "__main__":
    print("🚀 Starting A2A Agent on port 8000 with Logging enabled...")

    app = app_builder.build()
    app.add_middleware(TrafficLoggerMiddleware)

    uvicorn.run(app, host="0.0.0.0", port=8000)
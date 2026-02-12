This project demonstrates a minimal implementation of the Agent-to-Agent (A2A) protocol using Python.

This implementation uses a microservices-inspired architecture:
    - Server Framework: Starlette (ASGI) - Lightweight, high-performance async framework.
    - Client Framework: httpx(ASGI) - native async/await support
    - Transport Layer: HTTP/1.1 over TCP.
    - Wire Protocol: JSON-RPC 2.0 - Stateless, lightweight remote procedure calls.
    - Discovery Mechanism: .well-known/agent.json - Standardized metadata endpoint for dynamic agent identification.
    - Server Engine: Uvicorn - An infinite-loop ASGI server implementation.

# required packages:
pip install a2a-sdk uvicorn starlette httpx
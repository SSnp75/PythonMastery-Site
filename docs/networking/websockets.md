---
title: WebSockets
description: Real-time bidirectional communication with websockets library and FastAPI
---

# WebSockets <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🌐 Networking · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
  </div>
</div>

---

## Server with the `websockets` library

```python
import asyncio
import websockets
import json

connected_clients = set()

async def handler(websocket):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"  Received: {data}")

            # Broadcast to all connected clients
            broadcast = json.dumps({"user": data["user"], "text": data["text"]})
            await asyncio.gather(
                *[client.send(broadcast) for client in connected_clients if client != websocket]
            )
    finally:
        connected_clients.discard(websocket)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket server on ws://0.0.0.0:8765")
        await asyncio.Future()   # run forever

asyncio.run(main())
```

---

## Client

```python
import asyncio
import websockets
import json

async def chat_client(username: str):
    async with websockets.connect("ws://localhost:8765") as ws:
        # Send and receive concurrently
        async def send():
            while True:
                text = await asyncio.to_thread(input, f"{username}> ")
                await ws.send(json.dumps({"user": username, "text": text}))

        async def receive():
            async for message in ws:
                data = json.loads(message)
                print(f"\n  [{data['user']}]: {data['text']}")

        await asyncio.gather(send(), receive())

asyncio.run(chat_client("Alice"))
```

---

## FastAPI WebSockets

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import list

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, message: str):
        for conn in self.active:
            await conn.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket)
    await manager.broadcast(f"{username} joined the chat")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{username}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{username} left the chat")
```

---

## Practice Exercises

1. **Build a real-time chat** — server + web client (HTML/JS) with WebSocket.
2. **Build a live dashboard** — push server metrics to connected browsers every second.
3. **Implement reconnection** — client automatically reconnects with exponential backoff.
4. **Add authentication** — validate JWT token during WebSocket handshake.
5. **Build a collaborative editor** — multiple users edit the same document in real-time.

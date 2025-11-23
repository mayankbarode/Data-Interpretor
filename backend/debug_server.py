import uvicorn
from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    print(f"DEBUG: Connection attempt from {client_id}")
    await websocket.accept()
    print(f"DEBUG: Accepted connection from {client_id}")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"DEBUG: Received: {data}")
            await websocket.send_text(f"Message text was: {data}")
    except Exception as e:
        print(f"DEBUG: Error: {e}")

if __name__ == "__main__":
    print("Starting debug server on port 8002...")
    uvicorn.run(app, host="127.0.0.1", port=8002)

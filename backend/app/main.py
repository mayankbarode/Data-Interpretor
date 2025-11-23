from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import endpoints
import logging
import sys

# Configure logging to show up in Uvicorn
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

@app.on_event("startup")
async def startup_event():
    logger.info("Application is starting up...")
# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app.include_router(endpoints.router, prefix=settings.API_V1_STR)

# WebSocket Endpoint (Moved here to avoid router prefix issues)
from fastapi import WebSocket, WebSocketDisconnect
from app.api.endpoints import session_store
from app.agents.graph import app_graph
from langchain_core.messages import HumanMessage
import json
import traceback

@app.websocket("/ws/{file_id}")
async def websocket_endpoint(websocket: WebSocket, file_id: str):
    print(f"DEBUG: WebSocket connection attempt for file_id: {file_id}")
    await websocket.accept()
    print(f"DEBUG: WebSocket accepted for file_id: {file_id}")
    try:
        if file_id not in session_store:
            print(f"DEBUG: Session not found for file_id: {file_id}")
            await websocket.send_json({"type": "error", "content": "Session not found. Please upload a file first."})
            await websocket.close()
            return

        state = session_store[file_id]
        
        # Auto-generate summary if not already done
        if not state.get("df_head"):
            print(f"DEBUG: Generating initial summary for file_id: {file_id}")
            await websocket.send_json({"type": "log", "node": "System", "message": "Analyzing your data..."})
            
            try:
                from app.agents.nodes import summarizer_node
                summary_result = summarizer_node(state)
                state.update(summary_result)
                session_store[file_id] = state
                
                # Send the summary to the client
                if summary_result.get("messages"):
                    summary_content = summary_result["messages"][0].content
                    await websocket.send_json({
                        "type": "result",
                        "content": summary_content,
                        "image": None
                    })
            except Exception as e:
                print(f"ERROR generating summary: {e}")
                await websocket.send_json({
                    "type": "error",
                    "content": f"Error generating summary: {str(e)}"
                })
        else:
            # Session exists, send the existing summary/last message to ensure frontend state is consistent
            print(f"DEBUG: Session exists for file_id: {file_id}, sending last message.")
            if state.get("messages"):
                last_msg = state["messages"][-1]
                content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
                # Only send if it looks like a summary or AI response
                if "Summary" in content or "Analysis" in content or len(state["messages"]) == 1:
                     await websocket.send_json({
                        "type": "result",
                        "content": content,
                        "image": state.get("image_path"),
                        "plotly_figures": state.get("plotly_html", [])
                    })

        print(f"DEBUG: Session ready. Waiting for messages...")
        while True:
            data = await websocket.receive_text()
            request_data = json.loads(data)
            user_message_content = request_data.get("message")
            
            state = session_store[file_id]
            user_message = HumanMessage(content=user_message_content)
            state["messages"].append(user_message)
            
            # Stream the graph execution
            inputs = state
            async for event in app_graph.astream_events(inputs, version="v1"):
                kind = event["event"]
                
                if kind == "on_chain_start":
                    if event["name"] == "LangGraph":
                        continue
                    await websocket.send_json({"type": "log", "node": event["name"], "message": "Starting..."})
                
                elif kind == "on_chain_end":
                    if event["name"] == "LangGraph":
                        # The graph output contains data under the last node name ('executor')
                        final_output = event["data"]["output"]
                        print(f"DEBUG: final_output keys: {final_output.keys() if isinstance(final_output, dict) else type(final_output)}")
                        
                        # Extract the actual state data from under the executor key
                        executor_data = final_output.get("executor", {})
                        print(f"DEBUG: executor_data keys: {executor_data.keys() if isinstance(executor_data, dict) else type(executor_data)}")
                        
                        # Update session state with the executor output
                        current_state = session_store[file_id]
                        
                        print(f"DEBUG: Before update - message count: {len(current_state.get('messages', []))}")
                        
                        # Merge executor data into current state
                        if isinstance(executor_data, dict):
                            for key in ['image_path', 'df_head', 'analysis_code', 'analysis_output', 'plotly_html']:
                                if key in executor_data:
                                    current_state[key] = executor_data[key]
                            
                            # IMPORTANT: Update messages to include all AI responses for history
                            if 'messages' in executor_data:
                                # The executor_data messages contain the full conversation including user + AI
                                current_state['messages'] = executor_data['messages']
                                print(f"DEBUG: After update - message count: {len(current_state['messages'])}")
                                print(f"DEBUG: Last 3 messages: {[(m.type, m.content[:50] if hasattr(m, 'content') else str(m)[:50]) for m in current_state['messages'][-3:]]}")
                        
                        # Get response text from analysis_output or a message
                        response_text = executor_data.get('analysis_output', 'Analysis complete.')
                        
                        # Get image data and plotly figures
                        image_data = executor_data.get("image_path", "")
                        plotly_html = executor_data.get("plotly_html", [])
                        print(f"DEBUG: Sending image data length: {len(image_data) if image_data else 0}")
                        print(f"DEBUG: Sending plotly figures count: {len(plotly_html)}")
                        print(f"DEBUG: Response text preview: {response_text[:200] if response_text else 'None'}...")
                        
                        await websocket.send_json({
                            "type": "result", 
                            "content": response_text, 
                            "image": image_data if image_data else None,
                            "plotly_figures": plotly_html
                        })
                        
                        # Reset image path after sending
                        if image_data:
                            current_state["image_path"] = ""
                        
                        session_store[file_id] = current_state
                        print(f"DEBUG: Saved to session_store - total messages: {len(session_store[file_id]['messages'])}")
                    else:
                         await websocket.send_json({"type": "log", "node": event["name"], "message": "Completed."})
                         
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {file_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        traceback.print_exc()
        await websocket.send_json({"type": "error", "content": str(e)})

# Mount static files
frontend_path = os.path.join(os.getcwd(), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/assets", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)

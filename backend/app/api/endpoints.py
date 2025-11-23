from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from app.models import ChatRequest, ChatResponse
from app.agents.graph import app_graph
from app.agents.nodes import summarizer_node
from app.core.config import settings
import shutil
import os
import uuid
from langchain_core.messages import HumanMessage
import traceback
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for session state (for demo purposes)
session_store = {}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create session-specific directory
        session_dir = os.path.join(settings.UPLOAD_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Use original filename
        original_filename = file.filename
        file_path = os.path.join(session_dir, original_filename)
        
        # Check if file already exists
        if os.path.exists(file_path):
            # File already exists, reuse it (no duplication)
            print(f"File already exists: {file_path}, reusing...")
        else:
            # Save the new file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            print(f"Saved new file: {file_path}")
            
        # Initialize state for this session with session_id
        # Don't generate summary yet - let WebSocket handle it for better UX
        initial_state = {
            "messages": [],
            "file_path": file_path,
            "session_id": session_id,
            "df_head": "",
            "analysis_code": "",
            "analysis_output": "",
            "image_path": ""
        }
        
        session_store[session_id] = initial_state
        
        # Return immediately so frontend can show chat interface
        return {
            "message": "File uploaded successfully",
            "file_id": session_id,
            "filename": original_filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/chat/{file_id}", response_model=ChatResponse)
async def chat(file_id: str, request: ChatRequest):
    # Keep existing endpoint for backward compatibility or fallback
    if file_id not in session_store:
        raise HTTPException(status_code=404, detail="Session not found. Please upload a file first.")
    
    try:
        state = session_store[file_id]
        
        # Add user message
        user_message = HumanMessage(content=request.message)
        state["messages"].append(user_message)
        
        # Run the graph
        inputs = state
        result = app_graph.invoke(inputs)
        
        # Update state
        session_store[file_id] = result
        
        # Get the last message (from executor)
        last_message = result["messages"][-1]
        response_text = last_message.content
        
        # Include image if present
        history = []
        if result.get("image_path"):
            history.append({"type": "image", "data": result["image_path"]})
            # Reset image path so it doesn't persist to next turn unless regenerated
            result["image_path"] = ""
            session_store[file_id] = result
            
        return ChatResponse(response=response_text, history=history)
    except Exception as e:
        print("Error processing chat request:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

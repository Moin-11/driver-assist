#!/usr/bin/env python3
"""
Simple SSE Server for Driver Assist System

This FastAPI server acts as a real-time event router between backend modules
and the React frontend. It receives events from detection modules via POST
and streams them to connected clients via Server-Sent Events (SSE).

Endpoints:
- POST /emit - Receives events from backend modules
- GET /events - SSE stream for frontend clients
- GET /health - Health check endpoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
from collections import deque
from datetime import datetime
from typing import Dict, Any

app = FastAPI(title="Driver Assist Event Server")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory event queue (max 100 events to prevent memory issues)
event_queue = deque(maxlen=100)
event_counter = 0

@app.post("/emit")
async def emit_event(event: Dict[Any, Any]):
    """
    Receive events from backend modules.

    Expected event format:
    {
        "module": "Brake Checking" | "Lane Change Detection" | "Speed Monitoring",
        "eventType": str,
        "severity": "low" | "moderate" | "high",
        "message": str,
        ... (module-specific fields)
    }
    """
    global event_counter

    # Add timestamp if not present
    if 'timestamp' not in event:
        event['timestamp'] = datetime.now().isoformat()

    # Add unique ID
    event_counter += 1
    if 'id' not in event:
        event['id'] = event_counter

    # Add to queue
    event_queue.append(event)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Event received: {event.get('module', 'Unknown')} - {event.get('message', 'No message')}")

    return {"status": "ok", "event_id": event_counter}


@app.get("/events")
async def stream_events():
    """
    SSE endpoint that streams events to frontend clients.
    Checks for new events every 50ms.
    """
    async def event_generator():
        # Track which events this client has received
        last_seen_id = 0

        while True:
            # Send any new events
            new_events = [e for e in event_queue if e.get('id', 0) > last_seen_id]

            for event in new_events:
                yield {
                    "event": "message",
                    "data": json.dumps(event)
                }
                last_seen_id = event.get('id', 0)

            # Check for new events every 50ms (20Hz)
            await asyncio.sleep(0.05)

    return EventSourceResponse(event_generator())


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "events_in_queue": len(event_queue),
        "total_events_processed": event_counter,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Driver Assist Event Server",
        "version": "1.0.0",
        "endpoints": {
            "POST /emit": "Receive events from modules",
            "GET /events": "SSE stream for frontend",
            "GET /health": "Health check"
        },
        "events_processed": event_counter
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting Driver Assist Event Server on http://0.0.0.0:8000")
    print("SSE endpoint: http://0.0.0.0:8000/events")
    print("Health check: http://0.0.0.0:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000)

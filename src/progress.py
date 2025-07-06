# src/progress.py
import json

def create_sse_update(progress: int, message: str, stage: str, status: str, total_time: float = None) -> str:
    """Creates a server-sent event (SSE) update as a JSON string."""
    data = {
        "progress": progress,
        "message": message,
        "stage": stage,
        "status": status,
    }
    if total_time is not None:
        data["total_time"] = f"{total_time:.2f}"
        
    return f"data: {json.dumps(data)}\n\n" 
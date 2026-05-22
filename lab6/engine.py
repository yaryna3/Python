import asyncio
import time
from typing import Any
from classifier import classify_image

# Змінили Queue на PriorityQueue
job_queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=50)
job_store: dict[str, dict] = {}
store_lock: asyncio.Lock = asyncio.Lock()
inference_semaphore: asyncio.Semaphore = asyncio.Semaphore(4)
metrics: dict[str, Any] = {
    "received": 0,
    "completed": 0,
    "failed": 0,
    "total_time": 0.0
}

async def process_worker(worker_id: int) -> None:
    while True:
        job_data = None
        try:
            # Дістаємо завдання (пріоритет, час, дані)
            priority, _, job_data = await job_queue.get()
            job_id = job_data["job_id"]
            image_bytes = job_data["image_bytes"]

            async with store_lock:
                job_store[job_id]["status"] = "processing"

            start_time = time.monotonic()

            async with inference_semaphore:
                class_name, confidence = await asyncio.to_thread(classify_image, image_bytes)

            processing_time = time.monotonic() - start_time

            async with store_lock:
                job_store[job_id]["status"] = "completed"
                job_store[job_id]["result"] = {"class_name": class_name, "confidence": confidence}
                metrics["completed"] += 1
                metrics["total_time"] += processing_time

        except asyncio.CancelledError:
            raise
        except Exception as exc:
            if job_data:
                async with store_lock:
                    job_store[job_data["job_id"]]["status"] = "failed"
                    job_store[job_data["job_id"]]["error"] = str(exc)
                    metrics["failed"] += 1
        finally:
            if job_data:
                job_queue.task_done()
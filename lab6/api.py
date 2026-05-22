import asyncio
import uuid
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, status, Form
from typing import List

from engine import job_queue, job_store, store_lock, process_worker, metrics

worker_tasks: list[asyncio.Task] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    for i in range(4):
        task = asyncio.create_task(process_worker(i))
        worker_tasks.append(task)
    yield
    for task in worker_tasks:
        task.cancel()
    await asyncio.gather(*worker_tasks, return_exceptions=True)

app = FastAPI(lifespan=lifespan)

@app.post("/submit", status_code=status.HTTP_202_ACCEPTED)
async def submit(file: UploadFile = File(...)):
    if job_queue.full():
        raise HTTPException(status_code=503, detail="Queue is full")

    image_bytes = await file.read()
    job_id = str(uuid.uuid4())

    async with store_lock:
        job_store[job_id] = {"status": "pending"}
        metrics["received"] += 1

    # Звичайні завдання отримують пріоритет 3
    await job_queue.put((3, time.monotonic(), {"job_id": job_id, "image_bytes": image_bytes}))
    return {"job_id": job_id}


@app.post("/submit/priority", status_code=status.HTTP_202_ACCEPTED)
async def submit_priority(priority: int = Form(1), file: UploadFile = File(...)):
    if job_queue.full():
        raise HTTPException(status_code=503, detail="Queue is full")

    image_bytes = await file.read()
    job_id = str(uuid.uuid4())

    async with store_lock:
        job_store[job_id] = {"status": "pending"}
        metrics["received"] += 1

    # Кладемо в чергу із заданим пріоритетом
    await job_queue.put((priority, time.monotonic(), {"job_id": job_id, "image_bytes": image_bytes}))
    return {"job_id": job_id, "priority": priority}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    async with store_lock:
        if job_id not in job_store:
            raise HTTPException(status_code=404, detail="Not found")
        return {"status": job_store[job_id]["status"]}

@app.get("/result/{job_id}")
async def get_result(job_id: str):
    async with store_lock:
        if job_id not in job_store:
            raise HTTPException(status_code=404, detail="Not found")
        
        job = job_store[job_id]
        if job["status"] != "completed":
            raise HTTPException(status_code=400, detail=f"Job is still {job['status']}")
        return job["result"]

@app.post("/batch")
async def submit_batch(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        if job_queue.full():
            results.append({"filename": file.filename, "error": "Queue is full"})
            continue
            
        image_bytes = await file.read()
        job_id = str(uuid.uuid4())
        
        async with store_lock:
            job_store[job_id] = {"status": "pending"}
            metrics["received"] += 1
            
        await job_queue.put((3, time.monotonic(), {"job_id": job_id, "image_bytes": image_bytes}))
        results.append({"filename": file.filename, "job_id": job_id})
    return results

@app.get("/metrics")
async def get_metrics():
    async with store_lock:
        completed = metrics["completed"]
        avg_time = metrics["total_time"] / completed if completed > 0 else 0
        return {
            "received": metrics["received"],
            "completed": completed,
            "failed": metrics["failed"],
            "queue_depth": job_queue.qsize(),
            "avg_processing_time": avg_time
        }
import asyncio
import httpx
import time
from PIL import Image

API_URL = "http://127.0.0.1:8000"
IMAGE_PATH = "test_image.jpg"

async def submit_one(client, image_bytes, results, i):
    try:
        files = {'file': ('test.jpg', image_bytes, 'image/jpeg')}
        response = await client.post(f"{API_URL}/submit", files=files)
        if response.status_code == 202:
            results[i] = response.json()["job_id"]
        else:
            results[i] = f"Error {response.status_code}"
    except Exception as e:
        results[i] = f"Exception: {e}"

async def poll_until_done(client, job_id, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        resp = await client.get(f"{API_URL}/status/{job_id}")
        if resp.status_code == 200:
            status = resp.json()["status"]
            if status in ["completed", "failed"]:
                return status
        await asyncio.sleep(0.5)
    return "timeout"

async def main():
    # Створюємо тестове зображення
    img = Image.new('RGB', (224, 224), color='red')
    img.save(IMAGE_PATH)

    with open(IMAGE_PATH, "rb") as f:
        image_bytes = f.read()

    print("Починаємо навантажувальний тест...")
    start_time = time.monotonic()
    results = {}

    # Робимо 60 запитів, щоб перевірити заповнення черги (ліміт 50)
    async with httpx.AsyncClient(timeout=30.0) as client:
        submit_tasks = [submit_one(client, image_bytes, results, i) for i in range(60)]
        await asyncio.gather(*submit_tasks)

        accepted = 0
        rejected = 0

        poll_tasks = []
        for idx, res in results.items():
            if "Error 503" in res:
                rejected += 1
            elif not res.startswith("Error") and not res.startswith("Exception"):
                accepted += 1
                poll_tasks.append(poll_until_done(client, res))

        statuses = await asyncio.gather(*poll_tasks)
        completed = statuses.count("completed")

    duration = time.monotonic() - start_time
    print(f"Загальний час: {duration:.2f} сек")
    print(f"Прийнято запитів: {accepted}")
    print(f"Відхилено (Помилка 503): {rejected}")
    print(f"Успішно завершено: {completed}")

    # Отримуємо фінальні метрики сервера
    async with httpx.AsyncClient() as client:
        metrics = await client.get(f"{API_URL}/metrics")
        print("\nМетрики сервера:", metrics.json())

if __name__ == "__main__":
    asyncio.run(main())
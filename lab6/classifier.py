import io
import torch
from torchvision import models
from PIL import Image
from typing import Tuple

# Завантажуємо модель MobileNetV2 лише один раз на рівні модуля
weights = models.MobileNet_V2_Weights.DEFAULT
model = models.mobilenet_v2(weights=weights)
model.eval()

# Налаштовуємо необхідні трансформації для картинок
preprocess = weights.transforms()
categories = weights.meta["categories"]

def classify_image(image_bytes: bytes) -> Tuple[str, float]:
    # Це синхронна функція, яка виконується поза головним циклом подій (event loop)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0)

    # Виконуємо інференс без розрахунку градієнтів для економії пам'яті
    with torch.no_grad():
        output = model(input_batch)

    # Рахуємо ймовірності та знаходимо найкращий результат
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    confidence, class_id = torch.max(probabilities, 0)

    class_name = categories[class_id.item()]
    return class_name, confidence.item()
import requests
import logging
import base64
import os

OLLAMA_URL = "http://ollama:11434/api/generate"
MODEL_NAME = "moondream"
REQUEST_TIMEOUT = 180

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def _download_image_as_base64(image_url: str) -> str:
    if not os.path.exists(image_url):
        raise RuntimeError(f"Файл изображения не найден: {image_url}")

    with open(image_url, "rb") as f:
        content = f.read()

    logger.info(f"Loaded local image size: {len(content)} bytes from path {image_url}")
    return base64.b64encode(content).decode("utf-8")

def do_task(image_url: str, manual_text: str | None = None) -> str:
    try:
        image_base64 = _download_image_as_base64(image_url)

        prompt = (
            "You are analyzing a product label in the image.\n"
            "Answer in English with short phrases, not full sentences.\n\n"
            "Extract the following fields as clearly as possible from the label:\n"
            "1) Product type (e.g. shampoo, conditioner, body wash)\n"
            "2) Brand name\n"
            "3) Main benefit (e.g. hair fall control, volume, moisturizing)\n"
            "4) Hair type or target (if visible)\n\n"
            "Format your answer exactly like this:\n"
            "type: <type>\n"
            "brand: <brand>\n"
            "benefit: <benefit>\n"
            "target: <target or unknown>\n"
        )
        
        if manual_text:
            prompt += f"\nAdditional user note: {manual_text}"

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False
            },
            timeout=REQUEST_TIMEOUT
        )

        logger.info(f"Ollama response status code: {response.status_code}")
        logger.info(f"Ollama raw response text: {response.text}")

        if response.status_code == 404:
            raise RuntimeError("Модель moondream не найдена в Ollama")

        response.raise_for_status()
        data = response.json()

        result = data.get("response", "").strip()
        if not result:
            raise RuntimeError("Модель не вернула описание")

        return result

    except requests.Timeout:
        logger.error("Request timed out")
        raise RuntimeError("Превышено время ожидания ответа от модели")
    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        raise RuntimeError("Ошибка при обращении к модели или загрузке изображения")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise RuntimeError(f"Неожиданная ошибка при генерации описания: {str(e)}")

import requests
import logging
import base64
import os

OLLAMA_URL = "http://ollama:11434/api/generate"
MODEL_NAME = "qwen3.5:0.8b"
REQUEST_TIMEOUT = 360

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
            "OCR TASK.\n"
            "Extract ONLY visible text from image.\n"
            "Do NOT describe.\n"
            "Do NOT interpret.\n"
            "Do NOT add missing text.\n"
            "Return raw text exactly as seen.\n"
            "If unreadable, skip it.\n"
            "Output ONLY text.\n"
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
            raise RuntimeError(f"Модель {MODEL_NAME} не найдена в Ollama")

        response.raise_for_status()
        data = response.json()

        result = data.get("response", "").strip()
        if not result:
            thinking = data.get("thinking", "").strip()
            if thinking:
                result = thinking
            else:
                raise RuntimeError("Модель не вернула ни response, ни thinking")

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

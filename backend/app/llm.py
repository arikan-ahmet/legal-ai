import httpx

from app.config import settings


class LLMService:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    async def chat(self, messages: list[dict]) -> str:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                    },
                    timeout=120.0,
                )

            response.raise_for_status()

            data = response.json()

            return data["message"]["content"]

        except httpx.ConnectError:
            raise RuntimeError("Ollama service is unavailable.")

        except httpx.TimeoutException:
            raise RuntimeError("Ollama request timed out.")

        except httpx.HTTPStatusError as error:
            raise RuntimeError(
                f"Ollama request failed with status {error.response.status_code}."
            ) from error
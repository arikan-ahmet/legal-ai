import httpx


class LLMService:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "qwen2.5:7b"

    async def chat(self, message: str) -> str:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": message,
                            }
                        ],
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
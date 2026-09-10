import json
import httpx
from typing import Dict, Any
from app.config import settings

class BaseAgent:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.ollama_url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"
        self.model = settings.OLLAMA_MODEL


    async def call_llm(self, prompt: str, fallback_logic: callable = None, **kwargs) -> Dict[str, Any]:
        """
        Calls Ollama LLM endpoint. If Ollama is unavailable or fails, invokes heuristic fallback handler.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.ollama_url,
                    json={"model": self.model, "prompt": prompt, "stream": False, "format": "json"},
                    timeout=8.0
                )
                if response.status_code == 200:
                    try:
                        return json.loads(response.json()["response"])
                    except json.JSONDecodeError:
                        print(f"{self.agent_name}: Failed to parse JSON from LLM response.")
        except Exception as e:
            print(f"{self.agent_name}: LLM service unavailable ({e}). Using local heuristic processing.")
        
        if fallback_logic:
            return fallback_logic(**kwargs)
        return {}

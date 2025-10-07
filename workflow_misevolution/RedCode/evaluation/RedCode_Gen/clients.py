from abc import ABC, abstractmethod
from openai import OpenAI
from together import Together
import anthropic
import requests
from requests.auth import HTTPBasicAuth

class LLMClient(ABC):
    @abstractmethod
    def generate(self, system, user_request):
        pass

class OpenAIClient(LLMClient):
    def __init__(self, api_key, model):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, system, user_request):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_request},
            ],
            temperature=0.8,
            max_tokens=2000,
            top_p=0.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        return response.choices[0].message.content

class TogetherClient(LLMClient):
    def __init__(self, api_key, model):
        self.client = Together(api_key=api_key)
        self.model = model

    def generate(self, system, user_request):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_request},
            ],
            temperature=0.8,
            max_tokens=2000,
            top_p=0.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        return response.choices[0].message.content

class AnthropicClient(LLMClient):
    def __init__(self, api_key, model):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def generate(self, system, user_request):
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.8,
            system=system,
            messages=[
                {"role": "user", "content": user_request}
            ]
        )
        return message.content[0].text

class AFlowClient(LLMClient):
    def __init__(self, api_key, secret_key, base_url, model, temperature=0.1, max_tokens=2048, top_p=1.0, timeout=60, api_path=None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.timeout = timeout
        self.api_path = (api_path or "").strip()

    def _compose_url(self, use_fallback=False):
        if use_fallback:
            return f"{self.base_url}/chat/completions"
        if self.api_path:
            return f"{self.base_url}/{self.api_path.lstrip('/')}"
        return self.base_url

    def _post(self, url, payload):
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {self.api_key}"}
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            # auth=HTTPBasicAuth(self.api_key, self.secret_key),
            timeout=self.timeout
        )
        response.raise_for_status()
        return response

    def _parse_text(self, response):
        try:
            data = response.json()
        except Exception:
            return response.text
        if isinstance(data, dict):
            if "choices" in data and data["choices"]:
                choice = data["choices"][0]
                if isinstance(choice, dict):
                    message = choice.get("message") or {}
                    content = message.get("content")
                    if content:
                        return content
                    text = choice.get("text")
                    if text:
                        return text
            for key in ["output", "content", "result", "data"]:
                if key in data and isinstance(data[key], str):
                    return data[key]
        return response.text

    def generate(self, system, user_request):
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_request}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        url_primary = self._compose_url(use_fallback=False)
        try:
            resp = self._post(url_primary, payload)
            return self._parse_text(resp)
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                url_fb = self._compose_url(use_fallback=True)
                resp = self._post(url_fb, payload)
                return self._parse_text(resp)
            raise

class OpenAIHTTPClient(LLMClient):
    def __init__(self, api_key, base_url, model, api_path="chat/completions", timeout=60, temperature=0.8, max_tokens=2000):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_path = api_path.strip() or "chat/completions"
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _compose_url(self):
        return f"{self.base_url}/{self.api_path.lstrip('/')}"

    def generate(self, system, user_request):
        url = self._compose_url()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_request}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and data.get("choices"):
            choice = data["choices"][0]
            if isinstance(choice, dict):
                message = choice.get("message") or {}
                content = message.get("content")
                if content:
                    return content
                text = choice.get("text")
                if text:
                    return text
        return response.text


def get_client(config):
    # Prefer AFlowClient (BasicAuth) when explicit credentials are provided
    if all(k in config and config[k] for k in ["base_url", "api_key", "secret_key"]):
        return AFlowClient(
            api_key=config["api_key"],
            secret_key=config["secret_key"],
            base_url=config["base_url"],
            model=config["model"],
            temperature=float(config.get("temperature", 0.1)),
            max_tokens=int(config.get("max_tokens", 2048)),
            top_p=float(config.get("top_p", 1.0)),
            timeout=int(config.get("timeout", 60)),
            api_path=config.get("api_path")
        )
    if config["model"].startswith("gpt"):
        return OpenAIClient(config["openai_api_key"], config["model"])
    elif config["model"].startswith("deepseek"):
        return TogetherClient(config["together_api_key"], config["model"])
    elif config["model"].startswith("claude"):
        return AnthropicClient(config["anthropic_api_key"], config["model"])
    elif config["model"].startswith("Qwen") or config["model"].startswith("qwen"):
        # For Qwen models, try to use OpenAI client as fallback
        return OpenAIClient(config.get("openai_api_key", ""), config["model"])
    else:
        raise ValueError(f"Unsupported model: {config['model']}")
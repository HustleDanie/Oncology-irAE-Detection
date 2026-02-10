"""LLM client for API interactions with OpenAI/Anthropic."""

import os
import json
from typing import Optional, Any
from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> str:
        """Generate a completion from the LLM."""
        pass
    
    @abstractmethod
    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 3000,
    ) -> dict:
        """Generate a JSON completion from the LLM."""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI API client."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self._client = None
    
    def _get_client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
        return self._client
    
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> str:
        """Generate a completion using OpenAI."""
        client = self._get_client()
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.choices[0].message.content
    
    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 3000,
    ) -> dict:
        """Generate a JSON completion using OpenAI."""
        client = self._get_client()
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content
        return json.loads(content)


class HuggingFaceClient(BaseLLMClient):
    """Hugging Face client for Google MedGemma models from HAI-DEF."""

    def __init__(self, model_name: str = "google/medgemma-4b-it", use_quantization: bool = True):
        self.model_name = model_name
        self.use_quantization = use_quantization
        self._pipeline = None
        self._tokenizer = None
        self._hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
        self._model_loaded = False
        self._loading_error = None
    
    def is_model_loaded(self) -> bool:
        """Check if the model has been loaded."""
        return self._model_loaded
    
    def get_loading_error(self) -> str:
        """Get any error that occurred during model loading."""
        return self._loading_error
    
    def initialize_model(self):
        """Explicitly initialize the model (non-lazy loading)."""
        try:
            self._get_pipeline()
            return True
        except Exception as e:
            self._loading_error = str(e)
            return False

    def _get_pipeline(self, model_key: str = None):
        """Lazy initialization of Hugging Face pipeline for MedGemma."""
        if self._pipeline is None:
            try:
                import torch
                from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

                print(f"[MEDGEMMA] Starting model load: {self.model_name}")
                print(f"[MEDGEMMA] HF Token present: {self._hf_token is not None}")
                print(f"[MEDGEMMA] Use quantization: {self.use_quantization}")
                print(f"[MEDGEMMA] CUDA available: {torch.cuda.is_available()}")
                
                # Use token for gated model access
                token_kwargs = {"token": self._hf_token} if self._hf_token else {}
                
                print("[MEDGEMMA] Loading tokenizer...")
                self._tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name,
                    **token_kwargs
                )
                print("[MEDGEMMA] Tokenizer loaded successfully!")
                
                # Load with quantization if enabled and available
                load_kwargs = {
                    "device_map": "auto",
                    "torch_dtype": torch.bfloat16,
                    **token_kwargs
                }
                
                if self.use_quantization and torch.cuda.is_available():
                    try:
                        import bitsandbytes
                        # Use BitsAndBytesConfig for newer model architectures
                        quantization_config = BitsAndBytesConfig(
                            load_in_8bit=True,
                        )
                        load_kwargs["quantization_config"] = quantization_config
                        print("[MEDGEMMA] Using 8-bit quantization for memory efficiency.")
                    except ImportError:
                        print("[MEDGEMMA] bitsandbytes not available, loading without quantization.")
                
                print("[MEDGEMMA] Loading model weights (this may take several minutes)...")
                model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    **load_kwargs
                )

                self._pipeline = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=self._tokenizer,
                )
                self._model_loaded = True
                print(f"MedGemma model loaded successfully.")
                
            except ImportError as e:
                self._loading_error = str(e)
                raise ImportError(
                    f"Hugging Face packages required. Install with: pip install transformers torch accelerate sentencepiece bitsandbytes\nError: {e}"
                )
            except Exception as e:
                self._loading_error = str(e)
                raise RuntimeError(f"Failed to load MedGemma model: {e}")
        return self._pipeline

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        model_key: str = None  # Kept for backwards compatibility, ignored
    ) -> str:
        """Generate a completion using MedGemma model."""
        import asyncio
        import warnings
        from transformers import GenerationConfig

        pipe = self._get_pipeline()
        
        # MedGemma uses a chat format with system and user roles
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        # Use GenerationConfig to avoid deprecation warnings
        generation_config = GenerationConfig(
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=temperature if temperature > 0 else 0.01,
            top_k=50,
            top_p=0.95,
        )

        def _run_inference():
            # Suppress bitsandbytes casting warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="MatMul8bitLt")
                outputs = pipe(
                    prompt,
                    generation_config=generation_config,
                )
            return outputs[0]["generated_text"][len(prompt):]

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, _run_inference)
        return result

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 3000,
        model_key: str = None  # Kept for backwards compatibility, ignored
    ) -> dict:
        """Generate a JSON completion using MedGemma model."""
        json_system_prompt = f"{system_prompt}\n\nIMPORTANT: Your response MUST be a single, valid JSON object and nothing else. Do not include any text before or after the JSON."
        
        response_text = await self.complete(
            json_system_prompt, user_prompt, temperature, max_tokens
        )
        
        try:
            start_index = response_text.find('{')
            end_index = response_text.rfind('}')
            if start_index != -1 and end_index != -1 and end_index > start_index:
                json_str = response_text[start_index:end_index+1]
                return json.loads(json_str)
            else:
                raise json.JSONDecodeError("No JSON object found in response", response_text, 0)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from LLM response: {e}")
            print(f"Raw response: {response_text}")
            return {"error": "Failed to parse JSON from model response", "raw_response": response_text}


class AnthropicClient(BaseLLMClient):
    """Anthropic API client."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self._client = None
    
    def _get_client(self):
        """Lazy initialization of Anthropic client."""
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic
                self._client = AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package required. Install with: pip install anthropic")
        return self._client
    
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> str:
        """Generate a completion using Anthropic."""
        client = self._get_client()
        
        response = await client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.content[0].text
    
    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 3000,
    ) -> dict:
        """Generate a JSON completion using Anthropic."""
        # Add JSON instruction to system prompt
        json_system = system_prompt + "\n\nRespond ONLY with valid JSON. No other text."
        
        content = await self.complete(json_system, user_prompt, temperature, max_tokens)
        
        # Parse JSON from response
        try:
            # Try to extract JSON if wrapped in markdown
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end].strip()
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from LLM response: {e}")


class LLMClient:
    """
    Unified LLM client that supports multiple providers.
    
    Usage:
        client = LLMClient(provider="openai")  # or "anthropic"
        result = await client.complete(system_prompt, user_prompt)
    """
    
    def __init__(
        self, 
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize LLM client.
        
        Args:
            provider: "openai" or "anthropic"
            api_key: API key (defaults to environment variable)
            model: Model name (defaults to provider's best model)
        """
        self.provider = provider.lower()
        
        if self.provider == "openai":
            self._client = OpenAIClient(
                api_key=api_key,
                model=model or "gpt-4o",
            )
        elif self.provider == "anthropic":
            self._client = AnthropicClient(
                api_key=api_key,
                model=model or "claude-sonnet-4-20250514",
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> str:
        """Generate a completion."""
        return await self._client.complete(
            system_prompt, user_prompt, temperature, max_tokens
        )
    
    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 3000,
    ) -> dict:
        """Generate a JSON completion."""
        return await self._client.complete_json(
            system_prompt, user_prompt, temperature, max_tokens
        )

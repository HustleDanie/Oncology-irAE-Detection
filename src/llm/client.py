"""LLM client for Google MedGemma (HAI-DEF) via Hugging Face."""

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
        temperature: float = 0.05,  # Very low for consistent medical assessments
        max_tokens: int = 3000,
        model_key: str = None  # Kept for backwards compatibility, ignored
    ) -> dict:
        """Generate a JSON completion using MedGemma model with robust extraction."""
        
        # Simplified JSON instruction - be very explicit
        json_instruction = """

CRITICAL INSTRUCTIONS:
1. Your ENTIRE response must be a single valid JSON object
2. Start with { and end with }
3. Do NOT wrap in markdown code blocks (no ```)
4. Do NOT include any text before or after the JSON
5. All string values must be properly quoted
6. Use double quotes for keys and string values

BEGIN YOUR JSON RESPONSE NOW:"""
        
        json_system_prompt = f"{system_prompt}\n{json_instruction}"
        
        # Try up to 2 times
        for attempt in range(2):
            response_text = await self.complete(
                json_system_prompt, user_prompt, temperature, max_tokens
            )
            
            # Clean the response
            response_text = response_text.strip()
            
            # Try multiple extraction strategies
            json_obj = self._extract_json(response_text)
            if json_obj is not None:
                return json_obj
            
            # If first attempt failed, try with higher temperature
            if attempt == 0:
                print(f"[MEDGEMMA] JSON extraction failed, retrying with adjusted temperature...")
                temperature = 0.1
        
        # All attempts failed - return error dict
        print(f"[MEDGEMMA] Error: Could not extract valid JSON after retries")
        print(f"[MEDGEMMA] Raw response (first 500 chars): {response_text[:500]}")
        return self._create_fallback_response()
    
    def _extract_json(self, response_text: str) -> Optional[dict]:
        """Try multiple strategies to extract JSON from response."""
        
        # Strategy 1: Response is already valid JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract JSON from markdown code blocks
        if "```json" in response_text:
            try:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                if end > start:
                    json_str = response_text[start:end].strip()
                    if json_str:  # Not empty
                        return json.loads(json_str)
            except (json.JSONDecodeError, ValueError):
                pass
        
        # Strategy 3: Extract from generic code blocks
        if "```" in response_text:
            try:
                # Find content between first ``` and next ```
                parts = response_text.split("```")
                for part in parts[1::2]:  # Odd indices are inside code blocks
                    part = part.strip()
                    if part.startswith("json"):
                        part = part[4:].strip()
                    if part.startswith("{"):
                        return json.loads(part)
            except (json.JSONDecodeError, ValueError, IndexError):
                pass
        
        # Strategy 4: Find JSON object boundaries
        try:
            start_index = response_text.find('{')
            if start_index != -1:
                # Find matching closing brace
                depth = 0
                for i, char in enumerate(response_text[start_index:], start_index):
                    if char == '{':
                        depth += 1
                    elif char == '}':
                        depth -= 1
                        if depth == 0:
                            json_str = response_text[start_index:i+1]
                            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Strategy 5: Try to find any valid JSON object
        try:
            start_index = response_text.find('{')
            end_index = response_text.rfind('}')
            if start_index != -1 and end_index != -1 and end_index > start_index:
                json_str = response_text[start_index:end_index+1]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        return None
    
    def _create_fallback_response(self) -> dict:
        """Create a safe fallback response when JSON parsing fails."""
        return {
            "error": "Failed to parse JSON from model response",
            "irae_detected": False,
            "affected_systems": [],
            "overall_severity": "Unknown",
            "urgency": "routine",
            "causality": {
                "likelihood": "Uncertain",
                "reasoning": "Unable to complete assessment due to model response error"
            },
            "recommended_actions": [
                {
                    "action": "Manual clinical review required - automated assessment failed",
                    "priority": 1,
                    "rationale": "Model response could not be parsed"
                }
            ],
            "key_evidence": [],
            "severity_reasoning": "Assessment incomplete",
            "urgency_reasoning": "Assessment incomplete - manual review needed"
        }




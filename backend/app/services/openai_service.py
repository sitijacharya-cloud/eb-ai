"""OpenAI Service for LLM interactions."""

import json
import logging
from typing import Dict, Any, Optional, List
from openai import OpenAI

from ..core.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.embedding_model = settings.openai_embedding_model
        self.temperature = settings.openai_temperature
        
        logger.info(f"Initialized OpenAI service with model: {self.model}")
    
    def generate_completion(
        self,
        prompt: str,
        system_message: str = "You are a helpful assistant.",
        temperature: Optional[float] = None,
        max_tokens: int = 8000
    ) -> str:
        """
        Generate completion from OpenAI.
        
        Args:
            prompt: User prompt
            system_message: System message for context
            temperature: Sampling temperature (overrides default)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature or self.temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            return content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def generate_json_completion(
        self,
        prompt: str,
        system_message: str = "You are a helpful assistant that returns JSON.",
        temperature: Optional[float] = None,
        max_tokens: int = 8000
    ) -> Dict[str, Any]:
        """
        Generate JSON completion from OpenAI.
        
        Args:
            prompt: User prompt
            system_message: System message
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response (default 8000 for large JSON outputs)
            
        Returns:
            Parsed JSON dictionary
        """
        try:
            response = self.generate_completion(
                prompt=prompt,
                system_message=system_message,
                temperature=temperature or 0.3,  # Lower temperature for structured output
                max_tokens=max_tokens
            )
            
            # Try to extract JSON from response
            # Sometimes the model returns JSON wrapped in markdown code blocks
            cleaned_response = response.strip()
            
            # Remove markdown code blocks if present
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON
            parsed = json.loads(cleaned_response)
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from OpenAI response: {e}")
            logger.error(f"Response was: {response}")
            raise ValueError(f"Invalid JSON response from OpenAI: {e}")
        except Exception as e:
            logger.error(f"Error generating JSON completion: {e}")
            raise
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            embedding = response.data[0].embedding
            return embedding
            
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            raise
    
    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            return embeddings
            
        except Exception as e:
            logger.error(f"Error creating batch embeddings: {e}")
            raise


# Singleton instance
_openai_service: Optional[OpenAIService] = None


def get_openai_service() -> OpenAIService:
    """Get or create OpenAI service singleton."""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service

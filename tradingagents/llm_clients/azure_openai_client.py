import os
from typing import Any, Optional

from langchain_openai import AzureChatOpenAI

from .base_client import BaseLLMClient, normalize_content
from .validators import validate_model


class NormalizedAzureChatOpenAI(AzureChatOpenAI):
    """AzureChatOpenAI with normalized content output.

    The Responses API returns content as a list of typed blocks
    (reasoning, text, etc.). This normalizes to string for consistent
    downstream handling.
    """

    def invoke(self, input, config=None, **kwargs):
        return normalize_content(super().invoke(input, config, **kwargs))


# Kwargs forwarded to AzureChatOpenAI
_PASSTHROUGH_KWARGS = (
    "timeout", "max_retries", "reasoning_effort",
    "api_key", "callbacks", "http_client", "http_async_client",
)


class AzureOpenAIClient(BaseLLMClient):
    """Client for Azure OpenAI.

    Requires:
    - AZURE_OPENAI_API_KEY environment variable
    - AZURE_OPENAI_ENDPOINT environment variable (e.g., https://<resource>.openai.azure.com/)
    - base_url parameter from config or explicit parameter
    """

    def __init__(
        self,
        model: str,
        base_url: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(model, base_url, **kwargs)
        self.provider = "azure"

    def get_llm(self) -> Any:
        """Return configured AzureChatOpenAI instance."""
        self.warn_if_unknown_model()
        
        # Get Azure credentials from environment
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "AZURE_OPENAI_API_KEY environment variable is not set. "
                "Please set it to your Azure OpenAI API key."
            )
        
        # Use base_url as Azure endpoint, or get from environment
        azure_endpoint = self.base_url or os.environ.get("AZURE_OPENAI_ENDPOINT")
        if not azure_endpoint:
            raise ValueError(
                "Azure endpoint not provided. Set either base_url in config "
                "or AZURE_OPENAI_ENDPOINT environment variable. "
                "Example: https://<resource>.openai.azure.com/"
            )

        llm_kwargs = {
            "model": self.model,
            "api_key": api_key,
            "azure_endpoint": azure_endpoint,
            "api_version": os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
        }

        # Forward user-provided kwargs
        for key in _PASSTHROUGH_KWARGS:
            if key in self.kwargs:
                llm_kwargs[key] = self.kwargs[key]

        return NormalizedAzureChatOpenAI(**llm_kwargs)

    def validate_model(self) -> bool:
        """Validate model for Azure provider."""
        # Azure OpenAI uses deployment names which are user-defined
        # Just check it's a non-empty string
        return bool(self.model)

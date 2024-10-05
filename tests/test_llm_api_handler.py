import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from llm_api_handler import LLMAPIHandler
from models import RankingResponse, PaperAnalysis

@pytest.mark.asyncio
async def test_async_process_regular():
    handler = LLMAPIHandler()
    with patch.object(handler.async_openai_client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_message = MagicMock()
        mock_message.content = 'Test response'
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_create.return_value.choices = [mock_choice]
        response = await handler.async_process(
            prompts=["What's the capital of France?"],
            model="gpt-4o-mini",
            system_message="You are a helpful assistant.",
            temperature=0.7,
            response_format=None
        )
        assert response == ["Test response"]

@pytest.mark.asyncio
async def test_async_process_structured_response():
    handler = LLMAPIHandler()
    with patch.object(handler.async_openai_client.beta.chat.completions, 'parse', new_callable=AsyncMock) as mock_parse:
        mock_message = MagicMock()
        mock_message.parsed = {"answer": "Paris", "confidence": 0.99}
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_parse.return_value.choices = [mock_choice]
        from pydantic import BaseModel

        class ResponseModel(BaseModel):
            answer: str
            confidence: float

        response = await handler.async_process(
            prompts=["What's the capital of France?"],
            model="gpt-4o-mini",
            system_message=None,
            temperature=0.7,
            response_format=ResponseModel
        )
        # Determine the type of response (begin by printing it)
        print(type(response))
        # Print the content of the response
        print(response)
        # check if response is a pydantic object matching ResponseModel
        assert isinstance(response, ResponseModel), f"Expected response to be ResponseModel, but got {type(response)}"
        # Check if response is a list
        assert isinstance(response, list), f"Expected response to be a list, but got {type(response)}"
        # Check if the first item in the list is of type ResponseModel
        assert isinstance(response[0], ResponseModel), f"Expected response[0] to be ResponseModel, but got {type(response[0])}"
        # Assert on the content of the first item
        assert response[0].answer == "Paris"
        assert response[0].confidence == 0.99

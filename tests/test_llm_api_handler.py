import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from llm_api_handler import LLMAPIHandler
from pydantic import BaseModel
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice

class ResponseModel(BaseModel):
    answer: str
    confidence: float

@pytest.fixture
def handler():
    return LLMAPIHandler()

@pytest.mark.asyncio
async def test_async_process_openai_unstructured(handler):
    with patch.object(handler.async_openai_client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = ChatCompletion(
            id="chatcmpl-123",
            choices=[Choice(index=0, message=ChatCompletionMessage(role="assistant", content="Paris"), finish_reason="stop")],
            created=1677652288,
            model="gpt-4o-mini",
            object="chat.completion"
        )
        response = await handler.async_process(
            prompts=["What's the capital of France?"],
            model="gpt-4o-mini",
            system_message="You are a helpful assistant.",
            temperature=0.7
        )
        assert response == ["Paris"]
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_async_process_openai_structured(handler):
    with patch.object(handler.async_openai_client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = ChatCompletion(
            id="chatcmpl-123",
            choices=[Choice(index=0, message=ChatCompletionMessage(role="assistant", content='{"answer": "Paris", "confidence": 0.99}'), finish_reason="stop")],
            created=1677652288,
            model="gpt-4o-mini",
            object="chat.completion"
        )
        response = await handler.async_process(
            prompts=["What's the capital of France?"],
            model="gpt-4o-mini",
            system_message=None,
            temperature=0.7,
            response_format=ResponseModel
        )
        assert isinstance(response[0], ResponseModel)
        assert response[0].answer == "Paris"
        assert response[0].confidence == 0.99
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_async_process_claude_unstructured(handler):
    with patch.object(handler.async_anthropic_client.messages, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MagicMock(
            content=[MagicMock(text="Berlin")]
        )
        response = await handler.async_process(
            prompts=["What's the capital of Germany?"],
            model="claude-3-5-sonnet-20240620",
            temperature=0.5
        )
        assert response == ["Berlin"]
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_async_process_claude_structured(handler):
    with patch.object(handler.async_anthropic_client.messages, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MagicMock(
            content=[MagicMock(text='{"answer": "Berlin", "confidence": 0.95}')]
        )
        response = await handler.async_process(
            prompts=["What's the capital of Germany?"],
            model="claude-3-5-sonnet-20240620",
            temperature=0.5,
            response_format=ResponseModel
        )
        assert isinstance(response[0], ResponseModel)
        assert response[0].answer == "Berlin"
        assert response[0].confidence == 0.95
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_async_process_multiple_prompts(handler):
    with patch.object(handler.async_openai_client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = [
            ChatCompletion(
                id=f"chatcmpl-{i}",
                choices=[Choice(index=0, message=ChatCompletionMessage(role="assistant", content=city), finish_reason="stop")],
                created=1677652288,
                model="gpt-4o-mini",
                object="chat.completion"
            ) for i, city in enumerate(["Paris", "Berlin", "Rome"])
        ]
        response = await handler.async_process(
            prompts=["Capital of France?", "Capital of Germany?", "Capital of Italy?"],
            model="gpt-4o-mini"
        )
        assert response == ["Paris", "Berlin", "Rome"]
        assert mock_create.call_count == 3

@pytest.mark.asyncio
async def test_async_process_invalid_model(handler):
    with pytest.raises(ValueError, match="Invalid model: invalid-model"):
        await handler.async_process(
            prompts=["Test prompt"],
            model="invalid-model"
        )

@pytest.mark.asyncio
async def test_async_process_rate_limiting(handler):
    with patch.object(handler.async_openai_client.chat.completions, 'create', new_callable=AsyncMock) as mock_create, \
         patch.object(handler.limiter, '__aenter__', new_callable=AsyncMock) as mock_limiter_enter, \
         patch.object(handler.limiter, '__aexit__', new_callable=AsyncMock) as mock_limiter_exit:
        
        mock_create.return_value = ChatCompletion(
            id="chatcmpl-123",
            choices=[Choice(index=0, message=ChatCompletionMessage(role="assistant", content="Test response"), finish_reason="stop")],
            created=1677652288,
            model="gpt-4o-mini",
            object="chat.completion"
        )
        
        result = await handler.async_process(
            prompts=["Test prompt"],
            model="gpt-4o-mini"
        )
        
        print(f"Result: {result}")
        print(f"mock_create.call_count: {mock_create.call_count}")
        print(f"mock_limiter_enter.call_count: {mock_limiter_enter.call_count}")
        print(f"mock_limiter_exit.call_count: {mock_limiter_exit.call_count}")
        
        # Assert that the API call was made
        mock_create.assert_called_once()
        
        # Assert that the limiter was used
        mock_limiter_enter.assert_called_once()
        mock_limiter_exit.assert_called_once()

@pytest.mark.asyncio
async def test_async_process_claude_json_extraction(handler):
    with patch.object(handler.async_anthropic_client.messages, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MagicMock(
            content=[MagicMock(text='Here is the JSON response:\n{"answer": "Tokyo", "confidence": 0.98}')]
        )
        response = await handler.async_process(
            prompts=["What's the capital of Japan?"],
            model="claude-3-5-sonnet-20240620",
            temperature=0.5,
            response_format=ResponseModel
        )
        assert isinstance(response[0], ResponseModel)
        assert response[0].answer == "Tokyo"
        assert response[0].confidence == 0.98

if __name__ == "__main__":
    pytest.main()
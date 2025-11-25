import pytest
from unittest.mock import AsyncMock, patch
from backend.openrouter import query_personas_parallel

@pytest.mark.asyncio
@patch('backend.openrouter.query_model', new_callable=AsyncMock)
async def test_query_personas_parallel(mock_query_model):
    # Arrange
    base_model = "test_model"
    user_query = "test query"
    personas = [
        {"name": "Persona 1", "prompt": "Prompt 1"},
        {"name": "Persona 2", "prompt": "Prompt 2"},
    ]

    # Mock the return value of query_model
    mock_query_model.side_effect = [
        {"content": "Response 1"},
        {"content": "Response 2"},
    ]

    # Act
    result = await query_personas_parallel(base_model, user_query, personas)

    # Assert
    # Check that the result is a dictionary with persona names as keys
    assert isinstance(result, dict)
    assert "Persona 1" in result
    assert "Persona 2" in result

    # Check that the responses are mapped correctly
    assert result["Persona 1"]["content"] == "Response 1"
    assert result["Persona 2"]["content"] == "Response 2"

    # Check that query_model was called for each persona
    assert mock_query_model.call_count == 2

    # Check the arguments of the calls to query_model
    call_args_list = mock_query_model.call_args_list
    # First call
    assert call_args_list[0][0][0] == base_model
    assert call_args_list[0][0][1][0]["role"] == "system"
    assert call_args_list[0][0][1][0]["content"] == "Prompt 1"
    assert call_args_list[0][0][1][1]["role"] == "user"
    assert call_args_list[0][0][1][1]["content"] == user_query

    # Second call
    assert call_args_list[1][0][0] == base_model
    assert call_args_list[1][0][1][0]["role"] == "system"
    assert call_args_list[1][0][1][0]["content"] == "Prompt 2"
    assert call_args_list[1][0][1][1]["role"] == "user"
    assert call_args_list[1][0][1][1]["content"] == user_query

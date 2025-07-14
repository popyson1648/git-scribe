import pytest
from unittest.mock import MagicMock
from git_scribe.core import llm

@pytest.fixture
def mock_requests_post(mocker):
    """Fixture to mock requests.post."""
    return mocker.patch('requests.post')

def test_generate_text(mock_requests_post):
    """
    Tests that generate_text sends the correct payload to the Gemini API.
    """
    # Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "  Test response  "}]}}]
    }
    mock_requests_post.return_value = mock_response

    api_key = "test_api_key"
    system_prompt = "System instructions."
    user_prompt = "User request."
    
    llm.generate_text(api_key, system_prompt, user_prompt)

    # Verify the request URL and payload
    expected_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
    expected_payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_prompt},
                    {"text": user_prompt}
                ]
            }
        ]
    }
    
    mock_requests_post.assert_called_once()
    # We check args and kwargs separately to avoid issues with dictionary order
    call_args, call_kwargs = mock_requests_post.call_args
    assert call_args[0] == expected_url
    assert "json" in call_kwargs
    # The payload is passed as the 'json' kwarg in requests
    assert call_kwargs["json"] == expected_payload

def test_clean_llm_output():
    """
    Tests that markdown fencing and extra whitespace are removed.
    """
    raw_text = "  ```markdown\nHello World\n```  "
    cleaned_text = llm.clean_llm_output(raw_text)
    assert cleaned_text == "Hello World"

    raw_text_no_fencing = "  Just whitespace  "
    cleaned_text_no_fencing = llm.clean_llm_output(raw_text_no_fencing)
    assert cleaned_text_no_fencing == "Just whitespace"


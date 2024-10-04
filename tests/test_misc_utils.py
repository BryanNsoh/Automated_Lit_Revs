import pytest
from unittest.mock import patch
from misc_utils import get_api_keys

@patch('os.getenv')
def test_get_api_keys(mock_getenv):
    mock_getenv.side_effect = lambda key: 'test_key' if 'API_KEY' in key else None
    keys = get_api_keys()
    assert keys['OPENAI_API_KEY'] == 'test_key'
    assert keys['CORE_API_KEY'] == 'test_key'

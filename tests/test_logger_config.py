import pytest
from logger_config import get_logger

def test_get_logger():
    logger = get_logger("test_module")
    assert logger.name == "test_module"

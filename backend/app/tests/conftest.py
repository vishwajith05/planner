import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.app.main import app

@pytest.fixture
def client():
    return TestClient(app)

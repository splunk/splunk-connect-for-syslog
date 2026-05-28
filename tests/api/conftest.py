import importlib
import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def _enable_management_api():
    os.environ["SC4S_API_MANAGEMENT_ENABLED"] = "true"
    import api
    importlib.reload(api)
    yield

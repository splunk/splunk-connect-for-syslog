import pytest


@pytest.fixture(autouse=True)
def management_api_token(monkeypatch, tmp_path):
    token = "unit-test-management-token"
    token_file = tmp_path / "api-token"
    token_file.write_text(token)
    monkeypatch.setenv("SC4S_API_MANAGEMENT_ENABLED", "true")
    monkeypatch.setenv("SC4S_AUTH_TOKEN_FILE", str(token_file))
    return token

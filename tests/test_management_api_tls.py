"""Unit tests for package/sbin/tls.py (management API TLS configuration)."""

import datetime as dt

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from tls import (
    TLS_CERT_ENV,
    TLS_KEY_ENV,
    TLS_KEY_PASSWORD_ENV,
    TlsConfigError,
    build_gunicorn_ssl_kwargs,
    tls_is_enabled,
)


RSA_PUBLIC_EXPONENT = 65537
RSA_KEY_SIZE_BITS = 2048


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_key_cert_to_file(tmp_path, cert: x509.Certificate, key, password: bytes | None = None):
    cert_path = tmp_path / "cert.pem"
    key_path = tmp_path / "key.pem"

    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))

    encryption = (
        serialization.BestAvailableEncryption(password)
        if password is not None
        else serialization.NoEncryption()
    )
    key_path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption,
        )
    )

    return str(cert_path), str(key_path)


def _build_key_and_cert():
    key = rsa.generate_private_key(
        public_exponent=RSA_PUBLIC_EXPONENT, key_size=RSA_KEY_SIZE_BITS
    )
    now = dt.datetime.now(dt.timezone.utc)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "tls-test")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - dt.timedelta(minutes=5))
        .not_valid_after(now + dt.timedelta(minutes=60))
        .sign(key, hashes.SHA256())
    )
    return key, cert


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _isolate_tls_env(monkeypatch):
    """Ensure no real TLS env vars leak into a test."""
    monkeypatch.delenv(TLS_CERT_ENV, raising=False)
    monkeypatch.delenv(TLS_KEY_ENV, raising=False)
    monkeypatch.delenv(TLS_KEY_PASSWORD_ENV, raising=False)


@pytest.fixture
def key_cert_pair(tmp_path):
    """Fresh self-signed RSA-2048/SHA-256 cert + matching key written to disk."""
    key, cert = _build_key_and_cert()
    return _write_key_cert_to_file(tmp_path, cert, key)


@pytest.fixture
def encrypted_key_cert_pair(tmp_path):
    """Same as ``key_cert_pair`` but the key is encrypted with a passphrase."""
    key, cert = _build_key_and_cert()
    cert_path, key_path = _write_key_cert_to_file(tmp_path, cert, key, password=b"unit-test-pw")
    return cert_path, key_path, "unit-test-pw"


# ---------------------------------------------------------------------------
# build_gunicorn_ssl_kwargs() - opt-in semantics
# ---------------------------------------------------------------------------


def test_build_kwargs_returns_empty_dict_when_unset():
    assert build_gunicorn_ssl_kwargs() == {}


def test_build_kwargs_returns_empty_dict_when_paths_blank(monkeypatch):
    monkeypatch.setenv(TLS_CERT_ENV, "   ")
    monkeypatch.setenv(TLS_KEY_ENV, "")

    assert build_gunicorn_ssl_kwargs() == {}


def test_build_kwargs_returns_dict_when_both_set(monkeypatch, key_cert_pair):
    cert_path, key_path = key_cert_pair
    monkeypatch.setenv(TLS_CERT_ENV, cert_path)
    monkeypatch.setenv(TLS_KEY_ENV, key_path)

    kwargs = build_gunicorn_ssl_kwargs()

    assert kwargs == {
        "certfile": cert_path,
        "keyfile": key_path,
        "keyfile_password": None,
    }


def test_build_kwargs_passes_password_when_set(monkeypatch, encrypted_key_cert_pair):
    cert_path, key_path, password = encrypted_key_cert_pair
    monkeypatch.setenv(TLS_CERT_ENV, cert_path)
    monkeypatch.setenv(TLS_KEY_ENV, key_path)
    monkeypatch.setenv(TLS_KEY_PASSWORD_ENV, password)

    kwargs = build_gunicorn_ssl_kwargs()

    assert kwargs["certfile"] == cert_path
    assert kwargs["keyfile"] == key_path
    assert kwargs["keyfile_password"] == password


def test_build_kwargs_raises_when_only_cert_set(monkeypatch, key_cert_pair):
    cert_path, _ = key_cert_pair
    monkeypatch.setenv(TLS_CERT_ENV, cert_path)

    with pytest.raises(TlsConfigError) as exc:
        build_gunicorn_ssl_kwargs()

    assert TLS_KEY_ENV in str(exc.value)


def test_build_kwargs_raises_when_only_key_set(monkeypatch, key_cert_pair):
    _, key_path = key_cert_pair
    monkeypatch.setenv(TLS_KEY_ENV, key_path)

    with pytest.raises(TlsConfigError) as exc:
        build_gunicorn_ssl_kwargs()

    assert TLS_CERT_ENV in str(exc.value)


# ---------------------------------------------------------------------------
# tls_is_enabled()
# ---------------------------------------------------------------------------


def test_tls_is_enabled_false_when_unset():
    assert tls_is_enabled() is False


def test_tls_is_enabled_false_when_only_one_set(monkeypatch):
    monkeypatch.setenv(TLS_CERT_ENV, "/some/cert.pem")
    assert tls_is_enabled() is False


def test_tls_is_enabled_false_when_blank(monkeypatch):
    monkeypatch.setenv(TLS_CERT_ENV, "  ")
    monkeypatch.setenv(TLS_KEY_ENV, "/k.pem")
    assert tls_is_enabled() is False


def test_tls_is_enabled_true_when_both_set(monkeypatch):
    monkeypatch.setenv(TLS_CERT_ENV, "/c.pem")
    monkeypatch.setenv(TLS_KEY_ENV, "/k.pem")
    assert tls_is_enabled() is True

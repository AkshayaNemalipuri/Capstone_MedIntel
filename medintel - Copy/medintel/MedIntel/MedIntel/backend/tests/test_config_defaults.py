from app.core.config import Settings


def test_database_default_uses_sqlite_for_local_development():
    settings = Settings(_env_file=None)
    assert settings.database_url.startswith("sqlite://")

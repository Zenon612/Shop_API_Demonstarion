from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        extra="ignore",
    )
    
    # Environment
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    
    # Database
    mock_database_url: str = Field(..., validation_alias="MOCK_DATABASE_URL")
    database_url: str = Field(..., validation_alias="DATABASE_URL")
    redis_url: str = Field(..., validation_alias="REDIS_URL")
    
    # Celery & Tasks
    celery_broker: str = Field(..., validation_alias="CELERY_BROKER")
    
    # Security
    secret_key: str = Field(..., validation_alias="SECRET_KEY")
    webhook_secret: str = Field(..., validation_alias="WEBHOOK_SECRET")
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000"],
        validation_alias="ALLOWED_ORIGINS"
    )
    
    # App
    app_name: str = "Shop_backend_demo"
    
    # Monitoring
    sentry_dsn: str = Field(..., validation_alias="SENTRY_DSN")
    
    # Logging
    log_kafka_enabled: bool = Field(default=False, validation_alias="LOG_KAFKA_ENABLED")
    log_kafka_broker: str = Field(default="kafka:9092", validation_alias="LOG_KAFKA_BROKER")
    log_kafka_topic: str = Field(default="app-logs", validation_alias="LOG_KAFKA_TOPIC")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment.lower() == "production"


settings = Settings()

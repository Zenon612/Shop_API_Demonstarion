import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from app.core.config import settings


def init_sentry():
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[
            FastApiIntegration(transaction_style="url"),
            SqlalchemyIntegration(),
            CeleryIntegration(),
        ],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://neondb_owner:npg_f6pQM3sjFNVW@ep-jolly-math-atzkqon9-pooler.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
    )
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-this-super-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080")
    )
    CORS_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS", "https://homerental.sokheng429.workers.dev/"
        ).split(",")
        if o.strip()
    ]


settings = Settings()

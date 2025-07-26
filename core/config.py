from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# librería en Python que permite cargar variables de entorno
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Gestión Formación"
    PROJECT_VERSION: str = "0.0.1"
    PROJECT_DESCRIPTION: str = "Aplicación para administrar la gestión de la información"

    # Configuración de URLs
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Configuración de la base de datos
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "")

    DATABASE_URL: str = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Configuración JWT
    # jwt_secret: str = os.getenv("JWT_SECRET")
    jwt_secret: str = "04181439f357cffdc91135b0d90dc10c9462d4a8537d3aee499f1785c7f99274"
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Configuración de correo electrónico
    mail_username: str = os.getenv("MAIL_USERNAME", "")
    mail_password: str = os.getenv("MAIL_PASSWORD", "")
    mail_from: str = os.getenv("MAIL_FROM", "")
    mail_port: int = int(os.getenv("MAIL_PORT", "587"))
    mail_server: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    mail_from_name: str = os.getenv("MAIL_FROM_NAME", "Gestión Formación")
    mail_starttls: bool = os.getenv("MAIL_STARTTLS", "True").lower() == "true"
    mail_ssl_tls: bool = os.getenv("MAIL_SSL_TLS", "False").lower() == "true"
    use_credentials: bool = os.getenv("USE_CREDENTIALS", "True").lower() == "true"
    validate_certs: bool = os.getenv("VALIDATE_CERTS", "True").lower() == "true"

    class Config:
        env_file = ".env"

settings = Settings()
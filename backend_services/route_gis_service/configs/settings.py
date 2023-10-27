import os
from functools import lru_cache

import structlog
from pydantic import AnyUrl
from pydantic_settings import BaseSettings

REDIS_PREFIX = "REDIS_"
CASSANDRA_PREFIX = "CASSANDRA_"
AWS = "AWS_"
JAEGER = "JAEGER_"
MYSQL_PREFIX = "MYSQL_"
KAFKA_PREFIX = "KAFKA_"
RABBIT_PREFIX = "RABBIT_"
MONGODB_PREFIX = "MONGO_"

Logger = structlog.getLogger(__name__)


class Settings(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "dev")
    debug: bool = os.getenv("DEBUG", True)
    redis_url: AnyUrl = os.getenv(f"{REDIS_PREFIX}URL", "redis://redis")
    redis_password: str = os.getenv(f"{REDIS_PREFIX}PASSWORD", "redis_pass")
    redis_db: str = os.getenv(f"{REDIS_PREFIX}DB", "")
    redis_hash: str = os.getenv(f"{REDIS_PREFIX}HASH_KEY", "redis-hash")
    redis_host: str = os.getenv(f"{REDIS_PREFIX}HOST", "localhost")
    redis_port: int = os.getenv(f"{REDIS_PREFIX}PORT", 3456)
    redis_ttl: int = os.getenv(f"{REDIS_PREFIX}TTL", 36000)
    cassandra_client_id: str = os.getenv(f"{CASSANDRA_PREFIX}CLIENT_ID", "")
    cassandra_client_secret: str = os.getenv(f"{CASSANDRA_PREFIX}CLIENT_SECRET", "")
    aws_profile: str = os.getenv(f"{AWS}PROFILE", "")
    aws_region = os.getenv(f"{AWS}REGION", "")
    aws_access_key_id = os.getenv(f"{AWS}ACCESS_KEY", "")
    aws_access_secret = os.getenv(f"{AWS}ACCESS_SECRET", "")
    jaeger_service_name = os.getenv(f"{JAEGER}SERVICE_NAME", "")
    jaeger_service_namespace = os.getenv(f"{JAEGER}SERVICE_NAMESPACE")
    jaeger_user_name = os.getenv(f"{JAEGER}USERNAME", "")
    jaeger_password = os.getenv(f"{JAEGER}PASSWORD", "")
    log_file_path = os.getenv("LOG_FILE_PATH", "")
    trace_file_path = os.getenv("TRACE_FILE_PATH", "")
    jaeger_params = {
        "username": jaeger_user_name,
        "password": jaeger_password,
    }
    account_service_grpc_server_address = os.getenv("Account_Service_GRPC_SERVER_ADDRESS", "localhost:50051")
    mysql_user = os.getenv(f"{MYSQL_PREFIX}USER", "")
    mysql_password = os.getenv(f"{MYSQL_PREFIX}PASSWORD", "")
    kafka_post_topic = "post"
    kafka_servers = os.environ.get(f"{KAFKA_PREFIX}SERVERS", "http://localhost:2920,http://localhost:10900")
    kafka_ssl = "",
    kafka_consumer_group = "new-dispatch-consumer-group"
    kafka_schema_url = "http://localhost:8081"
    rabbitmq_port = int(os.environ.get(f"{RABBIT_PREFIX}PORT", 5672))
    rabbitmq_host = os.environ.get(f"{RABBIT_PREFIX}HOST", 'localhost')
    mongodb_uri = os.environ.get(f"{MONGODB_PREFIX}URI", "mongodb://localhost:27018")


@lru_cache()
def get_settings() -> Settings:
    Logger.info("Loading config settings from the environment")
    return Settings()


def _common_kafka_config():
    conf = get_settings()
    return {
        "bootstrap.servers": conf.kafka_servers,
        "schema.registry.url": conf.kafka_schema_url,
        "dispatch.topic": conf.kafka_post_topic,
    }


def producer_config():
    # settings = get_settings()
    common = _common_kafka_config()
    return common


def consumer_config():
    settings = get_settings()
    common = _common_kafka_config()

    common["group.id"] = settings.kafka_consumer_group
    return common


def get_schema_config():
    settings = get_settings()
    return {
        "url": settings.kafka_schema_url
    }

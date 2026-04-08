import os
import ipaddress
from dotenv import load_dotenv

load_dotenv()

# 로그 파일을 저장할 디렉토리 경로
DATA_DIR = os.getenv("DATA_DIR", "./data")
LOG_DIR = os.getenv("LOG_DIR", "./logs")

# # 로그 디렉토리가 존재하지 않으면 자동 생성
#os.makedirs(DATA_DIR, exist_ok=True)

# 로컬 실행 시 기본 주소
# Docker 환경에서는 "http://host.docker.internal:8000/v1/chat/completions"
VLLM_BASE_URL = os.getenv("VLLM_BASE_URL")
VLLM_BASE_URL2 = os.getenv("VLLM_BASE_URL2")

# vLLM에서 실제로 사용할 LLM 모델 이름
MODEL_NAME = os.getenv("MODEL_NAME")

# IP 화이트리스트 기능 활성화 여부
ENABLE_IP_WHITELIST = (
    os.getenv("ENABLE_IP_WHITELIST", "false").lower() == "true"
)

# 허용할 IP 또는 네트워크 목록
ALLOWED_NETWORKS = [
    ipaddress.ip_network(net.strip())
    for net in os.getenv(
        "ALLOWED_NETWORKS",
        "0.0.0.0"
    ).split(",")
]

# Redis
REDIS_URL = os.getenv("REDIS_URL")

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "localhost")
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", "9200"))
OPENSEARCH_USER = os.getenv("OPENSEARCH_USER", "admin")
OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD", "")
OPENSEARCH_USE_SSL = os.getenv("OPENSEARCH_USE_SSL", "false").lower() == "true"
OPENSEARCH_VERIFY_CERTS = os.getenv("OPENSEARCH_VERIFY_CERTS", "false").lower() == "true"
OPENSEARCH_HTTP_COMPRESS = os.getenv("OPENSEARCH_VERIFY_CERTS", "true").lower() == "true"


EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3")
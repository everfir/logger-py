import os


def get_container_ip() -> str:
    return os.getenv("PodIP") or "unknow"

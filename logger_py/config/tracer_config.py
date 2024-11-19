import os

from opentelemetry.exporter.otlp.proto.http import Compression

DEFAULT_OTEL_ENDPOINT = "otelcollector-service.everfir.svc.cluster.local:4317"


class TracerConfig:
    def __init__(self):
        self.enable: bool = os.getenv("ENV") == "production"
        self.Compression: Compression = Compression.NoCompression

        self.ServiceName: str = os.getenv("SERVICE_NAME") or ""
        self.CollectorEndpoint: str = os.getenv("OTEL_COLLECTOR_DNS") or DEFAULT_OTEL_ENDPOINT
        pass
    pass
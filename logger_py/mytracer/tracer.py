import time
from typing import Tuple, Optional

from logger_py.utils.env import get_container_ip
from logger_py.config.tracer_config import TracerConfig

from opentelemetry import trace
from opentelemetry.trace.span import Span
from opentelemetry.context import Context
from opentelemetry.propagators import textmap
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http import Compression
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.sampling import ALWAYS_ON

class Tracer():
    container_ip: str = get_container_ip()
    none_span: Span = trace.NonRecordingSpan(trace.SpanContext(trace_id=0, span_id=0, is_remote=False))

    def __init__(self, config: TracerConfig):
        self.config: TracerConfig = config # tracer配置
        self.provider: Optional[TracerProvider] = None  # 全局provider
        self.exporter: Optional[OTLPSpanExporter] = None  # 全局exporter
        self.propagator: Optional[TraceContextTextMapPropagator] = None  # 全局propagator
        self.compression: Optional[Compression] = Compression.NoCompression # 数据压缩方式, 默认不压缩
        pass

    def init(self) -> Optional[Exception]:
        return tracer_init(self)

    def close(self) -> None:
        if self.provider:
            self.provider.shutdown()    
        pass
    

    def fixFields(self, ctx: dict) -> None:
        ctx["container.ip"] = self.container_ip
        ctx["serviceName"] = self.config.ServiceName
        pass

    def start_span(self, ctx: dict, name: str) -> Tuple[dict, Span]:
        if not self.provider:
            return ctx, self.none_span

        span: Span = self.provider.get_tracer(name).start_span(
            name=name, 
            context=Context(ctx),
            start_time=int(time.time() * 1000),
        )
        return ctx, span

    def inject(self, ctx: dict, carrier: dict) -> None:
        if not self.propagator:
            return

        self.propagator.inject(carrier=carrier, context=Context(ctx))
        pass

    def extract(self, ctx: dict, carrier: dict) -> Optional[dict]:
        if not self.propagator:
            return None

        ctx = self.propagator.extract(carrier=carrier, context=Context(ctx))
        return ctx



def tracer_init(tcer: Tracer) -> Optional[Exception]:
    if not tcer.config.enable:
        return None
    
    tcer.compression = tcer.config.Compression  # 数据压缩方式
    tcer.exporter = OTLPSpanExporter(  # 数据上报方式
        compression=tcer.compression,
        endpoint=tcer.config.CollectorEndpoint,
    )
    tcer.propagator = TraceContextTextMapPropagator() 
    
    # provider 初始化
    tcer.provider = TracerProvider(
        sampler=ALWAYS_ON,  # 采样器
        resource=Resource.create({
            "service.name": tcer.config.ServiceName
        }),
    )   
    tcer.provider.add_span_processor(BatchSpanProcessor(tcer.exporter))

    trace.set_tracer_provider(tcer.provider)
    return None
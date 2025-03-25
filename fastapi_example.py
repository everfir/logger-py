import uvicorn
import requests
import threading
from typing import Dict
from fastapi import FastAPI, Request

from logger_py import logger
from opentelemetry import trace
from opentelemetry.context import Context
from logger_py.config import option, ERROR
from starlette.middleware.base import BaseHTTPMiddleware

# 创建 FastAPI 应用
app = FastAPI()
port = 10086

# 初始化 logger
logger.Init(
    [
        option.WithCaller(enable=True, keep_level=2),
        option.WithLogLevel(level=ERROR),
        option.WithTracer(enable=False),
        option.WithLogFile(file="logs/fastapi_example.log"),
    ]
)


# 创建追踪中间件
class TraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ctx, span = logger.StartSpan(ctx={}, name="fastapi_request")
        ctx = trace.set_span_in_context(span=span, context=Context(ctx))
        request.state.ctx = ctx
        request.state.span = span

        response = await call_next(request)

        if span:
            span.end()
        return response


# 添加中间件
app.add_middleware(TraceMiddleware)


# 定义路由
@app.get("/hello")
async def hello(request: Request):
    logger.Info(request.state.ctx, "Received request at /hello")
    return {"message": "Hello, World!"}


# 启动服务器的函数
def run_server():
    logger.Info({}, f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)


# 客户端上下文类
class BaseContext(object):
    def TracingHeader(self, header: dict) -> dict:
        carrier = {}
        logger.Inject(ctx=ctx, carrier=carrier)
        header.update(carrier)
        return header


# 客户端请求函数
def send_request(ctx: Dict[str, object]):
    header = {}
    header["test_header"] = "test_value"
    header = BaseContext().TracingHeader(header)

    logger.Info(ctx, "Sending request to server")
    response = requests.get(
        url=f"http://localhost:{port}/hello",
        headers=header,
    )

    logger.Info(ctx, "Client request sent")
    logger.Debug(ctx=ctx, msg="Client response received", response=response.text)


if __name__ == "__main__":
    # 启动服务器线程
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    # 客户端测试代码
    ctx = {}
    ctx, span = logger.StartSpan(ctx=ctx, name="client_request")
    if not span:
        logger.Error(ctx=ctx, msg="Failed to start span")
        exit(1)
    ctx = trace.set_span_in_context(span=span, context=Context(ctx))

    logger.Info(ctx=ctx, msg="client_request span started")

    with span:
        send_request(ctx)

import uvicorn
import requests
import threading
from typing import Dict
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

from logger_py import logger
from opentelemetry import trace
from opentelemetry.context import Context
from logger_py.config import option, LOG_LEVEL
from starlette.middleware.base import BaseHTTPMiddleware

# 创建 FastAPI 应用
app = FastAPI()
port = 10086

# 初始化 logger
logger.Init(
    [
        option.WithCaller(enable=True, keep_level=2),
        option.WithLogLevel(level=LOG_LEVEL.INFO),
        option.WithTracer(enable=True),
    ]
)


# 创建追踪中间件
# 创建追踪中间件
class TraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 从header中获取追踪信息
        headers = dict(request.headers)
        carrier = {"traceparent": headers.get("traceparent", "")}

        ctx: dict = {}
        if carrier.get("traceparent"):
            ctx = logger.Extract(ctx=ctx, carrier=carrier)
            logger.Info(ctx=ctx, msg="trace middleware carrier", carrier=ctx)

        try:
            ctx, span = logger.StartSpan(ctx=ctx, name="fastapi_request")
        except Exception as e:
            # 如果解析失败，创建新的span
            ctx, span = logger.StartSpan(ctx={}, name="fastapi_request")

        logger.Info(ctx=ctx, msg="trace middleware", span=span, carrier=ctx)

        # 设置请求上下文
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
def TracingHeader(ctx: dict, header: dict) -> dict:
    carrier = {}
    logger.Inject(ctx=ctx, carrier=carrier)
    header.update(carrier)
    return header


# 客户端请求函数
def send_request(ctx: Dict[str, object]):
    header = {}
    header["test_header"] = "test_value"
    header = TracingHeader(ctx=ctx, header=header)

    logger.Info(ctx, "Sending request to server")
    response = requests.get(
        url=f"http://localhost:{port}/hello",
        headers=header,
    )

    logger.Info(ctx, "Client request sent")
    logger.Debug(ctx=ctx, msg="Client response received", response=response.text)

class AccountInfo(BaseModel):
    account_id: int = Field(default=0, description="账户ID")
    username: str = Field(default="", description="用户名")


if __name__ == "__main__":
    # 启动服务器线程
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    # 客户端测试代码
    ctx = {
        "x-everfir-account-info": AccountInfo(
            account_id=123,
            username="user123",
        ),
        "x-everfir-platform": "test",
        "x-everfir-env": "test",
    }
    ctx, span = logger.StartSpan(ctx=ctx, name="client_request")
    if not span:
        logger.Error(ctx=ctx, msg="Failed to start span")
        exit(1)
    ctx = trace.set_span_in_context(span=span, context=Context(ctx))
    logger.Info(ctx=ctx, msg="client_request span started")

    with span:
        send_request(ctx)

from logger_py import logger
import flask
import requests  # 导入 requests 库以发送 HTTP 请求
import threading  # 导入 threading 模块以实现多线程
from typing import Optional, Dict

from trace import Trace
from opentelemetry import trace
from logger_py.config import option, DEBUG, ERROR
from opentelemetry.trace.span import Span
from opentelemetry.context import Context
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

# 初始化 logger
logger.Init([
    option.WithCaller(enable=True, keep_level=2),
    option.WithLogLevel(level=DEBUG),
    option.WithTracer(enable=True),
])

# 创建 Flask 应用
app = flask.Flask(__name__)
port = 10086


def trace_middleware(app: flask.Flask):
    @app.before_request
    def before_request():
        span:Span
        ctx, span = logger.StartSpan(ctx={}, name="flask_request")
        ctx = trace.set_span_in_context(span=span, context=Context(ctx))
        flask.g.ctx = ctx
        flask.g.span = span

    @app.after_request
    def after_request(response):
        span:Span = flask.g.span
        span.end()
        return response

trace_middleware(app)

# 定义一个简单的路由
@app.route('/hello', methods=['GET'])
def hello():
    logger.Info(flask.g.ctx, "Received request at /hello")  # 打印接收到请求的日志
    return "Hello, World!"  # 返回简单的问候信息

# 启动服务器的函数
def run_server():
    logger.Info({}, f"Starting server on port {port}")  # 打印服务器启动日志
    app.run(host='0.0.0.0', port=port)  # 在所有可用的 IP 地址上运行服务器，端口为 10086

# 启动服务器线程
server_thread = threading.Thread(target=run_server)
server_thread.start()  # 启动服务器线程


class BaseContext(object):
    def TracingHeader(self, header: dict) -> dict:
        carrier = {}
        logger.Inject(ctx=ctx, carrier=carrier)
        header.update(carrier)
        return header

# client， 模拟客户端，往服务端接口发送请求
def send_request(ctx: Dict[str, object]):
    # carrier = {}
    # logger.Inject(ctx=ctx, carrier=carrier)

    header = {}
    header["test_header"] = "test_value"
    header = BaseContext().TracingHeader(header)

    logger.Info(ctx, "Sending request to server")  # 打印发送请求的日志
    response = requests.get(
        url=f'http://localhost:{port}/hello', 
        headers=header,
    )

    logger.Info(ctx, "Client request sent")  # 打印客户端请求日志
    logger.Debug(ctx=ctx, msg="Client response received", response=response.text)  # 打印客户端响应日志


# 客户端需要为流程生成一个traceID+spanID下发下去, 通过ctx来传递
ctx = {}
span: Span
ctx, span = logger.StartSpan(ctx=ctx, name="client_request")
if not span:
    logger.Error(ctx=ctx, msg="Failed to start span")  # 打印错误日志
    exit(1)
ctx=trace.set_span_in_context(span=span, context=Context(ctx))

logger.Info(
    ctx=ctx, 
    msg="client_request span started", 
)

with span:

    send_request(ctx)  # 发送请求并打印日志
from setuptools import setup, find_packages

setup(
    name='logger',  # 项目名称
    version='0.1.0',  # 项目版本
    author='houyibin',  # 作者姓名
    author_email='houyibin@everfir.com',  # 作者邮箱
    description='A brief description of your project',  # 项目描述
    long_description=open('README.md').read(),  # 从 README 文件中读取长描述
    long_description_content_type='text/markdown',  # 长描述的内容类型
    url='https://github.com/everfir/logger-py',  # 项目主页
    packages=find_packages(),  # 自动查找项目中的包
    install_requires=[  # 项目依赖的库
        'blinker==1.9.0',  # 信号库
        'certifi==2024.8.30',  # SSL证书
        'charset-normalizer==3.4.0',  # 字符集归一化
        'click==8.1.7',  # 命令行工具
        'Deprecated==1.2.15',  # 过时的库
        'Flask==3.1.0',  # Flask框架
        'googleapis-common-protos==1.66.0',  # Google API公共协议
        'idna==3.10',  # IDNA编码
        'importlib_metadata==8.5.0',  # 导入库的元数据
        'itsdangerous==2.2.0',  # 安全的cookie
        'Jinja2==3.1.4',  # 模板引擎
        'MarkupSafe==3.0.2',  # 安全的标记
        'opentelemetry-api==1.28.1',  # OpenTelemetry API
        'opentelemetry-exporter-otlp-proto-common==1.28.1',  # OpenTelemetry OTLP导出器
        'opentelemetry-exporter-otlp-proto-http==1.28.1',  # OpenTelemetry HTTP导出器
        'opentelemetry-proto==1.28.1',  # OpenTelemetry协议
        'opentelemetry-sdk==1.28.1',  # OpenTelemetry SDK
        'opentelemetry-semantic-conventions==0.49b1',  # OpenTelemetry语义约定
        'opentracing==2.4.0',  # OpenTracing库
        'protobuf==5.28.3',  # Protobuf库
        'requests==2.32.3',  # HTTP请求库
        'setuptools==75.5.0',  # 包管理工具
        'structlog==24.4.0',  # 结构化日志
        'typing_extensions==4.12.2',  # 类型扩展
        'urllib3==2.2.3',  # HTTP库
        'Werkzeug==3.1.3',  # WSGI工具库
        'wrapt==1.16.0',  # 装饰器库
        'zipp==3.21.0',  # ZIP文件处理
    ],
    classifiers=[  # 项目分类
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Python 版本要求
) 
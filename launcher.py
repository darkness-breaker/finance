"""应用启动器：PyInstaller 打包成 exe 后的入口。

双击 exe → 启动 Streamlit 服务并自动打开浏览器。
记账数据（budget.db）保存在 exe 所在目录，保证重开应用数据不丢。
"""

import os
import socket
import sys
import threading
import time
import webbrowser


def _resource_dir():
    """资源目录：打包后 app.py / database.py / streamlit 静态文件在这里。"""
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS  # PyInstaller 运行时解压目录
    return os.path.dirname(os.path.abspath(__file__))


def _data_dir():
    """数据目录：budget.db 放在 exe 旁边，而不是临时的解压目录。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _free_port():
    """找一个空闲端口，避免 8501 被占用时报错。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _open_browser(port):
    time.sleep(2)  # 等服务真正起来再开浏览器
    webbrowser.open(f"http://localhost:{port}")


def main():
    resource = _resource_dir()
    data = _data_dir()

    # 进入数据目录，让 database.py 的 budget.db 落在 exe 旁边
    os.chdir(data)

    # 测试时可用环境变量固定端口 / 跳过自动开浏览器
    if os.environ.get("BUDGET_PORT"):
        port = int(os.environ["BUDGET_PORT"])
    else:
        port = _free_port()

    if not os.environ.get("BUDGET_NO_BROWSER"):
        threading.Thread(target=_open_browser, args=(port,), daemon=True).start()

    # PyInstaller 打包后 streamlit 被解压到临时目录，路径里没有 "site-packages"，
    # 会被误判为开发模式（去连不存在的 Node 前端）。这里强制切回正常模式。
    import streamlit.config as config
    config.set_option("global.developmentMode", False)

    # 进程内启动 Streamlit 服务（和 streamlit run 等价，但不需要单独的 Python）
    import streamlit.web.bootstrap as bootstrap

    bootstrap.run(
        os.path.join(resource, "app.py"),
        False,  # is_hello
        [],     # args
        {
            "server.headless": True,
            "server.port": str(port),
            "server.address": "localhost",
            "browser.gatherUsageStats": False,
        },
    )


if __name__ == "__main__":
    main()

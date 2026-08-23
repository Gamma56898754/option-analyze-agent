import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import webview


PROJECT_ROOT = Path(__file__).resolve().parent

HOST = "127.0.0.1"
PORT = 8000

SERVER_URL = (
    f"http://{HOST}:{PORT}"
)

HEALTH_URL = (
    f"{SERVER_URL}/health"
)


def start_api_server() -> subprocess.Popen:

    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "api.app:app",
            "--host",
            HOST,
            "--port",
            str(PORT),
        ],
        cwd=PROJECT_ROOT,
    )


def wait_for_api_server(
    timeout_seconds: int = 30,
) -> None:

    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:

        try:

            with urlopen(
                HEALTH_URL,
                timeout=1,
            ) as response:

                if response.status == 200:
                    return

        except URLError:
            time.sleep(0.3)

    raise RuntimeError(
        "FastAPI server did not become ready "
        "within 30 seconds."
    )


def stop_api_server(
    process: subprocess.Popen,
) -> None:

    if process.poll() is not None:
        return

    process.terminate()

    try:
        process.wait(timeout=5)

    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def main() -> None:

    api_process = start_api_server()

    try:

        wait_for_api_server()

        window = webview.create_window(
            title="Option Analyze Agent",
            url=SERVER_URL,
            width=1280,
            height=850,
            min_size=(900, 650),
        )

        webview.start()

    finally:
        stop_api_server(api_process)


if __name__ == "__main__":
    main()
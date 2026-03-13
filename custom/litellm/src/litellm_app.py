import os

import litellm
import uvicorn
from litellm.proxy.proxy_server import app

from config_loader import resolve_config_path
from hooks import FixOpenAIRequests


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def configure_proxy():
    litellm.callbacks = [c for c in litellm.callbacks if not isinstance(c, FixOpenAIRequests)]
    litellm.callbacks.append(FixOpenAIRequests())
    os.environ["CONFIG_FILE_PATH"] = resolve_config_path(BASE_DIR)
    return app


def run():
    configure_proxy()
    uvicorn.run(app, host="0.0.0.0", port=4001)

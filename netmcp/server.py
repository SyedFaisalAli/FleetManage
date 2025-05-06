import fastapi
import sys
import uvicorn
import argparse
import pkg_resources
import logging

from .routes.mcp import mcp
from .routes.api import api
from .routes.mcp_bridge import mcp_bridge_router
from fastapi import routing
from fastapi.middleware.cors import CORSMiddleware
from .config import CONFIG
from fastapi.staticfiles import StaticFiles
from .config import load_config

log = logging.getLogger('netmcp')
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)


origins = CONFIG.get("origins", [])

app = fastapi.FastAPI(
    redirect_slashes=True,
    routes=[
        routing.Mount('/api', app=api),
        routing.Mount('/mcp_bridge', app=mcp_bridge_router),
        routing.Mount('/', StaticFiles(directory=pkg_resources.resource_filename(__name__, 'static'), html=True), name='static'),
        routing.Mount('/', app=mcp.sse_app())
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def main():
    parser = argparse.ArgumentParser(description='NetMCP Server')
    parser.add_argument('--config', type=str, help='Path to the configuration file')
    args = parser.parse_args()
    if args.config is not None:
        load_config(args.config)

    try:
        uvicorn.run(app, host=CONFIG.get('host', '0.0.0.0'), port=CONFIG.get('port', 8000))
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == '__main__':
    main()

import fastapi
import sys
import uvicorn
from routes.mcp import mcp
from routes.api import api
from routes.mcp_bridge import mcp_bridge_router
from fastapi import routing
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "localhost:5173",
    "http://localhost:5713",
]

app = fastapi.FastAPI(
    redirect_slashes=True,
    routes=[
        routing.Mount('/api', app=api),
        routing.Mount('/mcp_bridge', app=mcp_bridge_router),
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
if __name__ == '__main__':
    try:
        uvicorn.run(app, host='0.0.0.0', port=8000)
    except KeyboardInterrupt:
        sys.exit(0)

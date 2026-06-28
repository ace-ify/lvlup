import time
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()


# PRODUCTION NOTE: While subclassing BaseHTTPMiddleware is standard,
# it has known issues with async context propagation, memory leaks on streaming responses 
# (like file downloads/WebSockets) in certain Starlette versions.
#
# Modern Production Alternative: Use the @app.middleware("http") decorator instead.
#
# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     response.headers["X-Process-Time"] = str(process_time)
#     return response

class TimerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        print(f'Request: {request.url.path} processed in {duration:.5f} seconds')
        return response


app.add_middleware(TimerMiddleware)


@app.get('/hello')
async def hello():
    for _ in range(10000000):
        pass
    return {'message': 'Hello World!'}
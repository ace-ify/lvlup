from fastapi import FastAPI
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

# PRODUCTION NOTE: While HTTPSRedirectMiddleware forces HTTP-to-HTTPS redirect in Python,
# it is highly recommended to do this at the Reverse Proxy level (Nginx, Traefik, AWS ALB, Cloudflare).
# Doing it in python consumes CPU cycles and increases latency for redirection requests.
app.add_middleware(HTTPSRedirectMiddleware)
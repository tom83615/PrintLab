"""Run the local development frontend against the production data API."""

import httpx
from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse

from printlab import api

PRODUCTION = 'http://127.0.0.1:10818'
DEV_HOSTS = {'localhost:8018', '127.0.0.1:8018'}
REQUEST_HEADERS = {'content-type', 'cookie', 'if-modified-since', 'if-none-match',
                   'if-range', 'range', 'x-printlab-csrf'}
RESPONSE_HEADERS = {'accept-ranges', 'cache-control', 'content-disposition',
                    'content-encoding', 'content-length', 'content-range',
                    'content-security-policy', 'content-type', 'etag', 'last-modified',
                    'referrer-policy', 'set-cookie', 'x-content-type-options', 'x-frame-options'}


async def forward(request, scope, receive, send):
    headers = {key: value for key, value in request.headers.items() if key in REQUEST_HEADERS}
    if 'origin' in request.headers:
        headers['origin'] = PRODUCTION
    headers['accept-encoding'] = 'identity'
    target = httpx.URL(PRODUCTION).copy_with(path=request.url.path)
    raw_path = scope.get('raw_path')
    if raw_path is not None:
        target = target.copy_with(raw_path=raw_path)
    target = target.copy_with(query=scope['query_string'] or None)
    async with httpx.AsyncClient(timeout=httpx.Timeout(300, connect=3), trust_env=False) as client:
        upstream_request = client.build_request(request.method, target, headers=headers, content=await request.body())
        try:
            upstream = await client.send(upstream_request, stream=True)
        except httpx.HTTPError:
            response = JSONResponse({'detail': '暫時無法連線到正式版工作台。'}, status_code=502)
            return await response(scope, receive, send)
        try:
            response_headers = {key: value for key, value in upstream.headers.items() if key in RESPONSE_HEADERS}
            response = StreamingResponse(upstream.aiter_raw(), status_code=upstream.status_code, headers=response_headers)
            await response(scope, receive, send)
        finally:
            await upstream.aclose()


async def app(scope, receive, send):
    if scope['type'] != 'http' or not scope['path'].startswith('/api/') or scope['path'] == '/api/health':
        return await api.app(scope, receive, send)
    request = Request(scope, receive)
    host = request.headers.get('host')
    origin = request.headers.get('origin')
    if (host not in DEV_HOSTS or request.headers.get('sec-fetch-site') == 'cross-site'
            or (origin and origin != f'http://{host}')
            or (request.method not in {'GET', 'HEAD'} and not origin)):
        response = JSONResponse({'detail': '僅允許從本機開發工作台操作。'}, status_code=403)
        return await response(scope, receive, send)
    await forward(request, scope, receive, send)

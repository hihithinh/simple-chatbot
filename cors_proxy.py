from flask import Flask, request, Response, send_from_directory, redirect
import requests
import os
import logging

app = Flask(__name__, static_folder='static')

# Cấu hình logging đơn giản ra console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Proxy API requests to Rasa
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy_api(path):
    target_url = f'http://localhost:5005/{path}'
    logger.info(f"Proxying {request.method} request to: {target_url}")
    if request.method == 'OPTIONS':
        response = Response()
    else:
        try:
            resp = requests.request(
                method=request.method,
                url=target_url,
                headers={key: value for key, value in request.headers if key.lower() != 'host'},
                params=request.args,
                data=request.get_data(),
                cookies=request.cookies,
                allow_redirects=False,
                timeout=30
            )
            response = Response(resp.content, resp.status_code)
            for key, value in resp.headers.items():
                if key.lower() != 'content-length':
                    response.headers[key] = value
        except Exception as e:
            logger.error(f"Proxy error: {e}")
            response = Response(f"Proxy error: {e}", status=500)
    # CORS headers (có thể không cần nếu cùng domain, nhưng thêm cho chắc)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, Authorization'
    response.headers['Access-Control-Max-Age'] = '3600'
    response.headers['Vary'] = 'Origin'
    return response

# Serve static UI files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if path == '' or path == 'index.html':
        return send_from_directory(app.static_folder, 'index.html')
    elif os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)

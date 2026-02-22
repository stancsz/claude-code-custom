import http.server
import socketserver
import urllib.request
import urllib.error
import json
import sys

TARGET_PORT = 4001
TARGET_URL = f"http://localhost:{TARGET_PORT}"

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        print(f"Request: {self.path}")
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            body = json.loads(post_data)
            # Modify max_tokens if present
            if 'max_tokens' in body:
                print(f"Intercepted max_tokens: {body['max_tokens']}, clamping to 4096")
                body['max_tokens'] = 4096

            new_data = json.dumps(body).encode('utf-8')

            # Forward to LiteLLM
            req = urllib.request.Request(
                f"{TARGET_URL}{self.path}",
                data=new_data,
                method="POST"
            )

            # Copy headers
            for key, value in self.headers.items():
                if key.lower() not in ['content-length', 'host']:
                    req.add_header(key, value)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Content-Length', str(len(new_data)))

            try:
                with urllib.request.urlopen(req) as response:
                    self.send_response(response.status)
                    for key, value in response.headers.items():
                        if key.lower() not in ['transfer-encoding', 'content-encoding']:
                             self.send_header(key, value)
                    self.end_headers()
                    self.wfile.write(response.read())
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                for key, value in e.headers.items():
                     if key.lower() not in ['transfer-encoding', 'content-encoding']:
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(e.read())

        except Exception as e:
            print(f"Error handling request: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))

    def do_GET(self):
        print(f"GET Request: {self.path}")
        req = urllib.request.Request(f"{TARGET_URL}{self.path}", method="GET")
        try:
            with urllib.request.urlopen(req) as response:
                self.send_response(response.status)
                for key, value in response.headers.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(500)
            self.end_headers()

if __name__ == "__main__":
    port = 4000
    # Allow reuse address
    socketserver.TCPServer.allow_reuse_address = True
    try:
        # Bind to localhost for security
        with socketserver.TCPServer(("127.0.0.1", port), ProxyHandler) as httpd:
            print(f"Shim listening on 127.0.0.1:{port}, forwarding to {TARGET_URL}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Stopping shim")

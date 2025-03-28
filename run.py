import json
import verifier
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer


class MyRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        
        # Set a timeout for the socket
        self.request.settimeout(5)  # Set timeout to 5 seconds

        # Check Content-Length header
        content_length = self.headers.get('Content-Length')
        if content_length is None:
            self.send_error(400, "Missing Content-Length header")
            return

        try:
            content_length = int(content_length)
        except ValueError:
            self.send_error(400, "Invalid Content-Length")
            return

        self.end_headers()

        _verifier = verifier.Verifier()
        defaultResult = _verifier.defaultResult()

        try:
            data = self.rfile.read(content_length).decode('utf-8')            
            response = _verifier.verify(json.loads(data))
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except socket.timeout:
            self.wfile.write(json.dumps({"error": "Request timed out"}).encode('utf-8'))
        except Exception as e:
            defaultResult["message"] = str(e)
            self.wfile.write(json.dumps( defaultResult ).encode('utf-8'))

PORT = 8000
with HTTPServer(('localhost', PORT), MyRequestHandler) as httpd:
    print(f'Serving on http://localhost:{PORT}')
    httpd.serve_forever()
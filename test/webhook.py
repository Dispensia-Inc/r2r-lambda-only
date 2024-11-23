import http.server
import socketserver
import datetime
from urllib.parse import parse_qs, urlparse

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        print('path = {}'.format(self.path))
        parsed_path = urlparse(self.path)
        print('parsed: path = {}, query = {}'.format(parsed_path.path, parse_qs(parsed_path.query)))
        print('headers\r\n-----\r\n{}-----'.format(self.headers))
        content_length = int(self.headers['content-length'])
        
        print(self.rfile.read(content_length).decode("utf-8"))
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'Hello from do_POST')

with socketserver.TCPServer(("", 7272), MyHandler) as httpd:
    httpd.serve_forever()
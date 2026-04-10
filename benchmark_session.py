import time
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Local server to simulate RSS feed
class MockRSSHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/rss+xml')
        self.end_headers()
        self.wfile.write(b'<?xml version="1.0" encoding="UTF-8"?><rss><channel><item><title>Test News 1</title></item><item><title>Test News 2</title></item></channel></rss>')

    def log_message(self, format, *args):
        return

def run_server():
    server = HTTPServer(('127.0.0.1', 8080), MockRSSHandler)
    server.serve_forever()

def benchmark():
    url = "http://127.0.0.1:8080"
    iterations = 50

    # Baseline with requests.get
    start_time = time.time()
    for _ in range(iterations):
        requests.get(url)
    baseline_duration = time.time() - start_time
    print(f"Baseline (requests.get): {baseline_duration:.4f} seconds")

    # Optimized with requests.Session
    session = requests.Session()
    start_time = time.time()
    for _ in range(iterations):
        session.get(url)
    optimized_duration = time.time() - start_time
    print(f"Optimized (requests.Session): {optimized_duration:.4f} seconds")

    improvement = (baseline_duration - optimized_duration) / baseline_duration * 100
    print(f"Improvement: {improvement:.2f}%")

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1) # Give server time to start
    benchmark()

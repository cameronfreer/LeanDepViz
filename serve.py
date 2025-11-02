#!/usr/bin/env python3
"""
Simple HTTP server for testing LeanDepViz locally

Usage:
    python serve.py [port]

Default port: 8000

Then open: http://localhost:8000/docs/
"""

import http.server
import socketserver
import sys
from pathlib import Path

# Default port
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

# Serve from repo root
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"✨ LeanDepViz Server")
    print(f"📡 Serving at: http://localhost:{PORT}/")
    print(f"📂 Directory: {DIRECTORY}")
    print(f"")
    print(f"📄 Available pages:")
    print(f"   http://localhost:{PORT}/docs/index.html")
    print(f"   http://localhost:{PORT}/docs/example-exchangeability.html")
    print(f"   http://localhost:{PORT}/docs/leanparanoia-test-demo.html")
    print(f"   http://localhost:{PORT}/docs/leanparanoia-examples-all.html")
    print(f"")
    print(f"Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n👋 Server stopped")
        sys.exit(0)

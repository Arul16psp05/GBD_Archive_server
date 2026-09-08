import os
import math
import http.server
import socketserver
import urllib.parse
import html
import io
import zipfile
import threading
import json

PORT = 8000

# Global visitor tracking variables
visitor_count = 0
count_lock = threading.Lock()

def format_bytes(size):
    if size == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return f"{s} {size_name[i]}"

class CustomDirectoryHandler(http.server.SimpleHTTPRequestHandler):
    def handle(self):
        """Gracefully catch client disconnects without printing ugly tracebacks."""
        try:
            super().handle()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_GET(self):
        """Intercept GET requests for ZIP downloads and the visitor API."""
        parsed_path = urllib.parse.urlparse(self.path)
        
        # Intercept the visitor counter API call
        if parsed_path.path == '/api/visitor_count':
            global visitor_count
            with count_lock:
                visitor_count += 1
                current_count = visitor_count
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'count': current_count}).encode('utf-8'))
            return
            
        # Intercept the zip download request
        if parsed_path.query == 'zip=true':
            self.send_zip_folder()
        else:
            super().do_GET()

    def send_zip_folder(self):
        """Streams a zipped version of the requested directory on the fly."""
        parsed_path = urllib.parse.urlparse(self.path)
        folder_path = self.translate_path(parsed_path.path)
        
        if not os.path.isdir(folder_path):
            self.send_error(404, "Directory not found")
            return
        
        folder_name = os.path.basename(os.path.normpath(folder_path))
        if not folder_name:
            folder_name = "archive"
        zip_filename = f"{folder_name}.zip"

        self.send_response(200)
        self.send_header('Content-Type', 'application/zip')
        self.send_header('Content-Disposition', f'attachment; filename="{zip_filename}"')
        self.end_headers()

        try:
            with zipfile.ZipFile(self.wfile, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, folder_path)
                        zf.write(file_path, arcname)
        except ConnectionResetError:
            pass

    def list_directory(self, path):
        """Overrides the default directory listing to include file sizes and a cleaner UI."""
        try:
            list_dir = os.listdir(path)
        except OSError:
            self.send_error(404, "No permission to list directory")
            return None
            
        list_dir.sort(key=lambda a: a.lower())
        
        r = []
        displaypath = html.escape(urllib.parse.unquote(self.path))
        r.append(f'<!DOCTYPE html><html lang="en"><head><title>Index of {displaypath}</title>')
        
        r.append('''
        <style>
            body { font-family: 'Segoe UI', Tahoma, sans-serif; background-color: #0b0f19; color: #e2e8f0; padding: 30px; }
            a { color: #38bdf8; text-decoration: none; font-weight: bold; }
            a:hover { text-decoration: underline; }
            table { width: 100%; max-width: 900px; border-collapse: collapse; margin-top: 20px; background: #1e293b; border-radius: 8px; overflow: hidden;}
            th, td { text-align: left; padding: 12px 15px; border-bottom: 1px solid #334155; }
            th { background-color: #0f172a; color: #94a3b8; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; }
            tr:hover { background-color: #0f172a; }
            .back-btn { background: #4f46e5; color: white; padding: 8px 15px; border-radius: 4px; display: inline-block; margin-bottom: 20px; font-size: 0.9rem; }
            .back-btn:hover { background: #4338ca; color: white; text-decoration: none; }
        </style>
        ''')
        r.append('</head><body>')
        r.append('<a href="/" class="back-btn">&larr; Return to Dashboard</a>')
        r.append(f'<h2>Index of {displaypath}</h2>')
        r.append('<table><tr><th>Filename</th><th>Size</th></tr>')
        
        for name in list_dir:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            size_str = "-"
            
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            else:
                try:
                    size = os.path.getsize(fullname)
                    size_str = format_bytes(size)
                except OSError:
                    pass
                    
            r.append('<tr><td><a href="%s">%s</a></td><td>%s</td></tr>' % (
                urllib.parse.quote(linkname),
                html.escape(displayname),
                size_str
            ))
        
        r.append('</table></body></html>')
        encoded = '\n'.join(r).encode('utf-8', 'surrogateescape')
        
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f

class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Handle requests in a separate thread so multiple users can download at once."""
    pass

with ThreadedHTTPServer(("", PORT), CustomDirectoryHandler) as httpd:
    print(f"GBD-DART Data Archive Custom Threaded Server running at http://localhost:{PORT}")
    httpd.serve_forever()

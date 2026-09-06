# test_server.py (فایل جدید)
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class MockInsuranceHandler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        # 1. داده ورودی را بخوان
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        print("\n" + "="*50)
        print("🎯 سرور بیمه: درخواست دریافت شد")
        print(f"📦 داده: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print("="*50)
        
        # 2. پاسخ ساختگی بساز
        response_data = {
            "success": True,
            "message": "بیمه‌نامه صادر شد",
            "policy_number": f"INS-{data.get('mosque_id', '000')}-2024",
            "premium": 8500000,
            "coverage": {
                "start_date": "2024-01-01",
                "end_date": "2025-01-01"
            },
            "received_data": data  # داده دریافتی را هم برمی‌گردانیم
        }
        
        # 3. پاسخ بده
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        
        response_json = json.dumps(response_data, ensure_ascii=False)
        self.wfile.write(response_json.encode('utf-8'))
        
        print("✅ پاسخ ارسال شد")
    
    def log_message(self, format, *args):
        # لاگ‌های پیش‌فرض را نشان نده
        pass

def run_test_server():
    print("🚀 سرور تست بیمه در حال اجرا...")
    print("📡 آدرس: http://localhost:8800")
    print("📮 برای توقف: Ctrl+C")
    
    server = HTTPServer(('localhost', 8800), MockInsuranceHandler)
    server.serve_forever()

if __name__ == '__main__':
    run_test_server()
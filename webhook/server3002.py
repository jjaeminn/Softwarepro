from flask import Flask, request, jsonify, render_template_string
import requests
import threading
import time

app_3002 = Flask(__name__)

# 저장할 데이터
current_value = {"data": "초기값", "timestamp": time.time()}

# 3003 서버에 알림을 보낼 URL
WEBHOOK_URL = "http://localhost:3003/webhook"

def notify_server_3003(data):
    """3003 서버에 데이터 변경을 알리는 함수"""
    try:
        response = requests.post(WEBHOOK_URL, json=data, timeout=5)
        print(f"3003 서버에 알림 전송: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"3003 서버 알림 실패: {e}")

@app_3002.route('/')
def index_3002():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>서버 3002 - 데이터 소스</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 600px; }
            input, button { padding: 10px; margin: 5px; }
            .current-value { background: #f0f0f0; padding: 20px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>서버 3002 - 데이터 소스</h1>
            <div class="current-value">
                <h3>현재 값: {{ current_value.data }}</h3>
                <small>마지막 업데이트: {{ current_value.timestamp }}</small>
            </div>
            
            <form method="post" action="/update">
                <input type="text" name="new_value" placeholder="새로운 값 입력" required>
                <button type="submit">값 업데이트</button>
            </form>
            
            <hr>
            <h3>API 엔드포인트:</h3>
            <ul>
                <li>GET /api/data - 현재 데이터 조회</li>
                <li>POST /update - 데이터 업데이트 (웹훅 알림 포함)</li>
            </ul>
        </div>
    </body>
    </html>
    ''', current_value=current_value)

@app_3002.route('/api/data', methods=['GET'])
def get_data():
    """현재 데이터를 반환하는 API"""
    return jsonify(current_value)

@app_3002.route('/update', methods=['POST'])
def update_data():
    """데이터를 업데이트하고 3003 서버에 알림"""
    global current_value
    
    new_value = request.form.get('new_value') or request.json.get('new_value')
    if new_value:
        current_value = {
            "data": new_value,
            "timestamp": time.time()
        }
        
        # 별도 스레드에서 3003 서버에 알림 (논블로킹)
        threading.Thread(target=notify_server_3003, args=(current_value,)).start()
        
        return jsonify({"success": True, "message": "데이터가 업데이트되었습니다.", "data": current_value})
    
    return jsonify({"success": False, "message": "새로운 값이 필요합니다."})

if __name__ == '__main__':
    app_3002.run(host='localhost', port=3002, debug=True)
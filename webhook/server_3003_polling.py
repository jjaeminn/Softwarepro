from flask import Flask, render_template_string, jsonify
import requests
import threading
import time

app_polling = Flask(__name__)

# 폴링으로 가져온 데이터
polled_data = {"data": "폴링 대기 중...", "timestamp": 0, "last_checked": "없음"}

def poll_server_3002():
    """3002 서버를 주기적으로 폴링하는 함수"""
    global polled_data
    
    while True:
        try:
            response = requests.get("http://localhost:3002/api/data", timeout=5)
            if response.status_code == 200:
                data = response.json()
                polled_data = {
                    "data": data.get("data", ""),
                    "timestamp": data.get("timestamp", 0),
                    "last_checked": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                print(f"폴링으로 데이터 확인: {polled_data}")
        except requests.exceptions.RequestException as e:
            print(f"폴링 실패: {e}")
        
        time.sleep(3)  # 3초마다 확인

@app_polling.route('/')
def index_polling():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>서버 3003 - 폴링 방식</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 600px; }
            .data-display { 
                background: #fff3cd; 
                padding: 20px; 
                margin: 20px 0; 
                border-left: 4px solid #ffc107;
            }
            .status { color: #666; font-size: 0.9em; }
        </style>
        <script>
            setTimeout(function() { location.reload(); }, 4000);
        </script>
    </head>
    <body>
        <div class="container">
            <h1>서버 3003 - 폴링 방식</h1>
            <div class="data-display">
                <h2>📊 폴링된 데이터:</h2>
                <h3>{{ polled_data.data }}</h3>
                <p class="status">
                    마지막 확인: {{ polled_data.last_checked }}<br>
                    원본 타임스탬프: {{ polled_data.timestamp }}
                </p>
            </div>
            
            <hr>
            <h3>폴링 정보:</h3>
            <p>이 서버는 3초마다 localhost:3002를 확인합니다.</p>
            <p>폴링은 정기적으로 데이터를 확인하는 방식으로, 실시간성은 떨어지지만 구현이 간단합니다.</p>
        </div>
    </body>
    </html>
    ''', polled_data=polled_data)

@app_polling.route('/start-polling')
def start_polling():
    """폴링을 시작하는 엔드포인트"""
    threading.Thread(target=poll_server_3002, daemon=True).start()
    return jsonify({"message": "폴링이 시작되었습니다."})

if __name__ == '__main__':
    # 서버 시작 시 폴링도 같이 시작
    threading.Thread(target=poll_server_3002, daemon=True).start()
    app_polling.run(host='localhost', port=3004, debug=True)
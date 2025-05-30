from flask import Flask, request, jsonify, render_template_string
import requests
import time

app_3003 = Flask(__name__)

# 3002 서버로부터 받은 데이터를 저장
received_data = {"data": "아직 데이터가 없습니다", "timestamp": 0, "last_updated": "없음"}

@app_3003.route('/')
def index_3003():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>서버 3003 - 데이터 표시</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 600px; }
            .data-display { 
                background: #e8f5e8; 
                padding: 20px; 
                margin: 20px 0; 
                border-left: 4px solid #4CAF50;
            }
            .refresh-btn { 
                background: #2196F3; 
                color: white; 
                padding: 10px 20px; 
                border: none; 
                cursor: pointer; 
            }
            .status { color: #666; font-size: 0.9em; }
        </style>
        <script>
            // 5초마다 자동으로 페이지 새로고침 (실시간 효과)
            setTimeout(function() {
                location.reload();
            }, 5000);
        </script>
    </head>
    <body>
        <div class="container">
            <h1>서버 3003 - 데이터 표시</h1>
            <div class="data-display">
                <h2>🔄 실시간 데이터:</h2>
                <h3>{{ received_data.data }}</h3>
                <p class="status">
                    마지막 업데이트: {{ received_data.last_updated }}<br>
                    원본 타임스탬프: {{ received_data.timestamp }}
                </p>
            </div>
            
            <button class="refresh-btn" onclick="location.reload()">수동 새로고침</button>
            
            <hr>
            <h3>수신 로그:</h3>
            <p>이 서버는 localhost:3002의 데이터 변경을 실시간으로 받아 표시합니다.</p>
            <p>웹훅 엔드포인트: POST /webhook</p>
        </div>
    </body>
    </html>
    ''', received_data=received_data)

@app_3003.route('/webhook', methods=['POST'])
def receive_webhook():
    """3002 서버로부터 데이터 변경 알림을 받는 웹훅"""
    global received_data
    
    try:
        data = request.get_json()
        if data:
            received_data = {
                "data": data.get("data", ""),
                "timestamp": data.get("timestamp", 0),
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            print(f"웹훅으로 데이터 수신: {received_data}")
            return jsonify({"success": True, "message": "데이터를 성공적으로 받았습니다."})
    except Exception as e:
        print(f"웹훅 처리 오류: {e}")
    
    return jsonify({"success": False, "message": "데이터 처리 실패"}), 400

@app_3003.route('/api/current', methods=['GET'])
def get_current_data():
    """현재 표시 중인 데이터 반환"""
    return jsonify(received_data)

if __name__ == '__main__':
    app_3003.run(host='localhost', port=3003, debug=True)
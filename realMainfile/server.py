from flask import Flask, jsonify, request, render_template
import os
from datetime import datetime

app = Flask(__name__)

# 센서 데이터 저장
sensor_data = {
    "temperature": 0,
    "humidity": 0,
    "soil_moisture": 1,
    "water_pump": False,
    "led_status": "off",
    "last_updated": "대기 중"
}

# 템플릿 폴더 생성
if not os.path.exists('templates'):
    os.makedirs('templates')

# 웹페이지 HTML 생성
html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>스마트팜 모니터링</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; margin: 20px; background: #f0f8ff; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: white; padding: 20px; margin: 10px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .sensor-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .sensor-value { font-size: 2em; font-weight: bold; text-align: center; margin: 10px 0; }
        .temp { color: #ff4444; }
        .humidity { color: #4444ff; }
        .soil { color: #44ff44; }
        .status { color: #888; }
        h1 { text-align: center; color: #333; }
        .update-time { text-align: center; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌱 스마트팜 실시간 모니터링</h1>
        
        <div class="sensor-grid">
            <div class="card">
                <h3>🌡️ 온도</h3>
                <div class="sensor-value temp" id="temperature">--</div>
                <div>°C</div>
            </div>
            
            <div class="card">
                <h3>💧 습도</h3>
                <div class="sensor-value humidity" id="humidity">--</div>
                <div>%</div>
            </div>
            
            <div class="card">
                <h3>🌱 토양 상태</h3>
                <div class="sensor-value soil" id="soil">--</div>
            </div>
            
            <div class="card">
                <h3>💦 물펌프</h3>
                <div class="sensor-value status" id="pump">--</div>
            </div>
        </div>
        
        <div class="card">
            <h3>💡 LED 상태: <span id="led">--</span></h3>
            <div class="update-time">마지막 업데이트: <span id="last-updated">--</span></div>
        </div>
    </div>

    <script>
        function updateData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('temperature').textContent = data.temperature || '--';
                    document.getElementById('humidity').textContent = data.humidity || '--';
                    document.getElementById('soil').textContent = data.soil_moisture ? '촉촉' : '건조';
                    document.getElementById('pump').textContent = data.water_pump ? 'ON' : 'OFF';
                    document.getElementById('led').textContent = data.led_status;
                    document.getElementById('last-updated').textContent = data.last_updated;
                });
        }
        
        updateData();
        setInterval(updateData, 2000);  // 2초마다 업데이트
    </script>
</body>
</html>'''

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    return jsonify(sensor_data)

@app.route('/api/sensor_data', methods=['POST'])
def receive_sensor_data():
    global sensor_data
    data = request.get_json()
    
    sensor_data.update(data)
    sensor_data['last_updated'] = datetime.now().strftime('%H:%M:%S')
    
    print(f"센서 데이터 수신: {data}")
    return jsonify({"status": "success"})



if __name__ == '__main__':
    print("🌐 스마트팜 웹서버 시작")
    print("📊 대시보드: http://localhost:5000")
    print("📡 라즈베리파이 연결 대기 중...")
    app.run(host='0.0.0.0', port=5000, debug=False)
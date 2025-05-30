

import json
import time
import threading
import os
from datetime import datetime
from flask import Flask, jsonify, request, render_template

# =============================================================================
# 1. 데이터 저장소
# =============================================================================

class SimpleDataStore:
    """간단한 메모리 데이터 저장소"""
    
    def __init__(self):
        self.data = {
            "temperature": 25.0,
            "humidity": 60.0,
            "soil_moisture": 45.0,
            "light_intensity": 500,
            "water_pump": False,
            "led_lights": False,
            "alerts": [],
            "last_updated": datetime.now().isoformat(),
            "source": "simulation"
        }
    
    def update_data(self, new_data):
        """데이터 업데이트"""
        self.data.update(new_data)
        self.data["last_updated"] = datetime.now().isoformat()
        print(f"📊 데이터 업데이트: {new_data}")
    
    def get_data(self):
        """현재 데이터 반환"""
        return self.data.copy()

# =============================================================================
# 2. 시뮬레이터 (테스트용)
# =============================================================================

class SimpleSimulator:
    """테스트용 간단한 데이터 시뮬레이터"""
    
    def __init__(self, data_store):
        self.data_store = data_store
        self.running = False
    
    def generate_data(self):
        """랜덤 센서 데이터 생성"""
        import random
        
        data = self.data_store.get_data()
        
        # 센서값 약간씩 변경
        data["temperature"] += random.uniform(-1, 1)
        data["humidity"] += random.uniform(-2, 2)
        data["soil_moisture"] += random.uniform(-1, 1)
        data["light_intensity"] += random.randint(-50, 50)
        
        # 범위 제한
        data["temperature"] = max(20, min(35, data["temperature"]))
        data["humidity"] = max(40, min(90, data["humidity"]))
        data["soil_moisture"] = max(30, min(80, data["soil_moisture"]))
        data["light_intensity"] = max(0, min(1000, data["light_intensity"]))
        
        # 자동 제어
        data["water_pump"] = data["soil_moisture"] < 35
        data["led_lights"] = data["light_intensity"] < 200
        
        # 간단한 알림
        alerts = []
        if data["temperature"] > 30:
            alerts.append("온도 높음")
        if data["soil_moisture"] < 35:
            alerts.append("토양 건조")
        data["alerts"] = alerts
        
        return data
    
    def start(self):
        """시뮬레이션 시작"""
        self.running = True
        
        def run():
            while self.running:
                new_data = self.generate_data()
                self.data_store.update_data(new_data)
                time.sleep(5)  # 5초마다 업데이트
        
        threading.Thread(target=run, daemon=True).start()
        print("🚀 시뮬레이터 시작")

# =============================================================================
# 3. 간단한 웹 애플리케이션 (템플릿 분리)
# =============================================================================

class SimpleWebApp:
    """간단한 웹 애플리케이션"""
    
    def __init__(self, data_store, port=5000):
        self.app = Flask(__name__, template_folder='templates')
        self.data_store = data_store
        self.port = port
        self.setup_routes()
        self.ensure_templates()
    
    
    
    def setup_routes(self):
        """라우트 설정"""
        
        @self.app.route('/')
        def dashboard():
            """메인 대시보드 - 템플릿 파일 사용"""
            try:
                return render_template('dashboard.html')
            except Exception as e:
                print(f"❌ 템플릿 렌더링 오류: {e}")
                return f"""
                <html>
                <body>
                    <h1>스마트팜 대시보드</h1>
                    <p>템플릿 파일 오류: {e}</p>
                    <p><a href="/api/data">API 데이터 보기</a></p>
                </body>
                </html>
                """
        
        @self.app.route('/api/data')
        def get_data():
            """센서 데이터 API"""
            return jsonify(self.data_store.get_data())
        
        @self.app.route('/api/external_data', methods=['POST'])
        def receive_external_data():
            """외부(라즈베리파이)에서 데이터 받기"""
            try:
                data = request.get_json()
                data["source"] = "raspberry_pi"
                self.data_store.update_data(data)
                return jsonify({"status": "success"})
            except Exception as e:
                print(f"❌ 외부 데이터 수신 오류: {e}")
                return jsonify({"status": "error", "message": str(e)}), 400
    
    def start(self):
        """웹 서버 시작"""
        print(f"🌐 웹 서버 시작: http://localhost:{self.port}")
        print(f"📄 템플릿: templates/dashboard.html")
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

# =============================================================================
# 4. 라즈베리파이 센서 클래스 (간소화)
# =============================================================================

class RaspberryPiSensor:
    """라즈베리파이 센서 클래스 (간소화)"""
    
    def __init__(self, server_url="http://192.168.1.100:5000"):
        self.server_url = f"{server_url}/api/external_data"
    
    def read_sensors(self):
        """센서 데이터 읽기 (시뮬레이션)"""
        import random
        return {
            "temperature": round(random.uniform(20.0, 30.0), 1),
            "humidity": round(random.uniform(50.0, 80.0), 1),
            "soil_moisture": round(random.uniform(30.0, 70.0), 1),
            "light_intensity": random.randint(200, 900)
        }
    
    def send_data(self):
        """데이터 서버로 전송"""
        try:
            import requests
            data = self.read_sensors()
            response = requests.post(self.server_url, json=data, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ 전송 성공: {data}")
            else:
                print(f"❌ 전송 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ 전송 오류: {e}")
    
    def start_sending(self):
        """데이터 전송 시작"""
        print(f"📡 라즈베리파이 센서 시작: {self.server_url}")
        while True:
            self.send_data()
            time.sleep(10)  # 10초마다 전송

# =============================================================================
# 5. 메인 실행
# =============================================================================

def main():
    """메인 실행 함수"""
    print("🌱 간단 스마트팜 시스템 시작 (템플릿 분리)")
    print("=" * 50)
    
    # 데이터 저장소 생성
    data_store = SimpleDataStore()
    
    # 시뮬레이터 시작 (테스트용)
    simulator = SimpleSimulator(data_store)
    simulator.start()
    
    # 웹 애플리케이션 시작
    web_app = SimpleWebApp(data_store, port=5000)
    
    print("📊 대시보드: http://localhost:5000")
    print("📡 API: http://localhost:5000/api/data")
    print("🔗 라즈베리파이 수신: http://localhost:5000/api/external_data")
    print("=" * 50)
    
    try:
        web_app.start()
    except KeyboardInterrupt:
        print("\n✅ 시스템 종료")

def test_raspberry_pi():
    """라즈베리파이 센서 테스트"""
    print("🧪 라즈베리파이 센서 테스트")
    sensor = RaspberryPiSensor("http://localhost:5000")
    
    try:
        for i in range(5):  # 5번 테스트
            sensor.send_data()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n✅ 테스트 종료")

# =============================================================================
# 6. 프로그램 시작점
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_raspberry_pi()
    else:
        main()

# =============================================================================
# 파일 구조:
# project/
# ├── simple_smart_farm.py    # 메인 실행 파일
# └── templates/
#     └── dashboard.html       # 대시보드 HTML (자동 생성)
#
# 사용 방법:
# 1. python simple_smart_farm.py      # 전체 시스템 실행
# 2. python simple_smart_farm.py test # 라즈베리파이 센서 테스트
# 3. 브라우저에서 http://localhost:5000 접속
# =============================================================================
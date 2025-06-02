import requests
import time
import random

SERVER_URL = "http://localhost:5000"

def send_test_data():
    # 랜덤 센서 데이터 생성
    data = {
        "temperature": round(random.uniform(20.0, 35.0), 1),
        "humidity": round(random.uniform(40.0, 80.0), 1),
        "soil_moisture": random.choice([0, 1]),  # 0: 건조, 1: 촉촉
        "water_pump": random.choice([True, False]),
        "led_status": random.choice(["on", "off"])
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/api/sensor_data", json=data, timeout=3)
        if response.status_code == 200:
            print(f"✅ 테스트 데이터 전송: {data}")
        else:
            print(f"❌ 전송 실패: {response.status_code}")
    except:
        print("❌ 서버 연결 실패")

if __name__ == "__main__":
    print("🧪 테스트 시뮬레이터 시작")
    print("📡 서버로 가짜 센서 데이터 전송 중...")
    
    while True:
        send_test_data()
        time.sleep(5)  # 5초마다 전송
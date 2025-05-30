import requests
import time
import random

class RaspberryPiSensor:
    def __init__(self, server_url="http://192.168.1.100:5000"):  # PC IP 주소
        self.server_url = f"{server_url}/api/external_data"
        
    def read_sensors(self):
        # 실제 GPIO 핀에서 센서 데이터 읽기
        # import RPi.GPIO as GPIO (실제 사용시)
        
        return {
            "temperature": round(random.uniform(20.0, 30.0), 1),
            "humidity": round(random.uniform(50.0, 80.0), 1),
            "soil_moisture": round(random.uniform(30.0, 70.0), 1),
            "light_intensity": random.randint(200, 900),
            "source": "RaspberryPi"
        }
    
    def send_data(self):
        try:
            data = self.read_sensors()
            response = requests.post(self.server_url, json=data, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ 데이터 전송 성공: {data}")
            else:
                print(f"❌ 전송 실패: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 전송 오류: {e}")
    
    def start_sending(self):
        print(f"📡 서버로 데이터 전송 시작: {self.server_url}")
        while True:
            self.send_data()
            time.sleep(10)  # 10초마다 전송

if __name__ == "__main__":
    sensor = RaspberryPiSensor()
    sensor.start_sending()
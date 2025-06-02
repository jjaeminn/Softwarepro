import RPi.GPIO as GPIO
import Adafruit_DHT
import time
import board
import neopixel
import random
import requests  # 추가

# --- 핀 설정 ---
SOIL_SENSOR_PIN = 17       # 토양 수분 센서 (DO)
RELAY_PIN = 27             # 릴레이 (펌프 제어)
DHT_PIN = 4                # 온습도 센서 (DHT11)
LED_PIN = board.D18        # WS2812B LED바 (GPIO18)
LED_COUNT = 8              # 연결된 LED 개수로 수정

# --- 서버 설정 (추가) ---
SERVER_URL = "http://"  # PC IP 주소로 변경

# --- GPIO 초기화 ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(SOIL_SENSOR_PIN, GPIO.IN)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)  # 기본은 펌프 꺼짐

# --- LED 초기화 ---
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, auto_write=True)

# --- 원하는 색상 중에서 랜덤으로 선택 ---
def set_random_led():
    color_list = [
        (255, 255, 0),    # 노란색
        (255, 105, 180),  # 분홍색
        (0, 0, 255),      # 파란색
        (128, 0, 128),    # 보라색
        (255, 0, 0)       # 빨간색
    ]
    for i in range(LED_COUNT):
        pixels[i] = random.choice(color_list)

# --- 서버로 데이터 전송 (추가) ---
def send_to_server(temperature, humidity, soil_dry):
    data = {
        "temperature": temperature,
        "humidity": humidity,
        "soil_moisture": 0 if soil_dry else 1,  # 0: 건조, 1: 촉촉
        "water_pump": not GPIO.input(RELAY_PIN),  # 펌프 상태
        "led_status": "on"
    }
    try:
        requests.post(f"{SERVER_URL}/api/sensor_data", json=data, timeout=3)
        print(f"서버 전송 완료")
    except:
        print("서버 전송 실패")

try:
    while True:
        # 토양 수분 감지
        soil_dry = GPIO.input(SOIL_SENSOR_PIN) == 0
        if soil_dry:
            print("토양이 건조합니다. 펌프 작동 중...")
            GPIO.output(RELAY_PIN, GPIO.LOW)
            time.sleep(5)
            GPIO.output(RELAY_PIN, GPIO.HIGH)
        else:
            print("토양이 촉촉합니다. 펌프 정지 중...")

        # 온습도 출력
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT_PIN)
        if humidity is not None and temperature is not None:
            print(f"현재 온도: {temperature:.1f}°C / 습도: {humidity:.1f}%")
            
            # 서버로 데이터 전송 (추가)
            send_to_server(temperature, humidity, soil_dry)
        else:
            print("온습도 센서 값을 읽을 수 없습니다.")

        # LED 랜덤 색상 설정
        set_random_led()

        time.sleep(2)

except KeyboardInterrupt:
    print("종료합니다.")
    GPIO.cleanup()
import RPi.GPIO as GPIO
import Adafruit_DHT
import time
import board
import neopixel
import random
from flask import Flask, render_template, jsonify, request # request 추가
import threading

# --- 핀 설정 ---
SOIL_SENSOR_PIN = 17
RELAY_PIN = 27
DHT_PIN = 4
LED_PIN = board.D18
LED_COUNT = 8

# --- GPIO 초기화 ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(SOIL_SENSOR_PIN, GPIO.IN)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)

# --- LED 초기화 ---
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, auto_write=False)

# --- Flask 앱 설정 ---
app = Flask(__name__)

# --- 실시간 데이터 저장을 위한 전역 변수 및 Lock ---
current_data = {
    "temperature": None,
    "humidity": None,
    "soil_is_dry": None,
    "pump_status": "정지",
    "auto_water_enabled": True  # 자동 물주기 기능 활성화 상태 (기본값: True)
}
data_lock = threading.Lock()

def set_random_led():
    color_list = [
        (255, 255, 0), (255, 105, 180), (0, 0, 255),
        (128, 0, 128), (255, 0, 0)
    ]
    for i in range(LED_COUNT):
        pixels[i] = random.choice(color_list)
    pixels.show()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data_route():
    with data_lock:
        return jsonify(current_data)

@app.route('/toggle_auto_water', methods=['POST'])
def toggle_auto_water():
    global current_data
    try:
        # 클라이언트로부터 받은 새로운 상태 (true/false 문자열로 올 수 있음)
        new_state_str = request.json.get('enabled')
        if new_state_str is None:
            return jsonify({"status": "error", "message": "Missing 'enabled' parameter"}), 400

        new_state = str(new_state_str).lower() == 'true' # 문자열을 boolean으로 변환

        with data_lock:
            current_data["auto_water_enabled"] = new_state
        print(f"자동 물주기 상태 변경됨: {current_data['auto_water_enabled']}")
        return jsonify({"status": "success", "auto_water_enabled": current_data["auto_water_enabled"]})
    except Exception as e:
        print(f"자동 물주기 상태 변경 중 오류: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def sensor_and_control_loop():
    global current_data
    print("센서 및 제어 루프 시작됨")
    while True:
        try:
            soil_dry = GPIO.input(SOIL_SENSOR_PIN) == 0
            local_pump_status = current_data.get("pump_status", "정지")
            auto_water_active = False
            with data_lock: # 현재 자동 물주기 활성화 상태 읽기
                auto_water_active = current_data.get("auto_water_enabled", True)

            if auto_water_active and soil_dry: # 자동 물주기가 활성화 되어 있고, 토양이 건조할 때만
                print("자동 물주기 활성: 토양이 건조합니다. 펌프 작동 중...")
                local_pump_status = "작동 중 (5초)"
                with data_lock:
                    current_data["soil_is_dry"] = True
                    current_data["pump_status"] = local_pump_status

                GPIO.output(RELAY_PIN, GPIO.LOW)
                time.sleep(5)
                GPIO.output(RELAY_PIN, GPIO.HIGH)
                local_pump_status = "정지 (급수 완료)"
                print("펌프 작동 완료. 5초간 급수.")
            elif not auto_water_active and soil_dry:
                print("자동 물주기 비활성: 토양은 건조하지만, 펌프를 작동하지 않습니다.")
                # 펌프 상태는 이전 상태를 유지하거나, "정지 (수동 모드)" 등으로 변경 가능
                if not local_pump_status == "정지 (급수 완료)": # 급수 직후가 아니라면
                     local_pump_status = "정지 (자동 꺼짐)"
            else: # 토양이 촉촉하거나, 자동 물주기가 비활성화된 경우 (토양 건조하지 않음)
                print("토양이 촉촉하거나 자동 물주기가 비활성 상태입니다. 펌프 정지 중...")
                if not local_pump_status == "정지 (급수 완료)":
                    local_pump_status = "정지"


            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT_PIN)

            with data_lock:
                if humidity is not None and temperature is not None:
                    current_data["temperature"] = round(temperature, 1)
                    current_data["humidity"] = round(humidity, 1)
                else:
                    print("온습도 센서 값을 읽을 수 없습니다.")
                current_data["soil_is_dry"] = soil_dry
                current_data["pump_status"] = local_pump_status
                

            set_random_led()
            time.sleep(2)

        except RuntimeError as error:
            print(f"센서 루프 중 오류 발생: {error.args[0]}")
            time.sleep(2)
            continue
        except Exception as e:
            print(f"예상치 못한 오류 발생: {e}")
            break

if __name__ == '__main__':
    flask_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False),
        daemon=True
    )
    flask_thread.start()
    print("Flask 서버가 http://<라즈베리파이_IP>:5000 에서 실행 중입니다.")
    print("센서 및 제어 루프를 시작합니다. 종료하려면 Ctrl+C를 누르세요.")

    try:
        sensor_and_control_loop()
    except KeyboardInterrupt:
        print("사용자에 의해 프로그램이 종료됩니다...")
    finally:
        print("GPIO 리소스를 정리하고 LED를 끕니다.")
        GPIO.cleanup()
        pixels.fill((0, 0, 0))
        pixels.show()
        print("정리 완료. 프로그램 종료.")

// static/script.js
const autoWaterToggle = document.getElementById('autoWaterToggle');
const growthDaysText = document.getElementById('growth_days_text');
const currentDateText = document.getElementById('current_date_text');
const startDateInput = document.getElementById('startDateInput');
const soilStatusTextElement = document.getElementById('soil_status_text'); // ID가 중복되어 수정
const temperatureElement = document.getElementById('temperature');
const humidityElement = document.getElementById('humidity');
const pumpStatusTextElement = document.getElementById('pump_status_text');


// 로컬 스토리지에서 시작일 불러오기 또는 기본값 설정
let startDateString = localStorage.getItem('ssukssukStartDate') || '2025-06-01'; // 기본 날짜는 적절히 수정하세요.

function updateGrowthAndDateInfo() {
  // 현재 날짜 표시
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0'); // 월은 0부터 시작하므로 +1
  const day = String(today.getDate()).padStart(2, '0');
  if (currentDateText) {
    currentDateText.textContent = `${year}.${month}.${day}`;
  }

  // 성장일 계산
  if (growthDaysText) {
    const startDate = new Date(startDateString);
    if (!isNaN(startDate.getTime())) { // 유효한 날짜인지 확인
      const timeDiff = today.getTime() - startDate.getTime();
      // 성장일이 0일 미만이면 (미래 날짜 선택 시) "시작 전" 또는 다른 메시지 표시 가능
      if (timeDiff < 0) {
        growthDaysText.textContent = `시작 전`;
      } else {
        const daysDiff = Math.floor(timeDiff / (1000 * 60 * 60 * 24)) + 1; // 오늘을 포함하여 +1일
        growthDaysText.textContent = `+ ${daysDiff}일째 쑥쑥 크는중`;
      }
    } else {
      growthDaysText.textContent = `날짜 오류`; // 시작일이 유효하지 않은 경우
    }
  }
  if(startDateInput) startDateInput.value = startDateString; // input 필드에 현재 시작일 표시
}

function updateData() {
  fetch('/data')
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
      }
      return response.json();
    })
    .then(data => {
      if(temperatureElement) temperatureElement.textContent = data.temperature !== null ? data.temperature.toFixed(1) : 'N/A';
      if(humidityElement) humidityElement.textContent = data.humidity !== null ? data.humidity.toFixed(1) : 'N/A';

      // 자동 물주기 토글 상태 업데이트
      if (autoWaterToggle) {
        autoWaterToggle.checked = data.auto_water_enabled === true;
      }

      if (soilStatusTextElement) {
        soilStatusTextElement.textContent = data.soil_is_dry === null ? 'N/A' : (data.soil_is_dry ? '건조함' : '촉촉함');
        soilStatusTextElement.className = data.soil_is_dry === null ? '' : (data.soil_is_dry ? 'dry' : 'moist');
      }

      if (pumpStatusTextElement) {
        pumpStatusTextElement.textContent = data.pump_status || 'N/A';
      }
    })
    .catch(error => {
      console.error('데이터를 가져오는 중 오류 발생:', error);
      if(temperatureElement) temperatureElement.textContent = '오류';
      if(humidityElement) humidityElement.textContent = '오류';
      if(soilStatusTextElement) soilStatusTextElement.textContent = '오류';
      if(pumpStatusTextElement) pumpStatusTextElement.textContent = '오류';
    });
}

// 토글 스위치 변경 이벤트 리스너
if (autoWaterToggle) {
    autoWaterToggle.addEventListener('change', function() {
    const isEnabled = this.checked;
    fetch('/toggle_auto_water', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled: isEnabled }),
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errData => {
                throw new Error(errData.message || 'Server error');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
        console.log('자동 물주기 상태 변경 성공:', data.auto_water_enabled);
        } else {
        console.error('자동 물주기 상태 변경 실패:', data.message);
        this.checked = !isEnabled;
        alert('자동 물주기 상태 변경에 실패했습니다: ' + (data.message || '알 수 없는 오류'));
        }
    })
    .catch(error => {
        console.error('자동 물주기 상태 변경 요청 오류:', error);
        this.checked = !isEnabled;
        alert('자동 물주기 상태 변경 요청 중 오류가 발생했습니다: ' + error.message);
    });
    });
}

// 시작일 변경 이벤트 리스너
if (startDateInput) {
  startDateInput.addEventListener('change', function() {
    startDateString = this.value;
    localStorage.setItem('ssukssukStartDate', startDateString);
    updateGrowthAndDateInfo();
  });
}

// 초기화 함수
function initializePage() {
    updateGrowthAndDateInfo();
    updateData();
    setInterval(updateData, 2000); // 2초마다 센서 데이터 업데이트
}

// DOM이 완전히 로드된 후 스크립트 실행
document.addEventListener('DOMContentLoaded', initializePage);

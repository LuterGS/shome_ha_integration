# sHome Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

**sHome 시스템 (직방 홈 IoT)** 을 Home Assistant에서 제어할 수 있게 해주는 커스텀 통합 구성요소입니다.

## sHome이란?

sHome은 삼성SDS에서 개발한 스마트홈 시스템으로, 주로 한국의 아파트 단지에 설치되어 있습니다. 직방 홈, 래미안 스마트홈 등 다양한 브랜드로 제공되며, 월패드를 통해 조명, 난방, 환기, 에어컨 등을 제어할 수 있습니다.

이 통합 구성요소를 사용하면 Home Assistant에서 sHome 기기들을 제어하고, 자동화를 구성할 수 있습니다.

## 지원 기기

### 완전 지원

| 기기 | Home Assistant 플랫폼 | 지원 기능 |
|------|----------------------|----------|
| **조명** | `light` | 개별 조명 ON/OFF, 방별 일괄 제어, 전체 조명 제어 |
| **에어컨** | `climate` | ON/OFF, 희망 온도 설정 (18-30°C), 현재 온도 표시 |
| **난방** | `climate` | ON/OFF, 희망 온도 설정, 현재 온도 표시 |
| **환기 (전열교환기)** | `fan` | ON/OFF, 3단계 풍량 조절 |
| **환경 센서** | `sensor` | 온도, 습도, CO2, 미세먼지(PM10) |

### 확인되었으나 미구현

| 기기 | 상태 |
|------|------|
| 가스 밸브 | API 확인됨, 구현 예정 |
| 현관 도어센서 | API 확인 필요 |
| 동작 감지 센서 | API 확인 필요 |
| SOS 버튼 | API 확인 필요 |
| 스마트 콘센트 | API 확인 필요 |

## 설치 방법

### HACS를 통한 설치 (권장)

1. HACS > Integrations > 우측 상단 메뉴 > Custom repositories
2. Repository URL에 `https://github.com/lutergs/shome_ha_integration` 입력
3. Category를 `Integration` 선택 후 추가
4. HACS에서 "sHome" 검색 후 설치
5. Home Assistant 재시작

### 수동 설치

1. 이 저장소의 `custom_components/shome_ha_integration` 폴더를 다운로드
2. Home Assistant의 `config/custom_components/` 폴더에 복사
3. Home Assistant 재시작

## 설정 방법

1. Home Assistant 설정 > 기기 및 서비스 > 통합 구성요소 추가
2. "sHome" 검색 후 선택
3. sHome 계정 정보 입력:
   - **사용자명**: sHome 앱에서 사용하는 아이디
   - **비밀번호**: sHome 앱에서 사용하는 비밀번호
   - **기기 ID**: 자동 생성됨 (변경 불필요)
4. 로그인 성공 시 자동으로 기기가 검색됩니다

## 기기별 상세 기능

### 조명 (Light)

- **개별 조명**: 각 조명을 독립적으로 ON/OFF
- **방 조명**: 같은 방의 조명을 일괄 ON/OFF
- **전체 조명**: 모든 조명을 일괄 ON/OFF

> 참고: 밝기 조절 및 색상 변경은 sHome API에서 지원하지 않습니다.

### 에어컨 (Climate)

- 지원 모드: OFF, 냉방(COOL)
- 온도 범위: 18°C ~ 30°C (1도 단위)
- 현재 실내 온도 표시

### 난방 (Climate)

- 지원 모드: OFF, 난방(HEAT)
- 희망 온도 설정
- 현재 바닥 온도 표시

### 환기 (Fan)

- ON/OFF 제어
- 3단계 풍량 조절:
  - 약풍: 33%
  - 중풍: 67%
  - 강풍: 100%

### 환경 센서 (Sensor)

하나의 환경 센서 기기에서 4개의 센서 엔티티가 생성됩니다:
- **온도**: °C 단위
- **습도**: % 단위
- **CO2**: ppm 단위
- **미세먼지 (PM10)**: μg/m³ 단위

센서 데이터는 3분마다 자동으로 업데이트됩니다.

## 자동화 예시

### 실내 CO2 농도가 높으면 환기 켜기

```yaml
automation:
  - alias: "CO2 높으면 환기"
    trigger:
      - platform: numeric_state
        entity_id: sensor.환경센서_co2
        above: 1000
    action:
      - service: fan.turn_on
        target:
          entity_id: fan.전열교환기
        data:
          percentage: 100
```

### 외출 시 전체 조명 끄기

```yaml
automation:
  - alias: "외출 모드"
    trigger:
      - platform: state
        entity_id: input_boolean.away_mode
        to: "on"
    action:
      - service: light.turn_off
        target:
          entity_id: light.전체조명
```

## 문제 해결

### 로그인이 안 되는 경우

1. sHome 앱에서 계정 정보가 올바른지 확인
2. sHome 앱에서 정상 로그인이 되는지 확인
3. Home Assistant 로그에서 에러 메시지 확인:
   - 설정 > 시스템 > 로그 > "shome" 검색

### 기기가 발견되지 않는 경우

1. sHome 앱에서 해당 기기가 정상적으로 표시되는지 확인
2. 통합 구성요소를 제거 후 다시 추가
3. Home Assistant를 재시작

### 기기 상태가 업데이트되지 않는 경우

- 센서: 3분 주기로 자동 업데이트
- 조명/에어컨/난방/환기: 수동 새로고침 또는 제어 시 업데이트

### 기기 다시 읽어오기 시 실패하는 경우

현재 해결중입니다. Home Assistant 를 restart 하면 해결됩니다.

## 알려진 제한 사항

- **클라우드 전용**: sHome API가 클라우드 기반이므로 인터넷 연결이 필요합니다
- **에어컨 모드**: 현재 냉방 모드만 지원합니다 (난방, 제습, 송풍 모드 미지원)
- **조명 밝기**: 밝기 조절이 지원되지 않습니다
- **실시간 업데이트**: Push 알림이 없어 상태 변경 감지가 지연될 수 있습니다

## 기여하기

버그 리포트, 기능 제안, Pull Request를 환영합니다!

- 이슈: [GitHub Issues](https://github.com/lutergs/shome_ha_integration/issues)
- 기여 가이드: Fork 후 Pull Request 제출

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 크레딧

- 개발: [@LuterGS](https://github.com/lutergs)
- sHome API 분석 및 역공학

---

**주의**: 이 프로젝트는 삼성SDS나 직방과 공식적인 관계가 없는 비공식 통합 구성요소입니다.

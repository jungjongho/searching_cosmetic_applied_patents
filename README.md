# 화장품 특허 검색 시스템

한국 특허청 KIPRIS API를 사용하여 화장품 특허를 검색하고 분석하는 시스템입니다.

## 🚀 기능

- **특허 검색**: 키워드와 등록권자 기반 특허 검색
- **상세 정보 추출**: 청구항, IPC 코드, 발명자 정보 추출
- **파일 다운로드**: PDF 전문 다운로드
- **비동기 처리**: 대량 특허 처리를 위한 백그라운드 태스크
- **REST API**: FastAPI 기반 웹 API 제공
- **CLI 인터페이스**: 명령줄에서 직접 실행 가능

## 📁 프로젝트 구조

```
searching_cosmetics_applied_patents/
├── app/
│   ├── api/                    # API 라우터
│   │   ├── __init__.py
│   │   └── patents.py
│   ├── core/                   # 핵심 설정
│   │   ├── __init__.py
│   │   └── config.py
│   ├── models/                 # 데이터 모델
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── services/               # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── kipris_api.py       # KIPRIS API 클라이언트
│   │   ├── patent_processor.py # 특허 처리 로직
│   │   └── task_manager.py     # 태스크 관리
│   ├── __init__.py
│   └── main.py                 # FastAPI 애플리케이션
├── config.json                 # 설정 파일
├── requirements.txt            # 의존성 목록
├── run.py                      # 메인 실행 파일
└── README.md
```

## ⚙️ 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 설정 파일 구성

`config.json` 파일에서 KIPRIS API 서비스 키를 설정하세요:

```json
{
  "api_settings": {
    "service_key": "YOUR_KIPRIS_API_KEY_HERE",
    "base_url": "http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice",
    "timeout": 30
  },
  "search_settings": {
    "search_keyword": "조성물",
    "right_holder": "코스맥스 주식회사",
    "right_holder_code": "120140131250",
    "max_patents_per_search": 20,
    "page_size": 100,
    "delay_between_requests": 1.0
  },
  "output_settings": {
    "output_directory": "patent_results",
    "save_search_results": true,
    "save_claims": true,
    "download_pdfs": true
  },
  "app_settings": {
    "debug": false,
    "host": "0.0.0.0",
    "port": 8000
  }
}
```

## 🎯 사용법

### API 서버 실행

```bash
# 기본 설정으로 실행
python run.py api

# 커스텀 포트로 실행
python run.py api --port 8080

# 디버그 모드로 실행
python run.py api --debug
```

API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

### CLI 모드 실행

```bash
# 기본 설정으로 검색
python run.py cli

# 특정 키워드로 검색
python run.py cli --keyword "조성물" --max-patents 10

# 특정 등록권자로 검색
python run.py cli --right-holder "코스맥스 주식회사" --right-holder-code "120140131250"
```

## 📡 API 엔드포인트

### 특허 검색
- `POST /patents/search`: 특허 검색
- `GET /patents/search/{application_number}`: 특허 상세 정보 조회

### 비동기 처리
- `POST /patents/process`: 특허 처리 작업 시작
- `GET /patents/process/{task_id}/status`: 처리 상태 조회
- `GET /patents/process/{task_id}/result`: 처리 결과 조회

### 기타
- `GET /`: 헬스 체크
- `GET /health`: 헬스 체크
- `GET /settings`: 현재 설정 조회
- `GET /patents/download/pdf/{application_number}`: PDF 다운로드 URL 조회

## 📊 API 사용 예시

### 특허 검색

```bash
curl -X POST "http://localhost:8000/patents/search" \
  -H "Content-Type: application/json" \
  -d '{
    "search_keyword": "조성물",
    "right_holder_code": "120140131250",
    "max_patents": 5
  }'
```

### 비동기 처리 시작

```bash
curl -X POST "http://localhost:8000/patents/process" \
  -H "Content-Type: application/json" \
  -d '{
    "search_keyword": "조성물",
    "max_patents": 10,
    "save_claims": true,
    "download_pdfs": false
  }'
```

### 처리 상태 확인

```bash
curl "http://localhost:8000/patents/process/{task_id}/status"
```

## 📁 출력 파일

처리 결과는 `patent_results/` 디렉토리에 저장됩니다:

```
patent_results/
├── claims/                     # 청구항 텍스트 파일
├── pdf_files/                  # PDF 전문 파일
├── search_results/             # 원본 검색 결과 JSON
└── summary_report_*.txt        # 요약 보고서
```

## 🔧 설정 옵션

### API 설정
- `service_key`: KIPRIS API 서비스 키
- `base_url`: API 기본 URL
- `timeout`: 요청 타임아웃 (초)

### 검색 설정
- `search_keyword`: 기본 검색 키워드
- `right_holder`: 기본 등록권자명
- `right_holder_code`: 기본 등록권자 코드
- `max_patents_per_search`: 검색당 최대 특허 수
- `page_size`: 페이지당 결과 수
- `delay_between_requests`: 요청 간 지연 시간 (초)

### 출력 설정
- `output_directory`: 결과 저장 디렉토리
- `save_search_results`: 검색 결과 저장 여부
- `save_claims`: 청구항 저장 여부
- `download_pdfs`: PDF 다운로드 여부

### 앱 설정
- `debug`: 디버그 모드
- `host`: 서버 호스트
- `port`: 서버 포트

## 🐛 문제 해결

### KIPRIS API 키 없음
```
경고: KIPRIS API 서비스 키가 설정되지 않았습니다.
```
→ `config.json`의 `service_key`를 설정하세요.

### 검색 결과 없음
```
검색된 특허가 없습니다.
```
→ 검색 키워드나 등록권자 정보를 확인하세요.

### API 요청 실패
```
특허 검색 요청 실패: ...
```
→ 네트워크 연결과 API 키를 확인하세요.

## 📝 개발 정보

- **언어**: Python 3.8+
- **프레임워크**: FastAPI
- **API**: KIPRIS (한국특허정보원)
- **비동기 처리**: asyncio
- **데이터 검증**: Pydantic

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

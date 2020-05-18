# todaysstock-redshirt

## 개요

- 매일 정해진 시간에 `주식 종목 정보` 및 `차트(일봉)`를 크롤링하여 S3 리소스 버킷에 해당 데이터(json) 업로드
- 1일치 32개 종목 * 4일치 (1일 전, 10일 전, 20일 전 / 채점기능 위해)
- AWS Lambda 에서 구동
- python 3.7

---

## Lambda 설정

- 제한시간: `15분`, 메모리: `512MB`
- `AWS_ID`, `AWS_SECRT`, `BUCKET` 환경 변수 설정
- 32개 종목 크롤링 소요시간 * 4일치 (메모리 512MB)
  - 약 680000ms `(11분 20초)`

### 외부 라이브러리

- `python.zip` 
  - 외부 라이브러리 압축 해 놓은 것
  - requests, bs4
- Lambda 내 새로운 레이어에 압축파일 업로드
- **python.zip 파일명 유지 필수**

### 트리거

- AWS CloudWatch Events
- 매일 18:30 (UTC 09:30)

---

## S3 업로드

### 키 이름 주의*

- 20200517/
  - today/
    - charts/
      - 20200517_001725_day.png `// 데이터 수집 날짜 기준`
      - ...외 31개 차트
    - 20200517_stock_infos.json
  - ago1/
    - charts/
      - ...today와 동일
    - 20200516_stock_infos.json `// 토너먼트 엔트리된 날짜 기준`
  - ago10/
    - ...
  - ago20/
    - ...
- 20200518/
  - ...

### 데이터 예

```json
// 20200425_stock_infos.json
[
  {
    "name": "티에스이",
    "code": "131290",
    "market": "코스닥",
    "price": {
      "today": "12,200",
      "exday": "12,950",
      "change": "-750",
      "changePercent": "-5.79",
      "high": "12,950",
      "low": "12,200",
      "start": "12,900",
      "volume": "67,304",
      "tradingValue": "835"
    },
    "more": {
      "cap": "1,349",
      "capRank": "407",
      "amountOfListed": "11,061,429",
      "week52high": "17,000",
      "week52low": "6,010",
      "per": "8.34",
      "pbr": "0.76",
      "dividendYield": "1.64",
      "industryPer": "15.69",
      "industryChange": "-1.14"
    }
  },
  ...외 31개 종목,
]
```

# todaysstock-redshirt

## 개요

- 매일 정해진 시간에 32개의 주식 종목 정보를 크롤링하여 S3 리소스 버킷에 해당 데이터(json) 업로드
- AWS Lambda 에서 구동
- python 3.7

---

## Lambda 설정

- 제한시간: `15분`, 메모리: `256MB`
- `AWS_ID`, `AWS_SECRT` 환경 변수 설정
  - S3 접근 위해, 향후 리소스 버킷 퍼블릭 설정 시 제거
- 32개 종목 크롤링 소요시간 (메모리 256MB)
  - 약 370000ms `(6분 10초)`

### 외부 라이브러리

- `python.zip` 
  - 코드 의존성 라이브러리 압축 해 놓은 것
  - requests, bs4
- Lambda 내 새로운 레이어에 압축파일 업로드
- **python.zip 파일명 유지 필수**

---

### S3 업로드 데이터 예

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
	...,
]
```
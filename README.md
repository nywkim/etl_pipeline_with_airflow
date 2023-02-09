# Airflow ETL Pipeline in AWS

##### 상세한 설명은 -> https://nywkim-private.notion.site/Airflow-ETL-Pipeline-0689a13db254447abd89fa57d39317d3
**요약**

- Batch ETL Pipeline + Airflow 관련 개인 프로젝트
- Spotipy API 활용 ~ 용도에 맞게 S3(Data Lake)에 데이터 저장 구성
- 클라우드 서비스(AWS)를 활용하여 데이터 분석 파이프라인 구축

**역할**

- 개인 프로젝트 (기여도 100%)
- Python을 활용하여 Spotify data ETL을 위한 함수 및 스크립트 작성
- ETL 활용을 위한 다양한 오퍼레이터를 Airflow DAG로 구현
- AWS 서비스를 활용한 아키텍쳐 구성

**성과**

- Batch Pipeline을 구축하여 일정 간격 ETL 작업 스케쥴링
- 데이터 흐름의 자동화와 간편해진 모니터링
- Data Lake 및 Data Warehouse 활용으로 적재적소에 데이터 제공 및 분석 용이

**시기**

- 프로젝트 기간 : 2022.12 - 2023.01

![image](https://user-images.githubusercontent.com/86825023/217900645-50487f5d-1e16-4807-902d-d2d70bdfb997.png)

**간단한 내용**

- AWS EC2 내에서 Apache Airflow 활용하여 DAG를 일정 시간마다 스케쥴링
- Spotify API를 활용하여 유저의 데이터를 가져와, ETL Pipeline을 거쳐 Data Lake, DW에 분석 가능한 데이터로 저장

**데이터 설명**

- 본인이 최근 감상한 음악의 MetaData를 추출
    - day, hour : 날짜와 시간
    - track_id, track_name : 음악의 id와 제목
    - artist_id, artist_name : 아티스트의 id와 제목
    - 그 외 향후 ML을 위한 음악의 음악적 특성과 기본 정보가 담긴 수치화된 데이터들
        - 댄서블한, 악기적인, 에너지 등의 특성과 음원의 길이 등
        
**파일 설명 (spotify_dag)**

- spotify_dag_1 : raw data to transform
- spotify_dag_2 : aggregation to load
- spotify_etl, refresh : Python Scripts

**결과**

- ETL 작업 스케쥴링으로 편해진 엔지니어링
- 데이터 흐름의 자동화와 간편해진 모니터링
- Data Lake 및 Data Warehouse 활용으로 적재적소에 데이터 제공 및 분석 용이

**추후 과제**

- 대용량 데이터의 ETL 대비 아키텍쳐 구성
- Sagemaker 등의 활용으로 ML Pipeline 구현
- 컨테이너 환경에 대한 이해 (Docker, k8s 등)
- 직접 구축한 파이프라인 Task에 필요한 Custom Operator 만들기
- 다양한 ETL, 데이터 관리 솔루션 학습

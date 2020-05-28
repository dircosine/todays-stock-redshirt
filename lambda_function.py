import json
import crawler
import boto3
import os
import random
import csv
from io import StringIO
from datetime import datetime, timedelta
import requests

AWS_ID = os.environ['AWS_ID']
AWS_SECRET = os.environ['AWS_SECRET']
BUCKET = os.environ['BUCKET']

s3_client = boto3.client('s3', aws_access_key_id=AWS_ID,
                         aws_secret_access_key=AWS_SECRET)


# NOW = datetime.strptime('20200518', '%Y%m%d')
NOW = datetime.now() + timedelta(days=1)
TODAY = NOW.strftime('%Y%m%d')

N = 32


# before: today | after1 | after3 | after10 | after20
def task_by_date(date, codes, after_string):  # 20200517, , after1
    INFO_FILE = f'{date}/{after_string}/{TODAY}_stock_infos.json'

    daily_info_array = []
    progress_index = 0

    for code in codes:
        progress_index += 1
        if progress_index > N:
            break
        print(progress_index, code)

        try:
            daily_info_array.append(crawler.crawl(code))

            CHART_OUT_FILE = f'{date}/{after_string}/charts/{TODAY}_{code}_day.png'
            CHART_URL = f'https://ssl.pstatic.net/imgfinance/chart/item/candle/day/{code}.png'
            res = requests.get(CHART_URL, stream=True)
            res.raw.decode_content = True
            s3_client.upload_fileobj(res.raw, BUCKET, CHART_OUT_FILE)
            s3_client.put_object_acl(
                ACL='public-read', Bucket=BUCKET, Key=CHART_OUT_FILE)

        except ValueError:
            print('코넥스 상장 종목')
            progress_index -= 1
        except Exception as e:
            print(e)
            progress_index -= 1

    s3_client.put_object(Body=json.dumps(
        daily_info_array, ensure_ascii=False), Bucket=BUCKET, Key=INFO_FILE)
    s3_client.put_object_acl(ACL='public-read', Bucket=BUCKET, Key=INFO_FILE)

    print(f'{after_string} Done!')


def lambda_handler(event, context):

    # *** 오늘 대상 종목
    codes_obj = s3_client.get_object(Bucket=BUCKET, Key='codes-krx.csv')
    codes_body = codes_obj['Body']
    csv_string = codes_body.read().decode('utf-8')
    codes = []
    csv_reader = csv.reader(StringIO(csv_string), delimiter=',')
    for row in csv_reader:
        codes.append(row)
    sample_codes = random.sample(codes[1:], 70)
    todays_codes = list(map(lambda e: e[0], sample_codes))
    task_by_date(TODAY, todays_codes, 'today')

    # *** 과거 대상 종목 (for 채점)
    after_map = {'after1': 1, 'after3': 3, 'after10': 10, 'after20': 20}
    for (key, value) in after_map.items():
        target_date = (NOW - timedelta(days=value)
                       ).strftime('%Y%m%d')  # 현재 시점에서 과거 날짜 디렉터리에 저장 필요하기 때문에 날짜 뺌
        res = requests.get(
            f'https://{BUCKET}.s3.ap-northeast-2.amazonaws.com/{target_date}/today/{target_date}_stock_infos.json')
        if res.status_code == 200:
            info = json.loads(res.text)
            codes = list(map(lambda e: e['code'], info))
            task_by_date(target_date, codes, key)

    print("All Done!")

    requests.get('https://todaysstock.herokuapp.com/update')

    return {
        'statusCode': 200,
        'body': "SUCCESS"
    }

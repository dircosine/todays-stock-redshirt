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

TODAY = datetime.now().strftime('%Y%m%d')

N = 32


# before: today | ago1 | ago10 | ago20
def task_by_date(date, codes, ago):
    INFO_FILE = f'{TODAY}/{ago}/{date}_stock_infos.json'

    daily_info_array = []
    progress_index = 0

    for code in codes:

        progress_index += 1
        if progress_index > N:
            break
        print(progress_index, code)

        try:
            daily_info_array.append(crawler.crawl(code))

            CHART_OUT_FILE = f'{TODAY}/{ago}/charts/{TODAY}_{code}_day.png'
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

    print(f'{ago} Done!')


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
    ago_map = {'ago1': 1, 'ago10': 10, 'ago20': 20}
    for (key, value) in ago_map.items():
        target_date = (datetime.now() - timedelta(days=value)
                       ).strftime('%Y%m%d')
        res = requests.get(
            f'https://{BUCKET}.s3.ap-northeast-2.amazonaws.com/{target_date}/today/{target_date}_stock_info.json')
        if res.status_code == 200:
            info = json.loads(res.text)
            codes = list(map(lambda e: e['code'], info))
            task_by_date(target_date, codes, key)

    print("All Done!")

    return {
        'statusCode': 200,
        'body': "SUCCESS"
    }


if __name__ == "__main__":
    lambda_handler(None, None)

import json
import crawler
import boto3
import os
import random
import csv
from io import StringIO
import datetime

AWS_ID = os.environ['AWS_ID']
AWS_SECRET = os.environ['AWS_SECRET']

CODES_FILE = 'codes-krx.csv'
BUCKET = 'res-todaysstock'
OUTPUT_FILE = datetime.datetime.now().strftime('%Y%m%d') + '_stock_infos.json'

s3_client = boto3.client('s3', aws_access_key_id=AWS_ID,
                         aws_secret_access_key=AWS_SECRET)

N = 32


def lambda_handler(event, context):
    daily_info_array = []
    progress_index = 0

    codes_obj = s3_client.get_object(Bucket=BUCKET, Key='codes-krx.csv')
    codes_body = codes_obj['Body']
    csv_string = codes_body.read().decode('utf-8')

    codes = []
    csv_reader = csv.reader(StringIO(csv_string), delimiter=',')
    for row in csv_reader:
        codes.append(row)

    daily_codes = random.sample(codes[1:], 50)

    for code in daily_codes:
        progress_index += 1
        if progress_index > N:
            break
        print(progress_index, code[0])

        try:
            daily_info_array.append(crawler.crawl(code[0]))
        except ValueError:
            print('코넥스 상장 종목')
            progress_index -= 1
        except Exception as e:
            print(e)
            progress_index -= 1

    s3_client.put_object(Body=json.dumps(
        daily_info_array, ensure_ascii=False), Bucket=BUCKET, Key=OUTPUT_FILE)

    print("Done!")

    return {
        'statusCode': 200,
        'body': "SUCCESS"
    }

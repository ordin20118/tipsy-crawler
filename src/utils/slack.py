import requests
import sys
import os

current_file_path = os.path.abspath(__file__)
pparent = os.path.abspath(os.path.join(current_file_path, '..', '..', '..'))
sys.path.append(pparent)

# 두 단계 상위 디렉토리의 파일 import
from config import SLACK_APP_ID


def send_message(title, content):
  
  # 생성한 웹훅 주소
  hook = 'https://hooks.slack.com/services/%s' % SLACK_APP_ID
  
  # 메시지 전송
  requests.post(
    hook,  
    headers={
      'content-type': 'application/json'
    },
    json={
      'text': title,
      'blocks': [
        {
          'type': 'section',  # 저는 메시지가 묶이지 않도록 section을 주로 사용합니다.
          'text': {
            'type': 'mrkdwn',
            'text': content
          }
        }
      ]
    }
  )
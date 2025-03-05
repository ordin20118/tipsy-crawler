import pymysql

# mariadb연동을 위한 모듈 import


# 컨넥트를 미리 만들어준다.

# 접속할 host, uesr, password, db, 인코딩 입력

#connect = pymysql.connect(host='119.205.221.220:3306', user='alcohol_master', password='rer1625vq',
#                          db='raw_data', charset='utf8')

connect = pymysql.connect(host='119.205.221.220', user='luxuna', password='rer1625vq',
                          db='lux_una', charset='utf8')

# 커서 생성

cur = connect.cursor()

# sql문 실행
sql = "select * from coupon"
cur.execute(sql)

# DB결과를 모두 가져올 때 사용
rows = cur.fetchall()

# 하나의 결과만 가져옴
row=fetchone()

# 한번에 다 출력
print(rows)

# 원하는 행만 출력
print(rows[0])

# for문으로 출력
for row in rows:
    print(row)

# 연결 해제
connect.close()
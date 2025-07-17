#q23-T123153.sql  CSVファイルをテーブルにインポートするプログラム

#レコードを検索するプログラム
from MyDatabase import my_open , my_query , my_close
from werkzeug.security import generate_password_hash, check_password_hash


#Data Source Nameのパラメータを辞書型変数で定義
dsn = {
    'host' : '172.30.0.10',  #ホスト名(IPアドレス)
    'port' : '3306',        #mysqlの接続ポート番号
    'user' : 'root',      #dbアクセスするためのユーザid
    'password' : '1234',    #ユーザidに対応するパスワード
    'database' : 'DB2025' #オープンするデータベース名
}

#userテーブル
dbcon,cur = my_open( **dsn )

import pandas as pd

i=0 #レコードの件数カウント用

my_query("USE DB2025;",cur)

#ファイルオープン
df = pd.read_csv("testdata/basic_info.csv",header=0)

#1行ずつ処理
for ind,rowdata in df.iterrows():

    sqlstring = f"""
        insert into user
        (personal_number,l_name,f_name,affiliation,tell,mail,addr,pass_hash)
        values
        ('{rowdata[0]}','{rowdata[1]}','{rowdata[2]}','{rowdata[3]}','{rowdata[4]}','{rowdata[5]}','{rowdata[6]}','{generate_password_hash(rowdata[7])}')
    """
    my_query(sqlstring,cur)
    i+=1

print(f"./basic_info.csvから{i}レコードを新規挿入しました。")

#テーブルに書き込み
dbcon.commit()

# 行動記録テーブル
i=0 #レコードの件数カウント用

my_query("USE DB2025;",cur)

#ファイルオープン
df = pd.read_csv("testdata/action.csv",header=0)

#1行ずつ処理
for ind,rowdata in df.iterrows():

    sqlstring = f"""
        insert into action_record
        (personal_number,date,start_time,end_time,place,move_method,departure,destination,with_companion,companion_note,remarks)
        values
        ('{rowdata[0]}','{rowdata[1]}','{rowdata[2]}','{rowdata[3]}','{rowdata[4]}','{rowdata[5]}','{rowdata[6]}','{str(rowdata[7])}','{rowdata[8]}','{rowdata[9]}','{rowdata[10]}')
    """
    my_query(sqlstring,cur)
    i+=1

print(f"action.csvから{i}レコードを新規挿入しました。")

#テーブルに書き込み
dbcon.commit()

# 体調記録テーブル
i=0 #レコードの件数カウント用

my_query("USE DB2025;",cur)

#ファイルオープン
df = pd.read_csv("testdata/health.csv",header=0)

#1行ずつ処理
for ind,rowdata in df.iterrows():

    sqlstring = f"""
        insert into health_records
        (personal_number,health_date,health_datetime,temperature,joint_muscle_pain,fatigue,headache,sore_throat,shortness_of_breath,cough_sneeze,nausea_vomiting,abdominal_pain_diarrhea,taste_disorder,smell_disorder)
        values
        ('{rowdata[0]}','{rowdata[1]}','{rowdata[2]}','{rowdata[3]}','{rowdata[4]}','{rowdata[5]}','{rowdata[6]}','{rowdata[7]}','{rowdata[8]}','{rowdata[9]}','{rowdata[10]}','{rowdata[11]}','{rowdata[12]}','{rowdata[13]}')
    """
    my_query(sqlstring,cur)
    i+=1

print(f"./uriage.csvから{i}レコードを新規挿入しました。")

#テーブルに書き込み
dbcon.commit()


# コロナテーブル
i=0 #レコードの件数カウント用

my_query("USE DB2025;",cur)

#ファイルオープン
df = pd.read_csv("testdata/covid.csv",header=0)

#1行ずつ処理
for ind,rowdata in df.iterrows():

    sqlstring = f"""
        insert into Covid
        (personal_number,health_condition,start_date,end_date,medical_insttution,doctor_name)
        values
        ('{rowdata[0]}','{rowdata[1]}','{rowdata[2]}','{rowdata[3]}','{rowdata[4]}','{rowdata[5]}')
    """
    my_query(sqlstring,cur)
    i+=1

print(f"./covid.csvから{i}レコードを新規挿入しました。")

#テーブルに書き込み
dbcon.commit()

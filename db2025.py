#FlaskモジュールでDBの操作
#FlaskモジュールでDBの操作

import pandas as pd
import numpy as np

#Data Source Nameのパラメータを辞書型変数で定義
dsn = {
    'host' : '172.30.0.10',  #ホスト名(IPアドレス)
    'port' : '3306',        #mysqlの接続ポート番号
    'user' : 'root',      #dbアクセスするためのユーザid
    'password' : '1234',    #ユーザidに対応するパスワード
    'database' : 'DB2025' #オープンするデータベース名
}

from flask import Flask
#Flaskのコンストラクタ
app = Flask(__name__ ,static_folder="static")

#ルーティング定義

@app.route('/admin')
def admin():
    #admin.htmlを返す
    return app.send_static_file('admin.html')

@app.route('/admin/todayReport')
def today_report():
    dbcon,cur = my_open( **dsn )
    sqlstring = f"""
        WITH RankedHealthRecords AS (
            SELECT
                *,
                ROW_NUMBER() OVER(PARTITION BY personal_number ORDER BY health_date DESC, health_datetime DESC) as rn
            FROM
                health_records
            )
            SELECT
                health_record_ID,
                personal_number,
                health_date,
                health_datetime,
                temperature,
                joint_muscle_pain,
                fatigue,
                headache,
                sore_throat,
                shortness_of_breath,
                cough_sneeze,
                nausea_vomiting,
                abdominal_pain_diarrhea,
                taste_disorder,
                smell_disorder
            FROM
                RankedHealthRecords
            WHERE
                rn = 1;
    """
    my_query(sqlstring,cur)
    recset = pd.DataFrame(cur.fetchall())
    
    my_close(dbcon,cur)
    
    return render_template( "todayReport.html",
        table_data = recset
    )

#プログラム起動
app.run(host="localhost",port=5000,debug=True)


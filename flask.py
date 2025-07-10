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

##############
#利用者上方修正ページ
##############

from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime

def get_db_connection():
    return mysql.connector.connect(**dsn)

@app.route('/user_update', methods=['GET', 'POST'])
def user_update():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    keyword = ''
    if request.method == 'POST':
        keyword = request.form.get('keyword', '')
        query = """
        SELECT * FROM user
        WHERE personal_number LIKE %s OR l_name LIKE %s OR f_name LIKE %s
        """
        like_keyword = f"%{keyword}%"
        cursor.execute(query, (like_keyword, like_keyword, like_keyword))
    else:
        cursor.execute("SELECT * FROM user")

    users = cursor.fetchall()
    conn.close()
    return render_template('UserUpdate_list.html', users=users, keyword=keyword)

@app.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        data = request.form
        query = """
        UPDATE user SET
            personal_number = %s,
            l_name = %s,
            f_name = %s,
            affiliation = %s,
            tell = %s,
            mail = %s,
            addr = %s,
            lastupdate = NOW()
        WHERE userID = %s
        """
        cursor.execute(query, (
            data['personal_number'], data['l_name'], data['f_name'],
            data['affiliation'], data['tell'], data['mail'], data['addr'],
            user_id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('update_complete'))

    cursor.execute("SELECT * FROM user WHERE userID = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return render_template('UserUpdate_edit.html', user=user)

@app.route('/user/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user SET deleteflag = %s WHERE userID = %s", (True, user_id))
    conn.commit()
    conn.close()
    return redirect(url_for('user_update'))

@app.route('/update_complete')
def update_complete():
    return render_template('UserUpdate_complete.html')



####################
#コロナ報告
####################

@app.route("/report", methods=["GET", "POST"])
def report():  # ← 関数名をエンドポイントと一致
    if request.method == "POST":
        affiliation = request.form.get("affiliation")
        personal_number = request.form.get("personal_number")
        l_name = request.form.get("l_name")
        f_name = request.form.get("f_name")
        health_condition = request.form.get("health_condition")
        medical_insttution = request.form.get("medical_insttution")
        doctor_name = request.form.get("doctor_name")
        end_date_str = request.form.get("end_date")

        if not all([affiliation, personal_number, l_name, f_name, health_condition, end_date_str]):
            return "入力に不備があります", 400

        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            return "終了日の形式が不正です", 400

        cnx = mysql.connector.connect(**dsn)
        cursor = cnx.cursor()

        cursor.execute(
            """
            INSERT INTO Covid 
            (personal_number, health_condition, start_date, end_date, medical_insttution, doctor_name, lastupdate, delflag)
            VALUES (%s, %s, NOW(), %s, %s, %s, NOW(), FALSE)
            """,
            (personal_number, int(health_condition), end_date, medical_insttution, doctor_name),
        )
        cnx.commit()
        cursor.close()
        cnx.close()

        return redirect(url_for("complete"))

    return render_template("covid_report.html")

@app.route("/complete")
def complete():
    return render_template("covid_complete.html")

#プログラム起動
app.run(host="localhost",port=5000,debug=True)


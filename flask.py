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


#############
#行動記録入力
#############
# 行動記録入力ページ（ルートを /action_input に変更）
@app.route('/action_input', methods=['GET', 'POST'])
def action_input():
    if request.method == 'POST':
        data = request.form

        # 固定の個人番号（本来はログイン情報から取得）
        personal_number = '12345678'

        # フォームからの入力値取得
        date_str = data['date']
        start_time = data['startTime']
        end_time = data['endTime']
        place = data['location']
        move_method = data['transportation']
        departure = data['departure']
        destination = data['arrival']
        with_companion = data['companionPresence'] == 'あり'
        companion_note = data['companionDetails']
        remarks = data['notes']

        # 日付・時刻の結合と現在時刻取得
        date = datetime.strptime(date_str, '%Y-%m-%d')
        start_datetime = datetime.strptime(f"{date_str} {start_time}", '%Y-%m-%d %H:%M')
        end_datetime = datetime.strptime(f"{date_str} {end_time}", '%Y-%m-%d %H:%M')
        now = datetime.now()

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # 行動記録テーブルにINSERT
            sql = """
                INSERT INTO action_record (
                    personal_number, date, start_time, end_time, place, move_method,
                    departure, destination, with_companion, companion_note,
                    remarks, lastupdate, delflag
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE)
            """
            values = (
                personal_number, date, start_datetime, end_datetime, place,
                move_method, departure, destination, with_companion,
                companion_note, remarks, now
            )
            cursor.execute(sql, values)

            # userテーブルのlastupdateを更新
            update_sql = "UPDATE user SET lastupdate = %s WHERE personal_number = %s"
            cursor.execute(update_sql, (now, personal_number))

            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for('action_done'))

        except Exception as e:
            return f"エラーが発生しました: {e}"

    return render_template('action_input.html')

# 完了ページ
@app.route('/action_done')
def action_done():
    return render_template('action_done.html')


#############
#体調観察入力
#############
@app.route('/condition_input', methods=['GET', 'POST'])
def condition_input():
    if request.method == 'POST':
        # フォームデータ取得
        personal_number = request.form['studentId']
        health_date = request.form['date']
        health_datetime = 1 if request.form['timeOfDay'] == 'pm' else 0
        temperature = float(request.form['temperature'])

        # 症状（チェック有無をBooleanとして取得）
        symptoms = {
            'joint_muscle_pain': 'symptom_jointMusclePain' in request.form,
            'fatigue': 'symptom_fatigue' in request.form,
            'headache': 'symptom_headache' in request.form,
            'sore_throat': 'symptom_soreThroat' in request.form,
            'shortness_of_breath': 'symptom_shortnessOfBreath' in request.form,
            'cough_sneeze': 'symptom_coughSneeze' in request.form,
            'nausea_vomiting': 'symptom_nauseaVomiting' in request.form,
            'abdominal_pain_diarrhea': 'symptom_abdominalDiarrhea' in request.form,
            'taste_disorder': 'symptom_tasteDisorder' in request.form,
            'smell_disorder': 'symptom_smellDisorder' in request.form,
        }

        # DBに挿入
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_sql = """
            INSERT INTO health_records (
                personal_number, health_date, health_datetime, temperature,
                joint_muscle_pain, fatigue, headache, sore_throat,
                shortness_of_breath, cough_sneeze, nausea_vomiting,
                abdominal_pain_diarrhea, taste_disorder, smell_disorder
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            personal_number, health_date, health_datetime, temperature,
            symptoms['joint_muscle_pain'], symptoms['fatigue'], symptoms['headache'],
            symptoms['sore_throat'], symptoms['shortness_of_breath'], symptoms['cough_sneeze'],
            symptoms['nausea_vomiting'], symptoms['abdominal_pain_diarrhea'],
            symptoms['taste_disorder'], symptoms['smell_disorder']
        )
        cursor.execute(insert_sql, values)
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('condition_done'))

    return render_template('condition_input.html')

@app.route('/condition_done')
def condition_done():
    return render_template('condition_done.html')



#プログラム起動
app.run(host="localhost",port=5000,debug=True)


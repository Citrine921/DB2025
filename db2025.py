#FlaskモジュールでDBの操作
#FlaskモジュールでDBの操作

import pandas as pd
import numpy as np
import os
from MyDatabase import my_open, my_query , my_close
from werkzeug.security import generate_password_hash, check_password_hash

#Data Source Nameのパラメータを辞書型変数で定義
dsn = {
    'host' : '172.30.0.10',  #ホスト名(IPアドレス)
    'port' : '3306',        #mysqlの接続ポート番号
    'user' : 'root',      #dbアクセスするためのユーザid
    'password' : '1234',    #ユーザidに対応するパスワード
    'database' : 'DB2025' #オープンするデータベース名
}

from flask import Flask,render_template ,request,session,url_for,flash,redirect
#Flaskのコンストラクタ
app = Flask(__name__ ,static_folder="static")

# セッション管理用の暗号化・署名に必要な秘密鍵を設定
app.config['SECRET_KEY'] = os.urandom(10)
# セッションの有効期限の設定（とりあえず5分）
app.config['PERMANENT_SESSION_LIFETIME'] = 300

#ルーティング定義

#基礎ページ 
@app.route("/")
def login1():
    # セッションにユーザー名が保存されていれば、ログイン済みとしてトップページにとばす
    if 'personal_number' in session:

        dbcon,cur = my_open(**dsn)

        #データベースの選択
        my_query("use DB2025;",cur)

        #sql文
        sqlstring = f"""
            select personal_number, l_name, f_name
            from user
            ;
        """

        my_query(sqlstring,cur)
        user_data = cur.fetchall()

        personal_number = session['personal_number']
        return f"ようこそ、{personal_number}さん  <a href=\"{url_for('top')}\">トップページへ</a> | <a href=\"{url_for('logout')}\">ログアウト</a>"
    # セッションにユーザー名が保存されていなければログインページにとばす
    return render_template("login.html")
  
#トップページ
@app.route('/top')
def top():
    # セッションにログイン情報があるか確認
    if 'logged_in' in session and session['logged_in']:
        user_number = session['personal_number']
        return f"トップ: こんにちは、{user_number}さん！<br><a href=\"{url_for('logout')}\">ログアウト</a>"
    else:
        # ログインしていない場合はログインページへリダイレクト
        flash('ログインしてください。', 'info')
        return redirect(url_for('login1'))


# ログインページ
@app.route("/login", methods=['GET','POST'])
def login():
    # 入力された個人番号とパスワードの受け取り
    personal_number = request.form['P_num']
    password = request.form['pass']
    
    dbcon,cur = my_open(**dsn)

    #データベースの選択
    my_query("use DB2025;",cur)

    #sql文
    sqlstring = f"""
        select personal_number, l_name, f_name, pass_hash
        from user
        ;
    """

    my_query(sqlstring,cur)
    user_data = cur.fetchall()

    for i in user_data:
        if i['personal_number'] == personal_number:
            if check_password_hash(i['pass_hash'],password):
                #認証成功 :　セッションに個人番号とログインフラグを保存
                    session['personal_number'] = personal_number
                    session['logged_in'] = True
                    return redirect(url_for('top'))
            else:
                print(check_password_hash(generate_password_hash("a"),'a'))
                print(i['pass_hash'])
                flash('パスワードが間違っています','error')
                return render_template('login.html')
                 
        
    #認証失敗    
    flash ('個人番号が間違っています。','error') # エラーメッセージ
    return render_template('login.html')

@app.route("/sign_up_page")
def sign_up_page():
    return render_template('sign_up.html')

#新規登録
@app.route("/sign_up", methods=['POST'])
def sign_up():
    # 入力された情報の受け取り
    personal_number = request.form['P_num']
    l_name = request.form['l_name']
    f_name = request.form['f_name']
    affiliation = request.form['affiliation']
    tell = request.form['tell']
    mail = request.form['mail']
    addr = request.form['addr']
    pass_hash = generate_password_hash(request.form['pass'])

    dbcon,cur = my_open(**dsn)
    print("debug1")
    print(cur)
    #データベースの選択
    my_query("use DB2025;",cur)

    # #sql文
    # sqlstring = f"""
    #     select *
    #     from user
    #     where personal_number = '{personal_number}'
    #     ;
    # """
    # print(sqlstring)
    # my_query(sqlstring,cur)
    # print("debug")
    # print(cur) #for debug
    # if(cur == None):

    #sql文
    sqlstring = f"""
        insert into user(personal_number,l_name,f_name,affiliation,tell,mail,addr,pass_hash)
        values('{personal_number}','{l_name}','{f_name}','{affiliation}','{tell}','{mail}','{addr}','{pass_hash}')
        ;
    """
    my_query(sqlstring,cur)
    #dbに書き込み
    dbcon.commit()
    #dbクローズ
    my_close(dbcon,cur)
    flash('登録が完了しました','info')
    return render_template('sign_up.html')

    # else:
    #     flash('個人番号がすでに登録されています。','error')
    #     return render_template('sign_up.html')
    
#ログアウト
@app.route("/logout")
def logout():
    #セッションからユーザー情報を削除
    session.pop('personal_number', None)
    session.pop('logged_in', None)
    flash('ログアウトしました。','info')
    return redirect(url_for('login1'))

#アドミン
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
    
    return render_template( "adomin_today_report.html",
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
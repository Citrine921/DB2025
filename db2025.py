#FlaskモジュールでDBの操作
#FlaskモジュールでDBの操作

import pandas as pd
import numpy as np
import os
from functools import wraps
from datetime import timedelta
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
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

"""
ログインを要求するデコレータ関数
セッションがない場合ユーザーをログインページにリダイレクトする
"""
def check_session(f):
    @wraps(f)
    def check(*args, **kwargs):
            # セッションにログイン情報があるか確認
        if 'logged_in' not in session or not session['logged_in']:
            # ログインしていない場合はログインページへリダイレクト
            flash('ログインしてください。', 'info')
            return redirect(url_for('login1'))
        
        # 管理者ページ用：一般ユーザーがアクセスした際にログインページに飛ばす
        if f.__name__.startswith('admin'):
            if not session['personal_number'].startswith('U'):
                flash('権限が必要です管理者のアカウントでログインして下さい','info')
                return redirect(url_for('login1'))
            
        # セッションの延長
        session.permanent = True
        return f(*args, **kwargs)
    return check

#ルーティング定義

#基礎ページ 
@app.route("/")
def login1():
    # ログインページにとばす
    return render_template("login.html")
  
#トップページ
@app.route('/top')
@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
def top():
    return render_template("top.html")

# ログインページ
@app.route("/login", methods=['GET','POST'])
def login():
    # 入力された個人番号とパスワードの受け取り
    personal_number = request.form['P_num']
    password = request.form['pass']
    
    dbcon,cur = my_open(**dsn)

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
                flash('パスワードが間違っています','error')
                return render_template('login.html')
                 
        
    #認証失敗    
    flash ('個人番号が間違っています。','error')
    return render_template('login.html')

# 新規登録用のページにとばす用
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

    #入力された個人番号がすでに登録されているかどうか判定する
    #sql文
    sqlstring = f"""
        select personal_number
        from user
        where personal_number = '{personal_number}'
        ;
    """

    my_query(sqlstring,cur)
    recset = cur.fetchall()

    if recset:
        flash('個人番号がすでに登録されています','error')
        return render_template('sign_up.html')
    
    #管理者を表す個人番号が入力された場合
    if personal_number.startswith('U'):
        flash('Uで始まる個人番号は管理者用のため設定できません','error')
        return render_template('sign_up.html')


    #個人番号が登録されていなかった場合insertを行う
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
    
#ログアウト
@app.route("/logout")
def logout():
    #セッションからユーザー情報を削除
    session.pop('personal_number', None)
    session.pop('logged_in', None)
    flash('ログアウトしました。','info')
    return redirect(url_for('login1'))

#パスワードを忘れたとき用のページに飛ばす
@app.route("/forget_pass")
def forget_pass():
    return render_template('forget_pass.html')

#パスワードを忘れたとき用
@app.route("/forget_pass2", methods=['POST'])
def forget_pass2():

    # ユーザーの入力内容の受け取り
    personal_number = request.form['P_num']
    l_name = request.form['l_name']
    f_name = request.form['f_name']
    affiliation = request.form['affiliation']
    tell = request.form['tell']
    mail = request.form['mail']
    addr = request.form['addr']

    # データベースに接続
    dbcon,cur = my_open(**dsn)

    #入力された個人番号がすでに登録されているかどうか判定する
    #sql文
    sqlstring = f"""
        select personal_number
        from user
        where personal_number = '{personal_number}'
        ;
    """

    my_query(sqlstring,cur)
    user_data = cur.fetchall()

    if user_data:
        #入力された個人番号に登録されているデータを持ってくる
        #sql文
        sqlstring = f"""
            select personal_number, l_name, f_name, affiliation, tell, mail, addr
            from user
            where personal_number = "{personal_number}"
            ;
        """

        my_query(sqlstring,cur)
        user_data = cur.fetchall()

        #ユーザーが入力した内容が登録されている内容とあっているかどうか確認
        if l_name == user_data[0]['l_name'] and f_name == user_data[0]['f_name'] and affiliation == user_data[0]['affiliation'] and tell == user_data[0]['tell'] and  mail == user_data[0]['mail'] and addr == user_data[0]['addr']:
            #認証成功：セッションを与えてパスワード変更画面に飛ばす
            session['personal_number'] = personal_number
            session['logged_in'] = True
            return render_template('change_pass2.html')

        #認証失敗：入力画面に戻す
        flash('入力内容に誤りがあります','error')
        return render_template('forget_pass.html')
    
    #入力された個人番号がデータベースになかった場合
    flash('この個人番号はまだ登録されていません','error')
    return render_template('forget_pass.html')


# パスワード変更ページに飛ばすよう
@app.route("/change_pass")
@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
def change_pass():
    return render_template('change_pass.html')

#パスワード変更ページ
@app.route('/change_pass2', methods=['POST'])
@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
def change_pass2():
        
        input_pass = request.form['pass']
        
        # データベースに接続して現在のパスワードを持ってくる
        dbcon,cur = my_open(**dsn)

        #sql文
        sqlstring = f"""
            select pass_hash
            from user
            where personal_number = "{session['personal_number']}"
            ;
        """

        my_query(sqlstring,cur)
        user_data = cur.fetchall()

        if check_password_hash(user_data[0]['pass_hash'],input_pass):
            #パスワード一致：新しいパスワードを入力するページに飛ばす
            return render_template('change_pass2.html')
        flash('パスワードが間違っています','error')
        return render_template('change_pass.html')

#パスワードの変更を反映させるページ
@app.route('/change_pass3', methods=['POST'])
@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
def change_pass3():

    input_pass = request.form['pass_input']
    check_pass = request.form['pass_check']

    if input_pass == check_pass:
        # データベースに接続して新しいパスワードを上書き
        dbcon,cur = my_open(**dsn)
        #パスワードをハッシュ化
        pass_hash = generate_password_hash(input_pass)

        #sql文
        sqlstring = f"""
            update user
            set pass_hash = "{pass_hash}"
            where personal_number = "{session['personal_number']}"
            ;
        """

        my_query(sqlstring,cur)
        #dbに書き込み
        dbcon.commit()
        #dbクローズ
        my_close(dbcon,cur)

        #更新が終わったらログアウトのページに飛ばす
        flash('パスワードの更新が完了しました','info')
        return redirect(url_for('logout'))
    
    #パスワードの入力欄と確認欄の入力が一致しない場合、もとのページに戻す
    flash('入力欄と確認欄に入力されたパスワードが異なっています','error')
    return render_template('change_pass2.html')


#アドミン
@app.route('/admin')
@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
def admin():
    #admin.htmlを返す
    return render_template('admin.html')

@app.route('/admin_today_report')
@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
def today_report():
    dbcon, cur = None, None  # 接続情報とカーソルを初期化
    try:
        dbcon, cur = my_open(**dsn)
        
        # ▼▼▼ 修正点: SQLクエリをMySQL 8.0未満のバージョンに対応させました ▼▼▼
        # WITH句とROW_NUMBER()関数を、ユーザー定義変数を使ったサブクエリに置き換えます。
        # これにより、古いMySQLバージョンでも同じ結果を得ることができます。
        sqlstring = """
            SELECT
                t.health_record_ID,
                t.personal_number,
                t.health_date,
                t.health_datetime,
                t.temperature,
                t.joint_muscle_pain,
                t.fatigue,
                t.headache,
                t.sore_throat,
                t.shortness_of_breath,
                t.cough_sneeze,
                t.nausea_vomiting,
                t.abdominal_pain_diarrhea,
                t.taste_disorder,
                t.smell_disorder
            FROM (
                SELECT
                    hr.*,
                    @row_num := IF(@current_person = hr.personal_number, @row_num + 1, 1) AS rn,
                    @current_person := hr.personal_number
                FROM
                    health_records hr,
                    (SELECT @row_num := 0, @current_person := '') AS vars
                ORDER BY
                    hr.personal_number, hr.health_date DESC, hr.health_datetime DESC
            ) AS t
            WHERE
                t.rn = 1;
        """
        my_query(sqlstring, cur)
        
        # cur.descriptionからカラム名を取得します。
        columns = [desc[0].lower() for desc in cur.description]
        
        # カラム名付きでDataFrameを作成します。
        recset = pd.DataFrame(cur.fetchall(), columns=columns)
        
        # health_date列を日付型に変換します。
        if not recset.empty and 'health_date' in recset.columns:
            recset['health_date'] = pd.to_datetime(recset['health_date'])

    except Exception as e:
        # エラー内容をコンソールに出力します。
        print(f"クエリ実行でエラー発生: {e}")
        # エラー時でもページが表示されるように、空のDataFrameを渡します。
        recset = pd.DataFrame()
        
    finally:
        # データベース接続を閉じます。
        if dbcon and cur:
            my_close(dbcon, cur)
    
    # テンプレートにDataFrameを渡してレンダリング
    return render_template("admin_today_report.html",
                           table_data=recset)

@app.route('/admin_report')
@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
def admin_report_index():
    """
    登録されている利用者の一覧を表示するためのルート。
    データベースから重複を除いたpersonal_numberを取得し、テンプレートに渡します。
    """
    # 実際の環境に合わせてデータベース接続処理を記述してください
    # dbcon, cur = my_open(dsn)
    # sqlstring = "SELECT DISTINCT personal_number FROM health_records ORDER BY personal_number;"
    # my_query(sqlstring, cur)
    # result = cur.fetchall()
    # my_close(dbcon, cur)
    
    # --- 以下はダミーデータです。実際には上記のDB処理の結果を使用してください ---
    # result は [(1001,), (1002,), (1003,)] のようなタプルのリストを想定
    result = [(f"100{i}",) for i in range(1, 6)] 
    # --------------------------------------------------------------------

    # テンプレートで扱いやすいように、タプルのリストから数値のリストに変換
    personal_numbers = [item[0] for item in result]
    
    return render_template("admin_report_index.html",
                           personal_numbers=personal_numbers)


@app.route('/admin_report/<personal_number>')
@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
def admin_report_detail(personal_number):
    """
    指定された利用者の過去の健康記録をすべて表示するためのルート。
    """
    # 実際の環境に合わせてデータベース接続処理を記述してください
    # dbcon, cur = my_open(dsn)
    # # SQLインジェクション対策のため、プレースホルダを使用することが望ましい
    # sqlstring = f"""
    #     SELECT * FROM health_records 
    #     WHERE personal_number = '{personal_number}' 
    #     ORDER BY health_date DESC, health_datetime DESC;
    # """
    # my_query(sqlstring, cur)
    # recset = pd.DataFrame(cur.fetchall())
    # my_close(dbcon, cur)

    # --- 以下はダミーデータです。実際には上記のDB処理の結果(DataFrame)を使用してください ---
    import random
    from datetime import datetime, timedelta
    if personal_number: # ダミーデータ生成
        data = []
        today = datetime.now()
        for i in range(random.randint(5, 15)):
            date = today - timedelta(days=i*random.randint(1,3))
            data.append({
                'health_record_ID': 200 + i,
                'personal_number': personal_number,
                'health_date': date,
                'health_datetime': date,
                'temperature': round(random.uniform(36.0, 38.0), 1),
                'joint_muscle_pain': random.choice([0, 1]),
                'fatigue': random.choice([0, 1]),
                'headache': random.choice([0, 1]),
                'sore_throat': random.choice([0, 1]),
                'shortness_of_breath': random.choice([0, 1]),
                'cough_sneeze': random.choice([0,1]),
                'nausea_vomiting': random.choice([0, 1]),
                'abdominal_pain_diarrhea': random.choice([0, 1]),
                'taste_disorder': random.choice([0, 1]),
                'smell_disorder': random.choice([0, 1]),
            })
        recset = pd.DataFrame(data)
    else:
        recset = pd.DataFrame()
    # --------------------------------------------------------------------

    return render_template("admin_report_detail.html",
                           table_data=recset,
                           personal_number=personal_number)
    
@app.route('/admin/inactive_users')
@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
def inactive_users():
    """
    過去3日間にデータの提出がない利用者をリストアップして表示する。
    """
    # 3日前の日付を計算
    three_days_ago = datetime.now() - timedelta(days=3)
    three_days_ago_str = three_days_ago.strftime('%Y-%m-%d')

    # 実際の環境に合わせてデータベース接続処理を記述してください
    # dbcon, cur = my_open(dsn)
    # # 各利用者の最終提出日を取得し、それが3日前より古い利用者を選択するSQL
    # # データベースの種類によって日付の比較方法が異なる場合があるため注意
    # sqlstring = f"""
    #     SELECT
    #         personal_number,
    #         MAX(health_date) AS last_submission_date
    #     FROM
    #         health_records
    #     GROUP BY
    #         personal_number
    #     HAVING
    #         MAX(health_date) < '{three_days_ago_str}';
    # """
    # my_query(sqlstring, cur)
    # result = cur.fetchall() # 結果は [(personal_number, last_date), ...] の形式を想定
    # my_close(dbcon, cur)

    # --- 以下はダミーデータです。実際には上記のDB処理の結果を使用してください ---
    # 全ユーザーのダミーデータを作成
    all_users_dummy_data = []
    today = datetime.now()
    users = [f"100{i}" for i in range(1, 8)]
    # 1001, 1002, 1003 は最近提出している
    all_users_dummy_data.append({'personal_number': users[0], 'health_date': today - timedelta(days=1)})
    all_users_dummy_data.append({'personal_number': users[1], 'health_date': today - timedelta(days=2)})
    all_users_dummy_data.append({'personal_number': users[2], 'health_date': today - timedelta(days=0)})
    # 1004, 1005, 1006 は3日以上前に提出
    all_users_dummy_data.append({'personal_number': users[3], 'health_date': today - timedelta(days=4)})
    all_users_dummy_data.append({'personal_number': users[4], 'health_date': today - timedelta(days=10)})
    all_users_dummy_data.append({'personal_number': users[5], 'health_date': today - timedelta(days=5)})
    # 1007は古いデータのみ
    all_users_dummy_data.append({'personal_number': users[6], 'health_date': today - timedelta(days=30)})
    
    df = pd.DataFrame(all_users_dummy_data)
    df['health_date'] = pd.to_datetime(df['health_date'])

    # 各ユーザーの最終提出日を計算
    last_submissions = df.groupby('personal_number')['health_date'].max().reset_index()
    
    # 最終提出日が3日前より古いユーザーをフィルタリング
    inactive_df = last_submissions[last_submissions['health_date'] < pd.to_datetime(three_days_ago_str)]
    
    # テンプレートに渡すために辞書のリストに変換
    inactive_list = inactive_df.rename(columns={'health_date': 'last_submission_date'}).to_dict('records')
    # --------------------------------------------------------------------

    return render_template("admin_inactive_users.html",
                           inactive_users=inactive_list)


##############
#利用者情報修正ページ
##############

from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime

from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
from functools import wraps

app.secret_key = '00000000'  # セッションで必要

# DB接続
import mysql.connector

# dsnはメインコードで定義済みとして、
# もし別ファイルであればインポートもしくはコピーしてください

def get_db_connection():
    return mysql.connector.connect(
        host=dsn['host'],
        port=int(dsn['port']),
        user=dsn['user'],
        password=dsn['password'],
        database=dsn['database'],
        charset='utf8'
    )


@app.route('/user_update', methods=['GET', 'POST'])
@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
def user_update():
    personal_number = session.get('personal_number')
    if not personal_number:
        return redirect(url_for('login1'))

    dbcon, cur = my_open(**dsn)
    try:
        cur.execute("""
            SELECT userID, l_name, f_name, affiliation, tell, mail, addr, personal_number, lastupdate
            FROM user
            WHERE personal_number = %s
        """, (personal_number,))
        users = cur.fetchall()
    except Exception as e:
        flash(f"データ取得エラー: {e}", "error")
        users = []
    finally:
        my_close(dbcon, cur)

    return render_template('UserUpdate_list.html', users=users)


@app.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])

@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
def edit_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    personal_number = session.get('personal_number')

    if request.method == 'POST':
        try:
            # フォームから編集内容を取得
            l_name = request.form['l_name']
            f_name = request.form['f_name']
            affiliation = request.form['affiliation']
            tell = request.form.get('tell', '')
            mail = request.form.get('mail', '')
            addr = request.form.get('addr', '')

            # 更新SQL（lastupdateをNOW()で更新）
            cursor.execute("""
                UPDATE user SET
                    l_name = %s,
                    f_name = %s,
                    affiliation = %s,
                    tell = %s,
                    mail = %s,
                    addr = %s,
                    lastupdate = NOW()
                WHERE userID = %s AND personal_number = %s
            """, (l_name, f_name, affiliation, tell, mail, addr, user_id, personal_number))

            conn.commit()
            flash("更新しました。")
            return redirect(url_for('user_update'))

        except Exception as e:
            flash(f"更新に失敗しました: {e}")
            conn.rollback()

        finally:
            conn.close()

    else:
        # GET時は対象ユーザー情報を取得（personal_number, lastupdateも含む）
        cursor.execute("""
            SELECT userID, l_name, f_name, affiliation, tell, mail, addr, personal_number, lastupdate
            FROM user
            WHERE userID = %s AND personal_number = %s
        """, (user_id, personal_number))
        user = cursor.fetchone()
        conn.close()

        if not user:
            flash("不正なアクセスです。")
            return redirect(url_for('user_update'))

        return render_template('UserUpdate_edit.html', user=user)


# 削除処理
@app.route('/user/delete/<int:user_id>', methods=['POST'])

@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    personal_number = session.get('personal_number')

    cursor.execute("DELETE FROM user WHERE userID = %s AND personal_number = %s", (user_id, personal_number))
    conn.commit()
    conn.close()

    return redirect(url_for('user_update'))

# 更新完了ページ
@app.route('/update_complete')
@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
def update_complete():
    return render_template('UserUpdate_complete.html')



####################
#コロナ報告
####################
@app.route('/covid_report', methods=['GET', 'POST'])
@check_session
def covid_report():
    personal_number = session.get('personal_number')
    
    # DBからユーザー情報を取得
    user_info = {
        'affiliation': '',
        'student_id': '',
        'last_name': '',
        'first_name': ''
    }

    dbcon, cur = my_open(**dsn)
    try:
        cur.execute("SELECT affiliation, personal_number, l_name, f_name FROM user WHERE personal_number = %s", (personal_number,))
        row = cur.fetchone()
        if row:
            user_info['affiliation'] = row['affiliation'] or ''
            user_info['student_id'] = row['personal_number'] or ''
            user_info['last_name'] = row['l_name'] or ''
            user_info['first_name'] = row['f_name'] or ''
    except Exception as e:
        flash(f"ユーザー情報の取得エラー: {e}", 'error')
    finally:
        my_close(dbcon, cur)
        
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

    if request.method == 'POST':
        affiliation = request.form.get('affiliation')
        student_id = request.form.get('student_id')
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        health_status = request.form.get('health_status')
        medical_institution = request.form.get('medical_institution')
        doctor_name = request.form.get('doctor_name')
        end_date = request.form.get('end_date')

        # 必要ならここでDB登録などの処理を書く

        flash('コロナ報告フォームを送信しました。', 'info')
        # ここを完了ページにリダイレクトに変更
        return redirect(url_for('complete'))  # ↓

    return render_template('covid_report.html', user=user_info)

@app.route("/complete")
@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
def complete():
    return render_template("covid_complete.html")

#############
#行動記録入力
#############
# 行動記録入力ページ（ルートを /action_input に変更）
@app.route('/action_input', methods=['GET', 'POST'])
@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
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
@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
def action_done():
    return render_template('action_done.html')


#############
#体調観察入力
#############
@app.route('/condition_input', methods=['GET', 'POST'])
@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
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
@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
def condition_done():
    return render_template('condition_done.html')



#プログラム起動
app.run(host="localhost",port=5000,debug=True)
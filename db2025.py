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
        # セッションの延長
        session.permanent = True
        return f(*args, **kwargs)
    return check

#ルーティング定義
@app.route("/")
def login1():
    # セッションにユーザー名が保存されていれば、ログイン済みとしてトップページにとばす
    if 'personal_number' in session:

        dbcon,cur = my_open(**dsn)

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
@check_session #セッションの確認・延長用の関数(ログインが必要なページには全てつける)
def top():
    return f"トップ: こんにちは、{session['personal_number']}さん！<br><a href=\"{url_for('logout')}\">ログアウト</a>"


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
                print(check_password_hash(generate_password_hash("a"),'a'))
                print(i['pass_hash'])
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
    print(sqlstring) #for debug
    my_query(sqlstring,cur)
    recset = cur.fetchall()
    print("debug")
    print(recset) #for debug

    if recset:
        flash('個人番号がすでに登録されています','error')
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

#プログラム起動
app.run(host="localhost",port=5000,debug=True)


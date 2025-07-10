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
@app.route("/")
def login1():
    # セッションにユーザー名が保存されていれば、ログイン済みとしてトップページにとばす
    if 'user_id' in session:

        dbcon,cur = my_open(**dsn)

        #sql文
        sqlstring = f"""
            select personal_number, l_name, f_name
            from user
            ;
        """

        my_query(sqlstring,cur)
        user_data = cur.fetchall()

        user_id = session['user_id']
        f_name = user_data.get(user_id,{}).get('f_name')
        l_name = user_data.get(user_id,{}).get('l_name')
        return f"ようこそ、{f_name}{l_name}さん  <a href=\"{url_for('/top')}\">トップページへ</a> | <a href=\"{url_for('/logout')}\">ログアウト</a>"
    # セッションにユーザー名が保存されていなければログインページにとばす
    return render_template("login.html")

# ログインページ
@app.route("/login", methods=['POST'])
def login2():
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
            if check_password_hash(password,i['pass_hash']):
                #認証成功 :　セッションに個人番号とログインフラグを保存
                    session['personal_number'] = personal_number
                    session['logged_in'] = True
                    flash('ログインしました。')
                    return redirect(url_for('top'))
            else:
                 
            
    #認証失敗    
    flash ('個人番号が間違っています。','error') # エラーメッセージ
    return render_template('login.html')

#新規登録
@app.route("sign_up", methods=['POST'])
def sign_up():
    # 入力された情報の受け取り
    personal_number = request.form['P_num']
    l_name = request.form['l_name']
    f_name = request.form['f_name']
    affiliation = request.form['affiliation']
    tell = request.form['tell']
    mail = request.form['mail']
    addr = request.form['addr']
    pass_hash = generate_password_hash(request.form['password'])

    dbcon,cur = my_open(**dsn)

    #sql文
    sqlstring = f"""
        insert into user(personal_number,l_name,f_name,affiliation,tell,mail,addr,pass_hash)
        values('{personal_number}','{l_name}','{f_name}','{affiliation}','{tell}','{mail}','{addr}','{pass_hash}','{personal_number}',)
        ;
    """


#ログアウト
@app.route("/logout")
def logout():
    #セッションからユーザー情報を削除
    session.pop('personal_number', None)
    session.pop('logged_in', None)
    flash.pop('ログアウトしました。')
    return redirect(url_for('/'))

#プログラム起動
app.run(host="localhost",port=5000,debug=True)


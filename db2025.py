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


#プログラム起動
app.run(host="localhost",port=5000,debug=True)


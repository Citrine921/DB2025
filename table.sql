-- ＜テーブル作成用sql＞

-- データベースの作成と選択
create database if not exists DB2025;
use DB2025;

-- テーブルが既に存在しているなら削除する
drop table if exists user;

-- ユーザーテーブル作成
create table user(
    userID int not null AUTO_INCREMENT,
    personal_number varchar(20) not null,
    l_name varchar(20) not null,
    f_name varchar(20) not null,
    affiliation varchar(20) not null,
    tell varchar(20),
    mail varchar(20),
    addr varchar(50),
    lastupdate datetime default NOW(),
    deleteflag boolean default False,
    primary key(userID)
);
-- 体調記録テーブル作成

-- 行動記録テーブル作成

-- コロナテーブル作成

-- 作成したテーブルの確認
desc user;
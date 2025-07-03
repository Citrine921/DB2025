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
CREATE TABLE DB2025.health_records (
    health_record_ID INT AUTO_INCREMENT PRIMARY KEY,
    personal_number TEXT NOT NULL,
    date DATE NOT NULL,
    datetime BOOLEAN NOT NULL,
    temperature FLOAT NOT NULL,
    joint_muscle_pain BOOLEAN NOT NULL DEFAULT 0,
    fatigue BOOLEAN NOT NULL DEFAULT 0,
    headache BOOLEAN NOT NULL DEFAULT 0,
    sore_throat BOOLEAN NOT NULL DEFAULT 0,
    shortness_of_breath BOOLEAN NOT NULL DEFAULT 0,
    cough_sneeze BOOLEAN NOT NULL DEFAULT 0,
    nausea_vomiting BOOLEAN NOT NULL DEFAULT 0,
    abdominal_pain_diarrhea BOOLEAN NOT NULL DEFAULT 0,
    taste_disorder BOOLEAN NOT NULL DEFAULT 0,
    smell_disorder BOOLEAN NOT NULL DEFAULT 0
);
-- 行動記録テーブル作成

-- コロナテーブル作成

--DROP TABLE if EXISTS Covid;
CREATE TABLE Covid (
    covid_ID INT NOT NULL AUTO_INCREMENT,
    personal_number INT NOT NULL, 
    condition INT NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    medical_insttution VARCHAR(30),
    doctor_name VARCHAR(20),
    lastupdate DATETIME,
    delflag BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (covid_ID),
    FOREIGN KEY (personal_number) 
		REFERENCES user(personal_number)
		ON DELETE cascade
		ON UPDATE cascade
);

--DESC Covid ;
--SELECT *
--FROM Covid;

-- 作成したテーブルの確認
desc user;
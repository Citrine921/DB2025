-- ＜テーブル作成用sql＞

-- データベースの作成と選択
create database if not exists DB2025;
use DB2025;

-- テーブルが既に存在しているなら削除する
drop table if exists health_records;
drop table if exists action_record;
drop table if exists Covid;
drop table if exists user;

-- ユーザーテーブル作成
create table user(
    userID int not null AUTO_INCREMENT,
    personal_number varchar(20) not null unique,
    l_name varchar(20) not null,
    f_name varchar(20) not null,
    affiliation varchar(20) not null,
    tell varchar(20) not null,
    mail varchar(50) not null,
    addr varchar(50) not null,
    pass_hash varchar(200) not null,
    lastupdate datetime default NOW(),
    delflag boolean default False,
    primary key(userID)
);
-- 体調記録テーブル作成
CREATE TABLE health_records (
    health_record_ID INT AUTO_INCREMENT PRIMARY KEY,
    personal_number varchar(20) NOT NULL,
    health_date DATE NOT NULL,
    health_datetime BOOLEAN NOT NULL,
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
    smell_disorder BOOLEAN NOT NULL DEFAULT 0,
    lastupdate datetime default NOW(),
    delflag boolean default False,
    FOREIGN KEY (personal_number)
        REFERENCES user(personal_number)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
-- 行動記録テーブル作成
CREATE TABLE action_record (
    action_recordID INT AUTO_INCREMENT PRIMARY KEY, 
    personal_number VARCHAR(20),                    
    date DATETIME,                                  
    start_time time NOT NULL,                   
    end_time time NOT NULL,                     
    place VARCHAR(30),                              
    move_method VARCHAR(50),                        
    departure VARCHAR(100),                        
    destination VARCHAR(100),                       
    with_companion BOOLEAN DEFAULT FALSE,           
    companion_note TEXT,                            
    remarks TEXT,                                    
    lastupdate DATETIME default NOW(),                            
    delflag BOOLEAN DEFAULT FALSE,                  
    FOREIGN KEY (personal_number) REFERENCES user(personal_number)
);
-- コロナテーブル作成
CREATE TABLE Covid (
    covid_ID INT NOT NULL AUTO_INCREMENT,
    personal_number varchar(20) not null, 
    health_condition INT NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    medical_insttution VARCHAR(30),
    doctor_name VARCHAR(20),
    lastupdate DATETIME default NOW(),
    delflag BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (covid_ID),
    FOREIGN KEY (personal_number) 
		REFERENCES user(personal_number)
		ON DELETE cascade
		ON UPDATE cascade
);

-- 作成したテーブルの確認

DESC health_records;
DESC action_record;
DESC Covid ;
DESC user;
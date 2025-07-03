-- ＜テーブル作成用sql＞

-- データベースの作成と選択

-- テーブルが既に存在しているなら削除する

-- ユーザーテーブル作成

-- 体調記録テーブル作成

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

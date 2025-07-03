-- ＜テーブル作成用sql＞

-- データベースの作成と選択

-- テーブルが既に存在しているなら削除する

-- ユーザーテーブル作成

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

-- 作成したテーブルの確認

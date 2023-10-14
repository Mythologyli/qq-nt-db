# 清理接收到文件（包括图片、视频）
import os
import sqlite3

TENCENT_FILES_PATH = "C:\\Users\\Myth\\Documents\\Tencent Files"
CUTOFF_TIMESTAMP = 1696095424  # 截止时间戳。此时间之前的文件会被清理。单位为秒

conn = sqlite3.connect("data/decrypted_db/files_in_chat.db")
cur = conn.cursor()

cur.execute(
    f"""SELECT "45403"
FROM files_in_chat_table
WHERE "45403" <> 0
AND "40021" = ''
AND "40050" <> 0
AND "40050" < {CUTOFF_TIMESTAMP};"""
)

print("以下文件正在被清理：")

for col in cur:
    file_path = TENCENT_FILES_PATH + col[0]
    print(file_path)
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass

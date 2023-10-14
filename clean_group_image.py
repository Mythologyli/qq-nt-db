# 清理群文件中的图片
import os
import sqlite3

import blackboxprotobuf

WHITE_LIST_MODE = True  # 白名单模式，除了列表中的群，其他群都清理；设置为 False 则为黑名单模式，只有列表中的群才会被清理
GROUP_LIST = []  # 群号列表。整数
CUTOFF_TIMESTAMP = 1696095424  # 截止时间戳。此时间之前的文件会被清理。单位为秒

conn = sqlite3.connect("data/decrypted_db/nt_msg.db")
cur = conn.cursor()

if WHITE_LIST_MODE:
    cur.execute(
        f"""SELECT "40800"
FROM group_msg_table
WHERE "40050" <> 0
AND "40050" < {CUTOFF_TIMESTAMP}
AND "40021" NOT IN ('{"','".join(map(str, GROUP_LIST))}')
ORDER BY "40050" DESC;"""
    )
else:
    cur.execute(
        f"""SELECT "40800"
FROM group_msg_table
WHERE "40050" <> 0
AND "40050" < {CUTOFF_TIMESTAMP}
AND "40021" IN ('{"','".join(map(str, GROUP_LIST))}')
ORDER BY "40050" DESC;"""
    )

print("以下文件正在被清理：")

for col in cur:
    try:
        value, _ = blackboxprotobuf.decode_message(col[0])
        if "45812" in value["40800"]:
            print(value["40800"]["45812"])
            try:
                os.remove(value["40800"]["45812"])
            except FileNotFoundError:
                pass
    except TypeError:
        pass

# QQ NT Windows 数据库解密+图片/文件清理

笔者测试时使用的 QQ 版本：9.9.3-17412

经验证的 QQ 版本：9.9.3-17749 9.9.12-26339

## 找到数据库 `passphrase`

1. 使用 IDA Pro 打开 `C:\Program Files\Tencent\QQNT\resources\app\versions\9.9.3-17412\wrapper.node`。打开 Strings 视图，搜索 `sqlite3_key_v2`

    ![](docs/1.png)

2. 跳转到主视图，再跳转到引用该字符串的位置

    ![](docs/2.png)

    ![](docs/3.png)

3. 按下 F5 反编译此函数

    ![](docs/4.png)

    参考[文档](https://www.zetetic.net/sqlcipher/sqlcipher-api/#sqlite3_key)可知 `sqlite3_key_v2` 的参数为：

    ```c
    int sqlite3_key_v2(
        sqlite3 *db,                   /* Database to be keyed */
        const char *zDbName,           /* Name of the database */
        const void *pKey, int nKey     /* The key */
    );
    ```
   
    可以猜测 a3 为我们所需的 `passphrase`。打上断点

4. 退出 QQ 并重新打开，但不要登录。使用 IDA Debug 的 Attach to Process 功能，附加到 QQ 进程。之后登录，可以看到断点被命中

    ![](docs/5.png)

    打开一个 Locals 视图(调试器视图->本地变量)查看参数的值

5. 命中后，跳转到 a3 对应的位置，直到看到如下图所示的 16 位字符串。`#8xxxxxxxxxxx@uJ` 即为我们需要的 `passphrase` (不一定是这个格式，但总字符数是一样的)

    ![](docs/6.png)

## 导出/修复数据库

数据库位置：`C:\Users\<USERNAME>\Documents\Tencent Files\<QQ>\nt_qq\nt_db`

你需要的是 .db 格式的文件。

首先，每个数据库文件头部有 1024 个字符的无用内容，去除这部分内容：

+ Windows
    ```bash
    type nt_msg.db | more +1025 > nt_msg.clean.db
    ```

+ UNIX
    ```bash
    cat nt_msg.db | tail -c +1025 > nt_msg.clean.db
    ```

此时文件已经可以通过 DB Browser for SQLCipher 直接查看，注意迭代次数填写 4000。

下面解释直接解密数据库的方法。

考虑到在 Windows 上编译 sqlcipher 较为困难，笔者使用了 MSYS2 环境并直接安装了`mingw-w64-x86_64-sqlcipher`

笔者处理了 `nt_msg.db`、`files_in_chat.db` 两个文件，并将处理后的文件移动到 `data/clean_db`

根据 sqlcipher 的文档，解密数据的流程为：

1. 打开数据库

    ```bash
    $ sqlcipher
    sqlite> .open nt_msg.clean.db
    ```
   
2. 输入 `passphrase`

    ```bash
    sqlite> PRAGMA key = '#8xxxxxxxxxxx@uJ'; PRAGMA kdf_iter = '4000';
    ```

3. 导出无加密的数据库

    ```bash
    sqlite> ATTACH DATABASE 'nt_msg.db' AS plaintext KEY ''; SELECT sqlcipher_export('plaintext'); DETACH DATABASE plaintext;
    sqlite> .exit 
    ```

不过，很有可能在导出时提示数据库损坏 `Runtime error: database disk image is malformed`。此时需要对数据库进行修复：

```bash
sqlite> .output nt_msg.sql
sqlite> .dump
sqlite> .exit
```

之后对得到的 `nt_msg.sql` 进行处理，并使用 `sqlite3` 生成无加密的数据库

```bash
$ cat nt_msg.sql | sed -e 's|^ROLLBACK;\( -- due to errors\)*$|COMMIT;|g' | sqlite3 nt_msg.db
```
将解密后的数据库移动到 `data/decrypted_db`

## 图片/文件清理

下图是 `nt_msg.db` 中的表：

![](docs/7.png)

注意 `c2c/group_msg_table` 中的 `40800`（消息内容）是 Protobuf 二进制。笔者暂时没有弄明白每个字段的意义

图片/文件清理可以参考仓库中的两个 Python 脚本

## 致谢

[QQBackup/qq-win-db-key](https://github.com/QQBackup/qq-win-db-key)

[https://lengyue.me/2023/09/19/ntqq-db/](https://lengyue.me/2023/09/19/ntqq-db/)

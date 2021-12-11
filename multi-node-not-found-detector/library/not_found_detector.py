#!/usr/bin/python
# -*- coding: utf-8 -*-

# Pythonのバージョンに応じて上記パスは変更すること
# pip install paramiko が必要
# テスト環境は Python 2.7.17

import paramiko
from ansible.module_utils.basic import *

def main():
    # モジュールの定義
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(required=True),
            host=dict(required=True, type=list),
            username=dict(required=True),
            password=dict(required=True))
    )
    args = module.params

    # 変数の読み込み
    path = args.get('path')
    host = args.get('host')
    username = args.get('username')
    password = args.get('password')

    # 存在しないファイル数のカウント変数生成
    count_not_found = 0

    # 以下の各ホストに対して実行するコマンド
    cmd = 'test -f {} ; echo $?'.format(path)

    # 事後処理コマンド(一時ファイルの削除)
    cmd_post = 'rm {}'.format(path)

    # 各ホストに対して一時ファイル(not_found.log)が存在するか確認し、ある場合は上記カウント変数に加算
    for h in host:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.WarningPolicy())
        client.connect(h, username=username, password=password)
        stdin, stdout, stderr = client.exec_command(cmd)
        buf = int(stdout.read())
        if buf == 0:
            count_not_found += 1
        # 事後処理
        stdin, stdout, stderr = client.exec_command(cmd_post)
        client.close()
        del client, stdin, stdout, stderr
    
    # 判定：全ノードに該当ファイルがない場合はfailして終了
    if count_not_found >= len(host):
        module.fail_json(msg="The log file was not found on all nodes.", path=path, count=count_not_found, changed=False)
    else:
        module.exit_json(msg="OK", path=path, count=count_not_found, changed=True)


if __name__ == '__main__':
    main()
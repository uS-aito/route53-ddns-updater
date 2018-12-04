# coding: utf-8
import urllib.request, urllib.error, urllib.parse
import json
import sys
import time
import os
import socket
import route53updater

# 前回実行時までのIP保存ファイルパス
LAST_IP_FILE_PATH = "./last_ip"
# ログファイルパス
LOG_FILE_PATH = "./ddns-update.log"
# 現在のGIPを確認するURL
CURRENT_ADDR_CHECK_URL = "https://ieserver.net/ipcheck.shtml"
# DDNSのレコードを更新するURL
DDNS_UPDATE_URL = "https://ieserver.net/cgi-bin/dip.cgi?username={subdomain}&domain={domain}&password={password}&updatehost=1"

# 更新するRoute53のドメイン名
DOMAIN = "vlsys.net."

# Slackのwebhook url
WEBHOOK_URL = "https://hooks.slack.com/services/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"
# Slackのチャンネル名
CHANNEL_NAME = "ip_checker"
# 投稿時のユーザ名
USERNAME = "ip_checker"
# 投稿時のアイコンURL
ICON_URL = ""
# 投稿時の絵文字
ICON_EMOJI = ":speech_balloon:"


# ファイルから前回実行時までのIPアドレスを取得
##　取得失敗したら終了
# try:
#     with open(LAST_IP_FILE_PATH, "r") as f:
#         last_ip = f.read().replace(os.linesep,"")
# except IOError:
#     if not os.path.exists(LAST_IP_FILE_PATH):
#         with open(LAST_IP_FILE_PATH,"w") as f:
#             pass
#         with open(LOG_FILE_PATH, "a") as f:
#             f.write("{t}: last ip file does not exist. creating it.".format(
#                 t=time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())))
#             f.write(os.linesep)
#         last_ip = ""
#     else:
#         with open(LOG_FILE_PATH, "a") as f:
#             f.write("{t}: cannot read last ip file.".format(
#                 t=time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())))
#             f.write(os.linesep)
#         sys.exit(-1)

# 要するに現在DOMAINに登録されているIPアドレスを確認したい
# ieServerはそういうAPIが無いのでファイルに出力していた
# Route53はあるのでそっちから引っ張ったほうが良い?

last_ip = socket.gethostbyname("{domain}".format(domain=DOMAIN))

# 現在のGIPをチェック
## 取得できてなかったら何もしないで終了
### sys.exit(-1)
try:
    current_ip = urllib.request.urlopen(CURRENT_ADDR_CHECK_URL).read().decode("utf-8")
except urllib.error.URLError:
    try:
        current_ip = urllib.request.urlopen(CURRENT_ADDR_CHECK_URL.replace(
            "https", "http")).read().decode("utf-8")
    except:
        with open(LOG_FILE_PATH, "a") as f:
            f.write("{t}: cannot check current ip (using http).".format(
                t=time.strftime("%Y/%m/%d %H:%M:%S",time.localtime())))
            f.write(os.linesep)
        sys.exit(-1)    
except:
    with open(LOG_FILE_PATH, "a") as f:
        f.write("{t}: cannot check current ip.".format(
            t=time.strftime("%Y/%m/%d %H:%M:%S",time.localtime())))
        f.write(os.linesep)
    sys.exit(-1)    


# GIPが変わっていたら、Route53のレコードをアップデート
if last_ip != current_ip:
    try:
        # レコードアップデート
        r53u.update_a_record(domain=DOMAIN, addr=current_ip)
    except:
        # 例外発生
        with open(LOG_FILE_PATH, "a") as f:
            f.write("{t}: Any error occured.".format(
                t=time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())))
            f.write(os.linesep)
            import traceback
            f.write(traceback.format_exc())
        sys.exit(-1)
    else:
        # 正常終了時のログ出力
        with open(LAST_IP_FILE_PATH,"w") as f:
            f.write(current_ip)
        with open(LOG_FILE_PATH, "a") as f:
            f.write("{t}: {domain} updated {lastip} to {currentip}.".format(
                t=time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()),
                domain=DOMAIN,
                lastip=last_ip,
                currentip=current_ip))
            f.write(os.linesep)


# 現在のIPとドメイン名を引いた時のIPが異なっている場合、Slackに現在のIPを通知
resolved_ip = socket.gethostbyname("{domain}".format(domain=DOMAIN))
if not resolved_ip == current_ip:
    content = {
        "icon_emoji": ICON_EMOJI,
        "icon_url": ICON_URL,
        "channel": CHANNEL_NAME,
        "text": "Current ip address is {address}".format(address=current_ip),
        "username": USERNAME
    }
    content = json.dumps(content)
    header = {
        "Content-Type": "application/json"
    }
    req = urllib.request.Request(WEBHOOK_URL, data=content.encode("utf-8"), headers=header)
    res = urllib.request.urlopen(req).read()
    print(res)
# coding: utf-8
import urllib.request, urllib.error, urllib.parse
import json
import sys
import time
import os
import socket
import route53updater

# スクリプトのパス
DIR = os.path.dirname(os.path.abspath(__file__))
# 現在のGIPを確認するURL
CURRENT_ADDR_CHECK_URL = "https://httpbin.org/ip"

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


# 要するに現在DOMAINに登録されているIPアドレスを確認したい
# ieServerはそういうAPIが無いのでファイルに出力していた
# Route53はあるのでそっちから引っ張ったほうが良い?
r53u = route53updater.Route53Updater()
records = r53u.list_resource_record_set(domain=DOMAIN)
# vlsys.netのAレコードがなかったら変なので終わり
for r in records:
    if r["Name"] == DOMAIN:
        break
else:
    print("{t}: Invalid A records: {records}".format(
        t=time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())),
        records=records
    )
    sys.exit(-1)    
last_ip = records[0]["ResourceRecords"][0]["Value"]


# 現在のGIPをチェック
## 取得できてなかったら何もしないで終了
### sys.exit(-1)
try:
    resp =  urllib.request.urlopen(CURRENT_ADDR_CHECK_URL).read().decode("utf-8")
    current_ip = json.loads(resp)["origin"]
except urllib.error.URLError:
    try:
        resp = urllib.request.urlopen(CURRENT_ADDR_CHECK_URL.replace(
            "https", "http")).read().decode("utf-8")
        current_ip = json.loads(resp)["origin"]
    except:
        print(
            "{t}: cannot check current ip (using http).".format(
            t=time.strftime("%Y/%m/%d %H:%M:%S",time.localtime()))
        )
        sys.exit(-1)    
except:
    print("{t}: cannot check current ip.".format(
        t=time.strftime("%Y/%m/%d %H:%M:%S",time.localtime()))
    )
    sys.exit(-1)    


# GIPが変わっていたら、Route53のレコードをアップデート
if last_ip != current_ip:
    try:
        # レコードアップデート
        r53u.update_a_record(domain=DOMAIN, addr=current_ip)
    except:
        # 例外発生
        print(
            "{t}: Any error occured.".format(
            t=time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))
        )
        import traceback
        traceback.print_exc()
        sys.exit(-1)
    else:
        # 正常終了時のログ出力
        print(
            "{t}: {domain} updated {lastip} to {currentip}.".format(
            t=time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()),
            domain=DOMAIN,
            lastip=last_ip,
            currentip=current_ip)
        )
else:
    print(
        "{t}: {domain} is already updated. Nothing to do.".format(
            t=time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()),
            domain=DOMAIN
        )
    )

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
else:
    print(
        "{t}: {domain} is resolved the latest record. Nothing to notify.".format(
            t=time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()),
            domain=DOMAIN
        )
    )

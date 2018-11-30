# coding: utf-8
import urllib2
import sys
import time
import os
import urlparse
import socket

# 前回実行時までのIP保存ファイルパス
LAST_IP_FILE_PATH = "./last_ip"
# ログファイルパス
LOG_FILE_PATH = "./ddns-update.log"
# 現在のGIPを確認するURL
CURRENT_ADDR_CHECK_URL = "https://ieserver.net/ipcheck.shtml"
# DDNSのレコードを更新するURL
DDNS_UPDATE_URL = "https://ieserver.net/cgi-bin/dip.cgi?username={subdomain}&domain={domain}&password={password}&updatehost=1"

# ieServerで取得したサブドメイン(アカウント名)
SUBDOMAIN = "vlmail"
# ieServerで選択したサブドメイン
DOMAIN = "dip.jp"
# ieServerのパスワード(環境変数から取得)
PASSWORD = ""

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
try:
    with open(LAST_IP_FILE_PATH, "r") as f:
        last_ip = f.read().replace(os.linesep,"")
except IOError:
    # ログにエラーの出力くらいしとこう
    with open(LOG_FILE_PATH, "a") as f:
        f.write("{t}: cannot read last ip file.".format(
            t=time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())))
        f.write(os.linesep)
    sys.exit(-1)


# 環境変数からパスワードを取得
## 失敗したら終了
try:
    PASSWORD = os.environ["DDNS_PASS"]
except KeyError:
    with open(LOG_FILE_PATH, "a") as f:
        f.write("{t}: cannot read DDNS_PASS.".format(
            t=time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())))
        f.write(os.linesep)
    sys.exit(-1)    


# 現在のGIPをチェック
## 取得できてなかったら何もしないで終了
### sys.exit(-1)
try:
    current_ip = urllib2.urlopen(CURRENT_ADDR_CHECK_URL).read()
except urllib2.URLError:
    try:
        current_ip = urllib2.urlopen(CURRENT_ADDR_CHECK_URL.replace(
            "https", "http")).read()
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

# GIPが変わっていたら、DDNSのレコードをアップデート
## 元のperl見てるとここでGIP取得確認してるけど、先にやったので不要
### DDNSのレコード更新用URLにリクエスト投げる
### レスポンスが現在のGIPと同じなら更新成功、異なっていたら更新失敗
if last_ip != current_ip:

    res = urllib2.urlopen(DDNS_UPDATE_URL.format(
        subdomain=SUBDOMAIN, domain=DOMAIN, password=PASSWORD)).read()
    
    if current_ip in res:
        with open(LAST_IP_FILE_PATH,"w") as f:
            f.write(current_ip)
        with open(LOG_FILE_PATH, "a") as f:
            f.write("{t}: {subdomain}.{domain} updated {lastip} to {currentip}.".format(
                t=time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()),
                subdomain=SUBDOMAIN,
                domain=DOMAIN,
                lastip=last_ip,
                currentip=current_ip))
            f.write(os.linesep)
    else:
        with open(LOG_FILE_PATH, "a") as f:
            f.write("{t}: update aborted.".format(
                t=time.strftime("%Y/%m/%d %H:%M:%S",time.localtime())))
            f.write(os.linesep)


# 現在のIPとドメイン名を引いた時のIPが異なっている場合、Slackに現在のIPを通知
resolved_ip = socket.gethostbyname("{subdomain}.{domain}".format(subdomain=SUBDOMAIN, domain=DOMAIN))
if not resolved_ip == current_ip:
    content = {
        "icon_emoji": ICON_EMOJI,
        "icon_url": ICON_URL,
        "channel": CHANNEL_NAME,
        "text": "Current ip address is {address}".format(address=current_ip),
        "username": USERNAME
    }
    header = {
        "Content-Type": "application/json"
    }
    res = urllib2.urlopen(WEBHOOK_URL).read()
    print res
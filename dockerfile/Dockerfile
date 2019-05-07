# 元となるイメージ
FROM python:3.6
# コメント
MAINTAINER yu.saito h2so40627@gmail.com

# 日本時間化(変更不可)
ENV TZ='Asia/Tokyo'

# ディレクトリ移動
WORKDIR /root

# gitに必要なものをコピー
RUN mkdir .ssh && chmod 700 .ssh
COPY ./container_send_files/gitlab-home .ssh/gitlab-home
COPY ./container_send_files/config .ssh/config
RUN chmod 600 .ssh/*

# cron実行に必要なファイルをコピー
COPY ./container_send_files/modify-cronfile.py ./modify-cronfile.py

# コンテナ実行時に必要なファイルをコピー
COPY ./container_send_files/runserver.sh ./runserver.sh
RUN chmod +x ./runserver.sh

# リポジトリ取得
RUN ssh-keyscan -t rsa -p 27292 192.168.0.251 >> .ssh/known_hosts
RUN git clone git@vlsys.net:yusaito/ieServer-ddns-updater.git

# リポジトリに移動
WORKDIR /root/ieServer-ddns-updater

# パッケージインストール
RUN pip install -r requirements.txt

# cron系インストール
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install -y cron vim rsyslog less

# rsyslog起動
RUN service rsyslog start

# 必要なファイルを送信
ADD ./container_send_files/ddns-updater /etc/cron.d/ddns-updater
RUN chmod 644 /etc/cron.d/ddns-updater

# cronが起動するよう設定を修正
RUN sed -i 's/.*pam_loginuid\.so/#&/g' /etc/pam.d/cron 

# コンテナ起動時に実行するコマンド
CMD /root/runserver.sh
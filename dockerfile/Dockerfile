# 元となるイメージ
FROM python:3.6.8-alpine3.9
# コメント
LABEL MAINTAINER="yu saito <h2so40627@gmail.com>"

# 日本時間化(変更不可)
ENV TZ='Asia/Tokyo'

# ディレクトリ移動
WORKDIR /root

# スクリプトをコピー
COPY ./scripts/ ./

# パッケージインストール
RUN pip install -r requirements.txt

# コンテナ起動時に実行するコマンド
CMD ["python","/root/ddns-updater.py"]
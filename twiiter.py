from datetime import datetime
import time
import tweepy
from config import CONFIG


class Twitter_Module:
    auth = tweepy.OAuthHandler(CONFIG["consumer_key"], CONFIG["consumer_secret"])
    auth.set_access_token(CONFIG["access_token_key"], CONFIG["access_token_secret"])
    api = tweepy.API(auth)

    # ツイートの送信
    def post_tweet(self):
        self.api.update_status("テストです")

    # プロフィール設定
    def post_profile(self):
        self.api.update_profile(name="API Developer", location="America", description="run test api now")

    # 予約
    @staticmethod
    def cal_datetime(y, m, d, h, mt):
        today = datetime(y, m, d, h, mt) - datetime.now()
        schedule_do = int(today.total_seconds())
        time.sleep(schedule_do)


TwitterClass = Twitter_Module()
TwitterClass.post_tweet()

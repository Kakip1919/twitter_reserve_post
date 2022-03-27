from datetime import datetime
import time
import tweepy
from config import CONFIG
from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.accounts'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)


class Accounts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(32), nullable=False, unique=True)
    consumer_key = db.Column(db.String(128), nullable=False)
    consumer_secret_key = db.Column(db.String(128), nullable=False)


class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(32), nullable=False)
    contents = db.Column(db.String(1028), nullable=False)
    reserved = db.Column(db.DateTime(), nullable=False)
    y = db.Column(db.Integer(), nullable=False)
    m = db.Column(db.Integer(), nullable=False)
    d = db.Column(db.Integer(), nullable=False)
    h = db.Column(db.Integer(), nullable=False)
    mt = db.Column(db.Integer(), nullable=False)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(32), nullable=False)
    url = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(128), nullable=False)


class Twitter_Module:
    auth = tweepy.OAuthHandler(CONFIG["consumer_key"], CONFIG["consumer_secret"])
    auth.set_access_token(CONFIG["access_token_key"], CONFIG["access_token_secret"])
    api = tweepy.API(auth)

    # ツイートの送信
    def post_tweet(self, contents):
        self.api.update_status(contents)

    # プロフィール設定
    def post_profile(self,name,location,description):
        self.api.update_profile(name=name, location=location, description=description)

    # 予約
    @staticmethod
    def cal_datetime(y, m, d, h, mt):
        today = datetime(y, m, d, h, mt) - datetime.now()
        schedule_do = int(today.total_seconds())
        time.sleep(schedule_do)


@app.before_first_request
def init():
    db.create_all()


@app.route("/", methods=["POST", "GET"])
def home():
    return render_template("home.html")


@app.route("/account")
def account():
    account_data = Accounts.query.all()
    return render_template("account/index.html", data=account_data)


@app.route("/account/create")
def account_create():
    return render_template("account/create.html")


@app.route("/account/store", methods=["POST"])
def account_store():
    account_name = request.form['account_name']
    consumer_key = request.form["consumer"]
    consumer_secret_key = request.form["consumer_secret"]
    insert = Accounts(account_name=account_name, consumer_key=consumer_key, consumer_secret_key=consumer_secret_key)
    db.session.add(insert)
    db.session.commit()
    return redirect("/account")


@app.route("/account/delete", methods=["POST"])
def account_delete():
    return redirect("/account")


@app.route("/tweet")
def tweet():
    tweet_info = Tweet.query.all()
    return render_template("Tweet/index.html", data=tweet_info)


@app.route("/tweet/create")
def tweet_create():
    account_name = Accounts.query.all()
    return render_template("Tweet/create.html", data=account_name)


@app.route("/tweet/store", methods=["POST"])
def tweet_store():
    account_name = request.form['account_name']
    contents = request.form["contents"]
    tweet_date = request.form["date"]
    tweet_time = request.form["time"]
    datetime_obj = datetime.strptime(tweet_date + " " + tweet_time, '%Y-%m-%d %H:%M')
    y = datetime_obj.year
    m = datetime_obj.month
    d = datetime_obj.day
    h = datetime_obj.hour
    mt = datetime_obj.minute
    insert = Tweet(account_name=account_name, contents=contents, reserved=datetime_obj, y=y, m=m, d=d, h=h, mt=mt)
    db.session.add(insert)
    db.session.commit()
    return redirect("/tweet")


@app.route("/tweet/delete")
def tweet_delete():
    return redirect("tweet")


@app.route("/profile")
def profile():
    return render_template("Profile/index.html")


@app.route("/profile/create")
def profile_create():
    return render_template("Tweet/create.html")


@app.route("/profile/store")
def profile_store():
    return redirect("/profile")


@app.route("/profile/delete")
def profile_delete():
    return redirect("/profile")


@app.route("/analytics")
def analytics():
    return render_template("Analytics/index.html")


@app.route("/analytics/detail/<int:id>")
def analytics_detail(id):
    return render_template("Analytics/index.html")


if __name__ == '__main__':
    app.run(debug=True)

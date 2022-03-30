import datetime
import time
import concurrent.futures
import tweepy
from config import CONFIG
from flask import Flask, render_template, request, redirect
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


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(32), nullable=True)
    url = db.Column(db.String(128), nullable=True)
    location = db.Column(db.String(64), nullable=True)
    description = db.Column(db.String(200), nullable=True)
    reserved = db.Column(db.DateTime(), nullable=False)


auth = tweepy.OAuthHandler(CONFIG["consumer_key"], CONFIG["consumer_secret"])
auth.set_access_token(CONFIG["access_token_key"], CONFIG["access_token_secret"])
api = tweepy.API(auth)


# ツイートの送信
def post_tweet(self, contents):
    self.update_status(contents)


# プロフィール設定


def tweet_expired_reserve_deleter():
    tweet_info = Tweet.query.order_by(Tweet.reserved.asc()).all()
    time.sleep(1)
    for items in tweet_info:
        time.sleep(1)
        if items.reserved < datetime.datetime.now() - datetime.timedelta(minutes=1):
            db.session.delete(items)
            db.session.commit()


def tweet_reserve():
    while True:
        tweet_info = Tweet.query.order_by(Tweet.reserved.asc()).all()
        time.sleep(1)
        for items in tweet_info:
            time.sleep(1)
            if items.reserved.strftime('%Y%m%d%H%M') == datetime.datetime.now().strftime('%Y%m%d%H%M'):
                post_tweet(api, items.contents)
                db.session.delete(items)
                db.session.commit()


def profile_expired_reserve_deleter():
    profile_info = Profile.query.order_by(Profile.reserved.asc()).all()
    time.sleep(1)
    for items in profile_info:
        time.sleep(1)
        if items.reserved < datetime.datetime.now():
            db.session.delete(items)
            db.session.commit()


def profile_reserve():
    while True:
        profile_info = Profile.query.order_by(Profile.reserved.asc()).all()
        time.sleep(1)
        for items in profile_info:
            time.sleep(1)
            if items.reserved.strftime('%Y%m%d%H%M') == datetime.datetime.now().strftime('%Y%m%d%H%M'):
                api.update_profile(name=items.name, location=items.location, description=items.description)
                db.session.delete(items)
                db.session.commit()


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
    id = request.form.get('id')
    account_info = Accounts.query.get(id)
    db.session.delete(account_info)
    db.session.commit()
    return redirect("/account")


@app.route("/tweet")
def tweet():
    tweet_info = Tweet.query.order_by(Tweet.reserved.asc()).all()
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
    datetime_obj = datetime.datetime.strptime(tweet_date + " " + tweet_time, '%Y-%m-%d %H:%M')
    insert = Tweet(account_name=account_name, contents=contents, reserved=datetime_obj)
    db.session.add(insert)
    db.session.commit()
    return redirect("/tweet")


@app.route("/tweet/delete", methods=["POST"])
def tweet_delete():
    id = request.form.get('id')
    tweet_info = Tweet.query.get(id)
    db.session.delete(tweet_info)
    db.session.commit()
    return redirect("/tweet")


@app.route("/profile")
def profile():
    profile_info = Profile.query.order_by(Profile.reserved.asc()).all()
    return render_template("Profile/index.html", data=profile_info)


@app.route("/profile/create")
def profile_create():
    account_name = Accounts.query.all()
    return render_template("Profile/create.html", data=account_name)


@app.route("/profile/store", methods=["POST"])
def profile_store():
    account_name = request.form['account_name']
    profile_name = request.form['name']
    profile_detail = request.form["detail"]
    profile_url = request.form["url"]
    profile_location = request.form["location"]
    tweet_date = request.form["date"]
    tweet_time = request.form["time"]
    datetime_obj = datetime.datetime.strptime(tweet_date + " " + tweet_time, '%Y-%m-%d %H:%M')
    insert = Profile(account_name=account_name, name=profile_name, description=profile_detail, url=profile_url,
                     location=profile_location, reserved=datetime_obj)
    db.session.add(insert)
    db.session.commit()
    return redirect("/profile")


@app.route("/profile/delete", methods=["POST"])
def profile_delete():
    id = request.form.get('id')
    profile_info = Profile.query.get(id)
    db.session.delete(profile_info)
    db.session.commit()
    return redirect("/profile")


@app.route("/analytics")
def analytics():
    return render_template("Analytics/index.html")


@app.route("/analytics/detail/")
def analytics_detail():
    return render_template("Analytics/index.html")


if __name__ == '__main__':
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
    tweet_expired_reserve_deleter()
    profile_expired_reserve_deleter()
    executor.submit(tweet_reserve)
    executor.submit(profile_reserve)
    app.run(debug=True, threaded=True)

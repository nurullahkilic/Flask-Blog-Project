from flask_wtf.csrf import CSRFError
from slugify import slugify
import base64
import io
import sys
from flask import Flask, render_template, flash, url_for, session, logging, request, redirect, abort, jsonify
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, FileField
from wtforms.widgets import TextArea
from passlib.hash import sha256_crypt
from functools import wraps
from werkzeug.utils import secure_filename
import os
import os.path
from os import path
from authlib.integrations.flask_client import OAuth
from rauth.service import OAuth2Service
import timeago
from datetime import date, datetime
import json
import requests
from sqlalchemy import exc
import locale


if sys.version_info < (3, 0):
    from urllib2 import urlopen
else:
    from urllib.request import urlopen


UPLOAD_FILE_INDEX = 'static/uploads'
UZANTILAR = set(['png', 'jpg', 'jpeg', 'gif'])


locale.setlocale(locale.LC_TIME, "tr_TR")

app = Flask(__name__)
app.secret_key = "kfmghsd84sd8f4gs8g"

app.config['UPLOAD_FOLDER'] = UPLOAD_FILE_INDEX
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/90551/Desktop/NURULLAH/Yazılım Denemeleri/Flask Project - ORM/blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'nurullahkilic@ogr.iu.edu.tr'
app.config['MAIL_DEFAULT_SENDER'] = 'nurullahkilic@ogr.iu.edu.tr'

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
mail = Mail(app)

oauth = OAuth(app)



def check_file(name):
    return '.' in name and \
        name.rsplit('.', 1)[1].lower() in UZANTILAR


# def color_picker(url):
#     fd = urlopen(url)
#     f = io.BytesIO(fd.read())
#     color_thief = ColorThief(f)
#     return color_thief.get_color(quality=10)


def timeAgo(date):
    if date == None or date == "":
        return date
    return timeago.format(date, datetime.now(), 'tr')


def getYear(date):
    if date == None or date == "":
        return date
    date_time = datetime.strptime(date, '%Y-%m-%d')
    return date_time.date().year


def getFullTime(date):
    if date == None or date == "":
        return date
    date_time = datetime.strptime(date, '%Y-%m-%d')
    return date_time.strftime("%d %B %Y")


def new_decoder(payload):
    return json.loads(payload.decode('utf-8'))


app.jinja_env.filters['timeAgo'] = timeAgo
app.jinja_env.filters['getYear'] = getYear
app.jinja_env.filters['getFullTime'] = getFullTime

# Form Classları


class RegistrationForm(Form):
    fullname = StringField(
        'Full Name', [validators.DataRequired(), validators.Length(min=4, max=30)])
    username = StringField(
        'Username', [validators.DataRequired(), validators.Length(min=4, max=25)])
    email = StringField(
        'Email Address', [validators.DataRequired(), validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Parola Eşleşmiyor')
    ])
    confirm = PasswordField('Repeat Password')


class LoginForm(Form):
    username = StringField('Username')
    password = PasswordField('Password')


class ArticleForm(Form):
    title = StringField("Article's Title", [
        validators.DataRequired(), validators.Length(min=4, max=300)])
    image = StringField("Image's Source", [
        validators.DataRequired()])
    content = TextAreaField("Content", [
        validators.DataRequired(), validators.Length(min=4)])


# Database ORM Classları

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    register_type = db.Column(db.String(300), default="normal", nullable=False)
    bio = db.Column(db.String(1000), nullable=True)
    male = db.Column(db.String(30), nullable=True)
    profile_pic = db.Column(db.String(30), nullable=True)
    banner_pic = db.Column(db.String(30), nullable=True)
    followers = db.Column(db.Integer)
    following = db.Column(db.Integer)
    register_date = db.Column(
        db.DateTime, default=datetime.now(), nullable=False)
    birth_date = db.Column(db.DateTime, nullable=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    is_private = db.Column(db.Boolean, default=False, nullable=False)

    def is_following(self, follower_id):
        return Follow.query.filter_by(user_id=self.id, follower_id=follower_id).count() > 0

    def count_publish_article(self):
        return Articles.query.filter_by(author_id=self.id, is_publish=True, is_confirm=True).count()

    def get_list_json(self):
        listArr = []
        for list in Lists.query.filter_by(user_id=self.id).all()[::-1]:
            data = {
                "id": list.id,
                "name": list.name,
                "picture": list.list_pic,
                "created_date": timeAgo(list.created_date),
                "username": self.fullname
            }
            listArr.append(data)
        return jsonify(listArr)

    def get_watchlist_json(self, start=None, finish=None):
        listArr = []
        for item in WatchLists.query.filter_by(user_id=self.id).all():
            for product in item.get_items()[::-1]:
                data = {
                    "product_type_name": product["type"],
                    "product_type": product["type_id"],
                    "product_id": product["item"].id,
                    "title": product["item"].title,
                    "director": product["item"].director,
                    "original_name": product["item"].original_name,
                    "overview": product["item"].overview,
                    "poster": product["item"].poster,
                    "backdrop": product["item"].backdrop,
                    "created_date": getYear(product["item"].created_date),
                }
                listArr.append(data)
        return jsonify(listArr[start:finish])

    # def get_watchlist_json(self, start=None, finish=None):
    #     listArr = []
    #     for item in WatchLists.query.filter_by(user_id=self.id).all()[::-1]:
    #         for product in Movies.query.all():
    #             data = {
    #                 "product_type": 'movies',
    #                 "product_id": product.id,
    #                 "title": product.title,
    #                 "director": product.director,
    #                 "original_name": product.original_name,
    #                 "overview": product.overview,
    #                 "poster": product.poster,
    #                 "backdrop": product.backdrop,
    #                 "created_date": product.created_date,
    #             }
    #             listArr.append(data)
    #     return jsonify(listArr[start:finish])

    def get_followers_json(self):
        follower = []
        for user in Follow.query.filter_by(user_id=self.id).all():
            user = User.query.get(user.follower_id)
            if "logged_in" in session:
                data = {
                    "id": user.id,
                    "fullname": user.fullname,
                    "username": user.username,
                    "profile_pic": user.profile_pic,
                    "banner_pic": user.banner_pic,
                    "is_following_viewer": user.is_following(session["user_id"])
                }
            else:
                data = {
                    "id": user.id,
                    "fullname": user.fullname,
                    "username": user.username,
                    "profile_pic": user.profile_pic,
                    "banner_pic": user.banner_pic
                }
            follower.append(data)
        return jsonify(follower)

    def get_following_json(self):
        follower = []
        for user in Follow.query.filter_by(follower_id=self.id).all():
            user = User.query.get(user.user_id)
            if "logged_in" in session:
                data = {
                    "id": user.id,
                    "fullname": user.fullname,
                    "username": user.username,
                    "profile_pic": user.profile_pic,
                    "banner_pic": user.banner_pic,
                    "is_following_viewer": user.is_following(session["user_id"])
                }
            else:
                data = {
                    "id": user.id,
                    "fullname": user.fullname,
                    "username": user.username,
                    "profile_pic": user.profile_pic,
                    "banner_pic": user.banner_pic
                }
            follower.append(data)
        return jsonify(follower)

    def get_followers(self):
        follower = []
        for user in Follow.query.filter_by(user_id=self.id).all():
            user = User.query.get(user.follower_id)
            follower.append(user)
        return follower

    def get_followings(self):
        following = []
        for user in Follow.query.filter_by(follower_id=self.id).all():
            user = User.query.get(user.user_id)
            following.append(user)
        return following

    def __repr__(self):
        return '<User %r>' % self.username


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    date = db.Column(
        db.DateTime, default=datetime.now(), nullable=False)
    is_manager = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return '<Admin %r>' % self.username


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    follower_id = db.Column(db.Integer, nullable=False)
    date = db.Column(
        db.DateTime, default=datetime.now(), nullable=False)

    def is_following(self, user_id, follower_id):
        return Follow.query.filter_by(user_id=user_id, follower_id=follower_id).count() > 0

    def get_follower(self):
        return User.query.filter_by(id=self.follower_id).first()

    def get_following(self):
        return User.query.filter_by(id=self.user_id).first()

    def __repr__(self):
        return '<Follower %r>' % self.user_id


class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.Text, nullable=False)
    slugify = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)
    thumbnail = db.Column(db.Text, nullable=False)
    thumbnail_color = db.Column(db.Text, nullable=True)
    likes = db.Column(db.Text, nullable=True)
    created_date = db.Column(
        db.DateTime, default=datetime.now(), nullable=False)
    updated_date = db.Column(
        db.DateTime, nullable=True)
    is_publish = db.Column(db.Boolean, default=True, nullable=False)
    is_confirm = db.Column(db.Boolean, default=True, nullable=False)

    def get_user(self):
        return User.query.get(self.author_id)

    def is_user_liked(self):
        return Likes.query.filter_by(user_id=session["user_id"], activity_id=self.id, activity_type=1).count() > 0

    def count_comment(self):
        return Comments.query.filter_by(type_id=1, post_id=self.id).count()

    def count_like(self):
        return Likes.query.filter_by(activity_type=1, activity_id=self.id).count()

    def __repr__(self):
        return '<Article %r>' % self.title


class Notions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    text_out = db.Column(db.Text, nullable=False)
    html_out = db.Column(db.Text, nullable=False)
    product_id = db.Column(db.Integer, primary_key=False)
    product_type = db.Column(db.Integer, primary_key=False)
    likes = db.Column(db.Text, nullable=True)
    created_date = db.Column(
        db.DateTime, default=datetime.now(), nullable=False)
    updated_date = db.Column(
        db.DateTime, nullable=True)
    is_confirm = db.Column(db.Boolean, default=True, nullable=False)

    def get_user(self):
        return User.query.get(self.user_id)

    def get_product(self):
        if self.product_type == 1:
            return Movies.query.filter_by(id=self.product_id).first()
        elif self.product_type == 2:
            return Series.query.filter_by(id=self.product_id).first()

    def is_owner(self, user_id):
        return self.user_id == user_id

    def __repr__(self):
        return '<Notions %r>' % self.text_out


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Text, nullable=True)
    created_date = db.Column(
        db.DateTime, default=datetime.now(), nullable=False)

    def get_user(self):
        return User.query.get(self.user_id)

    def __repr__(self):
        return '<Comment %r>' % self.content


class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    activity_id = db.Column(db.Integer, nullable=False)
    activity_type = db.Column(db.Text, nullable=False)
    created_date = db.Column(
        db.DateTime, default=datetime.now(), nullable=False)

    def get_user(self):
        return User.query.get(self.user_id)

    def has_liked(self):
        return Likes.query.filter_by(user_id=self.user_id, activitiy_id=self.activity_id, activity_type=self.activity_type).count() > 0

    def __repr__(self):
        return '<Like %r>' % self.user_id


class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_id = db.Column(db.Integer, primary_key=False)
    title = db.Column(db.Text, nullable=True)
    director = db.Column(db.Text, nullable=True)
    original_name = db.Column(db.Text, nullable=True)
    overview = db.Column(db.Text, nullable=True)
    country = db.Column(db.Text, nullable=True)
    poster = db.Column(db.Text, nullable=True)
    backdrop = db.Column(db.Text, nullable=True)
    created_date = db.Column(db.Text, nullable=True)

    def get_list(self):
        lists = []
        for item in ListItems.query.filter_by(product_id=self.id).all()[::-1]:
            list = Lists.query.get(item.list_id)
            lists.append(list)
        return lists

    def __repr__(self):
        return '<Series %r>' % self.title


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_id = db.Column(db.Integer, primary_key=False)
    title = db.Column(db.Text, nullable=True)
    director = db.Column(db.Text, nullable=True)
    original_name = db.Column(db.Text, nullable=True)
    overview = db.Column(db.Text, nullable=True)
    country = db.Column(db.Text, nullable=True)
    poster = db.Column(db.Text, nullable=True)
    backdrop = db.Column(db.Text, nullable=True)
    created_date = db.Column(db.Text, nullable=True)

    def get_list(self):
        lists = []
        for item in ListItems.query.filter_by(product_id=self.id).all()[::-1]:
            list = Lists.query.get(item.list_id)
            lists.append(list)
        return lists

    def __repr__(self):
        return '<Movies %r>' % self.title


class Lists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=False)
    name = db.Column(db.Text, nullable=False)
    slug = db.Column(db.Text, nullable=False, unique=True)
    desc = db.Column(db.Text, nullable=False)
    list_pic = db.Column(db.Text, nullable=True)
    likes = db.Column(db.Integer, nullable=True)
    created_date = db.Column(
        db.DateTime, default=datetime.now(), nullable=False)
    updated_date = db.Column(db.DateTime, nullable=True)

    def get_user(self):
        return User.query.get(self.user_id)

    def is_owner(self, user_id):
        return self.user_id == user_id

    def get_items(self):
        items = []
        for item in ListItems.query.filter_by(list_id=self.id).all():
            if item.product_type == 1:
                movie = Movies.query.get(item.product_id)
                data = {
                    "item": movie,
                    "type": "movies",
                    "added_date": item.created_date
                }
                items.append(data)
            elif item.product_type == 2:
                series = Series.query.get(item.product_id)
                data = {
                    "item": series,
                    "type": "series",
                    "added_date": item.created_date
                }
                items.append(data)
        return items

    def __repr__(self):
        return '<Lists %r>' % self.name


class WatchLists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=False)
    list_type = db.Column(db.Integer, primary_key=False)
    likes = db.Column(db.Integer, nullable=True)
    updated_date = db.Column(db.DateTime, nullable=True)

    def get_user(self):
        return User.query.get(self.user_id)

    def is_owner(self, user_id):
        return self.user_id == user_id

    def get_items(self):
        items = []
        for item in WatchListItems.query.filter_by(user_id=self.user_id).all():
            if item.product_type == 1:
                movie = Movies.query.get(item.product_id)
                data = {
                    "item": movie,
                    "type": "movies",
                    "type_id": 1,
                    "added_date": item.created_date
                }
                items.append(data)
            elif item.product_type == 2:
                series = Series.query.get(item.product_id)
                data = {
                    "item": series,
                    "type": "series",
                    "type_id": 2,
                    "added_date": item.created_date
                }
                items.append(data)
        return items

    def __repr__(self):
        return '<Watch Lists %r>' % self.name


class ListItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=False)
    list_id = db.Column(db.Integer, primary_key=False)
    product_id = db.Column(db.Integer, primary_key=False)
    product_type = db.Column(db.Integer, primary_key=False)
    created_date = db.Column(
        db.DateTime, default=datetime.now(), nullable=False)

    def is_exist(self, list_id, product_id, product_type):
        return ListItems.query.filter_by(list_id=list_id, product_id=product_id, product_type=product_type).count() > 0

    def get_list(self):
        return Lists.query.get(self.list_id)

    def __repr__(self):
        return '<List Item %r>' % self.product_id


class WatchListItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=False)
    list_type = db.Column(db.Integer, primary_key=False)
    product_id = db.Column(db.Integer, primary_key=False)
    product_type = db.Column(db.Integer, primary_key=False)
    created_date = db.Column(
        db.DateTime, default=datetime.now(), nullable=False)

    def is_exist(self, list_type, user_id, product_id, product_type):
        return WatchListItems.query.filter_by(list_type=list_type, user_id=user_id, product_id=product_id, product_type=product_type).count() > 0

    def get_list(self):
        return WatchLists.query.get(self.list_id)

    def get_user(self):
        return User.query.get(self.user_id)

    def __repr__(self):
        return '<Watch List Item %r>' % self.product_id


class ProductType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.Integer, primary_key=False)
    created_date = db.Column(
        db.DateTime, default=datetime.now(), nullable=False)

    def __repr__(self):
        return '<Product Type %r>' % self.product_name


class ListType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.Integer, primary_key=False)
    created_date = db.Column(
        db.DateTime, default=datetime.now(), nullable=False)

    def __repr__(self):
        return '<List Type %r>' % self.type_name


class CommentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.Integer, primary_key=False)

    def __repr__(self):
        return '<Comment Type %r>' % self.type_name


class LikeType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.Integer, primary_key=False)

    def __repr__(self):
        return '<Like Type %r>' % self.type_name


# for i in range(1, 501):
#     url = "https://api.themoviedb.org/3/movie/popular?api_key=70b723f8ee41cdb5e71a00b13021c160&language=tr-TR&page=" + \
#         str(i)
#     re = requests.get(url)
#     for j in re.json()['results']:
#         api_id = ""
#         title = ""
#         director = ""
#         original_name = ""
#         overview = ""
#         country = ""
#         poster = ""
#         backdrop = ""
#         created_date = ""
#         if "id" in j:
#             api_id = j['id']
#         if "title" in j:
#             title = j['title']
#         if "original_title" in j:
#             original_name = j['original_title']
#         if "overview" in j:
#             overview = j['overview']
#         if j['original_language'] == [] and "original_language" in j:
#             pass
#         else:
#             country = j['original_language']
#         if "poster_path" in j:
#             poster = j['poster_path']
#         if "backdrop_path" in j:
#             backdrop = j['backdrop_path']
#         if "release_date" in j:
#             created_date = j['release_date']
#         movies = Movies(api_id=api_id, title=title, original_name=original_name, overview=overview,
#                         country=country, poster=poster, backdrop=backdrop, created_date=created_date)
#         db.session.add(movies)
#         db.session.commit()

# i = 1
# for film in Movies.query.all()[9105:10300]:
#     print(i)
#     i = i+1
#     url = "http://www.omdbapi.com/?t={}&plot=full&apikey=98186c0d".format(
#         film.original_name)
#     re = requests.get(url)
#     if 'Director' in re.json():
#         if re.json()['Director'] == "N/A":
#             film.director = re.json()['Writer']
#             db.session.commit()
#         else:
#             film.director = re.json()['Director']
#             db.session.commit()
#     else:
#         pass


def login_required(f):
    @ wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("LÜTFEN GİRİŞ YAPINIZ!", "error")
            return redirect(url_for("login"))
    return decorated_function


@ app.route("/")
def index():
    return render_template("index.html")


@ app.route("/articles")
def articles():
    cursor = mysql.connection.cursor()
    sorgu = "SELECT * FROM articles WHERE confirm =1"
    result = cursor.execute(sorgu)
    if result > 0:
        articles = cursor.fetchall()
        cursor.close()
        return render_template("articles.html", articles=articles)
    else:
        return render_template("articles.html")


@ app.route("/article/<string:slugify>")
def article(slugify):
    article = Articles.query.filter_by(
        slugify=slugify).first()
    comments = Comments.query.filter_by(
        type_id=1, post_id=article.id).all()[::-1]
    if not article.is_publish:
        if article.author_id == session["user_id"]:
            return render_template("article.html", article=article, comments=comments)
        else:
            flash("BU MAKALEYE ERİŞMEYE YETKİNİZ YOK!", "error")
            return redirect(url_for("index"))
    else:
        return render_template("article.html", article=article, comments=comments)


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)

    if request.method == 'POST' and form.validate():
        fullname = form.fullname.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(form.password.data)

        user = User(fullname=fullname, email=email,
                    username=username, password=password, profile_pic="https://avatars.dicebear.com/api/jdenticon/" + username + ".svg?background=%23ffffff", followers=0, following=0)
        try:
            db.session.add(user)
            db.session.commit()
            flash('BAŞARIYLA KAYIT OLUNDU!', 'success')
        except exc.IntegrityError:
            flash('BU MAİL VEYA KULLANICI ADI KAYITLI!', 'error')
            db.session.rollback()
            return redirect(url_for("register"))
        return redirect(url_for("login"))
    else:
        return render_template('register.html', form=form)

# Normal giriş


@ app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST':
        username = form.username.data
        password_entered = form.password.data
        user = User.query.filter_by(username=username).first()

        if user:
            real_password = user.password
            if sha256_crypt.verify(password_entered, real_password):
                flash(
                    f"BAŞARIYLA GİRİŞ YAPILDI! HOŞGELDİNİZ {username}", 'success')

                session["logged_in"] = True
                session["username"] = username
                session["fullname"] = user.fullname
                session["user_id"] = user.id
                session["user_img"] = user.profile_pic
                session["user_banner"] = user.banner_pic
                return redirect(url_for("index"))
            else:
                flash('PAROLA HATALI!', 'error')
                return redirect(url_for("login"))
        else:
            flash("BÖYLE BİR KULLANICI BULUNAMADI!", "error")
            return redirect(url_for("login"))

    return render_template('login.html', form=form)

# Google ile giriş


@ app.route('/login_google')
def login_google():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@ app.route('/authorize')
def authorize():
    google = oauth.create_client('google')  # create the google oauth client
    # Access token from google (needed to get user info)
    token = google.authorize_access_token()
    # userinfo contains stuff u specificed in the scrope
    resp = google.get('userinfo')
    user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    print(user)
    cursor = mysql.connection.cursor()

    sorgu = "SELECT * FROM google_users WHERE email = %s"
    result = cursor.execute(sorgu, (user.email,))
    if result > 0:
        sorgu = "SELECT * FROM google_users"
        result = cursor.execute(sorgu)
        if result > 0:
            google_users = cursor.fetchall()
            for google_user in google_users:
                if google_user['username'] and user.email == google_user['email']:
                    flash(
                        f"BAŞARIYLA GİRİŞ YAPILDI! HOŞGELDİNİZ {user.name}", 'success')
                    session["logged_in"] = True
                    session["username"] = google_user['username']
                    session["login_type"] = "google"
                    return redirect('/')
                elif user.email == google_user['email'] and google_user['username'] == "":
                    session["email"] = user.email
                    session["login_type"] = "google"
                    return redirect(url_for("register_with"))
            return "tebrikler garip bi hata yakaladın. yazılımcıya sövebilirsin :)))"
        else:
            flash(
                f"BİR HATA OLUŞTU TEKRAR DENEYİNİZ'", 'error')
            return redirect(url_for("login"))
    else:
        sorgu = "INSERT INTO google_users(id,fullname,email,picture,locale) VALUES(%s,%s,%s,%s,%s)"
        cursor.execute(sorgu, (user.sub, user.name,
                       user.email, user.picture, user.locale))
        mysql.connection.commit()
        session["email"] = user.email
        session["login_type"] = "google"
        return redirect(url_for("register_with"))


@ app.route('/register_with', methods=["GET", "POST"])
def register_with():
    form = RegistrationForm(request.form)

    if request.method == 'POST':
        newUsername = form.username.data

        cursor = mysql.connection.cursor()
        sorgu = "SELECT * FROM users"
        cursor.execute(sorgu)
        users = cursor.fetchall()
        for user in users:
            if newUsername == user['username']:
                flash(newUsername+" KULLANICI ADI KAYITLI!", "error")
                return redirect(url_for("register_with"))
        sorgu = "SELECT * FROM google_users"
        cursor.execute(sorgu)
        users = cursor.fetchall()
        for user in users:
            if newUsername == user['username']:
                flash(newUsername+" KULLANICI ADI KAYITLI!", "error")
                return redirect(url_for("register_with"))

        sorgu = "SELECT * FROM google_users WHERE email = %s"
        result = cursor.execute(sorgu, (session["email"],))
        if result > 0:
            user = cursor.fetchone()
            sorgu2 = "UPDATE google_users SET username=%s WHERE email=%s"

            cursor.execute(sorgu2, (newUsername, user["email"]))
            mysql.connection.commit()
            cursor.close()

            flash(
                f"BAŞARIYLA GİRİŞ YAPILDI! HOŞGELDİNİZ {user['fullname']}", "success")
            session["logged_in"] = True
            session["username"] = newUsername
            session["login_type"] = "google"
            return redirect(url_for("index"))
        else:
            flash("İLGİNÇ BİR HATA OLUŞTU!", "error")
            return redirect(url_for("index"))
    elif request.method == 'GET':
        if "logged_in" in session:
            if session["login_type"] == "google":
                if "username" in session:
                    flash("ZATEN BİR KULLANICI ADINA SAHİPSİNİZ!", "error")
                    return redirect(url_for("index"))
                else:
                    return render_template("register_with.html", form=form)
            else:
                flash("BU İŞLEME YETKİNİZ YOK1", "error")
                return redirect(url_for("index"))
        else:
            if "login_type" in session:
                if session["login_type"] == "google":
                    return render_template("register_with.html", form=form)
                else:
                    flash("BAĞZI HATALAR DÖNÜYOR BURDA", "error")
                    return redirect(url_for("index"))
            else:
                flash("BU İŞLEME YETKİNİZ YOK", "error")
                return redirect(url_for("index"))

# Facebookile giriş


@ app.route('/facebook/login')
def login_facebook():
    redirect_uri = url_for('authorized', _external=True)
    params = {'redirect_uri': redirect_uri}
    return redirect(facebook.get_authorize_url(**params))


@ app.route('/facebook/authorized')
def authorized():
    # check to make sure the user authorized the request
    if not 'code' in request.args:
        flash('You did not authorize the request', 'error')
        return redirect(url_for('index'))

    # make a request for the access token credentials using code
    redirect_uri = url_for('authorized', _external=True)
    data = dict(code=request.args['code'], redirect_uri=redirect_uri)

    session = facebook.get_auth_session(data=data, decoder=new_decoder)
    me = session.get('me').json()
    print(me)
    return redirect(url_for('index'))


@ app.route('/logout')
@ login_required
def logout():
    session.clear()

    flash("BAŞARIYLA ÇIKIŞ YAPILDI", "success")
    return redirect(url_for("index"))


@ app.route('/dashboard')
@ login_required
def dashboard():
    user = User.query.get(session["user_id"])
    admin = Admin.query.filter_by(user_id=session["user_id"]).first()
    result = 0
    if admin:
        if result > 0:
            articles = cursor.fetchall()
            cursor.close()
            return render_template("dashboard.html", articles=articles)
        else:
            return render_template("dashboard.html")
    else:
        if result > 0:
            articles = cursor.fetchall()
            cursor.close()
            return render_template("dashboard.html", articles=articles, admin=user['admin'])
        else:
            return render_template("dashboard.html")


@app.route('/addarticle', methods=['GET', 'POST'])
@login_required
def addarticle():
    if request.method == 'POST':
        result = request.json
        query = request.args.get('query')
        type = request.args.get('type')
        if query == "add":
            if not Articles.query.filter(Articles.slugify == slugify(result["title"])).first():
                slugify_article = slugify(result["title"])
            else:
                slugify_article = slugify(
                    result["title"] + str(datetime.now().strftime("%d/%m/%Y, %H:%M:%S")))
            if type == "draft":
                article = Articles(author_id=session["user_id"], title=result["title"], slugify=slugify_article, content=result["content"],
                                   thumbnail=result["link"], thumbnail_color=result["color"], created_date=datetime.now(), is_publish=False)
                message = "Makale taslak olarak kaydedildi!"
            else:
                article = Articles(author_id=session["user_id"], title=result["title"], slugify=slugify_article, content=result["content"],
                                   thumbnail=result["link"], thumbnail_color=result["color"], created_date=datetime.now(), is_publish=True)
                message = "Makale başarıyla yayınlandı!"
            db.session.add(article)
            db.session.commit()
            return jsonify({"message": message, "location": "/article/"+slugify_article})
        elif query == "update":
            article = Articles.query.filter_by(
                id=result["id"], author_id=session["user_id"]).first()
            if article and type == "publish":
                article.title = result["title"]
                article.content = result["content"]
                article.thumbnail = result["link"]
                article.thumbnail_color = result["color"]
                article.updated_date = datetime.now()
                article.is_publish = True
                slugify_article = article.slugify
                db.session.add(article)
                db.session.commit()
                message = "Makale başarıyla yayına alındı!"
                return jsonify({"message": message, "location": "/article/"+slugify_article})
            if article:
                article.title = result["title"]
                article.content = result["content"]
                article.thumbnail = result["link"]
                article.thumbnail_color = result["color"]
                article.updated_date = datetime.now()
                slugify_article = article.slugify
                db.session.add(article)
                db.session.commit()
                message = "Makale başarıyla güncellendi!"
                return jsonify({"message": message, "location": "/article/"+slugify_article})
            else:
                message = "Eğer kod yanlış çalışmıyorsa bu makale size ait değil maalesef!"
                return jsonify({"message": message, "location": "/"})
    else:
        return render_template("addarticle.html")


@app.route('/delete/<string:slug>')
@login_required
def delete(slug):
    if request.method == "GET":
        article = Articles.query.filter_by(slugify=slug).first()
        if not article.author_id == session["user_id"]:
            flash("BÖYLE BİR MAKALE YOK VEYA BUNA YETKİNİZ YOK!", "error")
            return redirect(url_for("index"))
        else:
            comments = Comments.query.filter_by(
                type_id=1, post_id=article.id).delete()
            likes = Likes.query.filter_by(
                activity_id=article.id, activity_type=1).delete()
            db.session.delete(article)
            db.session.commit()
            flash("MAKALE BAŞARIYLA SİLİNDİ!", "succes")
            return redirect(url_for("index"))


@app.route('/update/<string:slug>', methods=['GET', 'POST'])
@login_required
def update(slug):
    if request.method == "GET":
        article = Articles.query.filter_by(slugify=slug).first()

        if not article.author_id == session["user_id"]:
            flash("BÖYLE BİR MAKALE YOK VEYA BUNA YETKİNİZ YOK!", "error")
            return redirect(url_for("index"))
        else:
            return render_template("update.html", article=article)


@app.route('/admin')
@login_required
def admin():
    cursor = mysql.connection.cursor()
    sorgu = "SELECT * FROM users WHERE username=%s"
    cursor.execute(sorgu, (session["username"],))
    user = cursor.fetchone()

    if user['admin'] == 0:
        flash("BU İŞLEMİ GERÇEKLEŞTİREBİLMEK İÇİN YÖNETİCİ OLMANIZ GEREKMEKTEDİR!", "error")
        return redirect(url_for("dashboard"))
    elif user['admin'] == 1:
        sorgu3 = "SELECT * FROM articles"
        result = cursor.execute(sorgu3)
        if result > 0:
            articles = cursor.fetchall()
            cursor.close()
            return render_template("admin.html", articles=articles)


@ app.route('/confirm/<string:id>')
@ login_required
def confirm(id):
    cursor = mysql.connection.cursor()
    sorgu = "SELECT * FROM users WHERE username=%s"
    cursor.execute(sorgu, (session["username"],))
    user = cursor.fetchone()

    if user['admin'] == 0:
        flash("BU İŞLEMİ GERÇEKLEŞTİREBİLMEK İÇİN YÖNETİCİ OLMANIZ GEREKMEKTEDİR!", "error")
        return redirect(url_for("dashboard"))
    elif user['admin'] == 1:
        cursor = mysql.connection.cursor()
        sorgu = "SELECT * FROM articles WHERE id=%s"
        result = cursor.execute(sorgu, (id,))

        if result > 0:
            sorgu2 = "UPDATE articles SET confirm = 1 WHERE id = %s"
            cursor.execute(sorgu2, (id,))
            mysql.connection.commit()
            flash("MAKALE ONAYLANDI", "success")
            return redirect(url_for("admin"))
        else:
            flash("BÖYLE BİR MAKALE YOK VEYA BUNA YETKİNİZ YOK!", "error")
            return redirect(url_for("admin"))


@app.route('/reject/<string:id>')
@login_required
def reject(id):
    cursor = mysql.connection.cursor()
    sorgu = "SELECT * FROM users WHERE username=%s"
    cursor.execute(sorgu, (session["username"],))
    user = cursor.fetchone()

    if user['admin'] == 0:
        flash("BU İŞLEMİ GERÇEKLEŞTİREBİLMEK İÇİN YÖNETİCİ OLMANIZ GEREKMEKTEDİR!", "error")
        return redirect(url_for("dashboard"))
    elif user['admin'] == 1:
        cursor = mysql.connection.cursor()
        sorgu = "SELECT * FROM articles WHERE id=%s"
        result = cursor.execute(sorgu, (id,))

        if result > 0:
            sorgu2 = "UPDATE articles SET confirm = 0 WHERE id = %s"
            cursor.execute(sorgu2, (id,))
            mysql.connection.commit()
            flash("MAKALE ONAYI KALDIRILDI!", "error")
            return redirect(url_for("admin"))
        else:
            flash("BÖYLE BİR MAKALE YOK VEYA BUNA YETKİNİZ YOK!", "error")
            return redirect(url_for("admin"))


@ app.route('/account', methods=["POST", "GET"])
@ login_required
def account():
    user = User.query.filter_by(id=session["user_id"]).first()

    if request.method == "GET":
        form = RegistrationForm()
        form.fullname.data = user.fullname
        form.username.data = user.username
        form.email.data = user.email
        return render_template("account.html", form=form)
    else:
        if session["login_type"] == "normal":
            form = RegistrationForm(request.form)

            newFullname = form.fullname.data
            newUsername = form.username.data
            newEmail = form.email.data
            newPassword = sha256_crypt.encrypt(form.password.data)

            cursor = mysql.connection.cursor()
            sorgu2 = "SELECT * FROM users"
            cursor.execute(sorgu2)
            users = cursor.fetchall()
            sorgu3 = "SELECT * FROM users WHERE username = %s"
            cursor.execute(sorgu3, (session["username"],))
            session_user_mail = cursor.fetchone()
            for user in users:
                if newEmail == user['email'] and newUsername == user['username']:
                    if not newEmail == session_user_mail['email'] and not newUsername == session["username"]:
                        flash("BU MAİL VE KULLANICI ADI KAYITLI!", "error")
                        return redirect(url_for("account"))
                elif newUsername == user['username']:
                    if not newUsername == session["username"]:
                        flash(newUsername+" KULLANICI ADI KAYITLI!", "error")
                        return redirect(url_for("account"))
                elif newEmail == user['email']:
                    if not newEmail == session_user_mail['email']:
                        flash("BU MAİL KAYITLI!", "error")
                        return redirect(url_for("account"))

            sorgu4 = "UPDATE users SET fullname = %s, username =%s, email=%s, password=%s WHERE username=%s"
            cursor = mysql.connection.cursor()
            cursor.execute(sorgu4, (newFullname, newUsername,
                                    newEmail, newPassword, session["username"]))
            mysql.connection.commit()
            session["username"] = newUsername
            flash("KİŞİ BİLGİLERİ BAŞARIYLA GÜNCELLENDİ!", "success")
            return redirect(url_for("account"))

        elif session["login_type"] == "google":
            form = RegistrationForm(request.form)

            newUsername = form.username.data

            cursor = mysql.connection.cursor()
            sorgu2 = "SELECT * FROM users"
            cursor.execute(sorgu2)
            users = cursor.fetchall()
            for user in users:
                if newUsername == user['username']:
                    flash(newUsername+" KULLANICI ADI KAYITLI!", "error")
                    return redirect(url_for("account"))
            sorgu = "SELECT * FROM google_users"
            cursor.execute(sorgu)
            users = cursor.fetchall()
            for user in users:
                if newUsername == user['username']:
                    flash(newUsername+" KULLANICI ADI KAYITLI!", "error")
                    return redirect(url_for("account"))

            sorgu = "UPDATE google_users SET username =%s WHERE username=%s"
            cursor = mysql.connection.cursor()
            cursor.execute(sorgu, (newUsername, session["username"]))
            mysql.connection.commit()
            session["username"] = newUsername
            flash("KİŞİ BİLGİLERİ BAŞARIYLA GÜNCELLENDİ!", "success")
            return redirect(url_for("account"))


@ app.route('/upload_image', methods=['POST'])
@ login_required
def upload_image():
    user = User.query.get(session["user_id"])
    if request.method == 'POST':
        query = request.args.get('query')
        # formdan dosya gelip gelmediğini kontrol edelim
        if 'image_file' not in request.files:
            flash('Dosya seçilmedi')
            return redirect('dosyayukleme')

            # kullanıcı dosya seçmemiş ve tarayıcı boş isim göndermiş mi
        image_file = request.files['image_file']
        if image_file.filename == '':
            flash('DOSYA SEÇİLEMEDİ!', 'error')
            return redirect(url_for("account"))

            # gelen dosyayı güvenlik önlemlerinden geçir
        if image_file and check_file(image_file.filename):
            # dosyaadi = secure_filename(image_file.filename)
            if query == "profile":
                image_file.save(os.path.join(
                    app.config['UPLOAD_FOLDER'], str(session["user_id"]) + "_" + query + ".jpg"))
                user.profile_pic = "/static/uploads/" + \
                    str(session['user_id']) + "_" + query + ".jpg"
                db.session.commit()
                flash("FOTOĞRAF BAŞARIYLA YÜKLENDİ", "success")
                return redirect(url_for("account"))
            elif query == "list":
                list_id = int(request.args.get('list_id'))
                list = Lists.query.filter_by(id=list_id).first()
                if list.user_id == session["user_id"]:
                    image_file.save(os.path.join(
                        app.config['UPLOAD_FOLDER'], str(list.id) + "_" + query + ".jpg"))
                    list.list_pic = "/static/uploads/" + \
                        str(list.id) + "_" + query + ".jpg"
                    db.session.commit()
                    flash("FOTOĞRAF BAŞARIYLA YÜKLENDİ", "success")
                    return redirect(url_for("index"))
                flash("BUNA YETKİNİZ YOK", "error")
                return redirect(url_for("index"))
        else:
            flash('İZİN VERİLMEYEN DOSYA UZANTISI!', 'error')
            return redirect(url_for("account"))
    else:
        abort(401)


@ app.route('/@<string:username>')
def profile(username):
    query = request.args.get('query')
    user = User.query.filter_by(username=username).first_or_404()
    lists = Lists.query.filter_by(user_id=user.id).all()[::-1]
    watchlist = WatchLists.query.filter_by(
        user_id=user.id, list_type=1).first()
    articles = Articles.query.filter_by(author_id=user.id).all()
    notions = Notions.query.filter_by(user_id=user.id).all()
    follow = Follow()
    if query == "list":
        return render_template("user-sidebar.html", user=user, lists=lists, follow=follow, query=query, notions=notions)
    elif query == "notion":
        return render_template("user-sidebar.html", user=user, lists=lists, follow=follow, query=query, notions=notions)
    elif query == "watchlist":
        return render_template("user-watchlist.html", user=user, lists=lists, follow=follow, query=query, notions=notions, watchlist=watchlist)
    return render_template("user.html", user=user, lists=lists, follow=follow, articles=articles, notions=notions)


@ app.route('/list/<string:slug>')
def list(slug):
    query = request.args.get('query')
    list = Lists.query.filter_by(slug=slug).first_or_404()
    user = User.query.get(list.user_id)
    if query == "table":
        return render_template("list-table.html", list=list, user=user)
    return render_template("list.html", list=list, user=user)


@ app.route('/search')
def search():
    users = User.query.all()[:4]
    movies = Movies.query.all()[:4]
    series = Series.query.all()[:4]
    articles = Articles.query.filter_by(is_publish=True).order_by(
        Articles.created_date.desc()).all()[:4]
    return render_template("search_page.html", articles=articles, movies=movies, series=series, users=users)


@app.route('/web/create-list', methods=['POST'])
@login_required
def new_list():
    if request.method == "POST":
        listName = request.form['listName']
        desc = request.form['desc']
        if not Lists.query.filter(Lists.slug == slugify(listName)).first():
            list = Lists(user_id=session["user_id"], name=listName, slug=slugify(
                listName), desc=desc,  created_date=datetime.now())
        else:
            list = Lists(user_id=session["user_id"], name=listName, slug=slugify(
                listName + str(datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))), desc=desc, created_date=datetime.now())
        db.session.add(list)
        db.session.commit()
        flash("Liste Başarıyla Oluşturuldu", "success")
        return redirect(url_for("index"))


@app.route('/web/follow', methods=['POST'])
@login_required
def follower():
    if request.method == "POST":
        user_id = request.json["user_id"]
        if int(user_id) == int(session["user_id"]):
            return jsonify({"message": "Birbirini Gösteren Spiderman!"})
        else:
            follow = Follow(user_id=user_id, follower_id=session["user_id"])
            user = User.query.get(session["user_id"])
            user2 = User.query.get(user_id)
            if not follow.is_following(user_id, session["user_id"]):
                follow = Follow(user_id=user_id,
                                follower_id=session["user_id"])
                user.following = int(user.following) + 1
                user2.followers = int(user2.followers) + 1
                db.session.add(user)
                db.session.add(user2)
                db.session.add(follow)
                db.session.commit()
                return jsonify({"message": "Başarıyla Takip Edildi!"})
            else:
                follow = Follow.query.filter_by(user_id=user_id,
                                                follower_id=session["user_id"]).first()
                user.following = int(user.following) - 1
                user2.followers = int(user2.followers) - 1
                db.session.add(user)
                db.session.add(user2)
                db.session.delete(follow)
                db.session.commit()
                return jsonify({"message": "Takipten Çıkıldı!"})


def moviesSearch(param=None, limit=None):
    search = "%{}%".format(param)
    title_search = Movies.query.filter(Movies.title.ilike(
        search)).all()
    original_name_search = Movies.query.filter(Movies.original_name.ilike(
        search)).all()
    director_search = Movies.query.filter(Movies.director.ilike(
        search)).all()
    movies = title_search+original_name_search+director_search
    movies = set(movies[:limit])
    movies_data = []
    for movie in movies:
        data = {
            "movie_id": movie.id,
            "type_id": 1,
            "type_name": "movies",
            "title": movie.title,
            "original_name": movie.original_name,
            "director": movie.director,
            "backdrop": movie.backdrop,
            "year": getYear(movie.created_date),
        }
        movies_data.append(data)
    return movies_data


def seriesSearch(param=None, limit=None):
    search = "%{}%".format(param)
    title_search = Series.query.filter(Series.title.ilike(
        search)).all()
    original_name_search = Series.query.filter(Series.original_name.ilike(
        search)).all()
    director_search = Series.query.filter(Series.director.ilike(
        search)).all()
    series = title_search+original_name_search+director_search
    series = set(series[:limit])
    series_data = []
    for serie in series:
        data = {
            "movie_id": serie.id,
            "type_id": 1,
            "type_name": "series",
            "title": serie.title,
            "original_name": serie.original_name,
            "director": serie.director,
            "backdrop": serie.backdrop,
            "year": getYear(serie.created_date),
        }
        series_data.append(data)
    return series_data


def usersSearch(param=None, limit=None):
    search = "%{}%".format(param)
    username_search = User.query.filter(User.username.ilike(
        search)).all()
    fullname_search = User.query.filter(User.fullname.like(search)).all()
    user_id_search = User.query.filter(User.id.ilike(search)).all()
    users = username_search+fullname_search+user_id_search
    users = set(users[:limit])
    users_data = []
    for user in users:
        data = {
            "id": user.id,
            "fullname": user.fullname,
            "username": user.username,
            "profile_pic": user.profile_pic,
            "banner_pic": user.banner_pic,
        }
        users_data.append(data)
    return users_data


def articlesSearch(param=None, limit=None):
    search = "%{}%".format(param)
    author_fullname = User.query.filter(User.fullname.ilike(search)).first()
    if author_fullname:
        author = Articles.query.filter_by(
            author_id=author_fullname.id, is_publish=True).all()
    else:
        author = []
    articles = Articles.query.filter(Articles.title.ilike(
        search), Articles.is_publish.is_(True)).all()
    articles = articles+author
    articles = set(articles[:limit])
    articles_data = []
    for article in articles:
        data = {
            "id": article.id,
            "title": article.title,
            "author_username": article.get_user().username,
            "author_fullname": article.get_user().fullname,
            "slug": article.slugify,
            "thumbnail": article.thumbnail,
            "thumbnail_color": article.thumbnail_color,
            "created_date": timeAgo(article.created_date),
            "like": article.count_like(),
            "comment": article.count_comment(),
        }
        articles_data.append(data)
    return articles_data


@app.route('/web/api/search', methods=['GET'])
def searchApi():
    query = request.args.get('query')
    if query == "" or query == None:
        return jsonify({"message": "Herhangi bir parametre gönderilmediği için arama yapmakta zorlanıyorum. Mazur görün."})
    return jsonify({"articles": articlesSearch(query, 4), "users": usersSearch(query, 4), "movies": moviesSearch(query, 4), "series": seriesSearch(query, 4)})


@app.route('/web/api/like', methods=['POST'])
def like():
    if request.method == "POST":
        type = request.args.get('type')
        activity_id = request.json["activity_id"]
        if type == "article":
            like = Likes.query.filter_by(
                user_id=session["user_id"], activity_id=activity_id, activity_type=1).first()
            if like:
                db.session.delete(like)
                db.session.commit()
                return jsonify({"message": "Başarıyla kaldırıldı!", "activity_id": activity_id, "activity_type": 1})
            else:
                like = Likes(
                    user_id=session["user_id"], activity_id=activity_id, activity_type=1)
                db.session.add(like)
                db.session.commit()
                return jsonify({"message": "Makaleye değer verdin!", "activity_id": activity_id, "activity_type": 1})


@app.route('/web/api/comment', methods=["POST"])
@login_required
def comment():
    if request.method == "POST":
        action = request.args.get('action')
        if action == "add":
            article_id = request.json["article_id"]
            type_id = request.json["type_id"]
            content = request.json["content"]
            if not content == "" or content == None:
                comment = Comments(
                    type_id=type_id, user_id=session["user_id"], post_id=article_id, content=content, created_date=datetime.now())
                db.session.add(comment)
                db.session.commit()
                return jsonify({'message': 'Yorum başarıyla eklendi!', "fullname": session["fullname"], "user_img": session["user_img"], "username": session["username"]})
            return jsonify({'message': 'Yorum boş gönderilemez!'})
        elif action == "remove":
            article_id = request.json["article_id"]
            comment_id = request.json["comment_id"]
            comment = Comments.query.filter_by(
                type_id=1, id=comment_id, post_id=article_id, user_id=session["user_id"]).first()
            if comment:
                db.session.delete(comment)
                db.session.commit()
                return jsonify({'message': 'Yorum sonsuzluğa doğru yol aldı!'})
            return jsonify({'message': 'Böyle bir yorum yok varsa bile kaldırmaya yetkiniz yok!'})


@app.route('/web/api/notions', methods=["POST"])
@login_required
def addnotions():
    if request.method == "POST":
        query = request.args.get('query')
        if query == "add":
            product_id = request.json["product_id"]
            product_type = request.json["product_type"]
            html_out = request.json["html_out"]
            text_out = request.json["text_out"]
            if not text_out == " " or text_out == None:
                notion = Notions(user_id=session["user_id"], text_out=text_out, html_out=html_out,
                                 product_id=product_id, product_type=product_type, created_date=datetime.now())
                db.session.add(notion)
                db.session.commit()
                return jsonify({'message': 'Görüş başarıyla eklendi!'})
            return jsonify({'message': 'Görüş boş gönderilemez!'})


@app.route('/web/api/addlist', methods=["POST"])
@login_required
def addlist():
    if request.method == "POST":
        query = request.args.get('query')

        product_id = request.json["product_id"]
        product_type = request.json["product_type"]
        item = WatchListItems()
        if query == "watchlist":
            watchlist = WatchLists.query.filter_by(
                user_id=session["user_id"]).first()
            if not watchlist:
                new_watchlist = WatchLists(
                    list_type=1, user_id=session["user_id"], updated_date=datetime.now())
                db.session.add(new_watchlist)
                db.session.commit()
            if not item.is_exist(list_type=1, user_id=session["user_id"], product_id=product_id, product_type=product_type):
                list_item = WatchListItems(
                    user_id=session["user_id"], list_type=1, product_id=product_id, product_type=product_type, created_date=datetime.now())
                db.session.add(list_item)
                db.session.commit()
                return jsonify({'message': 'İzlenceklere başarıyla eklendi!',  'product_id': product_id, 'product_type': product_type})
            return jsonify({'message': 'Bu içerik zaten ekli!'})
        else:
            list_id = request.json["list_id"]
            item = ListItems()
            list = Lists.query.get(list_id)
            if list.is_owner(session["user_id"]):
                if not item.is_exist(list_id=list_id, product_id=product_id, product_type=product_type):
                    list_item = ListItems(
                        user_id=session["user_id"], list_id=list_id, product_id=product_id, product_type=product_type, created_date=datetime.now())
                    db.session.add(list_item)
                    db.session.commit()
                    return jsonify({'message': 'Başarıyla eklendi!', 'list_id': list_id, 'product_id': product_id, 'product_type': product_type, 'is_owner': list.is_owner(session["user_id"])})
                return jsonify({'message': 'Bu içerik zaten ekli!'})
            return jsonify({'message': 'Buna erişiminiz yok!'})


@app.route('/web/api/removelist', methods=["POST"])
@login_required
def removelist():
    if request.method == "POST":
        query = request.args.get('query')

        product_id = request.json["product_id"]
        product_type = request.json["product_type"]
        if query == "watchlist":
            list_item = WatchListItems.query.filter_by(
                user_id=session["user_id"], product_id=product_id, product_type=product_type).first()
            if list_item:
                db.session.delete(list_item)
                db.session.commit()
                return jsonify({'message': 'İzleme listenden kaldırıldı!', "user_id": session["user_id"],  "product_id": product_id, "product_type": product_type})
            return jsonify({'message': 'Buna erişiminiz yok!'})
        else:
            list_id = request.json["list_id"]
            list_item = ListItems.query.filter_by(
                user_id=session["user_id"], list_id=list_id, product_id=product_id, product_type=product_type).first()
            if list_item:
                db.session.delete(list_item)
                db.session.commit()
                return jsonify({'message': 'İçerik başarıyla kaldırıldı!', "user_id": session["user_id"], "list_id": list_id, "product_id": product_id, "product_type": product_type})
            return jsonify({'message': 'Buna erişiminiz yok!'})


@app.route('/web/api/<string:user_id>')
def follow(user_id):
    query = request.args.get('query')
    user = User.query.get(user_id)
    if query == "follower":
        if user:
            return user.get_followers_json()
    elif query == "following":
        if user:
            return user.get_following_json()
    elif query == "list":
        if user:
            return user.get_list_json()
    elif query == "watchlist":
        quantity = 9
        counter = request.args.get('counter')
        if user and counter:
            return user.get_watchlist_json(int(counter), int(counter)+quantity)
        else:
            return user.get_watchlist_json()
    return {"message": "Lütfen doğru düzgün bir request atın efenim!"}


@app.route('/<string:product>/<string:id>')
def movie(id, product):
    notion_id = request.args.get('notion')
    if product == "movies":
        type = 1
        notions = Notions.query.filter_by(
            product_id=id, product_type=type).all()
        product = Movies.query.filter_by(id=id).first_or_404()
    elif product == "series":
        type = 2
        notions = Notions.query.filter_by(
            product_id=id, product_type=type).all()
        product = Series.query.filter_by(id=id).first_or_404()
    if notion_id:
        notion = Notions.query.filter_by(id=notion_id,
                                         product_id=id, product_type=type).first_or_404()
        return render_template("notion.html", product=product, type=type, notion=notion)
    return render_template("product.html", product=product, type=type, notions=notions)


@app.route('/data')
def data():
    msg = Message("farklı Maili", sender="nurullahkilic@ogr.iu.edu.tr",
                  recipients=["nurullahkilic28@gmail.com"])
    msg.html = render_template("mail2.html")
    # mail.send(msg)
    # return render_template("mail2.html")
    return render_template("HelloAnalytics.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html"), 404


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('error.html', reason=e.description), 400


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, host="192.168.1.26", port="8080")

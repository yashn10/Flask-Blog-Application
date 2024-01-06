from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
import secrets
import math
from datetime import datetime


with open("config.json", "r") as c:
    params = json.load(c)["params"]

server = params["local_server"]

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

if (server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]

db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    contact = db.Column(db.String(10), unique=True, nullable=False)
    message = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String, nullable=False)


class Blogs(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    postedby = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String, nullable=False)


@app.route("/", methods=['GET'])
def home():
    posts = Blogs.query.filter_by().all()
    last = math.ceil(len(posts)/int(params["no_of_posts"]))
    page = request.args.get('page')
    if(not str(page).isnumeric()):
        page = 1
    page = int(page)

    posts = posts[(page-1)*int(params["no_of_posts"]): (page-1)*int(params["no_of_posts"])+ int(params["no_of_posts"])]

    if (page==1):
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif (page == last):
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    return render_template("home.html", posts=posts, prev=prev, next=next)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if ('admin' in session and session['admin'] == params['admin_username']):
        posts = Blogs.query.all()
        return render_template("dashboard.html", posts=posts)

    if request.method == 'POST':
        adminusername = request.form.get("username")
        adminpassword = request.form.get("password")
        if (adminusername == params['admin_username'] and adminpassword == params['admin_password']):
            session['admin'] = adminusername
            posts = Blogs.query.all()
            return render_template("dashboard.html", posts=posts)
    
    return render_template("login.html")


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    post = Blogs.query.filter_by(sno=sno).first()

    if request.method == 'POST':
        title = request.form.get('title')
        postedby = request.form.get('postedby')
        content = request.form.get('content')

        if sno == '0':
            add = Blogs(title=title, postedby=postedby, content=content, date=datetime.now())
            db.session.add(add)
            db.session.commit()
            return redirect("/dashboard")

        else:
            post.title = title
            post.postedby = postedby
            post.content = content
            post.date = datetime.now()
            db.session.commit()
            return redirect("/dashboard")

    return render_template("edit.html", post=post, sno=sno)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        contact = request.form.get('contact')
        message = request.form.get('message')

        user = Contacts(name=name, email=email, contact=contact, message=message, date=datetime.now())

        db.session.add(user)
        db.session.commit()

    return render_template("contact.html")


@app.route("/post/<string:title>", methods=['GET'])
def post(title):
    posts = Blogs.query.filter_by(title=title).first()
    return render_template("post.html", posts=posts)


@app.route("/delete/<string:sno>")
def delete(sno):
    post = Blogs.query.filter_by(sno=sno).first()
    db.session.delete(post)
    db.session.commit()
    return redirect("/dashboard")


app.run(debug=True, port=10000)

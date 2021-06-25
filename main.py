from flask import Flask, render_template, request , session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_mail import Mail
import os
import math
import pymysql
import json

local_server = True

with open('config.json','r') as c:
    params = json.load(c)["params"]

app=Flask(__name__,template_folder='Template')
app.secret_key = 'super-secret-key'
'''app.config.update(
    MAIL_SERVER = 'smpt.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail_user'],
    MAIL_PASSWORD = params['gmail_passward']
)'''
app.config['UPLOAD FOLDER']=params['upload_location']
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = params['gmail_user']
app.config['MAIL_PASSWORD'] = params['gmail_passward']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

db = SQLAlchemy(app)
class Feedbacks(db.Model):
    Sr_No = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    Phone= db.Column(db.String(12), nullable=False)
    Message = db.Column(db.String(120), nullable=False)
    Date = db.Column(db.String(12), nullable=True)
    Email = db.Column(db.String(20), nullable=False)

class Posts(db.Model):
    sno= db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug= db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    postby = db.Column(db.String(30), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(30), nullable=True)

class Users(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email= db.Column(db.String(12), nullable=False)
    passward = db.Column(db.String(120), nullable=False)
    college = db.Column(db.String(12), nullable=True)
    from_day = db.Column(db.String(20), nullable=False)

class contribute(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    title= db.Column(db.String(12), nullable=False)
    tagline = db.Column(db.String(12), nullable=True)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(20), nullable=False)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts) / int(params['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page - 1) * int(params['no_of_posts']):(page - 1) * int(params['no_of_posts']) + int(
        params['no_of_posts'])]
    if page == 1:
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)
   # return render_template('index.html',params=params,posts=posts,prev=prev,next=next)

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
   # post = db.session.query(Postinformation).filter_by(Slug=post_slug).first()
    return render_template('post.html', params=params ,post=post)


@app.route('/discuss')
def discuss():
    return render_template('/discuss.html',params=params)


@app.route("/dash",methods=['GET', 'POST'])
def dash():
    if 'user' in session and session['user']==params['admin_user']:
        posts = Posts.query.all()
        return render_template('/dashboard.html',params=params,posts=posts)
    if request.method=='POST':
        #REDIRECT TO ADMIN PANEL
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params['admin_user'] and userpass == params['admin_passward']):
            # set session
            session['user'] = username
            posts=Posts.query.all()
            return render_template('/dashboard.html',params=params,posts=posts)
    else:
        return render_template('login.html',params=params)
    return render_template('login.html',params=params)

@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            #sno=request.form.get('sno')
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            postby = request.form.get('postby')
            img_file = request.form.get('img_file')
            date = datetime.now()

            if sno == '0':
                post = Posts(title = box_title , slug = slug , content=content,postby = postby ,img_file=img_file,tagline = tline,date=date)
                db.session.add(post)
                db.session.commit()
                # sending email when new post is added
                '''
                postt2 = Users.query.filter_by().all()
                messege = "New Post is added link of post is https:/learninghubg/edit/<string:sno> "
                mail.send_message(
                    'Thank you for your feedback , We will try to improve us if we found any described problem in  your emaIl '
                    , sender=params['gmail_user'], recipients=[postt2.email], body=messege)
                '''
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.slug = slug
                post.content = content
                post.tagline = tline
                post.postby  = postby
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/'+sno)
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',params=params,post = post,sno=sno)


@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if (request.method=='POST'):
            f = request.files['file1']
            f.save(os.path.join("C:\\Users\\shubh\\PycharmProjects\\CollegeProject\\Static\\assets\\img",secure_filename(f.filename)))
            return "UPLOAD SUCCESSFULLY"



@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dash')


@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
@app.route("/delete")
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dash')



@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        #Database
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Feedbacks(name=name, Phone = phone, Message = message, Date= datetime.now(),Email = email )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('Thank you for your feedback , We will try to improve us if we found any described problem in  your emaIl '
                          , sender=params['gmail_user'], recipients=[email] ,body = message+"\n"+phone)
    return render_template('contact.html',params=params)

@app.route("/signup", methods = ['GET', 'POST'])
def signup():
    if (request.method == 'POST'):
        # Database
        name = request.form.get('name')
        email = request.form.get('email')
        passward = request.form.get('passward')
        college = request.form.get('college')
        messege = "Thank You for join with learning hub , Explore learning hub and start contributing to earn reputation"
        entry = Users(name=name, email=email, passward=passward ,college=college,from_day=datetime.now())
        db.session.add(entry)
        mail.send_message(
            'Thank you Subscribe with learning hub'
            , sender=params['gmail_user'], recipients=[email], body=messege)
        db.session.commit()
    return render_template('signup.html',params=params)

@app.route("/contribute", methods = ['GET', 'POST'])
def contribute_now():
    if (request.method == 'POST'):
        # Database
        name = request.form.get('name')
        email = request.form.get('email')
        title = request.form.get('title')
        tagline = request.form.get('tagline')
        content = request.form.get('content')
        messege = "Thank you for contribue the article and share your knowladge all over the world ."
        entry = contribute(name = name , email = email ,title=title,tagline = tagline , content=content,date=datetime.now())
        postt = Posts(title=title, slug=tagline, content=content, postby=name, img_file="img1.jpg", tagline=tagline,date=datetime.now())
        mail.send_message(
            subject = 'Thank you for your Contribute '
            , sender=params['gmail_user'], recipients=[email], body=messege)
        db.session.add(entry)
        db.session.add(postt)
        db.session.commit()
    return render_template('contribute.html',params=params)

@app.route("/contributions",methods=['GET', 'POST'])
def contri():
    if 'user' in session and session['user']==params['admin_user']:
        posts = contribute.query.all()
        return render_template('/contributions.html',params=params,posts=posts)
    if request.method=='POST':
        #REDIRECT TO ADMIN PANEL
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params['admin_user'] and userpass == params['admin_passward']):
            # set session
            session['user'] = username
            posts=contribute.query.all()
            return render_template('/contributions.html',params=params,posts=posts)
    else:
        return render_template('login.html',params=params)
    return render_template('login.html',params=params)


@app.route("/contri/<string:sno>", methods=['GET', 'POST'])
def contris(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = contribute.query.filter_by(sno=sno).first()
        return render_template('edit.html',params=params,post = post,sno=sno)



@app.route("/compiler")
def compiler():
    return render_template('compiler.html',params=params)

@app.route("/compilers/cpp")
def cpp():
    return render_template('compilers/cpp.html',params=params)

@app.route("/compilers/python")
def python():
    return render_template('compilers/python.html',params=params)

@app.route("/compilers/java")
def java():
    return render_template('compilers/java.html',params=params)

@app.route("/compilers/sqls")
def sqls():
    return render_template('compilers/sqls.html',params=params)


@app.route("/compilers/javascripts")
def javascript():
    return render_template('compilers/javascripts.html',params=params)


@app.route("/compilers/chash")
def chash():
    return render_template('compilers/chash.html',params=params)


@app.route("/compilers/clanguage")
def c():
    return render_template('compilers/clanguage.html',params=params)


@app.route("/compilers/kotlin")
def kotlin():
    return render_template('compilers/kotlin.html',params=params)


@app.route("/compilers/swift")
def swift():
    return render_template('compilers/swift.html',params=params)

@app.route("/compilers/ruby")
def ruby():
    return render_template('compilers/ruby.html',params=params)

@app.route("/compilers/dotnet")
def dotnet():
    return render_template('compilers/dotnet.html',params=params)

@app.route("/compilers/go")
def go():
    return render_template('compilers/go.html',params=params)

@app.route("/compilers/pascal")
def pascal():
    return render_template('compilers/pascal.html',params=params)

@app.route("/compilers/text")
def text():
    return render_template('compilers/text.html',params=params)


app.run(debug=True)

import secrets
import os
from donors.models import User, Post 
from donors import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from donors.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, NeedBlood
from flask_login import login_user, current_user, logout_user, login_required
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Say

@app.route("/")
@app.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm();
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user = User(username = form.username.data, email = form.email.data, bloodgroup = form.list_blood.data, phonenumber = form.phonenumber.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your Account Created {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form = form)


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/login", methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else(url_for('home'))
        else:
            flash('incorrect credentials', 'danger')

    return render_template('login.html', title='login', form=form)

@app.route("/admin", methods = ['GET', 'POST'])
def admin():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == "admin@bdm.com" and form.password.data == "tamilsel":
            return redirect(url_for('ahome'))
    return render_template('login.html', title='login', form=form)

@app.route("/ahome")
def ahome():
    details = User.query.all()
    return render_template('admin.html', details=details)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

    
@app.route("/account", methods = ['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phonenumber=form.phonenumber.data
        current_user.bloodgroup=form.list_blood.data
        db.session.commit()
        flash("your account has been updated", 'success')
        return redirect(url_for('account'))
    elif request.method =='GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.list_blood.data = current_user.bloodgroup
        form.phonenumber.data = current_user.phonenumber
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash('you post created successfully')
        return redirect(url_for('home'))    
    form = PostForm()
    return render_template('create_post.html', title='New Post', form=form, legend = "New Post")

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template ('post.html', title=post.title, post=post)


@app.route("/need", methods=['GET', 'POST'])
@login_required
def needed():
    form = NeedBlood()
    if form.validate_on_submit():
        details = User.query.filter_by(bloodgroup = form.list_blood.data)
        flash("Members Found", 'success')
        return render_template('search.html', details = details)
    return render_template('need.html', form = form)

@app.route("/emer/<string:blg>")
def search(blg):
    details = User.query.filter_by(bloodgroup=blg)
    if details:
        return render_template('search.html', details = details)
    else:
        return "Sorry no results found"
    
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
def updatepost(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('your post has been updated', 'success')
        return redirect(url_for('post', post_id = post.id))
    elif request.method == 'GET':       
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='update Post', form=form, legend = "Update Post")

@app.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def deletepost(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)    
    db.session.delete(post)
    db.session.commit()
    flash("your account has been deleted", 'success')
    return redirect(url_for('home'))

@app.route("/emer/<string:blg>/json")
def getjs(blg):
    details = User.query.filter_by(bloodgroup = blg)
    return jsonify(details =[detail.serialize for detail in details])

@app.route('/sendsms', methods=['POST'])
def sendsms():
    account_sid = '**************'
    auth_token = '************'
    client = Client(account_sid, auth_token)
    phonenumber = request.form['phonenumber']
    call = client.calls.create(
                        url="http://sankarankovil.com/res.xml",
                        to='+91' + phonenumber,
                        from_='+12*****'
                    )
    
    print(call.sid)
    return redirect(url_for('home'))    

@app.route('/sending', methods=['POST'])
def sending():
    account_sid = '****************'
    auth_token = '*************'
    client = Client(account_sid, auth_token)
    phonenumber = request.form['phonenumber']
    message = client.messages.create(
                              from_= '+12****',
                              body='test message',
                              to= '+91' + phonenumber
                              )
    print(message.sid)


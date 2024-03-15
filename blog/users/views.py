from flask import render_template,url_for,flash,redirect,request,Blueprint
from flask_login import login_user,current_user,logout_user,login_required
from blog import db
from blog.modles import User,BlogPost
from blog.users.forms import RegistrationForm,LoginForm,UpdateUserForm
from blog.users.picture_handler import add_profile_pic
import email_validator

users = Blueprint('users', __name__)


# Registration
@users.route('/register' , methods=['GET','POST'])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(email = form.email.data,
                    username= form.username.data,
                    password = form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Thank for registration')
        return redirect(url_for('users.login'))
    return render_template('register.html', form = form)
       
#login
@users.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            flash("Login Successful" , "success")
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('core.index')
            return redirect(next_page)
        else:
            flash("Invalid email or password. Please try again.", "error")
    return render_template('login.html', form=form)
 
# Logout
@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('core.index'))


#account
@users.route('/account',methods=['GET','POST'])
@login_required
def account():
    form = UpdateUserForm()
    if form.validate_on_submit():
        
        if form.email.data != current_user.email and User.query.filter_by(email=form.email.data).first():
            flash("Email already taken. Please choose a different one.", "user_error")
        elif form.username.data != current_user.usename and User.query.filter_by(usename=form.username.data).first():
            flash("Username already taken. Please choose a different one.", "user_error")
        else:
            if form.picture.data:
                username = current_user.usename
                pic = add_profile_pic(form.picture.data,username)
                current_user.profile_image = pic
            current_user.usename = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash("User account Updated", "user_success")
            return redirect(url_for('users.account'))
    
    elif request.method =='GET':
        form.username.data = current_user.usename
        form.email.data = current_user.email
    profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image)
    return render_template('account.html', profile_image = profile_image, form = form)

@users.route("/<username>")
def user_post(username):
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(usename=username).first_or_404()
    blog_post = BlogPost.query.filter_by(author=user).order_by(BlogPost.date.desc()).paginate(page=page,per_page=5)

    return render_template('user_blog_posts.html', blog_posts=blog_post,user=user)
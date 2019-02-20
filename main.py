from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@127.0.0.1:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'abc123'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_entry = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog_title, blog_entry, owner):
        self.blog_title = blog_title
        self.blog_entry = blog_entry
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    owner = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email=email
        self.password=password

@app.before_request
def require_login():
    not_allowed_routes = ['newpost']
    if request.endpoint in not_allowed_routes and 'email' not in session:
         return redirect('/login')


@app.route('/singleUser')
def single_user():
    single_user_blog = int(request.args.get('user'))
    single_user_entries = Blog.query.filter_by(owner_id=single_user_blog).all()
    owners = User.query.filter_by(id=single_user_blog).all()
    return render_template('singleUser.html',title="Single User's Blog", single_user_blog=single_user_blog, single_user_entries=single_user_entries,owners=owners)



@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            #remember that the user has logged in
            session['email'] = email
            flash('Logged in!')
            return redirect('/newpost')
        elif not user:
            flash('User does not exist', 'error')
        else:
            flash('User password incorrect','error')

    return render_template('login.html')

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify_password']


        #email needs @ and . followed by extension and 3-30 char long
        if len(email) < 3 or len(email) > 30 or '@' not in email or '.' not in email:
            username = form.format(username)
            email = ''
            flash('This is not a valid email.','error')
            return render_template('register.html')
        #need pw to be at least 3-20 char long
        if len(password) < 3 or len(password) > 20:
            flash('Your password must be between 3 and 20 characters','error')
            return render_template('register.html')
        #need verify==pw
        if verify != password:
            flash('Verify password must match your password','error')
            return render_template('register.html')

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email,password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/newpost')

        else:
            flash('User already exists', 'error')
            return render_template('register.html', title='Register')

    return render_template('register.html', title='Register')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/newpost', methods=['POST','GET'])
def new_post():
    owner = User.query.filter_by(email=session['email']).first()

    if request.method =='POST':
        blog_title = request.form['blog-title']
        blog_entry = request.form['blog-entry']
        if len(blog_title) == 0:
            flash('You must give this entry a title', 'error')
            return render_template('newpost.html',title='New Post')

        elif len(blog_entry) == 0:
            flash('You must write an entry', 'error')
            return render_template('newpost.html',title='New Post')
        else:
            new_blog = Blog(blog_title, blog_entry, owner)
            db.session.add(new_blog)
            db.session.commit()
            id = str(new_blog.id)
            new_url = '/blog?id='+id
            return redirect(new_url)

    return render_template('newpost.html',title='New Post')

@app.route('/blog', methods=['POST','GET'])
def list_blogs():
    owner = User.query.filter_by(email=session['email']).first()
    blogs = Blog.query.all()
    # all_blogs = Blog.query.all()
    single_blog = int(request.args.get('id'))
    single_blog_entry = Blog.query.filter_by(id=single_blog).all()

    return render_template('blog.html',title='Build A Blog',single_blog_entry=single_blog_entry, single_blog=single_blog, blogs=blogs, owner=owner, all_blogs=all_blogs)

@app.route('/', methods=['POST','GET'])
def index():
    usernames = User.query.all()

    return render_template('index.html',title='Home',usernames=usernames)

if __name__ == '__main__':
    app.run()

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory, current_app
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr.auth import login_required
from flaskr.db import get_db

import os

ALLOWED_EXTENSIONS = set(["png", "jpg", "jpge", "jpeg"])

bp = Blueprint('blog', __name__)

@bp.route('/')
def home():
    return render_template('blog/home.html')

@bp.route('/index')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username, address, size, price, url, image'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/about')
def about():
    return render_template('blog/about.html')

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        address = request.form['address']
        size = request.form['size']
        url = request.form['url']
        price = request.form['price']
        image = request.files['image']
       
        error = None

        if not title:
            error = 'Title is required.'
        elif not address: 
        	error = 'Address is required'
        elif not size:
        	error = 'Size is required'
        elif not image:
            error = 'Image is required'
        elif not url:
            error = 'URL is required'
        elif not price: 
            error = 'Price is required'

        if error is not None:
            flash(error)
        else:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id, address, size, price, url, image)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (title, body, g.user['id'], address, size, price, url, filename)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

@bp.route("/static/<filename>")
def get_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username, address, size, price, url, image'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        address = request.form['address']
        size = request.form['size']
        price = request.form['price']
        url = request.form['url']
        image = request.form['image']
        error = None

        if not title:
            error = 'Title is required.'
        elif not address:
        	error = 'Address is required'
        elif not size:
        	error = 'Size is required'
        elif not url:
            error = 'URL is required'
        elif not image:
            error = 'Image is required'
        elif not price:
            error = 'Price is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?, address = ?, size = ?, price = ?, url = ?, image = ?'
                ' WHERE id = ?',
                (title, body, address, size, price, url, image, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

@bp.route('/post/<int:id>/', methods=('GET', 'POST'))
@login_required
def post(id):
    post=get_post(id)
    return render_template('blog/post.html', post=post)

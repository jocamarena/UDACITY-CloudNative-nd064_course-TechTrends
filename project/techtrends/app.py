import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

get_db_connection_count = 0
get_db_post_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global get_db_connection_count
    get_db_connection_count += 1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    global get_db_post_count
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    get_db_post_count = len(posts)
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.error("Article by id:{0} was not found, 404.".format(post_id))
      return render_template('404.html'), 404
    else:
      app.logger.debug("Article by id:{0} title:{1} was found, 200.".format(post_id, post['title']))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.debug("About  found, 200")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
            app.logger.error("Post saved without title, 500.")
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.debug("Post created with title:{0}, 201.".format(title))
            return redirect(url_for('index'))

    # app.logger.debug("post created title:{0} , 201".format(title))
    # app.logger.debug("Post created with title:{0}, 201.".format(title))
    return render_template('create.html')

#health endpoint
@app.route('/healthz')
def health():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.debug("healthz endpoint selected, 200")
    return response

@app.route('/metrics')
def metrics():
    response = app.response_class(
            response=json.dumps({"db_connection_count": get_db_connection_count, "post_count": get_db_post_count}),
            status=200,
            mimetype='application/json'
    )
    app.logger.debug("metrics endpoint selected, 200")
    return response


# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(filename='app.log',
                       format='%(asctime)s - %(levelname)s - %(message)s', 
                       datefmt='%Y-%m-%d %H:%M:%S',
                       level=logging.DEBUG)
   


   handler = logging.StreamHandler(sys.stdout)
   handler.setLevel(logging.DEBUG)  # Set the desired log level
   formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
   handler.setFormatter(formatter)

   handler_err = logging.StreamHandler(sys.stderr)
   handler_err.setLevel(logging.ERROR)
   handler_err.setFormatter(formatter)

   app.logger.addHandler(handler)
   app.logger.addHandler(handler_err)

   app.run(host='0.0.0.0', port='3111')

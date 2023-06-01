import os
from flask import Flask, render_template, request, make_response, g, url_for, flash, redirect
from redis import Redis
import socket
import random
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'derp')

color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#2980b9",
    "blue2": "#30336b",
    "pink": "#be2edd",
    "darkblue": "#130f40"
}

messages = [{'title': 'Message One', 'content': 'Message One content'}, {'title': 'Message Two', 'content': 'Message Two Content'}]

color = os.environ.get('APP_COLOR') or random.choice(["red","green","blue","blue2","darkblue","pink"])

redis_password = os.getenv('REDIS_PASSWORD', 'derp')

def is_redis_available(g):
    try:
        g.ping()
        print("Successfully connected to redis")
    except (redis.exceptions.ConnectionError, ConnectionRefusedError):
        print("Redis connection error!")
        return False
    return True

def get_redis():
    if not hasattr(g, 'redis'):
        print("Connecting to redis db")
        g.redis = Redis(host="redis-2", db=0, password=redis_password, socket_timeout=5, decode_responses=True)

    #is_redis_available(g.redis)
    return g.redis

@app.route("/index")
def index():
    return render_template("index.html", messages=messages)

@app.route("/")
def main():
    #return 'Hello'
    print(color)
    return render_template('hello.html', name=socket.gethostname(), color=color_codes[color])

@app.route('/redis')
def redis():
    g = get_redis()
    g.set("test","run")
    f = open("/data/testfile.txt", "a")
    f.write(g.get("test"))
    f.close()
    f = open("/data/testfile.txt")
    contents = f.read()
    return render_template('hello.html', name=socket.gethostname(), contents=contents, color=color_codes[color])

@app.route('/color/<new_color>')
def new_color(new_color):
    return render_template('hello.html', name=socket.gethostname(), color=color_codes[new_color])

@app.route('/read_file')
def read_file():
    f = open("./testfile.txt")
    contents = f.read()
    return render_template('hello.html', name=socket.gethostname(), contents=contents, color=color_codes[color])

@app.route('/read_mounted_file')
def read_file_2():
    f = open("/data/testfile.txt")
    contents = f.read()
    return render_template('hello.html', name=socket.gethostname(), contents=contents, color=color_codes[color])

@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        notes = request.form['notes']

        if not title:
            flash('Title is required!')
        elif not content:
            flash('Content is required!')
        else:
            messages.append({'title': title, 'content': content})
            return redirect(url_for('index'))

    return render_template('create.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8081")

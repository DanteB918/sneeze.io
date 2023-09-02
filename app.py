from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from flask_cors import CORS, cross_origin #Getting passed COR's policy
import requests #Used for decoding utf charset 8
from flask_assets import Environment, Bundle #SCSS compiler
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flaskwebgui import FlaskUI # import FlaskUI
from flask_socketio import SocketIO
from engineio.async_drivers import gevent


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

socketio = SocketIO(app, async_mode='gevent')

# socketio = SocketIO(app)
ui = FlaskUI(app=app, socketio=socketio, fullscreen=False, server="flask_socketio", width=800,height=600,)

app.config['ASSETS_DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=True)
    sneezes = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    def __repr__(self):
        return f'<Worker {self.firstname}>'


title = "Sneeze.io"
location = os.getcwd() #Get current working directory

CORS(app) #Allow headers from anywhere

assets = Environment(app)
print(location + '\\assets')

scss = Bundle('custom.scss', filters='pyscss', output='custom.css')

assets.config['SECRET_KEY'] = 'secret!'
assets.config['PYSCSS_LOAD_PATHS'] = assets.load_path
assets.config['PYSCSS_STATIC_URL'] = assets.url
assets.config['PYSCSS_STATIC_ROOT'] = assets.directory
assets.config['PYSCSS_ASSETS_URL'] = assets.url
assets.config['PYSCSS_ASSETS_ROOT'] = assets.directory

assets.register('scss_all', scss)
with app.app_context():
    db.create_all()



@app.route("/", methods=['GET', 'POST', 'OPTIONS'],)
def hello_world(title=title): #Sign up
    if request.method == 'POST':
        newWorker = Worker(
            firstname = request.form.get('firstname'),
            lastname = request.form.get('lastname'),
            sneezes = 0
        )
        db.session.add(newWorker)
        db.session.commit()

        workers = Worker.query.all()
        return redirect(url_for('chart'))
    else:
        return render_template('index.html', title=title)

@app.route("/chart", methods=['GET', 'POST', 'OPTIONS'],)
def chart(title=title): #Sign up
        workers = Worker.query.all()
        return render_template('app.html', workers=workers, title=title)
    
@app.post("/clear")
def clear_ppl():
    Worker.query.delete()
    db.session.commit()
    return jsonify([True])

@app.post("/decrease/<id>")
def decrease_sneezes(id):
    worker = Worker.query.get(id)
    worker.sneezes -= 1
    db.session.commit()
    return jsonify([worker.sneezes])

@app.post("/increase/<id>")
def increase_sneezes(id):
    worker = Worker.query.get(id)
    worker.sneezes += 1
    db.session.commit()
    return jsonify([worker.sneezes])

@app.errorhandler(Exception)
def exception_handler(error):
    return "!!!!"  + repr(error)

if __name__ == '__main__':
    #socketio.run(app)
    ui.run()
from flask import Flask
from flask_sslify  import SSLify
from flask.ext.mongoengine import MongoEngine
from pymongo import MongoClient
from flask_wtf.csrf import CsrfProtect
from flask.ext.login import LoginManager

app = Flask(__name__)
UPLOAD_FOLDER = "uploads/"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CsrfProtect(app)
app.config["SECRET_KEY"] = "secret"
conn = MongoClient('mongodb://127.0.0.1:27017')
db = conn.test
lm = LoginManager()
lm.init_app(app)
lm.login_view = '/'



from app import routes


if __name__ == '__main__':
  app.run(debug=True)
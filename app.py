import os
import secrets
import traceback

from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

from helpers import *

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
api = Api(app)
# database
app.config["SECRET_KEY"] = '9bbd8f44c4ec734042fd241973766449'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///app.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['UPLOAD_FOLDER'] = "files/"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# init db
db = SQLAlchemy(app)
# init ma
ma = Marshmallow(app)
# init bcrypt
bcrypt = Bcrypt(app)



class HelloWorld(Resource):
    def get(self):
        data={"data":"Hello World"}
        return data
  
api.add_resource(HelloWorld,'/hello')

# run Server
if __name__ == '__main__':
    app.run(debug=True)

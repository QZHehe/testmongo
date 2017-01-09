import matplotlib
matplotlib.use('Agg')

import numpy as np
import simplejson as json
from bson import json_util
import cStringIO as StringIO
from skimage.io import imsave
from flask import Flask, render_template, request, make_response, send_file, redirect, url_for, Markup
import sys
import os
from urllib2 import unquote
from werkzeug.utils import secure_filename


repo_dirname = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, repo_dirname)
app = Flask(__name__)
#app.debug = False  # TODO: make sure this is False in production
app.debug = True
UPLOAD_FOLDER='static/Uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'gif', 'bmp', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

def make_json_response(body, status_code=200):
    print 'body:', body
    resp = make_response(json.dumps(body, default=json_util.default))
    resp.status_code = status_code
    resp.mimetype = 'application/json'
    return resp


@app.route('/')
def index():
    return render_template(
        'hello.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)

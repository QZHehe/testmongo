# coding = utf-8
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
from collection import get_mongodb_collection
#testqqq_s
import image as rayleigh
import util
from bson import Binary
import cPickle
#testqqq_e


repo_dirname = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, repo_dirname)
app = Flask(__name__)
#app.debug = False  # TODO: make sure this is False in production
app.debug = True
UPLOAD_FOLDER='static/Uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'gif', 'bmp', 'jpeg', 'JPG'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

def make_json_response(body, status_code=200):
    print 'body:', body
    resp = make_response(json.dumps(body, default=json_util.default))
    resp.status_code = status_code
    resp.mimetype = 'application/json'
    return resp

collection = get_mongodb_collection()


@app.route('/')
def index():
    # sum numbers
    # results = collection.find().count()
    return render_template(
        'backstage.html')


@app.route('/main_mongo')
def main_mongo():
    # data = collection.find().limmit(3)
    #
    # return make_json_response({data: data})
    return render_template(
        'upload.html')

@app.route('/getimage')
def getimage():
    results = []
    datas = collection.find(fields={'hist': False, 'spa_hist': False}).limit(20)
    for data in datas:
        results.append(data)
    return make_json_response({'results': results})


@app.route('/post_mongo_image', methods=['POST'])
def post_mongo_image():
    file = request.files['myPhoto']
    if file and allowed_file(file.filename):
        fname=secure_filename(file.filename)
        # img = ImageUpload(file, filename)
        img = rayleigh.ImageMongo(file)
        # dui=img.dui
        # dui= "data:image/png;base64,"+dui
        hash = img.get_texture()
        hist = img.get_texture()
        bson_hist = Binary(cPickle.dumps(hist, protocol=2))
        bson_spa_hist = bson_hist
        img_data = dict(img.as_dict().items() + {'hist': bson_hist}.items() + {'spa_hist': bson_spa_hist}.items())
        collection.insert(img_data)

    return render_template(
        'upload.html')


@app.route('/delete_image', methods=['POST'])
def delete_image():
    id = request.values['id']
    collection.remove({"id": id})
    return make_json_response({'results': True})





if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)

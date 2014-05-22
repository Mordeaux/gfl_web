"""
Created Fall 2013

@author: Michael Mordowanec (Mordeaux)
"""
import sys
import os
import codecs
import json
import time
import glob

from flask import Flask, render_template, request, redirect, send_file, url_for
from flask.ext.login import LoginManager, login_required, login_user, current_user

from conf import *

sys.path.insert(0, filename)
import view
from functions import *
from forms import LoginForm, UploadForm
from gfl_web import GFLWeb
from user import User

project = GFLWeb()

login_manager = LoginManager()
app = Flask(__name__)

login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(userid):
    return User.get(userid)

@app.route("/")
@login_required
def home():
    return render_template('index.html', userDict=current_user.load(), 
                           username=current_user.get_id())


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    validates = request.method == 'POST' and form.validate()
    if validates and User.check_password(request.form.get('username'), request.form.get('password')):
        login_user(User(request.form.get('username')))
        return redirect(request.args.get("next") or url_for("home"))
    return render_template('login.html', form=form)


@app.route('/annotate')
@login_required
def annotate():
    return render_template('annotate.html',  
                           c=current_user.get_current_anno(), 
                           username=current_user.get_id())


@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin():
        return 'Not Authorized', 500
    project.updateDatasets()
    with codecs.open(os.path.join(DIRECTORY, 'metaData.json'), 'r', 'utf-8') as f:
        assignments = json.loads(f.read())['assignments']
    return render_template('admin.html', users=User.get_user_list(), 
                           assignments=assignments, username=current_user.get_id())


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if not current_user.is_admin():
        return 'Not Authorized', 500
    form = UploadForm(request.form)
    if form.validate_on_submit():
        #save and process it
        pass
    return render_template('upload.html', form=form)
    

@app.route('/api/setCurrent')
@login_required
def setCurrent():
    dataset = request.args.get('dataset')
    batch = request.args.get('batch')
    current_user.set_current_anno(dataset, str(batch))
    return 'OK',200


@app.route('/api/getBatch')
@login_required
def getBatch():
    annoDic = current_user.load()
    if request.args.get('dataset') == 'new':
        return json.dumps({'0':{'id':int(time.time()), 'sent':'', 'anno':'', 
                       'last':True, 'number':0, 'userAdd':True, 'analyzed':[], 
                       'accessed':[], 'submitted':[], 'pos':None}, 
                       '1':'', '2':'', '3':''})
    return json.dumps(annoDic[request.args.get('dataset')][request.args.get('batch')])


@app.route('/api/updateBatch', methods=['POST'])
@login_required
def updateBatch():
    if current_user.get_current_anno()[0] == 'new':
        return 'OK',200
    annoDic = current_user.load()
    newBatch = json.loads(request.form.get('batch'))
    annoDic[current_user.get_current_anno()[0]][current_user.get_current_anno()[1]] = newBatch
    current_user.save(annoDic)
    return 'OK',200


@app.route('/api/submit', methods=['POST'])
@login_required
def submit():
    if current_user.get_current_anno()[0] in ['training', 'new']:
          return 'OK',200
    with codecs.open(os.path.join(OUTPUT_DIR, current_user.get_current_anno()[0]+'_'+current_user.get_id()+OUTPUT), 'a', 'utf-8') as f:
        f.write(request.form.get('anno'))
        f.write('\n')
    x = True
    batch = current_user.load()[current_user.get_current_anno()[0]][current_user.get_current_anno()[1]]
    for anno in batch:
        if anno not in ['assignedTo', 'locked']:
            if not batch[anno]['submitted']:
                x = False
    if x:
        with codecs.open(os.path.join(DATA_DIR, current_user.get_current_anno()[0]+'.json'), 'r', 'utf-8') as f:
            dataset = f.readlines()
            batch = json.loads(dataset[int(current_user.get_current_anno()[1])])
        for name in batch['assignedTo']:
            if name == current_user.get_id():
                batch['assignedTo'][batch['assignedTo'].index(name)] = name + ' (completed)'
        dataset[int(current_user.get_current_anno()[1])] = json.dumps(batch) + '\n'
        with codecs.open(os.path.join(DATA_DIR, current_user.get_current_anno()[0]+'.json'), 'w', 'utf-8') as f:
            for line in dataset:
                f.write(line)
    return 'OK',200


@app.route('/api/analyzegfl.png', methods=['GET'])
@login_required
def analyze(): 
    sent = request.args.get('sentence')
    annotation = request.args.get('anno')
    preproc = u'% TEXT\n{0}\n% ANNO\n{1}'.format(sent, annotation)
    with codecs.open(os.path.join(TEMP_DIR, current_user.get_id()+'.txt'), 'w', 'utf-8') as f:
        f.write(preproc)
    try: 
        view.main([os.path.join(TEMP_DIR, current_user.get_id()+'.txt')])
        return send_file(os.path.join(TEMP_DIR, current_user.get_id()+'.0.png'), mimetype='image/png')
    except Exception as ex:
        return str(ex), 500 

		
@app.route('/api/assign')
@login_required
def assign():
    if not current_user.is_admin():
        return 'Not Authorized', 500
    dataset = request.args.get('dataset')
    batch = int(request.args.get('batch'))
    user = User.get(request.args.get('user'))
    with codecs.open(os.path.join(DATA_DIR, dataset+'.json'), 'r', 'utf-8') as f:
        lines = f.readlines()
    dic = json.loads(lines[batch])
    dic['assignedTo'].append(user.get_id())
    userDict = user.load()
    if dataset not in userDict:
        userDict[dataset] = {}
    assert str(batch-1) not in userDict[dataset] and str(batch+1) not in userDict[dataset]		
    userDict[dataset][str(batch)] = dic
    user.save(userDict)
    lines[batch] = json.dumps(dic) + '\n'
    with codecs.open(os.path.join(DATA_DIR, dataset+'.json'), 'w', 'utf-8') as f:
        for line in lines:
            f.write(line)
    with codecs.open(os.path.join(DIRECTORY, 'metaData.json'), 'r', 'utf-8') as f:
        meta = json.loads(f.read())
    meta['assignments'][dataset][str(batch)] = username
    with codecs.open(os.path.join(DIRECTORY, 'metaData.json'), 'w', 'utf-8') as f:
        f.write(json.dumps(meta))
    return 'OK',200

		
@app.route('/api/newUser')
def newUser(username=False):
    if not username:
        username = request.args.get('newUser')
    userDict = {}
    with codecs.open(os.path.join(DIRECTORY, 'training.json'), 'r', 'utf-8') as f:
        userDict['training'] = json.loads(f.read())
    with codecs.open(os.path.join(USER_DIR, username+'.json'), 'w', 'utf-8') as f:
        f.write(json.dumps(userDict))
    return 'OK', 200


@app.route('/api/admin')
@login_required
def apiAdmin():
    if not current_user.is_admin():
        return 'Not Authorized', 500
    if request.args.get('req') == 'submissions':
        dic = {}
        regex = r'(?:.*?/)+(.*?)_(.*?)'+OUTPUT
        for filename in glob.glob(os.path.join(OUTPUT_DIR, '*')):
            username = re.search(regex, filename).group(2)
            dataset = re.search(regex, filename).group(1)
            if username not in dic:
                dic[username] = {}
            if dataset not in dic[username]:
                dic[username][dataset] = {}
            with codecs.open(filename, 'r', 'utf-8') as f:
                dic[username][dataset] = [json.loads(line) for line in f.readlines()]
        return render_template('viewSubmissions.html', displayDict=dic, 
                           username=current_user.get_id())
    elif request.args.get('req') == 'assignments':
        dic = {}
        regex = r'(?:.*?/)+data/(.*?)\.json'
        for filename in glob.glob(os.path.join(DATA_DIR, '*.json')):
            dataset = re.search(regex, filename).group(1)
            with codecs.open(filename, 'r', 'utf-8') as f:
                dic[dataset] = [json.loads(line) for line in f.readlines()]
        return render_template('viewAssignments.html', dic=dic, 
                           username=current_user.get_id())
  

app.secret_key = SECRET_KEY

if __name__ == "__main__":
    directories = [DIRECTORY, DATA_DIR, OUTPUT_DIR, 
                   USER_DIR, PREPROC_DIR, TEMP_DIR]
    for directory in directories:
        if not os.path.exists(directory):
            os.mkdir(directory)
    if not os.path.isfile(os.path.join(DIRECTORY, 'training.json')):
        training()
    if glob.glob(os.path.join(DIRECTORY, 'users', '*.json')) == []:
        newUser(username='default')


    app.run(debug=True)

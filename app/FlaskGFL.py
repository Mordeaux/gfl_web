"""
Created Fall 2013

@author: Michael Mordowanec (Mordeaux)
"""
from flask import Flask, render_template, request, redirect, send_file, session
import sys, os, codecs, json, time, glob
dirname = os.path.dirname(__file__)
parentDir = os.path.abspath(os.path.join(dirname, os.path.pardir))
filename = os.path.join(parentDir, 'gfl_syntax', 'scripts')
sys.path.insert(0, filename)
import view
sys.path.insert(0, parentDir)
from config import *
DATA_DIR = os.path.join(DIRECTORY, 'data')
USER_DIR = os.path.join(DIRECTORY, 'users')
TEMP_DIR = os.path.join(DIRECTORY, 'temp')
OUTPUT_DIR = os.path.join(DIRECTORY, 'output')


app = Flask(__name__)

from functions import *

@app.route("/")
def home():
  if request.environ.get('REMOTE_USER') or request.args.get('REMOTE_USER'):
	  session['username'] = alias(request.environ.get('REMOTE_USER') or request.args.get('REMOTE_USER'))
  username = session.get('username')
  if not username:
    return 'Permission denied', 403
  return render_template('index.html', userDict=getUserDict(username), username=session['username'])

@app.route('/login')
def login():
  username = request.args.get('user')
  if not os.path.isfile(os.path.join(USER_DIR, username+'.json')):
    newUser(username=username)
  session['username'] = username
  return redirect('/')

@app.route('/annotate')
def annotate():
  username = session.get('username')
  if not username: return home()
  if not session.get('current'): return home()
  return render_template('annotate.html', newswire=NORMALIZATION_TASK, c=session.get('current'), username=session['username'])

@app.route('/admin')
def admin():
    if unicode(session['username']) not in ADMINS:
        return 'Not Authorized', 500
    updateDatasets()
    userlist = [re.search(USER_DIR+os.sep+r'(.*)\.json', file).group(1) for file in glob.glob(os.path.join(USER_DIR, '*.json'))]
    with codecs.open(os.path.join(DIRECTORY, 'metaData.json'), 'r', 'utf-8') as f:
        assignments = json.loads(f.read())['assignments']
    return render_template('admin.html', users=userlist, assignments=assignments, username=session['username'])

@app.route('/api/setCurrent')
def setCurrent():
  username = session.get('username')
  if not username: return home()
  dataset = request.args.get('dataset')
  batch = request.args.get('batch')
  session['current'] = (dataset, str(batch))
  print session.get('current')
  return 'OK',200

@app.route('/api/getBatch')
def getBatch():
  username = session.get('username')
  if not username: return home()
  annoDic = getUserDict(username)
  if request.args.get('dataset') == 'new':
    return json.dumps({'0':{'id':int(time.time()), 'sent':'', 'anno':'', 'last':True, 'number':0, 'userAdd':True, 'analyzed':[], 'accessed':[], 'submitted':[], 'pos':None}, '1':'', '2':'', '3':''})
  return json.dumps(annoDic[request.args.get('dataset')][request.args.get('batch')])

@app.route('/api/updateBatch', methods=['POST'])
def updateBatch():
  username = session.get('username')
  if not username: return home()
  if session.get('current')[0] == 'new':
    return 'OK',200
  annoDic = getUserDict(username)
  newBatch = json.loads(request.form.get('batch'))
  annoDic[session.get('current')[0]][session.get('current')[1]] = newBatch
  saveUserDict(username, annoDic)
  return 'OK',200

@app.route('/api/submit', methods=['POST'])
def submit():
  username = session.get('username')
  if not username: return home()
  if session.get('current')[0] in ['training', 'new']:
      return 'OK',200
  with codecs.open(os.path.join(OUTPUT_DIR, session.get('current')[0]+'_'+username+OUTPUT), 'a', 'utf-8') as f:
    f.write(request.form.get('anno'))
    f.write('\n')
  x = True
  batch = getUserDict(username)[session.get('current')[0]][session.get('current')[1]]
  for anno in batch:
    if anno not in ['assignedTo', 'locked']:
      if not batch[anno]['submitted']:
        x = False
  if x:
    with codecs.open(os.path.join(DATA_DIR, session.get('current')[0]+'.json'), 'r', 'utf-8') as f:
      dataset = f.readlines()
      batch = json.loads(dataset[int(session.get('current')[1])])
    for name in batch['assignedTo']:
      if name == username:
        batch['assignedTo'][batch['assignedTo'].index(name)] = name + ' (completed)'
    dataset[int(session.get('current')[1])] = json.dumps(batch) + '\n'
    with codecs.open(os.path.join(DATA_DIR, session.get('current')[0]+'.json'), 'w', 'utf-8') as f:
      for line in dataset:
        f.write(line)
  return 'OK',200

@app.route('/api/analyzegfl.png', methods=['GET'])
def analyze(): 
	username = session.get('username')
	sent = request.args.get('sentence')
	annotation = request.args.get('anno')
	preproc = u'% TEXT\n{0}\n% ANNO\n{1}'.format(sent, annotation)
	with codecs.open(os.path.join(TEMP_DIR, username+'.txt'), 'w', 'utf-8') as f:
		f.write(preproc)
	try: 
		view.main([os.path.join(TEMP_DIR, username+'.txt')])
		return send_file(os.path.join(TEMP_DIR, username+'.0.png'), mimetype='image/png')
	except Exception as ex:
		return str(ex), 500 
		
@app.route('/api/assign')
def assign():
  if not session.get('username'): return home()
  dataset = request.args.get('dataset')
  batch = int(request.args.get('batch'))
  username = alias(request.args.get('user'))
  with codecs.open(os.path.join(DATA_DIR, dataset+'.json'), 'r', 'utf-8') as f:
    lines = f.readlines()
  dic = json.loads(lines[batch])
  dic['assignedTo'].append(username)
  userDict = getUserDict(username)
  if dataset not in userDict:
    userDict[dataset] = {}
  assert str(batch-1) not in userDict[dataset] and str(batch+1) not in userDict[dataset]		
  userDict[dataset][str(batch)] = dic
  saveUserDict(username, userDict)
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
def apiAdmin():
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
    return render_template('viewSubmissions.html', displayDict=dic, username=session['username'])
  elif request.args.get('req') == 'assignments':
    dic = {}
    regex = r'(?:.*?/)+data/(.*?)\.json'
    for filename in glob.glob(os.path.join(DATA_DIR, '*.json')):
      dataset = re.search(regex, filename).group(1)
      with codecs.open(filename, 'r', 'utf-8') as f:
        dic[dataset] = [json.loads(line) for line in f.readlines()]
    return render_template('viewAssignments.html', dic=dic, username=session['username'])
  

	


app.secret_key = SECRET_KEY

if __name__ == "__main__":
    directories = [DIRECTORY, DATA_DIR, OUTPUT_DIR, USER_DIR, PREPROC_DIR, TEMP_DIR]
    for directory in directories:
        print directory
        if not os.path.exists(directory):
            os.mkdir(directory)
    if not os.path.isfile(os.path.join(DIRECTORY, 'training.json')):
        training()
    if glob.glob(os.path.join(DIRECTORY, 'users', '*.json')) == []:
        newUser(username='default')


    app.run(debug=True)

"""
Created Fall 2013

@author: Michael Mordowanec (Mordeaux)
"""

# may want to distinguish between username and name on system
#lock mode for particular batches, lets user see but not modify--not finished
#make it possible for admin to impersonate users--not finished

from flask import Flask, render_template, request, redirect, send_file, session
from functions import *
import sys, os, codecs, json, time, glob
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'gfl_syntax/scripts')
sys.path.insert(0, filename)
import view


OUTPUT = '_output.json' # Will be appended to usernames to create the output file name
NEWSWIRE = True # Toggles normalization task
DIRECTORY =os.path.join(dirname, 'app_data/') # The directory where the app will store its data.
ANNOTATIONS_PER_BATCH = 10 # Number of annotation units to be in each batch assigned to annotator
OVERLAP = 4 #how many annotations per batch will be doubly annotated, must be even number.

app = Flask(__name__)

@app.route("/")
def home():
  if request.environ.get('REMOTE_USER') or request.args.get('REMOTE_USER'):
	  session['username'] = alias(request.environ.get('REMOTE_USER') or request.args.get('REMOTE_USER'))
  username = session.get('username')
  if not username:
    return 'Permission denied', 403
  return render_template('index.html', userDict=getUserDict(username))

@app.route('/login')
def login():
  username = request.args.get('user')
  if not os.path.isfile(DIRECTORY+'users/'+username+'.json'):
    newUser(username=username)
  session['username'] = username
  return redirect('/')

@app.route('/annotate')
def annotate():
  username = session.get('username')
  if not username: return home()
  if not session.get('current'): return home()
  return render_template('annotate.html', newswire=NEWSWIRE, c=session.get('current'))

@app.route('/admin')
def admin():
	if unicode(session['username']) not in [u'mordo', u'nschneid', u'lingpenk']:
		return 'Not Authorized', 500
	updateDatasets()
	userlist = [re.search(r'users.(.*)\.json', file).group(1) for file in glob.glob(DIRECTORY+'users/*.json')]
	with codecs.open(DIRECTORY+'metaData.json', 'r', 'utf-8') as f:
		assignments = json.loads(f.read())['assignments']
	return render_template('admin.html', users=userlist, assignments=assignments)

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
  with codecs.open(DIRECTORY+'output/'+session.get('current')[0]+'_'+username+OUTPUT, 'a', 'utf-8') as f:
    f.write(request.form.get('anno'))
    f.write('\n')
  x = True
  batch = getUserDict(username)[session.get('current')[0]][session.get('current')[1]]
  for anno in batch:
    if anno not in ['assignedTo', 'locked']:
      if not batch[anno]['submitted']:
        x = False
  if x:
    print 'working'
    with codecs.open(DIRECTORY+'/data/'+session.get('current')[0]+'.json', 'r', 'utf-8') as f:
      dataset = f.readlines()
      batch = json.loads(dataset[int(session.get('current')[1])])
    for name in batch['assignedTo']:
      if name == username:
        print name
        print batch['assignedTo']
        print batch['assignedTo'].index(name)
        batch['assignedTo'][batch['assignedTo'].index(name)] = name + ' (completed)'
    dataset[int(session.get('current')[1])] = json.dumps(batch) + '\n'
    with codecs.open(DIRECTORY+'/data/'+session.get('current')[0]+'.json', 'w', 'utf-8') as f:
      for line in dataset:
        f.write(line)
  return 'OK',200

@app.route('/api/analyzegfl.png', methods=['GET'])
def analyze(): 
	username = session.get('username')
	sent = request.args.get('sentence')
	annotation = request.args.get('anno')
	preproc = u'% TEXT\n{0}\n% ANNO\n{1}'.format(sent, annotation)
	with codecs.open(DIRECTORY+'temp/'+username+'.txt', 'w', 'utf-8') as f:
		f.write(preproc)
	try: 
		view.main([DIRECTORY+'temp/'+username+'.txt'])
		return send_file(DIRECTORY+'temp/'+username+'.0.png', mimetype='image/png')
	except Exception as ex:
		return str(ex), 500 
		
@app.route('/api/assign')
def assign():
  if not session.get('username'): return home()
  dataset = request.args.get('dataset')
  batch = int(request.args.get('batch'))
  username = alias(request.args.get('user'))
  with codecs.open(DIRECTORY+'data/'+dataset+'.json', 'r', 'utf-8') as f:
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
  with codecs.open(DIRECTORY+'data/'+dataset+'.json', 'w', 'utf-8') as f:
    for line in lines:
      f.write(line)
  with codecs.open(DIRECTORY+'metaData.json', 'r', 'utf-8') as f:
    meta = json.loads(f.read())
  meta['assignments'][dataset][str(batch)] = username
  with codecs.open(DIRECTORY+'metaData.json', 'w', 'utf-8') as f:
    f.write(json.dumps(meta))
  return 'OK',200
		
@app.route('/api/newUser')
def newUser(username=False):
	if not username:
		username = request.args.get('newUser')
	userDict = {}
	with codecs.open(DIRECTORY+'training.json', 'r', 'utf-8') as f:
		userDict['training'] = json.loads(f.read())
	with codecs.open(DIRECTORY+'users/'+username+'.json', 'w', 'utf-8') as f:
		f.write(json.dumps(userDict))
	return 'OK', 200

@app.route('/api/admin')
def apiAdmin():
  if request.args.get('req') == 'submissions':
    dic = {}
    regex = r'(?:.*?/)+(.*?)_(.*?)'+OUTPUT
    for filename in glob.glob(DIRECTORY+'output/*'):
      username = re.search(regex, filename).group(2)
      dataset = re.search(regex, filename).group(1)
      if username not in dic:
        dic[username] = {}
      if dataset not in dic[username]:
        dic[username][dataset] = {}
      with codecs.open(filename, 'r', 'utf-8') as f:
        dic[username][dataset] = [json.loads(line) for line in f.readlines()]
    return render_template('viewSubmissions.html', displayDict=dic)
  elif request.args.get('req') == 'assignments':
    dic = {}
    regex = r'(?:.*?/)+data/(.*?)\.json'
    for filename in glob.glob(DIRECTORY+'data/*.json'):
      dataset = re.search(regex, filename).group(1)
      with codecs.open(filename, 'r', 'utf-8') as f:
        dic[dataset] = [json.loads(line) for line in f.readlines()]
    return render_template('viewAssignments.html', dic=dic)
  

	


app.secret_key = "$e\x1c~:\xa0\xf7\xcfK\xc6\xe3Nr\xae\x84\n'\x9a\x9f\x1f\xfaJ\xc7\x97"

if __name__ == "__main__":
	directories = [DIRECTORY, DIRECTORY+'data/', DIRECTORY+'output/', DIRECTORY+'users/', DIRECTORY+'preproc/', DIRECTORY+'temp/']
	for directory in directories:
		if not os.path.exists(directory):
			os.mkdir(directory)
	if not os.path.isfile(DIRECTORY+'training.json'):
		training()
	if glob.glob(DIRECTORY+'users/*.json') == []:
		newUser(username='default')


	app.run(debug=True)
    #app.run(debug=True) #in debug mode server reloads itself automatically on code changes. 
						#Do not use on the actual server, hackers can exploit it somehow to run arbitrary code
    


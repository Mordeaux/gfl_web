# may want to distinguish between username and name on system
#lock mode for particular batches, lets user see but not modify--not finished
#make it possible for admin to impersonate users--not finished
#json for each data set
#make separate directories for user data and output--not finished

from flask import Flask, render_template, request, send_file, redirect
from functions import *
import sys, os, codecs, json, time, glob
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'gfl_syntax/scripts')
sys.path.insert(0, filename)
import view

OUTPUT = '_output.json'
NEWSWIRE = True
DIRECTORY ='app_data/'
ANNOTATIONS_PER_BATCH = 10
OVERLAP = 4 #how many annotations per batch will be doubly annotated, must be even number.

app = Flask(__name__)

@app.route("/")
def home():
	return render_template("index.html", userDict=getUserDict(str(request.environ.get('REMOTE_USER'))))

@app.route("/n")
def newEntry():
	return render_template("annotate.html", c=('new', '0', 0), anno={'id':int(time.time()), 'sent':'', 'anno':'', 'last':True, 'number':0, 'userAdd':True, 'analyzed':[], 'accessed':[], 'submitted':[], 'pos':None}, newswire=False)

@app.route("/annotate/<dataset>/<int:b>/<int:i>", methods=['POST', 'GET'])
def goTo(dataset, b, i):
	if int(i)<0:
		i = 0
	username = alias(str(request.environ.get('REMOTE_USER')))
	annoDic = getUserDict(username)
	c = (dataset, str(b), str(i))
	annoDic['current'] = c
	anno = annoDic[dataset][str(b)][str(i)]
	
	if request.method == 'GET':
		anno['accessed'].append(int(time.time()))

	elif request.method == 'POST':
		anno['anno'] = request.form['anno'].strip()
		if NEWSWIRE:
			anno['newswire'] = request.form['newswire']
		anno['comment'] = request.form['comment']
		anno['submitted'].append(int(time.time()))
		anno['user'] = username
		if anno['userAdd']:
			anno['sent'] = request.form['sent'].strip()
		else:
			with codecs.open(DIRECTORY+'output/'+c[0]+'_'+username+OUTPUT, 'a', 'utf-8') as f:
				f.write(json.dumps(anno))
				f.write('\n')
		annoDic['current'] = (dataset, str(b), str(int(i)+1))
	saveUserDict(username, annoDic)
	c = (dataset, str(b), int(i))
	return render_template("annotate.html", c=c, anno=anno, t=int(time.time()), newswire=NEWSWIRE)

@app.route('/admin')
def admin():
	if unicode(request.environ.get('REMOTE_USER')) not in [u'mordo', u'nschneid', u'lingpenk', u'None']:
		return 'Not Authorized', 500
	updateDatasets()
	userlist = [re.search(r'users.(.*)\.json', file).group(1) for file in glob.glob(DIRECTORY+'users/*.json')]
	with codecs.open(DIRECTORY+'metaData.json', 'r', 'utf-8') as f:
		assignments = json.loads(f.read())['assignments']
	return render_template('admin.html', users=userlist, assignments=assignments)

@app.route('/api/analyzegfl.png', methods=['GET'])
def analyze(): 
	username = alias(str(request.environ.get('REMOTE_USER')))
	annoDic = getUserDict(username)
	c = annoDic['current']
	anno = annoDic[c[0]][c[1]][c[2]]
	sent = request.args.get('sentence')
	annotation = request.args.get('anno')
	preproc = u'% TEXT\n{0}\n% ANNO\n{1}'.format(sent, annotation)
	with codecs.open(DIRECTORY+'temp/'+username+'.txt', 'w', 'utf-8') as f:
		f.write(preproc)
	anno['analyzed'].append(int(time.time()))
	try: 
		view.main([DIRECTORY+'temp/'+username+'.txt'])
		saveUserDict(username, annoDic)
		return send_file(DIRECTORY+'temp/'+username+'.0.png', mimetype='image/png')
	except Exception as ex:
		saveUserDict(username, annoDic)
		return str(ex), 500 


		
@app.route('/api/assign')
def assign():
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
	return '',200
		
@app.route('/api/newuser')
def newUser(username=False):
	if not username:
		username = request.args.get('newUser')
	userDict = {}
	with codecs.open(DIRECTORY+'training.json', 'r', 'utf-8') as f:
		userDict['training'] = json.loads(f.read())
	with codecs.open(DIRECTORY+'users/'+username+'.json', 'w', 'utf-8') as f:
		f.write(json.dumps(userDict))
	return '', 200


if __name__ == "__main__":
	directories = [DIRECTORY, DIRECTORY+'data/', DIRECTORY+'output/', DIRECTORY+'users/', DIRECTORY+'preproc/', DIRECTORY+'temp/']
	for directory in directories:
		if not os.path.exists(directory):
			os.mkdir(directory)
	if not os.path.isfile(DIRECTORY+'training.json'):
		training()
	if glob.glob(DIRECTORY+'users/*.json') == []:
		newUser(username='None')

	app.run(debug=True)
    #app.run(debug=True) #in debug mode server reloads itself automatically on code changes. 
						#Do not use on the actual server, hackers can exploit it somehow to run arbitrary code
    
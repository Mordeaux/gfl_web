import re, codecs, json, time, os, sys, glob
from FlaskGFL import DIRECTORY, ANNOTATIONS_PER_BATCH, OVERLAP, USER_DIR, PREPROC_DIR, DATA_DIR

def training():
	sents = """Birds sing .
	We have been studying .
	Peter Pan's voice rang out gaily .
	Away sped Paul Revere's horse .
	The cattle were grazing peacefully in the meadow .
	Swiftly over the~1 dark waters sailed the~2 three little vessels .
	Red and white streamers fluttered from the~1 top of the~2 May-pole .
	Is June a~1 spring or a~2 summer month ?
	I like my next lesson , which is arithmetic .
	The fisherman who owned the boat now demanded payment .
	When he~1 saw me , he~2 stopped .
	The prettiest toy of~1 all was a little lady , who stood at the~1 open door of~2 the~2 castle .
	Jack~1 be~1 nimble , Jack~2 be~2 quick , Jack~3 jump over the candlestick .
	The sun smiles , and the~1 whole world returns the~2 smile .
	'Tis the prettiest little parlor that ever you did spy ."""

	anno = """Birds sing 
	We have been studying
	Peter Pan's voice rang out gaily
	Away sped Paul Revere's horse
	The cattle were grazing peacefully in the meadow
	Swiftly over the~1 dark waters sailed the~2 three little vessels
	Red and white streamers fluttered from the~1 top of the~2 May-pole
	Is June a~1 spring or a~2 summer month
	I like my next lesson which is arithmetic
	The fisherman who owned the boat now demanded payment
	When he~1 saw me he~2 stopped
	The prettiest toy of~1 all was a little lady who stood at the~1 open door of~2 the~2 castle
	Jack~1 be~1 nimble Jack~2 be~2 quick Jack~3 jump over the candlestick
	The sun smiles and the~1 whole world returns the~2 smile
	'Tis the prettiest little parlor that ever you did spy"""
	sents = sents.splitlines()
	anno = anno.splitlines()
	
	annoList = []

	for x,sent in enumerate(sents):
		dic = {
			'id':'training'+str(x),
			'pos':None,
			'sent':sent.strip(), 
			'anno':anno[x].strip(),
			'newswire':'', 'comment':'', 'last':False, 'number':x, 'userAdd':True,
			'analyzed': [], 'accessed':[], 'submitted':[], 'user':None,
			'dataset':'training'}
		annoList.append(dic)
	annoList[-1]['last'] = True
	chunk = {'assignedTo':[], 'locked':False}
	for i in range(len(annoList)):
		chunk[str(i)] = annoList[i]
	dic = {'0':chunk}
	with codecs.open(os.path.join(DIRECTORY, 'training.json'), 'w', 'utf-8') as f:
		f.write(json.dumps(dic))

def addDataSet(preproc, sizeOfBatch=10, overlap=4):
	"""Takes a .preproc path as string. sizeOfBatch is the number of annotations per batch to be assigned. overlap must be even. Sometimes fails on EOL issues."""
	assert sizeOfBatch > overlap
	assert overlap%2 == 0
	assert os.path.isfile(preproc)
	print sizeOfBatch
	datasetName = re.search(r'.*preproc.(.*)\.preproc', preproc).group(1)
	print datasetName
	text = ''.join(codecs.open(preproc, 'r', 'utf-8').readlines())
	assert not os.path.isfile(os.path.join(DATA_DIR, datasetName+'.json'))
	preprocList = re.findall(r'---\n.*?(?=---\n|$)', text, re.DOTALL)

	annoList = []
	for i,anno in enumerate(preprocList):
		if '% POS TEXT' in anno:
			pos = re.search(r'% POS TEXT\n+(.*?)\n+% TEXT', anno).group(1)
		else:
			pos = None
		dic = {
				'id':re.search(r'\n+% ID (.*?)\n+', anno).group(1),
				'pos':pos,
				'sent':re.search(r'% TEXT\n+(.*?)\n+% ANNO', anno).group(1), 
				'anno':re.search(r'% ANNO\n+(.*?)$', anno, re.DOTALL).group(1),
				'newswire':'', 'comment':'', 'last':False, 'number':i, 'userAdd':False,
				'analyzed': [], 'accessed':[], 'submitted':[], 'user':None,
				'dataset':datasetName
				}
		annoList.append(dic)
	annoList[-1]['last'] = True
	with codecs.open(os.path.join(DATA_DIR, datasetName+'.json'), 'w', 'utf-8') as f:
		while len(annoList) > sizeOfBatch * 1.5:
			chunk = {'assignedTo':[], 'locked':False}
			for i in range(sizeOfBatch):
				chunk[str(i)] = annoList[i].copy()
			chunk[str(sizeOfBatch-1)]['last'] = True
			f.write(json.dumps(chunk)+'\n')
			annoList = annoList[sizeOfBatch-(overlap/2):]
		chunk = {'assignedTo':[], 'locked':False}
		for i in range(len(annoList)):
			chunk[str(i)] = annoList[i]
		f.write(json.dumps(chunk))


def updateMetaData():
    """Assignments, aliases."""
    meta = {'assignments':{}, 'aliases':{}}
    if os.path.isfile(os.path.join(DIRECTORY, 'metaData.json')):
        meta = json.loads(codecs.open(os.path.join(DIRECTORY, 'metaData.json'), 'r', 'utf-8').read())
    for file in glob.glob(os.path.join(DATA_DIR, '*.json')):
        datasetName = re.search(DATA_DIR+os.sep+r'(.*)\.json', file).group(1)
        if datasetName not in meta['assignments']:
            with codecs.open(file, 'r', 'utf-8') as f:
                dataset = f.readlines()
            meta['assignments'][datasetName] = {}
            for i in range(len(dataset)):
                meta['assignments'][datasetName][str(i)] = ''
    with codecs.open(os.path.join(DIRECTORY, 'metaData.json'), 'w', 'utf-8') as f:
        f.write(json.dumps(meta))


def updateDatasets():
    for file in glob.glob(os.path.join(PREPROC_DIR, '*.preproc')):
        jsonPath = os.path.join(DATA_DIR, re.search(r'.*preproc.(.*)\.preproc', file).group(1)+'.json')
        if not os.path.isfile(jsonPath):
            addDataSet(file, sizeOfBatch=ANNOTATIONS_PER_BATCH, overlap=OVERLAP)
    updateMetaData()


def getUserDict(username):
	with codecs.open(os.path.join(USER_DIR, alias(username)+'.json'), 'r', 'utf-8') as f:
		annoDic = json.loads(f.read())
		return annoDic
		
def saveUserDict(username, annoDic):
	with codecs.open(os.path.join(USER_DIR, alias(username)+'.json'), 'w', 'utf-8') as f:
		f.write(json.dumps(annoDic))
		


def alias(username):
	return username
		

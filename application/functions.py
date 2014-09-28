import codecs
import json
import os

from . import DIRECTORY

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


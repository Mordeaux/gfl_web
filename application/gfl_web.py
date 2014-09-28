import re
import codecs
import json
import os
import glob

from config import *

class GFLWeb(object):



    def addDataSet(preproc, sizeOfBatch=10, overlap=4):
        """Takes a .preproc path as string. sizeOfBatch is the number of 
        annotations per batch to be assigned. overlap must be even. Sometimes 
        fails on EOL issues."""
        assert sizeOfBatch > overlap
        assert overlap%2 == 0
        assert os.path.isfile(preproc)
        print sizeOfBatch
        datasetName = re.search(r'.*preproc.(.*)\.preproc', preproc).group(1)
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
                   'newswire':'', 'comment':'', 'last':False, 'number':i, 
                   'userAdd':False, 'analyzed': [], 'accessed':[], 
                   'submitted':[], 'user':None, 'dataset':datasetName
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

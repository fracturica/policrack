

import shelve
import os
import errors
import numpy as np


def getMessageFilePaths():
    filePath = os.path.abspath(__file__)
    dirName = os.path.dirname(filePath)
    filesDir = os.path.join(dirName, 'messages')
    fileNames = os.listdir(filesDir)
    filePaths = []
    for fn in fileNames:
        filePaths.append(os.path.join(filesDir, fn))
    return filePaths


def checkLine(l):
    if 'saveMdb' in l:
        return True
    if 'Number of nodes merged out:' in l:
        return True
    return False


def filterLine(line):
    l = line.rstrip('\n').rstrip('\r')
    if 'saveMdb' in l:
        a, b = l.split(' ')
    elif 'Number of nodes merged out:' in l:
        a, b = l.split(': ')
    return b


def extractDataFromFile(filePath):
    with open(filePath, 'r') as f:
        data = f.readlines()
    info = []
    for l in data:
        if checkLine(l):
            l = filterLine(l)
            info.append(l)
    data = []
    for i in range(len(info)):
        if (i % 3) == 0:
            a = []
        a.append(info[i])
        if (i % 3) == 2:
            data.append(a)
    return data


def getDataFromFiles():
    reps = []
    for path in getMessageFilePaths():
        reps = reps + extractDataFromFile(path)
    return np.array(reps)


def updateShelveEntries():
    dbPath = errors.getDbPath()
    db = shelve.open(dbPath)
    try:
        manipulateShelve(db)
    finally:
        db.close()


def manipulateShelve(db):
    keys = db.keys()
    keys.remove('metadata')
    reps = getDataFromFiles()
    keysToDel = []
    keysModified = []
    for k in keys:
        analysis = db[k]
        analysisType = analysis['input']['analysisType']
        if (k not in reps[:, 2]) and analysisType == 'FEM':
            keysToDel.append(k)
        else:
            i = list(reps[:, 2]).index(k)
            a = int(reps[i][0])
            b = int(reps[i][1])
            analysis['reports']['mesh']['icsNodeMerge'] = [a, b]
            if a != b:
                analysis['reports']['mesh']['successfulAnalysis'] = False
            db[k] = analysis
            print reps[i], 'analysis {0} modified'.format(k)
            keysModified.append(k)

    confirm = ''
    while confirm not in ['y', 'n']:
        confirm = raw_input(
            'Delete {0} simulations? [y/n]: '.format(len(keysToDel)))
    if confirm == 'y':
        for k in keysToDel:
            del db[k]
        print 'keys deleted: ', len(keysToDel)
    else:
        print 'nothing deleted'
    print 'keys modified: ', len(keysModified)


if __name__ == '__main__':
    updateShelveEntries()

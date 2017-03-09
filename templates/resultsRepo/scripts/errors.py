

import shelve
import pickle
import os


def getDbPath():
    filePath = os.path.abspath(__file__)
    fileDir = os.path.dirname(filePath)
    (head, tail) = os.path.split(fileDir)
    (dbRepo, dbName) = os.path.split(head)

    resultsDb = os.path.join(head, 'resultsDb')
    shelvePath = os.path.join(resultsDb, dbName)
    return shelvePath


def getPicklePaths():
    filePath = os.path.abspath(__file__)
    fileDir = os.path.dirname(filePath)
    pickleDir = os.path.join(fileDir, 'inputPickleFiles')
    picFileNames = os.listdir(pickleDir)
    picklePaths = []
    for fileName in picFileNames:
        picklePaths += os.path.join(pickleDir, fileName),
    return picklePaths


def printPickleContents():
    picklePath = getPicklePaths()[0]
    print picklePath
    pickleFile = open(picklePath, 'rb')
    print pickleFile
    data = pickle.load(pickleFile)
    pickleFile.close()
    print data['reports']


def updateDbWithEntriesForFailedSimulations():
    picklePaths = getPicklePaths()
    dbPath = getDbPath()
    db = shelve.open(dbPath)
    for path in picklePaths:
        directory, fileName = os.path.split(path)
        simName, extension = fileName.split('.')
        print "checking simulation: ", simName
        if simName not in db.keys():
            print "entry not in database. Importing..."
            pickleFile = open(path, 'rb')
            data = pickle.load(pickleFile)
            pickleFile.close()
            data['reports']['successfulAnalysis'] = False
            db[simName] = data
            print "entry imported to the database."
        else:
            print "entry already in the database"
    db.close()
    print "done."


if __name__ == "__main__":
    updateDbWithEntriesForFailedSimulations()



import shelve
import pickle
import scripts.dataStr.femDataStr as femDataStr
import scripts.dataStr.xfemSimpleDataStr as xfemSimpleDataStr
import scripts.dataStr.xfemDataStrMP as xfemDataStrMP
import scripts.dataStr.xfemTETdataStr as xfemTETdataStr
import scripts.processOdb.readOdb as readOdb
import scripts.persistence.persistence as persistence


def extractData(**kargs):
    """
    """
    odbPath = kargs["odbPath"]
    odbName = kargs["odbName"]
    confFile = kargs["confFile"]
    outputDb = kargs["outputDb"]

    confFile = open(confFile, 'r')
    data = pickle.load(confFile)
    confFile.close()

    analysisType = data["input"]["analysisType"]
    modelType = data["input"]["modelType"]

    if analysisType == "FEM":
        dataStr = femDataStr.FEMdataStr()
    elif analysisType == "XFEM":
        if modelType == "simple":
            dataStr = xfemSimpleDataStr.XFEMsimpleDataStr()
        elif modelType == "crackPartition":
            dataStr = xfemTETdataStr.XFEMtetDataStr()
        elif modelType == "multiplePartitions":
            dataStr = xfemDataStrMP.XFEMdataStrMP()

    dataStr.setDataStr(data)
    odb = readOdb.ReadOdb(dataStr)
    db = persistence.PersistentData(dataStr)

    odb.openSpecificOdb(odbName, odbPath)
    odb.readHistoryOutputs()

    odb.extractValuesFromHistoryOutput()
    odb.calculateBetas()

    odb.sortData()
    odb.add360DegreeDataPoint()

    odb.writeOutputResultsToDataStr()

    db.specifyActiveShelve(outputDb)
    db.createDbMetadata()
    db.writeToDb()

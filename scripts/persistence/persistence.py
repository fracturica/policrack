

import shelve
import pickle
import os
import sharedFunctions
import info


class PersistentData:
    """
    """
    def __init__(self, inputData=None):
        """
        """
        self.inputData = inputData
        self.dbPath = sharedFunctions.getDbRepoDir()
        self.activeShelve = None
        self.data = {}

    def determineActiveShelve(self):
        """
        """
        crackType = self.inputData.getCrackType()
        self.activeShelve = self.shelves[crackType]

    def createDbMetadata(self):
        """
        """
        crackType = self.inputData.getCrackType()
        dataStr = self.inputData.getDataStr()

        historyOutputs = dataStr["input"]["interactionProperties"][
                "crack"]["historyOutputs"].keys()
        historyOutputs.sort()
        loadType = dataStr["input"]["createPredefinedLoads"]
        if loadType:
            loads = "infiniteBody"
        else:
            loads = "custom"
        self.metadata = {
            "crackType": crackType,
            "dbVersion": info.dbVersion,
            "historyOutputs": historyOutputs,
            "loads": loads,
            "description": ""}

    def verifyMetadataCompatibility(self):
        """
        """
        db = shelve.open(self.activeShelve)
        dbMeta = db["metadata"]
        db.close()
        dbMeta["historyOutputs"].sort()
        if self.metadata["crackType"] != dbMeta["crackType"]:
            return False
        elif self.metadata["loads"] != dbMeta["loads"]:
            return False
        elif self.metadata["dbVersion"] != dbMeta["dbVersion"]:
            return False
        elif self.metadata["historyOutputs"] != dbMeta["historyOutputs"]:
            return False
        else:
            return True

    def verifyActiveShelve(self):
        """
        """
        if (os.path.exists(self.activeShelve + ".dat") or
                os.path.exists(self.activeShelve)):
            if self.verifyMetadataCompatibility():
                return True
            else:
                raise Exception(
                    "Output database is incompatible with the analysis. \
                    Specify a different output database.")
        else:
            sharedFunctions.createResultsDirStr(self.dbName)
            db = shelve.open(self.activeShelve)
            db["metadata"] = self.metadata
            db.close()
            return True

    def specifyActiveShelve(self, dbName):
        """
        """
        self.dbName = dbName
        self.activeShelve = sharedFunctions.getDbPath(dbName)

    def readAll(self):
        """
        """
        data = {}
        db = shelve.open(self.activeShelve)
        for key in db.keys():
            data[key] = db[key]
        db.close()
        return data

    def writeToDb(self):
        """
        """
        self.prepareDataForShelving()
        key = self.inputData.getModelName()
        db = shelve.open(self.activeShelve)
        db[key] = self.picklingData
        db.close()

    def prepareDataForShelving(self):
        """
        """
        self.picklingData = self.inputData.getDataForPickling()

    def pickleConfFile(self):
        """
        """
        self.prepareDataForShelving()
        fileName = self.inputData.getOdbName() + ".pickle"
        confFile = open(fileName, 'wb')
        pickle.dump(self.picklingData, confFile)
        confFile.close()

    def checkForDuplicate(self):
        """
        """
        db = shelve.open(self.activeShelve)
        for key in db.keys():
            if db[key] == self.inputData:
                db.close()
                return True
        db.close()
        return False

    def getDuplicates(self):
        """
        """
        duplicateKeys = ()
        db = shelve.open(self.activeShelve)
        for key in db.keys():
            if db[key] == self.inputData:
                duplicateKeys += key,
        db.close()
        return duplicateKeys

    def readKey(self, key):
        """
        """
        db = shelve.open(self.activeShelve)
        data = db[key]
        db.close()
        return data

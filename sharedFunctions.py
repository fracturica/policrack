

import os
import shelve
import shutil
import info


def parseInput(fileName):
    """
    """
    config = open(fileName, 'r')

    try:
        textInput = []
        for line in config:
            if not line.isspace():
                line = line.rstrip().strip()
                if not line.startswith("#"):
                    textInput += line,
        print textInput
        parameters = {}

        for parameter in textInput:
            name, values = parameter.split(":")
            print parameter
            parameters[name.rstrip().strip()] = getValues(values)
        return parameters
    except:
        raise Exception("non-standard file format")


def getValues(vals):
    """
    """
    sepVals = []
    values = vals.split("#")[0]
    values = values.split(",")
    print values
    for val in values:
        val = val.strip().rstrip()
        try:
            val = float(val)
        except:
            pass
        sepVals += val,
    return sepVals


def createID(inputData, modelName):
    """
    """
    analysisType = inputData["analysisType"]
    if analysisType == "FEM":
        ID = createIDfem(inputData, modelName)
    if analysisType == "XFEM":
        ID = createIDxfem(inputData, modelName)
    return ID


def createIDfem(inputData, modelName):
    """
    """
    ID = {}
    ID["01_material"] = inputData["material"]["name"]

    a = inputData["crackParameters"]["a"]
    b = inputData["crackParameters"]["b"]
    crackRatio = "a/b = {0}/{1}".format(a, b)
    ID["02_crackRatio"] = crackRatio

    height = inputData["geometricParameters"]["containerHeight"]
    radius = inputData["geometricParameters"]["containerRadius"]
    geometry = "h{0}r{1}".format(height, radius)
    ID["03_geometry"] = geometry

    bc = ''
    for key in sorted(inputData["analysisParameters"].keys()):
        bc += key + str(inputData["analysisParameters"][key])
    ID["04_BCs"] = bc

    modelType = inputData["modelType"]
    ID["05_modelType"] = modelType

    meshTransform = inputData["meshParameters"]["transformationType"]
    ID["06_meshTransform"] = meshTransform

    elements = inputData["meshParameters"]["elements"]
    ID["07_elements"] = elements

    czm = inputData["seedParameters"]["crackZoneMainSeeds"]
    czr = inputData["seedParameters"]["crackZoneRefinementSeeds"]
    ar = inputData["seedParameters"]["arcSeeds"]
    cr = inputData["seedParameters"]["containerRefinementSeeds"]
    seeds = "czm{0}czr{1}ar{2}cr{3}".format(czm, czr, ar, cr)
    ID["08_seeds"] = seeds

    midNode = inputData["interactionProperties"]["crack"]["midNodePosition"]
    czs = inputData["geometricParameters"]["crackZoneSide"]
    cts = inputData["geometricParameters"]["crackTipSide"]
    miscParameters = "czs{0}cts{1}mn{2}".format(czs, cts, midNode)
    ID["09_miscParameters"] = miscParameters

    ID["10_modelName"] = modelName

    return ID


def createIDxfem(inputData, modelName):
    """
    """
    ID = {}
    ID["01_materialName"] = inputData["material"]["name"]

    a = inputData["crackParameters"]["a"]
    b = inputData["crackParameters"]["b"]
    crackRatio = "a/b = {0}/{1}".format(a, b)
    ID["02_crackRatio"] = crackRatio

    height = inputData["geometricParameters"]["containerHeight"]
    radius = inputData["geometricParameters"]["containerRadius"]
    geometry = "h{0}r{1}".format(height, radius)
    ID["03_geometry"] = geometry

    bc = ''
    for key in sorted(inputData["analysisParameters"].keys()):
        bc = bc + key + str(inputData["analysisParameters"][key])
    ID["04_BCs"] = bc

    modelType = inputData["modelType"]
    ID["05_modelType"] = modelType

    elements = inputData["meshParameters"]["elements"]
    ID["06_elements"] = elements

    seeds = ""
    for key in inputData["seedParameters"].keys():
        seeds += key[0] + "e" + str(inputData["seedParameters"][key])
    ID["07_seeds"] = seeds

    singularityCalcRadius = inputData["interactionProperties"][
        "crack"]["singularityCalcRadius"]
    ID["08_singularityRadius"] = str(singularityCalcRadius)

    if modelType == "multiplePartitions":
        smallContainerHeight = inputData[
            "geometricParameters"]["smallContainerHeight"]
        smallContainerOffset = inputData[
            "geometricParameters"]["crackFrontOffset"]
        ID["07a_miscParameters"] = ("h" + str(smallContainerHeight) +
                                    "offset" + str(smallContainerOffset))

    ID["09_modelName"] = modelName
    return ID


def getDbRepoDir():
    """
    """
    thisPath = os.path.abspath(__file__)
    thisDir = os.path.dirname(thisPath)
    dbRepoDir = os.path.join(thisDir, "db")
    return dbRepoDir


def getDbPath(dirName):
    """
    """
    dbRepo = os.path.join(getDbRepoDir(), dirName)
    dbPath = dbRepo + "\\resultsDb\\" + dirName
    return dbPath


def getListOfDbs():
    """
    """
    dbRepoDir = getDbRepoDir()
    dbRepos = os.listdir(dbRepoDir)
    dbNames = []
    for dirName in dbRepos:
        dirPath = os.path.join(dbRepoDir, dirName)
        if os.path.isdir(dirPath):
            if verifyIfRepo(dirName):
                dbNames += dirName,
    return dbNames


def verifyIfRepo(dirName):
    """
    """
    dbPath = getDbPath(dirName)
    print dbPath
    try:
        if verifyShelveVersionCompatibility(dbPath):
            return True
        else:
            return False
    except:
        return False


def verifyShelveVersionCompatibility(dbPath):
    """
    """
    metadata = False
    try:
        db = shelve.open(dbPath, 'r')
        if "metadata" in db:
            metadata = db["metadata"]
        db.close()
        if metadata:
            if str(metadata["dbVersion"]) == info.dbVersion:
                return True
            else:
                return False
        else:
            return False
    except:
        return False


def createResultsDirStr(name):
    """
    """
    dbDir = os.path.join(getDbRepoDir(), name)
    (parentDir, currentDir) = os.path.split(getDbRepoDir())
    templatesDir = os.path.join(parentDir, "templates")
    sampleStrDir = os.path.join(templatesDir, "resultsRepo")

    shutil.copytree(sampleStrDir, dbDir)

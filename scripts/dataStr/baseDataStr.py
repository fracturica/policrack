

import math
import time
import pickle
import copy

import info


class BaseDataStr:
    """
    """
    def __init__(self):
        """
        """
        self.inputData = {
            "interactionProperties": {
                "crack": {
                    "historyOutputName": "SIFs",
                    "historyOutputs": {},
                    "numberOfContours": 5,
                    "name": "crack",
                    "averagingContourSpan": ()},
                "contact": {
                    "crackContactName": "crackContact",
                    "crackContactPropertyName": "crackContactProperty"}},
            "crackParameters": {
                "a": 0,
                "b": 0,
                "crackType": ""},
            "createPredefinedLoads": True,
            "analysisParameters": {
                "sigma": 100,
                "gamma": 0,
                "omega": 0}}
        self.reportsData = {
            "successfulAnalysis": True,
            "mesh": {},
            "analysis": {
                "creationTimeStamp": "",
                "MdbCreationTime": "",
                "timeOfCalculation": ""}}
        self.odbData = {"name": ""}
        self.mdbData = {
            "geometricParameters": {"revolutionAngle": 0},
            "modelName": "",
            "stepName": "ApplyLoads",
            "sectionName": "SolidHomogeneousSection",
            "meshParameters": {},
            "sets": {
                "nodeSetsData": {
                    "externalNodesSet": {
                        "name": "externalNodeSet"}}}}
        self.dataStr = {
            "input": copy.deepcopy(self.inputData),
            "reports": copy.deepcopy(self.reportsData),
            "odb": copy.deepcopy(self.odbData),
            "mdb": copy.deepcopy(self.mdbData)}
        self.setPolicrackVersion()

    def setMaterialProperties(self, materialParameters):
        """
        """
        self.dataStr["input"]["material"] = materialParameters

    def setCrackParameters(self, crackParameters):
        """
        """
        self.dataStr["input"]["crackParameters"] = crackParameters

    def setAnalysisParameters(self, analysisParameters):
        """
        """
        self.dataStr["input"]["analysisParameters"] = analysisParameters

    def setAveragingContourSpan(self, contoursToAverage):
        """
        """
        self.dataStr["input"]["interactionProperties"][
            "crack"]["averagingContourSpan"] = contoursToAverage

    def calculateRevolutionAngle(self):
        """
        """
        angles = {
            "embedded": 360,
            "surface": 180,
            "edge": 90}
        crackType = self.dataStr["input"]["crackParameters"]["crackType"]
        self.dataStr["mdb"][
            "geometricParameters"]["revolutionAngle"] = angles[crackType]

    def setAnalysisCreationTimeStamp(self):
        """
        """
        self.dataStr["reports"]["analysis"]["creationTimeStamp"] = time.time()

    def setMeshParameters(self, meshParameters):
        """
        """
        self.dataStr["input"]["meshParameters"] = meshParameters

    def setSeedParameters(self, seedParameters):
        """
        """
        self.dataStr["input"]["seedParameters"] = seedParameters

    def determineAnalysisSuccess(self):
        """
        """
        for key in self.dataStr["reports"]["mesh"].keys():
            if self.dataStr["reports"]["mesh"][key]["failedElements"] != 0:
                self.dataStr["reports"]["successfulAnalysis"] = False

    def setPriorMeshTransformationReport(self, meshReport):
        """
        """
        self.dataStr["reports"]["mesh"]["priorTransformation"] = meshReport

    def setPostMeshTransformationReport(self, meshReport):
        """
        """
        self.dataStr["reports"]["mesh"]["postTransformation"] = meshReport

    def createModelName(self):
        """
        """
        timeStamp = str(self.dataStr[
            "reports"]["analysis"]["creationTimeStamp"])
        splitName = timeStamp.split(".")
        modelName = splitName[0] + "dot" + splitName[1]

        self.dataStr["mdb"]["modelName"] = modelName
        self.setOdbName()

    def setModelName(self, name):
        """
        """
        self.dataStr["mdb"]["modelName"] = name
        self.setOdbName()

    def setOdbName(self):
        """
        """
        self.dataStr["odb"]["name"] = self.dataStr["mdb"]["modelName"]

    def setTimeOnMdbCreation(self):
        """
        """
        self.dataStr["reports"]["analysis"]["MdbCreationTime"] = time.time()

    def setTimeOnAnalysisCalculation(self):
        """
        """
        self.dataStr["reports"]["analysis"]["timeOfCalculation"] = time.time()

    def setGeometricParameters(self, geometricParameters):
        """
        """
        self.dataStr["input"]["geometricParameters"] = geometricParameters

    def setSIFsHistoryOutput(self):
        """
        """
        self.dataStr["input"]["interactionProperties"]["crack"][
                "historyOutputs"]["SIFs"] = "K_FACTORS"

    def setJIntHistoryOutput(self):
        """
        """
        self.dataStr["input"]["interactionProperties"]["crack"][
                "historyOutputs"]["J-Int"] = "J_INTEGRAL"

    def setCIntHistoryOutput(self):
        """
        """
        self.dataStr["input"]["interactionProperties"]["crack"][
                "historyOutputs"]["C-Int"] = "C_INTEGRAL"

    def setTStressHistoryOutput(self):
        """
        """
        self.dataStr["input"]["interactionProperties"]["crack"][
                "historyOutputs"]["T-Stress"] = "T_STRESS"

    def setCreatePredefinedBCsFlag(self, flag):
        """
        """
        if (flag is True) or (repr(flag) == "ON"):
            self.dataStr["input"]["createPredefinedLoads"] = True
        else:
            self.dataStr["input"]["createPredefinedLoads"] = False

    def setPolicrackVersion(self):
        """
        """
        self.dataStr["input"]["policrack"] = {"version": info.version}

    def getCreatePredefinedBCsFlag(self):
        """
        """
        return self.dataStr["input"]["createPredefinedLoads"]

    def getBCParameters(self):
        """
        """
        self.dataStr["mdb"]["BCdata"] = {}
        self.dataStr["mdb"]["BCdata"]["E"] = self.dataStr["input"]["material"]["E"]
        self.dataStr["mdb"]["BCdata"]["v"] = self.dataStr["input"]["material"]["v"]
        for key in self.dataStr["input"]["analysisParameters"].keys():
            self.dataStr["mdb"]["BCdata"][key] = self.dataStr[
                "input"]["analysisParameters"][key]
        return self.dataStr["mdb"]["BCdata"]

    def getSeedInputParameters(self):
        """
        """
        return self.dataStr["input"]["seedParameters"]

    def getGeometricParameters(self):
        """
        """
        return self.dataStr["input"]["geometricParameters"]

    def getMdbGeometricParameters(self):
        """
        """
        return self.dataStr["mdb"]["geometricParameters"]

    def getRadiiParameters(self):
        """
        """
        return self.dataStr["mdb"]["geometricParameters"]["radii"]

    def getVerticalLevelsParameters(self):
        """
        """
        return self.dataStr["mdb"]["geometricParameters"]["verticalLevels"]

    def getElementType(self):
        """
        """
        return self.dataStr["input"]["meshParameters"]["elements"]

    def getMdbSeedParameters(self):
        """
        """
        return self.dataStr["mdb"]["seeds"]

    def getModelName(self):
        """
        """
        return self.dataStr["mdb"]["modelName"]

    def getOdbName(self):
        """
        """
        return self.dataStr["odb"]["name"]

    def getMaterialProperties(self):
        """
        """
        return self.dataStr["input"]["material"]

    def getAnalysisParameters(self):
        """
        """
        return self.dataStr["input"]["analysisParameters"]

    def getElementCodes(self):
        """
        """
        return self.dataStr["mdb"]["meshParameters"]["elementCodes"]

    def getCrackParameters(self):
        """
        """
        return self.dataStr["input"]["crackParameters"]

    def getNumberOfContours(self):
        """
        """
        return self.dataStr["input"][
            "interactionProperties"]["crack"]["numberOfContours"]

    def getSolidPartsParameters(self):
        """
        """
        return self.dataStr["mdb"]["parts"]["sketchPoints"]["solidParts"]

    def getShellPartsParameters(self):
        """
        """
        return self.dataStr["mdb"]["parts"]["sketchPoints"]["shellParts"]

    def getMergedPartName(self):
        """
        """
        return self.dataStr["mdb"]["parts"]["mergedPart"]["name"]

    def getDatumsData(self):
        """
        """
        return self.dataStr["mdb"]["datumsData"]

    def getSectionName(self):
        """
        """
        return self.dataStr["mdb"]["sectionName"]

    def getStepName(self):
        """
        """
        return self.dataStr["mdb"]["stepName"]

    def getCrackInteractionProperties(self):
        """
        """
        return self.dataStr["input"]["interactionProperties"]["crack"]

    def getCrackContactProperties(self):
        """
        """
        return self.dataStr["input"]["interactionProperties"]["contact"]

    def getPartitionData(self):
        """
        """
        return self.dataStr["mdb"]["partitionData"]

    def getSetData(self):
        """
        """
        return self.dataStr["mdb"]["sets"]["setData"]

    def getExternalNodeSetName(self):
        """
        """
        return self.dataStr["mdb"]["sets"][
            "nodeSetsData"]["externalNodesSet"]["name"]

    def getAnalysisSuccess(self):
        """
        """
        return self.dataStr["reports"]["successfulAnalysis"]

    def getNodeSelectionTolerance(self):
        """
        """
        return self.dataStr["mdb"][
            "geometricParameters"]["nodeSelectionTolerance"]

    def writeOdbResults(self, data):
        """
        """
        self.dataStr["odb"]["results"] = data

    def writeAnalyticalResults(self, data):
        """
        """
        self.dataStr["odb"]["analytical"] = data

    def writeVisualizationResults(self, data):
        """
        """
        self.dataStr["odb"]["visualization"] = data

    def writeErrorResults(self, data):
        """
        """
        self.dataStr["odb"]["errors"] = data

    def getCrackType(self):
        """
        """
        return self.dataStr["input"]["crackParameters"]["crackType"]

    def getModelType(self):
        """
        """
        return self.dataStr["input"]["modelType"]

    def getAveragingRange(self):
        """
        """
        return self.dataStr["input"][
            "interactionProperties"]["crack"]["averagingContourSpan"]

    def getAnalysisType(self):
        """
        """
        return self.dataStr["input"]["analysisType"]

    def getSortedBetaAngles(self):
        """
        """
        return self.dataStr["odb"]["results"]["sortedBetaAngles"]

    def getSortedAveragedSIFs(self):
        """
        """
        return self.dataStr["odb"]["results"]["sortedAveragedSIFs"]

    def getSortedContourSIFs(self):
        """
        """
        return self.dataStr["odb"]["results"]["sortedSIFs"]

    def getAnalyticalResults(self):
        """
        """
        return self.dataStr["odb"]["analytical"]

    def getVisualizationResults(self):
        """
        """
        return self.dataStr["odb"]["visualization"]

    def getErrorResults(self):
        """
        """
        return self.dataStr["odb"]["errors"]

    def getInputData(self):
        """
        """
        return self.dataStr["input"]

    def getReportData(self):
        """
        """
        return self.dataStr["reports"]

    def getOdbData(self):
        """
        """
        return self.dataStr["odb"]

    def getMdbData(self):
        """
        """
        return self.dataStr["mdb"]

    def setDataStr(self, data):
        """
        """
        self.dataStr = data

    def setAnalysisSuccess(self, successStatusBool):
        """
        """
        self.dataStr["reports"]["successfulAnalysis"] = successStatusBool

    def getDataForPickling(self):
        """
        """
        data = {
            "input": self.getInputData(),
            "reports": self.getReportData(),
            "odb": self.getOdbData(),
            "mdb": self.mdbData}
        modelName = self.getModelName()
        data["mdb"]["modelName"] = modelName
        return data

    def getDataStr(self):
        """
        """
        return self.dataStr

    def __eq__(self, other):
        """
        """
        try:
            if self.getInputData() != other["input"]:
                return False
            else:
                return True
        except:
            return False


def calculateTimeDifference(startTime, endTime):
    """
    """
    timePeriod = endTime - startTime
    hours = timePeriod // 3600
    minutes = (timePeriod % 3600) // 60
    seconds = timePeriod - (hours*3600 + minutes*60)
    return "{0}:{1}:{2}".format(hours, minutes, seconds)

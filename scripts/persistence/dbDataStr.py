

from scripts.dataStr.baseDataStr import BaseDataStr


class DbDataStr:
    """
    """
    def __init__(self, dbData):
        """
        """
        self.dataStr = BaseDataStr()
        self.dataStr.setDataStr(dbData)

    def getAnalyticalResults(self):
        """
        """
        return self.dataStr.getAnalyticalResults()

    def getVisualizationResults(self):
        """
        """
        return self.dataStr.getVisualizationResults()

    def getAnalysisType(self):
        """
        """
        return self.dataStr.getAnalysisType()

    def getSortedBetaAngles(self):
        """
        """
        return self.dataStr.getSortedBetaAngles()

    def getSortedContourSIFs(self):
        """
        """
        return self.dataStr.getSortedContourSIFs()

    def writeErrorResults(self, data):
        """
        """
        self.dataStr.writeErrorResults(data)

    def getErrorResults(self):
        """
        """
        return self.dataStr.getErrorResults()

    def writeAnalyticalResults(self, data):
        """
        """
        self.dataStr.writeAnalyticalResults(data)

    def writeVisualizationResults(self, data):
        """
        """
        self.dataStr.writeVisualizationResults(data)

    def writeResultRequests(self, data):
        """
        """
        self.dataStr.dataStr["odb"]["resultRequests"] = data

    def getResultRequests(self):
        """
        """
        return self.dataStr.dataStr["odb"]["resultRequests"]

    def getCrackType(self):
        """
        """
        return self.dataStr.getCrackType()

    def getMaterialProperties(self):
        """
        """
        return self.dataStr.getMaterialProperties()

    def getCrackParameters(self):
        """
        """
        return self.dataStr.getCrackParameters()

    def getAnalysisParameters(self):
        """
        """
        return self.dataStr.getAnalysisParameters()

    def getModelName(self):
        """
        """
        return self.dataStr.dataStr["input"]["modelName"]

    def setModelName(self, modelName):
        """
        """
        self.dataStr.dataStr["input"]["modelName"] = modelName

    def calculateAveragedSIFs(self):
        """
        """
        contoursToAverage = self.getResultRequests()["contoursToAverage"]
        sortedContourSIFs = self.getSortedContourSIFs()
        betaAngles = self.getSortedBetaAngles()
        for SIFkey in sortedContourSIFs.keys():
            contourKeys = sortedContourSIFs[SIFkey].keys()
            for index in range(len(betaAngles)):
                sumOfSIFs = 0

                for contour in contoursToAverage:
                    sumOfSIFs += sortedContourSIFs[SIFkey][contour][index]

                averagedSIFvalue = sumOfSIFs / len(contoursToAverage)
                self.dataStr.dataStr["odb"]["results"]["sortedAveragedSIFs"][SIFkey] += averagedSIFvalue,

    def getDataStr(self):
        """
        """
        return self.dataStr.dataStr

    def getSortedAveragedSIFs(self):
        """
        """
        return self.dataStr.dataStr["odb"]["results"]["sortedAveragedSIFs"]

    def getSortedCrackCoordinates(self):
        """
        """
        return self.dataStr.dataStr["odb"]["results"]["sortedCrackCoordinates"]

    def get3dGraphDataForSize(self):
        """
        """
        errors = self.getErrorResults()
        crackParameters1 = self.dataStr.dataStr["input"]["crackParameters"]
        crackParameters2 = self.getCrackParameters()
        crackParameters3 = self.dataStr.dataStr["input"]["interactionProperties"]["crack"]
        crackParameters = {}
        for key in crackParameters1.keys():
            crackParameters[key] = crackParameters1[key]

        for key in crackParameters3.keys():
            crackParameters[key] = crackParameters3[key]

        mesh = self.dataStr.dataStr["input"]["meshParameters"]
        geometricParameters = self.dataStr.dataStr["input"]["geometricParameters"]
        seedParameters = self.dataStr.dataStr["input"]["seedParameters"]
        height = geometricParameters["containerHeight"]
        radius = geometricParameters["containerRadius"]
        info = {
            "height": height,
            "radius": radius,
            "errors": errors["maxErrors"],
            "crack": crackParameters,
            "seeds": seedParameters,
            "mesh": mesh}
        return info

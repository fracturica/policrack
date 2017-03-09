

import math
import miscFunctions


class BaseAnalyticalExpressions:
    """
    """
    def __init__(self, dataStr, SIFkeys):
        """
        """
        self.dataStr = dataStr
        self.SIFkeys = SIFkeys
        self.SIFmethods = {
            "J": self.j,
            "K1": self.k1,
            "K2": self.k2,
            "K3": self.k3}
        self.data = {"input": {}}
        material = self.dataStr.getMaterialProperties()
        crackParameters = self.dataStr.getCrackParameters()
        analysisParameters = self.dataStr.getAnalysisParameters()
        dataTypes = (material, crackParameters, analysisParameters)
        for dataType in dataTypes:
            for key in dataType.keys():
                self.data["input"][key] = dataType[key]

    def calculateSolutionForAngle(self, beta):
        """
        """
        values = {}
        for key in self.SIFkeys:
            values[key] = self.SIFmethods[key](beta)
        return values

    def getSolutionsForVisualization(self):
        """
        """
        self.calculateSolutionsForVisualization()
        return self.data["solutionsForVisualization"]

    def calculateSolutionsForVisualization(self):
        """
        """
        values = {}
        for key in self.SIFkeys:
            values[key] = ()
        betaAngles = range(0, 361, 1)
        for beta in betaAngles:
            for key in self.SIFkeys:
                values[key] += self.SIFmethods[key](beta),

        values["betaAngles"] = betaAngles
        self.data["solutionsForVisualization"] = values

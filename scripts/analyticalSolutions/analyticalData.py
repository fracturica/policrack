

import math
import miscFunctions
import embeddedAE
import surfaceAE
import edgeAE


class AnalyticalData:
    """
    """
    def __init__(self, dataStr):
        """
        """
        self.dataStr = dataStr
        resultRequests = self.dataStr.getResultRequests()
        analysisKeys = resultRequests["analysisKeys"]
        analyticalKeys = resultRequests["analyticalKeys"]
        self.results = {
            "analytical": {},
            "maxErrors": {},
            "errors": {}}

        errorKeys = set(analyticalKeys) & set(analysisKeys)
        self.keys = {
            "analytical": analyticalKeys,
            "analysis": analysisKeys,
            "errors": errorKeys}

        for key in self.keys["analytical"]:
            self.results["analytical"][key] = ()
        for key in self.keys["errors"]:
            self.results["errors"][key] = ()

        self.results["analysis"] = self.dataStr.getSortedAveragedSIFs()
        crackType = self.dataStr.getCrackType()
        if crackType == "embedded":
            self.expressions = embeddedAE.EmbeddedCrackAnalyticalSolutions(
                self.dataStr, self.keys["analytical"])

        elif crackType == "surface":
            self.expressions = surfaceAE.SurfaceCrackAnalyticalSolutions(
                self.dataStr, self.keys["analytical"])

        elif crackType == "edge":
            self.expressions = edgeAE.EdgeCrackAnalyticalSolutions(
                self.dataStr, self.keys["analytical"])

        self.expressions.initializeParameters()

    def calculateAnalyticalResults(self):
        """
        """
        betaAngles = self.dataStr.getSortedBetaAngles()
        for beta in betaAngles:
            values = self.expressions.calculateSolutionForAngle(beta)
            for key in values.keys():
                self.results["analytical"][key] += values[key],

    def writeAnalyticalResultsToDataStr(self):
        """
        """
        data = {}
        for key in self.keys["analytical"]:
            data[key] = self.results["analytical"][key]
        data["betaAngles"] = self.dataStr.getSortedBetaAngles()
        self.dataStr.writeAnalyticalResults(data)

    def calculateVisualizationResults(self):
        """
        """
        self.results["visualization"] = self.expressions.getSolutionsForVisualization()

    def writeVisualizationResultsToDataStr(self):
        """
        """
        self.dataStr.writeVisualizationResults(self.results["visualization"])

    def calculateErrors(self):
        """
        """
        errors = ()
        for key in self.keys["errors"]:
            referenceValue = max(max(self.results["analytical"][key]),
                                 abs(min(self.results["analytical"][key])))

            for (analyticalValue, analysisValue) in zip(
                    self.results["analytical"][key],
                    self.results["analysis"][key]):
                if referenceValue != 0:
                    self.results["errors"][key] += abs(
                        (analysisValue - analyticalValue) / referenceValue) * 100,
                elif analyticalValue != 0 or analysisValue != 0:
                    self.results["errors"][key] += abs(
                        (analysisValue - analyticalValue)) / (
                            max(abs(analysisValue), abs(analyticalValue))) * 100,
                else:
                    self.results["errors"][key] += 0,

            self.results["maxErrors"][key] = max(self.results["errors"][key])
        self.results["maxAbsoluteError"] = max(self.results["maxErrors"].values())

    def writeErrorsToDataStr(self):
        """
        """
        self.dataStr.writeErrorResults({
            "SIFerrors": self.results["errors"],
            "maxErrors": self.results["maxErrors"],
            "maxAbsoluteError": self.results["maxAbsoluteError"],
            "betaAngles": self.dataStr.getSortedBetaAngles()})

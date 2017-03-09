

import math

from abaqus import *
from abaqusConstants import *

import part
import material
import section
import assembly
import step
import interaction
import sketch
import regionToolset, displayGroupMdbToolset as dgm, mesh, load, job
import inpReader
import meshEdit

from odbAccess import *
from odbMaterial import *
from odbSection import *


class ReadOdb:
    """
    """
    def __init__(self, dataStr):
        """
        """
        self.dataStr = dataStr
        self.odb = None
        self.outputData = {
            "historyRegionName": "ElementSet  PIBATCH",
            "historyOutputs": {},
            "contourIntegralNames": (),
            "rawSIFs": {},
            "rawBetaAngles": (),
            "rawCrackCoordinates": {"X": {}, "Y": {}, "Z": {}},
            "sortedSIFs": {},
            "sortedAveragedSIFs": {},
            "sortedCrackCoordinates": (),
            "outputParameters": {
                "K_FACTORS": ("K1", "K2", "K3", "JKs", "Cpd"),
                "J_INTEGRAL": ("J",),
                "C_INTEGRAL": ("C",),
                "T_STRESS": ("T",)},
            "sifIntTree": {}}

    def initializeValues(self):
        """
        """
        crackParameters = self.dataStr.getCrackInteractionProperties()
        histRequests = crackParameters["historyOutputs"]
        histOutNames = histRequests.keys()

        for histOutName in histRequests.keys():
            keyVal = histRequests[histOutName]
            histParameters = self.outputData["outputParameters"][keyVal]
            for histParam in histParameters:
                self.outputData["rawSIFs"][histParam] = {}
                self.outputData["sortedAveragedSIFs"][histParam] = ()
        for key in histOutNames:
            self.outputData["contourIntegralNames"] += key.upper(),

        for SIFkey in self.outputData["rawSIFs"].keys():
            for name in histOutNames:
                keyVal = histRequests[name]
                SIFs = self.outputData["outputParameters"][keyVal]
                if SIFkey in SIFs:
                    self.outputData["sifIntTree"][SIFkey] = name.upper()

    def openOdb(self):
        """
        """
        odbName = self.dataStr.getModelName()
        odbFileName = odbName + ".odb"

        self.odb = session.openOdb(
            name=odbName,
            path=odbFileName,
            readOnly=False)
        self.createOdbViewport(odbName)

    def openSpecificOdb(self, odbName, odbPath):
        """
        """
        self.odb = session.openOdb(
            name=odbName,
            path=odbPath,
            readOnly=False)
        self.createOdbViewport(odbName)

    def createOdbViewport(self, odbName):
        """
        """
        viewport = session.Viewport(name=odbName)
        viewport.makeCurrent()
        viewport.maximize()

    def readHistoryOutputs(self):
        """
        """
        self.initializeValues()
        stepName = self.dataStr.getStepName()
        historyRegionName = self.outputData["historyRegionName"]
        self.outputData["historyOutputs"] = self.odb.steps[
            stepName].historyRegions[historyRegionName].historyOutputs

    def extractValuesFromHistoryOutput(self):
        """
        """
        numberOfContours = self.dataStr.getNumberOfContours()
        SIFkeys = self.outputData["rawSIFs"].keys()
        for SIFkey in SIFkeys:
            for contourNumber in range(1, numberOfContours+1):
                contourKey = "Contour_" + str(contourNumber)
                self.outputData["rawSIFs"][SIFkey][contourKey] = {}

        for dataKey in self.outputData["historyOutputs"].keys():
            self.assignSIFvalue(dataKey)
            self.assignCoordinates(dataKey)
        self.alignValues()

    def alignValues(self):
        """
        """
        rawSIFs = {}
        rawCrackCoordinates = {}
        length = len(str(len(
            self.outputData["rawCrackCoordinates"]["X"].keys())))
        for SIFkey in self.outputData["rawSIFs"].keys():
            rawSIFs[SIFkey] = {}
            for contour in self.outputData["rawSIFs"][SIFkey].keys():
                rawSIFs[SIFkey][contour] = ()
                keys = self.outputData["rawSIFs"][SIFkey][contour].keys()
                keys.sort(
                    cmp=lambda x, y: cmp(
                        self.stripAlpha(x, length),
                        self.stripAlpha(y, length)))
                for key in keys:
                    rawSIFs[SIFkey][contour] += self.outputData[
                        "rawSIFs"][SIFkey][contour][key],

        for coordKey in self.outputData["rawCrackCoordinates"].keys():
            rawCrackCoordinates[coordKey] = ()
            keys = self.outputData["rawCrackCoordinates"][coordKey].keys()
            keys.sort(
                cmp=lambda x, y: cmp(
                    self.stripAlpha(x, length),
                    self.stripAlpha(y, length)))
            for key in keys:
                rawCrackCoordinates[coordKey] += self.outputData[
                    "rawCrackCoordinates"][coordKey][key],
        self.outputData["rawSIFs"] = rawSIFs
        self.outputData["rawCrackCoordinates"] = rawCrackCoordinates

    def stripAlpha(self, name, length):
        """
        """
        number = ""
        if "Contour" in name:
            index = name.rfind("C")
            name = name[:index]
        name = name.rstrip("_")
        counter = -1

        while name[counter].isdigit():
            counter = counter - 1

        number = name[counter+1:len(name)]
        while len(number) < length:
            number = "0" + number
        return number

    def assignSIFvalue(self, dataKey):
        """
        """
        SIFkeys = self.outputData["rawSIFs"].keys()
        contourKeys = self.outputData["rawSIFs"][SIFkeys[0]].keys()

        for SIFkey in SIFkeys:
            for contourKey in contourKeys:
                contIntName = self.outputData["sifIntTree"][SIFkey]
                sifID = dataKey.split(' ')[0]
                if (SIFkey == sifID and contourKey in dataKey):
                    name = self.outputData["historyOutputs"][dataKey].name
                    self.outputData["rawSIFs"][SIFkey][
                        contourKey][name] = self.outputData[
                        "historyOutputs"][dataKey].data[0][1]

    def assignCoordinates(self, dataKey):
        """
        """
        analysisType = self.dataStr.getAnalysisType()
        if analysisType == "FEM":
            contIntName = self.outputData["contourIntegralNames"][0]
            if (dataKey[0] in self.outputData["rawCrackCoordinates"].keys() and
                    contIntName in dataKey):
                name = self.outputData["historyOutputs"][dataKey].name
                self.outputData[
                    "rawCrackCoordinates"][dataKey[0]][name] = self.outputData[
                    "historyOutputs"][dataKey].data[0][1]
        else:
            if (dataKey[0] in self.outputData["rawCrackCoordinates"].keys() and
                    "Repeated" not in dataKey):
                name = self.outputData["historyOutputs"][dataKey].name
                self.outputData[
                    "rawCrackCoordinates"][dataKey[0]][name] = self.outputData[
                    "historyOutputs"][dataKey].data[0][1]

    def calculateBetas(self):
        """
        """
        print "X length"
        print len(self.outputData["rawCrackCoordinates"]["X"])
        print "-----"
        print "Y length"
        print len(self.outputData["rawCrackCoordinates"]["Z"])

        for (x, y) in zip(self.outputData["rawCrackCoordinates"]["X"],
                          self.outputData["rawCrackCoordinates"]["Y"]):
            self.outputData[
                "rawBetaAngles"] += self.calculateCrackPointAngle(x, y),

    def calculateCrackPointAngle(self, x, y):
        """
        """
        if x == 0 and y > 0:
            beta = 90.0
        elif x == 0 and y < 0:
            beta = 270.0
        elif x > 0 and y >= 0:
            beta = math.degrees(math.atan(y/x))
        elif x < 0 and y > 0:
            beta = 180 - math.degrees(math.atan(abs(y/x)))
        elif x < 0 and y <= 0:
            beta = 180 + math.degrees(math.atan(abs(y/x)))
        elif x > 0 and y < 0:
            beta = 360 - math.degrees(math.atan(abs(y/x)))
        return beta

    def sortData_new(self):
        """
        """
        SIFkeys = self.outputData["rawSIFs"].keys()

    def sortData(self):
        """
        """
        for SIFkey in self.outputData["rawSIFs"].keys():
            self.outputData["sortedSIFs"][SIFkey] = {}
            for contour in self.outputData["rawSIFs"][SIFkey].keys():
                self.outputData["sortedSIFs"][SIFkey][contour] = ()

        self.outputData[
            "sortedBetaAngles"] = set(self.outputData["rawBetaAngles"])
        self.outputData[
            "sortedBetaAngles"] = list(self.outputData["sortedBetaAngles"])
        self.outputData[
            "sortedBetaAngles"].sort()

        for angle in self.outputData["sortedBetaAngles"]:
            index = self.outputData["rawBetaAngles"].index(angle)

            self.outputData["sortedCrackCoordinates"] += (
                self.outputData["rawCrackCoordinates"]["X"][index],
                self.outputData["rawCrackCoordinates"]["Y"][index],
                self.outputData["rawCrackCoordinates"]["Z"][index]),

            for SIFkey in self.outputData["sortedSIFs"].keys():
                for contour in self.outputData["sortedSIFs"][SIFkey].keys():
                    self.outputData[
                        "sortedSIFs"][SIFkey][contour] += self.outputData[
                        "rawSIFs"][SIFkey][contour][index],

    def add360DegreeDataPoint(self):
        """
        """
        analysisType = self.dataStr.getAnalysisType()
        crackType = self.dataStr.getCrackType()
        if crackType == "embedded":
            self.outputData[
                "sortedBetaAngles"] += self.outputData[
                "sortedBetaAngles"][0] + 360,
            self.outputData[
                "sortedCrackCoordinates"] += self.outputData[
                "sortedCrackCoordinates"][0],

            for SIFkey in self.outputData["sortedSIFs"].keys():
                for contour in self.outputData["sortedSIFs"][SIFkey].keys():
                    self.outputData[
                        "sortedSIFs"][SIFkey][contour] += self.outputData[
                        "sortedSIFs"][SIFkey][contour][0],

    def averageSortedSIFs(self):
        """
        """
        averagingRange = self.dataStr.getAveragingRange()
        numberOfCrackValues = len(self.outputData["sortedBetaAngles"])

        for SIFkey in self.outputData["sortedSIFs"].keys():
            contourKeys = self.outputData["sortedSIFs"][SIFkey].keys()

            for index in range(numberOfCrackValues):
                sumOfSIFs = 0

                for contourNumber in averagingRange:
                    contourKey = contourKeys[contourNumber - 1]
                    sumOfSIFs += self.outputData[
                        "sortedSIFs"][SIFkey][contourKey][index]

                self.outputData["sortedAveragedSIFs"][
                    SIFkey] += (sumOfSIFs / len(averagingRange)),

    def writeOutputResultsToDataStr(self):
        """
        """
        data = {
            "sortedBetaAngles": self.outputData["sortedBetaAngles"],
            "sortedAveragedSIFs": self.outputData["sortedAveragedSIFs"],
            "sortedCrackCoordinates": self.outputData["sortedCrackCoordinates"],
            "sortedSIFs": self.outputData["sortedSIFs"]}
        self.dataStr.writeOdbResults(data)

    def getOdb(self):
        """
        """
        return self.odb

    def closeOdb(self):
        """
        """
        self.odb.close()

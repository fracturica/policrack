

import math
import shelve
from scripts.persistence.dbDataStr import DbDataStr

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


class XYPlotDataFromDbEntry:
    """
    """
    def __init__(self, dataStr):
        """
        """
        self.plots = {
            "visualization": {},
            "contours": {},
            "averaged": {},
            "errors": {},
            "analytical": {}}
        self.yLabels = {
            "K1": "Stress Intensity Factors",
            "K2": "Stress Intensity Factors",
            "K3": "Stress Intensity Factors",
            "J": "J-Integral",
            "JKs": "J-Integral",
            "Cpd": "Crack Propagation Direction",
            "T": "T-Stress",
            "C": "Ct-Integral"}
        self.dataStr = dataStr

    def createAnalyticalXYPlotData(self):
        """
        """
        resultRequests = self.dataStr.getResultRequests()
        betaAngles = self.dataStr.getSortedBetaAngles()
        modelName = self.dataStr.getModelName()
        analysisType = self.dataStr.getAnalysisType()
        analyticalKeys = resultRequests["analyticalKeys"]
        data = self.dataStr.getAnalyticalResults()

        for SIFkey in analyticalKeys:
            try:
                dataPair = zip(betaAngles, data[SIFkey])
                self.plots["analytical"][modelName+SIFkey] = session.XYData(
                    name="{0} - {1} - {2} - Analytical".format(
                        modelName, SIFkey, analysisType),
                    data=dataPair,
                    sourceDescription="{0} analytical solution".format(SIFkey),
                    legendLabel="{0} - {1} - {2} - analytical solution".format(
                        modelName, analysisType, SIFkey),
                    xValuesLabel="beta",
                    yValuesLabel=self.yLabels[SIFkey])
            except KeyError:
                print "No analytical solution is coded for {0}".format(SIFkey)

    def createAveragedXYPlotData(self):
        """
        """
        resultRequests = self.dataStr.getResultRequests()
        numberOfAveragedContours = len(resultRequests["contoursToAverage"])
        analysisKeys = resultRequests["analysisKeys"]
        betaAngles = self.dataStr.getSortedBetaAngles()
        analysisType = self.dataStr.getAnalysisType()
        modelName = self.dataStr.getModelName()
        averagedSIFs = self.dataStr.getSortedAveragedSIFs()

        for SIFkey in analysisKeys:
            try:
                dataPair = zip(betaAngles, averagedSIFs[SIFkey])
                self.plots["averaged"][modelName+SIFkey] = session.XYData(
                    name="{0} - {1} - {2} - Averaged".format(
                        modelName, SIFkey, analysisType),
                    data=dataPair,
                    sourceDescription="{0} calculated from the FEA model".format(SIFkey),
                    legendLabel="{0} - {1} - {2} - averaged over {3} contours".format(
                        modelName, SIFkey, analysisType, numberOfAveragedContours),
                    xValuesLabel="beta",
                    yValuesLabel=self.yLabels[SIFkey])
            except KeyError:
                print "{0} database record has no {1} entry".format(modelName, SIFkey)

    def createContourXYPlotData(self):
        """
        """
        resultRequests = self.dataStr.getResultRequests()
        analysisKeys = resultRequests["analysisKeys"]
        betaAngles = self.dataStr.getSortedBetaAngles()
        analysisType = self.dataStr.getAnalysisType()
        modelName = self.dataStr.getModelName()
        SIFs = self.dataStr.getSortedContourSIFs()

        for SIFkey in analysisKeys:
            try:
                self.plots["contours"][SIFkey] = {}
                for contour in SIFs[SIFkey].keys():
                    dataPair = zip(betaAngles, SIFs[SIFkey][contour])
                    self.plots["contours"][SIFkey][contour] = session.XYData(
                        name="{0} - {1} - {2} - Contour - {3}".format(
                            modelName, SIFkey, analysisType, str(contour.split("_")[1])),
                        data=dataPair,
                        sourceDescription="{0} calculated from the FEA model".format(SIFkey),
                        legendLabel="{0} - {1} - {2} - Contour - {3}".format(
                            modelName, SIFkey, analysisType, str(contour.split("_")[1])),
                        xValuesLabel="beta",
                        yValuesLabel=self.yLabels[SIFkey])
            except:
                pass

    def createErrorXYPlotData(self):
        """
        """
        data = self.dataStr.getErrorResults()
        betaAngles = self.dataStr.getSortedBetaAngles()
        SIFerrors = data["SIFerrors"]
        analysisType = self.dataStr.getAnalysisType()
        modelName = self.dataStr.getModelName()

        for SIFkey in SIFerrors.keys():
            try:
                dataPair = zip(betaAngles, SIFerrors[SIFkey])
                self.plots["errors"][modelName + SIFkey] = session.XYData(
                    name="{0} - {1} - {2} - Errors".format(
                        modelName, SIFkey, analysisType),
                    data=dataPair,
                    sourceDescription="{0} errors FEA/Analytical solution".format(SIFkey),
                    legendLabel="{0} - {1} - {2} - errors".format(
                        modelName, analysisType, SIFkey),
                    xValuesLabel="beta",
                    yValuesLabel="Error [%]")
            except:
                pass

    def createVisualizationXYPlotData(self):
        """
        """
        data = self.dataStr.getVisualizationResults()
        betaAngles = data["betaAngles"]
        resultRequests = self.dataStr.getResultRequests()
        analyticalKeys = resultRequests["analyticalKeys"]
        modelName = self.dataStr.getModelName()
        analysisType = self.dataStr.getAnalysisType()

        for SIFkey in analyticalKeys:
            try:
                dataPair = zip(betaAngles, data[SIFkey])
                self.plots["visualization"][modelName+SIFkey] = session.XYData(
                    name="{0} - {1} - {2} - Visualization".format(
                        modelName, SIFkey, analysisType),
                    data=dataPair,
                    sourceDescription="{0} analytical solution".format(SIFkey),
                    legendLabel="{0} - {1} - {2} - analytical solution (visualization)".format(
                        modelName, analysisType, SIFkey),
                    xValuesLabel="beta",
                    yValuesLabel=self.yLabels[SIFkey])
            except:
                pass

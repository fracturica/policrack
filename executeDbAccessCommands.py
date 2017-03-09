

import sys
import shelve
import sharedFunctions
import scripts.processOdb.xyPlotDataFromDbEntry as xyPlotDataFromDbEntry
import scripts.visualizationOdb.visualizationOdb as visualizationOdb
import scripts.persistence.dbDataStr as dbDataStr
from scripts.analyticalSolutions.analyticalData import AnalyticalData


def readFromDb(**kargs):
    """
    """
    dbKeys = kargs["dbKeys"].split("_")
    dbPath = sharedFunctions.getDbPath(kargs["dbName"])
    analytical = ()
    analysis = ()
    for key in kargs:
        if kargs[key] is True:
            if "analysis" in key:
                analysis += key[:-8],
            if "analytical" in key:
                analytical += key[:-10],

    contours = kargs["contoursToAverage"].split(",")
    contoursToAverage = ()
    for key in contours:
        newKey = key.replace(" ", "_")
        contoursToAverage += newKey,

    requests = {
        "contoursToAverage": contoursToAverage,
        "includeContours": kargs["includeContours"],
        "analysisKeys": analysis,
        "analyticalKeys": analytical}

    info = {}
    for dbKey in dbKeys:
        db = shelve.open(dbPath, 'r')
        data = db[dbKey]
        db.close()
        dataStr = prepareDbDataStr(data, requests, dbKey)
        calcAnalyticalSolutions(dataStr)
        if kargs["XYPlotData"]:
            createXYPlots(dataStr)
        if kargs["printData"]:
            printData(dataStr)
        if kargs["VisualizationOdb"]:
            createVisualizationOdb(dataStr)


def prepareDbDataStr(data, requests, dbKey):
    """
    """
    dataStr = dbDataStr.DbDataStr(data)
    dataStr.setModelName(dbKey)
    dataStr.writeResultRequests(requests)
    dataStr.calculateAveragedSIFs()
    return dataStr


def calcAnalyticalSolutions(dataStr):
    """
    """
    requests = dataStr.getResultRequests()
    if requests["analyticalKeys"]:
        ae = AnalyticalData(dataStr)
        ae.calculateAnalyticalResults()
        ae.calculateVisualizationResults()
        ae.calculateErrors()

        ae.writeAnalyticalResultsToDataStr()
        ae.writeVisualizationResultsToDataStr()
        ae.writeErrorsToDataStr()


def createXYPlots(dataStr):
    """
    """
    xyPlotData = xyPlotDataFromDbEntry.XYPlotDataFromDbEntry(dataStr)
    xyPlotData.createAveragedXYPlotData()
    resultRequests = dataStr.getResultRequests()
    if resultRequests["includeContours"]:
        xyPlotData.createContourXYPlotData()
    if resultRequests["analyticalKeys"]:
        xyPlotData.createAnalyticalXYPlotData()
        xyPlotData.createErrorXYPlotData()
        xyPlotData.createVisualizationXYPlotData()


def printData(dataStr):
    """
    """
    print 30*"-"
    print ""
    print 30*"-"
    print ""
    print dataStr.getModelName()
    print 10*"-"
    print dataStr.getDataStr()


def createVisualizationOdb(dataStr):
    """
    """
    visOdb = visualizationOdb.VisualizationOdbFromDbEntry(dataStr)
    visOdb.initializeAbaqusOdb()
    visOdb.initializeViewport()
    visOdb.setViewportViewingPoint()

    visOdb.createMaterial()
    visOdb.createSections()
    visOdb.createPart()
    visOdb.createNodes()

    visOdb.createStepFrame()
    visOdb.createElements()
    visOdb.createInstance()
    visOdb.createFieldOutput()
    visOdb.setDefaultField()

    visOdb.saveOdb()
    visOdb.reopenOdb()

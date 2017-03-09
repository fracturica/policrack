

import sys
import time
import math
import os
import osutils
import customKernel

import modelDb.fem.femCrack as femCrack
import modelDb.fem.orphanMesh as orphanMesh

import modelDb.xfem.xfemTETcrack as xfemTETcrack
import modelDb.xfem.xfemCrackMP as xfemCrackMP
import modelDb.xfem.xfemSimpleCrack as xfemSimpleCrack

import dataStr.femDataStr as femDataStr
import dataStr.xfemTETdataStr as xfemTETdataStr
import dataStr.xfemDataStrMP as xfemDataStrMP
import dataStr.xfemSimpleDataStr as xfemSimpleDataStr

import processOdb.readOdb as readOdb
import persistence.persistence as persistence


class MdbCommands():
    """
    """
    def __init__(self, dataStr, parameters):
        """
        """
        self.dataStr = dataStr
        self.pars = parameters
        self.db = persistence.PersistentData(self.dataStr)

    def createSingleMdb(self):
        """
        """
        self.initializeDataStr()
        self.createMdb()
        self.saveMdb()
        self.savePickleConfig()

    def setBatchMode(self):
        self.initializeDataStr()
        self.initializeDb()
        self.initializeMdb()

    def initializeMdb(self):
        """
        """
        if not self.dataStr.getCreatePredefinedBCsFlag():
            self.createMdb()
        else:
            self.initializeDb()
            if not self.db.checkForDuplicate():
                self.savePickleConfig()
                self.createMdb()
                self.processJob()
                self.db.writeToDb()

    def initializeDataStr(self):
        """
        """
        modelType = self.dataStr.getModelType()
        analysisType = self.dataStr.getAnalysisType()

        self.dataStr.setSIFsHistoryOutput()
        self.dataStr.setJIntHistoryOutput()
        self.dataStr.setTStressHistoryOutput()

        if analysisType == "FEM":
            self.dataStr.calculateMdbGeometricParameters()
            self.dataStr.calculateRevolutionAngle()
            self.dataStr.createPartsData()

            self.dataStr.createDatumsData()
            self.dataStr.createPartitionData()

            self.dataStr.createPolarCoordinatesOfAPointOnEntityForASet()

            self.dataStr.createAnglesForAPointOnZeroDegreePlane()
            self.dataStr.createCompleteSetsData()
            self.dataStr.createSeedsData()
            self.dataStr.createElementTypeData()
        elif analysisType == "XFEM":
            if modelType == "crackPartition":
                self.dataStr.calculateMdbGeometricParameters()
                self.dataStr.calculateRevolutionAngle()
                self.dataStr.createPartsData()
                self.dataStr.createCrackPartitionPartData()

                self.dataStr.createDatumsData()

                self.dataStr.createCompleteSetsData()
                self.dataStr.createSeedsData()
                self.dataStr.createElementTypeData()
            elif modelType == "multiplePartitions":
                self.dataStr.calculateMdbGeometricParameters()
                self.dataStr.calculateRevolutionAngle()
                self.dataStr.createPartsData()
                self.dataStr.createParametersForLoft()
                self.dataStr.createCrackPartitionPartData()

                self.dataStr.createDatumsData()

                self.dataStr.createCompleteSetsData()
                self.dataStr.createAdditionalSetsData()
                self.dataStr.createSeedsData()
                self.dataStr.createElementTypeData()
            elif modelType == "simple":
                self.dataStr.calculateMdbGeometricParameters()
                self.dataStr.calculateRevolutionAngle()
                self.dataStr.createPartsData()

                self.dataStr.createDatumsData()

                self.dataStr.createCompleteSetsData()
                self.dataStr.createSeedsData()
                self.dataStr.createElementTypeData()

    def initializeDb(self):
        """
        """
        self.db.specifyActiveShelve(self.pars["outputDatabase"][0])
        self.db.createDbMetadata()
        self.db.verifyActiveShelve()

    def createMdb(self):
        """
        """
        modelType = self.dataStr.getModelType()
        analysisType = self.dataStr.getAnalysisType()

        if analysisType == "FEM":
            self.createFEMmdb()
        elif analysisType == "XFEM":
            if modelType == "crackPartition":
                self.createXFEM_CP_mdb()
            elif modelType == "multiplePartitions":
                self.createXFEM_MP_mdb()
            elif modelType == "simple":
                self.createXFEM_simple_mdb()
        self.saveMdb()

    def createXFEM_simple_mdb(self):
        """
        """
        self.mdb = xfemSimpleCrack.SimpleXFEMcrackMdb(self.dataStr)

        self.mdb.initializeAbaqusModel()
        self.mdb.initializeViewport()

        self.mdb.createAllParts()
        self.mdb.createMaterial()
        self.mdb.createSection()

        self.mdb.createInstancesFromAllParts()
        self.mdb.assignSectionToCrackDomain()
        self.mdb.createCrackAndCrackDomainInstances()

        self.mdb.createDatums()

        self.mdb.createSets()
        self.mdb.createStep()

        self.mdb.createContactInteractionProperty()
        self.mdb.createXFEMcrack()

        self.mdb.createFieldOutputRequest()

        self.mdb.deleteHistoryOutputs()
        self.mdb.createHistoryOutput()

        self.mdb.assignMeshControls()
        self.mdb.seedEdges()
        self.mdb.generateMesh()

        self.mdb.createSetForExternalNodes()

        self.createLoads()

        self.mdb.createJob()

    def createXFEM_MP_mdb(self):
        """
        """
        self.mdb = xfemCrackMP.XFEMcrackMdbMP(self.dataStr)

        self.mdb.initializeAbaqusModel()
        self.mdb.initializeViewport()

        self.mdb.createAllParts()
        self.mdb.createMaterial()
        self.mdb.createSection()

        self.mdb.createInstancesForPartitioning()

        self.mdb.createMergedPart()
        self.mdb.createLoftsOnCrackDomain()
        self.mdb.deleteAllInstances()
        self.mdb.assignSectionToMergedPart()

        self.mdb.createCrackAndCrackDomainInstances()

        self.mdb.createDatums()
        self.mdb.createPiePartitions()

        self.mdb.createSets()
        self.mdb.createStep()

        self.mdb.createContactInteractionProperty()
        self.mdb.createXFEMcrack()

        self.mdb.createFieldOutputRequest()

        self.mdb.deleteHistoryOutputs()
        self.mdb.createHistoryOutput()

        self.mdb.assignMeshControls()
        self.mdb.seedEdges()
        self.mdb.generateMesh()

        self.mdb.createSetForExternalNodes()
        self.createLoads()

        self.mdb.createJob()

    def createXFEM_CP_mdb(self):
        """
        """
        self.mdb = xfemTETcrack.XFEMtetCrackMdb(self.dataStr)

        self.mdb.initializeAbaqusModel()
        self.mdb.initializeViewport()

        self.mdb.createAllParts()
        self.mdb.createMaterial()
        self.mdb.createSection()

        self.mdb.createInstancesForPartitioning()

        self.mdb.createMergedPart()
        self.mdb.deleteAllInstances()
        self.mdb.assignSectionToMergedPart()

        self.mdb.createCrackAndCrackDomainInstances()

        self.mdb.createDatums()

        self.mdb.createSets()
        self.mdb.createStep()

        self.mdb.createContactInteractionProperty()
        self.mdb.createXFEMcrack()

        self.mdb.createFieldOutputRequest()

        self.mdb.deleteHistoryOutputs()
        self.mdb.createHistoryOutput()

        self.mdb.assignMeshControls()
        self.mdb.seedEdges()
        self.mdb.generateMesh()

        self.mdb.createSetForExternalNodes()
        self.createLoads()

        self.mdb.createJob()

    def createFEMmdb(self):
        """
        """
        self.fem = femCrack.FEMcrackMdb(self.dataStr)
        self.om = orphanMesh.FEMcrackOrphanMesh(self.dataStr)

        self.fem.initializeAbaqusModel()
        self.fem.initializeViewport()
        self.fem.setViewportViewingPoint()

        self.fem.createAllParts()

        self.fem.createDatums()
        self.fem.createInstancesFromAllParts()
        self.fem.createMergedPart()
        self.fem.deleteAllInstances()
        self.fem.createMaterial()
        self.fem.createSection()
        self.fem.assignSectionToMergedPart()
        self.fem.createMergedPartInstance()
        self.fem.partitionMergedPartInstance()
        self.fem.createSets()
        self.fem.createStep()
        self.fem.createCrackInteraction()
        self.fem.deleteHistoryOutputs()
        self.fem.createDummyHistoryOutput()
        self.fem.createContactInteractionProperty()
        self.fem.createContactInteraction()
        self.fem.meshInstance()

        meshReport = self.fem.verifyMesh()
        print meshReport

        self.dataStr.setPriorMeshTransformationReport(meshReport)
        self.fem.createJob()

        self.fem.writeInputFile()
        self.fem.closeMdb()

        self.om.initializeAbaqusModel()
        self.om.clearImportedModel()
        self.om.createElementSets()

        crackParameters = self.dataStr.getCrackParameters()
        a = crackParameters["a"]
        b = crackParameters["b"]
        if a != b:
            self.om.deleteCentralWedgeElements()
            self.om.createSetForExternalNodes()
            self.om.createSetFromInnerCylinderNodes()
            self.om.applyMeshTransformation()
            self.om.closeInnerCylinderHole()
        else:
            self.om.createSetForExternalNodes()

        self.om.regenerateAssembly()
        self.om.deleteHistoryOutputs()
        self.om.redefineCrackInteraction()
        self.om.createHistoryOutput()

        self.mdb = self.om

        self.createLoads()

        self.mdb.createJob()
        self.dataStr.setTimeOnMdbCreation()

        meshReport = self.mdb.verifyMesh()
        self.dataStr.setPostMeshTransformationReport(meshReport)
        self.dataStr.determineAnalysisSuccess()

    def createLoads(self):
        """
        """
        if self.dataStr.getCreatePredefinedBCsFlag():
            self.mdb.createBC()

    def savePickleConfig(self):
        """
        """
        if self.pars["saveMdb"][0] == "yes":
            self.db.pickleConfFile()

    def saveMdb(self):
        """
        """
        if self.pars["saveMdb"][0] == "yes":
            self.mdb.saveMdb()

    def processJob(self):
        """
        """
        modelType = self.dataStr.getModelType()
        analysisType = self.dataStr.getAnalysisType()

        if self.dataStr.getAnalysisSuccess():

            self.odb = readOdb.ReadOdb(self.dataStr)

            self.mdb.submitJob()
            self.dataStr.setTimeOnAnalysisCalculation()

            self.odb.openOdb()
            self.odb.readHistoryOutputs()

            self.odb.extractValuesFromHistoryOutput()
            self.odb.calculateBetas()

            self.odb.sortData()
            self.odb.add360DegreeDataPoint()

            self.odb.writeOutputResultsToDataStr()

            self.odb.closeOdb()

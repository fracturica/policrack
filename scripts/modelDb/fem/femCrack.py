

import sys

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

import scripts.modelDb.baseCrack as baseCrack


class FEMcrackMdb(baseCrack.BaseCrackMdb):
    """
    """
    def createAllParts(self):
        """
        """
        self.createSolidParts()
        self.createShellParts()

    def partitionMergedPartInstance(self):
        """
        """
        self.partitionInnerCylinderCells()
        self.partitionContainerAsPie()

    def partitionInnerCylinderCells(self):
        """
        """
        partitionsData = self.inputData.getPartitionData()["innerCylinderPartitions"]
        for partition in partitionsData:
            self.mdb["assembly"].PartitionCellByDatumPlane(
                cells=self.mdb["mergedInstance"].cells.findAt(partition["cellPoint"]),
                datumPlane=self.mdb["assembly"].datums[partition["datum"]])

    def partitionContainerAsPie(self):
        """
        """
        datumsForPartitioning = self.inputData.getPartitionData()["piePartitionsDatum"]
        for datumNumber in range(1, datumsForPartitioning):
            self.mdb["assembly"].PartitionCellByDatumPlane(
                cells=self.mdb["mergedInstance"].cells,
                datumPlane=self.mdb["assembly"].datums[datumNumber])

    def createSets(self):
        """
        """
        self.mdb["sets"] = {
            "edges": {},
            "cells": {},
            "faces": {}}
        self.createSetsForEdges()
        self.createSetsForFaces()
        self.createSetsForCells()

    def createSetsForEdges(self):
        """
        """
        setsData = self.inputData.getSetData()["edges"]
        for setName in setsData.keys():

            points = setsData[setName]
            selectedEdges = ()

            for point in points:
                point = point,
                selectedEdges += (self.mdb["mergedInstance"].edges.findAt(point)),

            self.mdb["sets"]["edges"][setName] = self.mdb["assembly"].Set(
                edges=selectedEdges[:][:], name=setName)

    def createSetsForCells(self):
        """
        """
        setsData = self.inputData.getSetData()["cells"]
        for setName in setsData.keys():

            points = setsData[setName]
            selectedCells = ()

            for point in points:
                point = point,
                selectedCells += (self.mdb["mergedInstance"].cells.findAt(point)),

            self.mdb["sets"]["cells"][setName] = self.mdb["assembly"].Set(
                cells=selectedCells[:][:], name=setName)

    def createSetsForFaces(self):
        """
        """
        setsData = self.inputData.getSetData()["faces"]
        for setName in setsData.keys():

            points = setsData[setName]
            selectedFaces = ()

            for point in points:
                point = point,
                selectedFaces += (self.mdb["mergedInstance"].faces.findAt(point)),

            self.mdb["sets"]["faces"][setName] = self.mdb["assembly"].Set(
                faces=selectedFaces[:][:], name=setName)

    def createCrackInteraction(self):
        """
        """
        crackInteractionProperties = self.inputData.getCrackInteractionProperties()
        contourIntegralName = crackInteractionProperties["name"]
        midNodePosition = crackInteractionProperties["midNodePosition"]

        self.mdb["assembly"].engineeringFeatures.assignSeam(
            regions=self.mdb["sets"]["faces"]["crackFlanks"])

        self.mdb["assembly"].engineeringFeatures.ContourIntegral(
            name=contourIntegralName,
            crackFront=self.mdb["sets"]["edges"]["crackFrontEdges"],
            crackTip=self.mdb["sets"]["edges"]["crackFrontEdges"],
            extensionDirectionMethod=Q_VECTORS,
            symmetric=False,
            midNodePosition=midNodePosition,
            collapsedElementAtTip=SINGLE_NODE,
            qVectors=((
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0)),))

    def createContactInteraction(self):
        """
        """
        contactProperties = self.inputData.getCrackContactProperties()
        crackContactName = contactProperties["crackContactName"]
        crackContactPropertyName = contactProperties["crackContactPropertyName"]

        self.mdb["assembly"].Surface(
            side1Faces=self.mdb["sets"]["faces"]["crackFlanks"].faces,
            name="crackFace1")
        self.mdb["assembly"].Surface(
            side2Faces=self.mdb["sets"]["faces"]["crackFlanks"].faces,
            name="crackFace2")
        self.mdb["model"].SurfaceToSurfaceContactStd(
            name=crackContactName,
            createStepName="Initial",
            master=self.mdb["assembly"].surfaces["crackFace1"],
            slave=self.mdb["assembly"].surfaces["crackFace2"],
            sliding=FINITE,
            interactionProperty=crackContactPropertyName,
            enforcement=SURFACE_TO_SURFACE)

    def createDummyHistoryOutput(self):
        """
        """
        stepName = self.inputData.getStepName()
        crackProperties = self.inputData.getCrackInteractionProperties()
        contourIntegralName = crackProperties["name"]
        numberOfContours = crackProperties["numberOfContours"]
        historyOutputName = crackProperties["historyOutputName"]
        self.mdb["model"].HistoryOutputRequest(
            name=historyOutputName,
            createStepName=stepName,
            contourIntegral=contourIntegralName,
            numberOfContours=numberOfContours,
            contourType=K_FACTORS)

    def meshInstance(self):
        """
        """
        self.seedEdges()
        self.assignMeshControls()
        self.assignElementType()
        self.generateMesh()

    def assignMeshControls(self):
        """
        """
        self.mdb["assembly"].setMeshControls(
            regions=self.mdb["sets"]["cells"]["crackTipCells"].cells,
            elemShape=WEDGE,
            technique=SWEEP)
        self.mdb["assembly"].setMeshControls(
            regions=self.mdb["sets"]["cells"]["innerCylinderCells"].cells,
            elemShape=HEX_DOMINATED,
            technique=SWEEP,
            algorithm=MEDIAL_AXIS)

    def writeInputFile(self):
        """
        """
        modelName = self.inputData.getModelName()
        mdb.jobs[modelName].writeInput()

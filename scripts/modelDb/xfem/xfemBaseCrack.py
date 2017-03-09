

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


class BaseXFEMcrackMdb(baseCrack.BaseCrackMdb):
    """
    """
    def createCrackPart(self):
        """
        """
        crackPart = self.inputData.getCrackPartData()
        (crackPartName,) = crackPart.keys()
        a = crackPart[crackPartName]["a"]
        b = crackPart[crackPartName]["b"]

        crackGeometrySketch = self.mdb["model"].ConstrainedSketch(
            name="crackGeometrySketch",
            sheetSize=2 * max(a, b),
            transform=(
                1.0, 0.0, 0.0,
                0.0, 0.0, -1.0,
                0.0, 1.0, 0.0,
                0.0, 0.0, 0.0))
        crackGeometrySketch.EllipseByCenterPerimeter(
            center=(0.0, 0.0),
            axisPoint1=(0.0, b/2.0),
            axisPoint2=(a/2.0, 0.0))
        self.mdb["parts"][crackPartName] = self.mdb["model"].Part(
            name=crackPartName,
            dimensionality=THREE_D,
            type=DEFORMABLE_BODY)
        self.mdb["parts"][crackPartName].BaseShell(sketch=crackGeometrySketch)

    def createCrackAndCrackDomainInstances(self):
        """
        """
        crackPart = self.inputData.getCrackPartData()
        (crackPartName,) = crackPart.keys()
        self.createInstance(crackPartName)
        self.createMergedPartInstance()

    def createCrackPartitionPart(self):
        """
        """
        partitionData = self.inputData.getCrackPartitionData()
        crackParameters = self.inputData.getCrackParameters()
        partName = partitionData["name"]

        planarShellSketch = self.mdb["model"].ConstrainedSketch(
            name=partName,
            sheetSize=2*max(crackParameters["a"], crackParameters["b"]),
            transform=(
                1.0, 0.0, 0.0,
                0.0, 1.0, 0.0,
                0.0, 0.0, 1.0,
                0.0, 0.0, 0.0))
        ellipse = planarShellSketch.EllipseByCenterPerimeter(
            center=(0.0, 0.0),
            axisPoint1=(crackParameters["a"], 0.0),
            axisPoint2=(0.0, crackParameters["b"]))
        planarShellSketch.Line(
            point1=partitionData["lines"][0][0],
            point2=partitionData["lines"][0][1])
        planarShellSketch.Line(
            point1=partitionData["lines"][1][0],
            point2=partitionData["lines"][1][1])
        planarShellSketch.autoTrimCurve(
            curve1=ellipse,
            point1=partitionData["trimPoint"])

        self.mdb["parts"][partName] = self.mdb["model"].Part(
            name=partName,
            dimensionality=THREE_D,
            type=DEFORMABLE_BODY)
        self.mdb["parts"][partName].BaseShell(sketch=planarShellSketch)

    def repositionCrackInstance(self):
        """
        """
        crackPart = self.inputData.getCrackPartData()
        (crackPartName,) = crackPart.keys()
        crackInstanceName = crackPartName

        self.mdb["assembly"].instances[crackInstanceName].rotateAboutAxis(
            axisPoint=(0.0, 0.0, 0.0),
            axisDirection=(1.0, 0.0, 0.0),
            angle=90)

    def createSets(self):
        """
        """
        self.mdb["assembly"].DatumCsysByThreePoints(
            name='Datum csys-1',
            coordSysType=CARTESIAN,
            origin=(0.0, 0.0, 0.0),
            line1=(1.0, 0.0, 0.0),
            line2=(0.0, 1.0, 0.0))
        self.mdb["sets"] = {
            "edges": {},
            "cells": {},
            "faces": {},
            "nodeSets": {}}
        self.createSetsForEdges()
        self.createSetsForFaces()

    def createSetsForEdges(self):
        """
        """
        setData = self.inputData.getSetData()["edges"]

        for setName in setData.keys():
            center1 = setData[setName]["center1"]
            center2 = setData[setName]["center2"]
            radius = setData[setName]["radius"]
            edges = self.mdb["mergedInstance"].edges.getByBoundingCylinder(
                center1=center1,
                center2=center2,
                radius=radius)
            self.mdb["sets"]["edges"][setName] = self.mdb["assembly"].Set(
                edges=edges,
                name=setName)

    def createSetsForFaces(self):
        """
        """
        setData = self.inputData.getSetData()["faces"]
        crackPart = self.inputData.getCrackPartData()
        (crackPartName,) = crackPart.keys()
        crackInstanceName = crackPartName

        for setName in setData.keys():
            center1 = setData[setName]["center1"]
            center2 = setData[setName]["center2"]
            radius = setData[setName]["radius"]

            faces = self.mdb["assembly"].instances[
                crackInstanceName].faces.getByBoundingCylinder(
                center1=center1,
                center2=center2,
                radius=radius)
            self.mdb["sets"]["faces"][setName] = self.mdb["assembly"].Set(
                faces=faces,
                name=setName)

    def createXFEMcrack(self):
        """
        """
        crackName = self.inputData.getCrackInteractionProperties()["name"]
        contactPropertiesName = self.inputData.getCrackContactProperties()["crackContactPropertyName"]
        singularityCalcRadius = self.inputData.getSingularityCalcRadius()

        if singularityCalcRadius == 0.0:
            singularityCalcRadius = None

        crackDomainRegion = regionToolset.Region(
            cells=self.mdb["mergedInstance"].cells)
        crackLocationRegion = regionToolset.Region(
            faces=self.mdb["sets"]["faces"]["crackFlanks"].faces)

        self.mdb["assembly"].engineeringFeatures.XFEMCrack(
            name=crackName,
            allowCrackGrowth=False,
            crackDomain=crackDomainRegion,
            crackLocation=crackLocationRegion,
            interactionProperty=contactPropertiesName,
            singularityCalcRadius=singularityCalcRadius)

    def createFieldOutputRequest(self):
        """
        """
        stepName = self.inputData.getStepName()
        self.mdb["model"].FieldOutputRequest(
            name="crackOpening",
            createStepName=stepName,
            variables=('PHILSM',))

    def deleteFieldOutputs(self):
        """
        """
        fieldOutputs = self.mdb["model"].fieldOutputRequests
        for key in fieldOutputs.keys():
            del fieldOutputs[key]

    def assignMeshControls(self):
        """
        """
        elementType = self.inputData.getElementType()
        if "Tet" in elementType:
            elemShape = TET
            self.mdb["assembly"].setMeshControls(
                regions=self.mdb["mergedInstance"].cells,
                elemShape=elemShape,
                technique=FREE)
        else:
            elemShape = HEX
            self.mdb["assembly"].setMeshControls(
                regions=self.mdb["mergedInstance"].cells,
                elemShape=elemShape)

    def seedEdges(self):
        """
        """
        seeds = self.inputData.getMdbSeedParameters()
        for edgesSetName in seeds.keys():
            seedSize = seeds[edgesSetName][0]
            seedConstraint = seeds[edgesSetName][1]
            self.mdb["assembly"].seedEdgeBySize(
                edges=self.mdb["sets"]["edges"][edgesSetName].edges,
                size=seedSize,
                constraint=seedConstraint)

    def createSetForExternalNodes(self):
        """
        """
        containerHeight = self.inputData.getVerticalLevelsParameters()["surface"]
        containerRadius = self.inputData.getRadiiParameters()["containerRadius"]
        tolerance = self.inputData.getNodeSelectionTolerance()
        nodeSelectionRadiusSquared = containerRadius**2 - tolerance
        externalNodeSetName = self.inputData.getExternalNodeSetName()

        nodeLabels = ()

        for node in self.mdb["mergedInstance"].nodes:
            (x, y, z) = node.coordinates

            if abs(z) == containerHeight:
                nodeLabels += node.label,

            if node.label not in nodeLabels:
                nodeRadiusSquare = x**2 + y**2

                if nodeRadiusSquare >= nodeSelectionRadiusSquared:
                    nodeLabels += node.label,

        nodeSequence = self.mdb["mergedInstance"].nodes.sequenceFromLabels(
            labels=nodeLabels)

        self.mdb['sets']['nodeSets'][externalNodeSetName] = self.mdb["assembly"].Set(
            name=externalNodeSetName,
            nodes=nodeSequence)

    def getExternalNodes(self):
        """
        """
        externalNodeSetName = self.inputData.getExternalNodeSetName()
        return self.mdb["sets"]["nodeSets"][externalNodeSetName].nodes

    def getCrackContainerInstance(self):
        """
        """
        return self.mdb["mergedInstance"]

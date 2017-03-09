

import sys
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

import xfemBaseCrack


class XFEMcrackMdbMP(xfemBaseCrack.BaseXFEMcrackMdb):
    """
    """
    def createAllParts(self):
        """
        """
        self.createCrackPart()
        self.createSolidParts()
        self.createSmallContainer()

    def createSmallContainer(self):
        """
        """
        partData = self.inputData.getSmallContainerPartData()
        crackType = self.inputData.getCrackType()
        smallContainerAxes = self.inputData.getMdbGeometricParameters()[
            "smallContainerAxes"]
        a = smallContainerAxes["a"]
        b = smallContainerAxes["b"]
        extrusionDepth = partData["extrusionDepth"]

        baseSketch = self.mdb["model"].ConstrainedSketch(
            name=partData["name"],
            sheetSize=2*max(a, b),
            transform=(
                1.0, 0.0, 0.0,
                0.0, 1.0, 0.0,
                0.0, 0.0, 1.0,
                0.0, 0.0, -0.5*extrusionDepth))

        ellipse = baseSketch.EllipseByCenterPerimeter(
            center=(0.0, 0.0),
            axisPoint1=partData["ellipse"][0],
            axisPoint2=partData["ellipse"][1])

        if crackType != "embedded":
            baseSketch.Line(
                point1=partData["lines"][0][0],
                point2=partData["lines"][0][1])
            baseSketch.Line(
                point1=partData["lines"][1][0],
                point2=partData["lines"][1][1])
            baseSketch.autoTrimCurve(
                curve1=ellipse,
                point1=partData["trimPoint"])

        self.mdb["parts"][partData["name"]] = self.mdb["model"].Part(
            name=partData["name"],
            dimensionality=THREE_D,
            type=DEFORMABLE_BODY)
        self.mdb["parts"][partData["name"]].BaseSolidExtrude(
            sketch=baseSketch,
            depth=extrusionDepth)
        self.createPartOrientation(self.mdb["parts"][partData["name"]])

    def createInstancesForPartitioning(self):
        """
        """
        smallContainerName = self.inputData.getSmallContainerPartData()["name"]
        self.createInstance(smallContainerName)
        (crackContainerPartName,) = self.inputData.getSolidPartsParameters().keys()
        self.createInstance(crackContainerPartName)

    def createLoftsOnCrackDomain(self):
        """
        """
        partData = self.inputData.getSmallContainerPartData()
        edgePoints = partData["loft"]["edgePoints"]
        (partName,) = self.inputData.getSolidPartsParameters().keys()
        for edgePair in edgePoints:
            edge1 = self.mdb["parts"][partName].edges.findAt(edgePair[0])
            edge2 = self.mdb["parts"][partName].edges.findAt(edgePair[1])
            self.mdb["parts"][partName].ShellLoft(
                loftsections=((edge1,), (edge2,),),
                keepInternalBoundaries=ON)

    def createPiePartitions(self):
        """
        """
        print self.mdb["model"].rootAssembly.datums.keys()
        crackType = self.inputData.getCrackType()
        datumNumbers = ()

        if crackType == "embedded":
            datumNumbers = sorted(self.mdb["assembly"].datums.keys())
        elif crackType == "surface":
            datumNumbers = (sorted(self.mdb["assembly"].datums.keys())[0],)
        elif crackType == "edge":
            datumNumbers = ()

        for datumNumber in datumNumbers:
            datum = self.mdb["assembly"].datums[datumNumber]
            self.mdb["assembly"].PartitionCellByDatumPlane(
                cells=self.mdb["mergedInstance"].cells,
                datumPlane=datum)

    def createSets(self):
        """
        """
        self.mdb["sets"] = {
            "edges": {},
            "faces": {},
            "nodeSets": {}}
        self.mdb["assembly"].DatumCsysByThreePoints(
            name='Datum csys-1',
            coordSysType=CARTESIAN,
            origin=(0.0, 0.0, 0.0),
            line1=(1.0, 0.0, 0.0),
            line2=(0.0, 1.0, 0.0))
        self.createSetsForExteriorEdges()
        self.createSetsByBoundingBox()
        self.createSetsForFaces()

    def createSetsForExteriorEdges(self):
        """
        """
        xfemBaseCrack.BaseXFEMcrackMdb.createSetsForEdges(self)

    def createSetsByBoundingBox(self):
        """
        """
        setsData = self.inputData.getSetData()["selectByBoundingBoxEdges"]

        for setName in setsData.keys():
            setParameters = setsData[setName]
            selectedEdges = self.mdb["mergedInstance"].edges.getByBoundingBox(
                xMin=setParameters["xMin"],
                xMax=setParameters["xMax"],
                yMin=setParameters["yMin"],
                yMax=setParameters["yMax"],
                zMin=setParameters["zMin"],
                zMax=setParameters["zMax"])
            self.mdb["sets"]["edges"][setName] = self.mdb["assembly"].Set(
                edges=selectedEdges,
                name=setName)

    def assignMeshControls(self):
        """
        """
        elementType = self.inputData.getElementType()
        if "Tet" in elementType:
            elemShape = TET
            self.mdb["assembly"].setMeshControls(
                regions=self.mdb["mergedInstance"].cells,
                elemShape=elemShape,
                technique=FREE,
                allowMapped=False)
        else:
            elemShape = HEX
            self.mdb["assembly"].setMeshControls(
                regions=self.mdb["mergedInstance"].cells,
                elemShape=elemShape,
                technique=STRUCTURED)

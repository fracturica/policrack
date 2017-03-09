

import sys
import math

from abaqus import *
# import testUtils
from abaqusConstants import *

import part
import material
import section
import assembly
import step
import interaction
import sketch
import regionToolset
import displayGroupMdbToolset as dgm, mesh, load, job
import inpReader
import meshEdit

import baseDataStr

# testUtils.setBackwardCompatibility()


class FEMdataStr(baseDataStr.BaseDataStr):
    """
    """
    def __init__(self):
        """
        """
        baseDataStr.BaseDataStr.__init__(self)

        self.dataStr["input"]["analysisType"] = "FEM"

        self.dataStr["mdb"]["sets"]["setData"] = {
            "edges": {},
            "cells": {},
            "faces": {}}
        self.dataStr["mdb"]["sets"]["pointsProjectedOnZeroDegreePlane"] = {}
        self.dataStr["mdb"]["sets"]["angles"] = {}

    def setMidNodePosition(self, midNodePosition):
        """
        """
        self.dataStr["input"]["interactionProperties"][
            "crack"]["midNodePosition"] = midNodePosition

    def createDatumsData(self):
        """
        """
        czs = self.dataStr["input"]["geometricParameters"]["crackZoneSide"]
        self.dataStr["mdb"]["datumsData"] = (
            ("XYPLANE", 0.0),
            ("YZPLANE", 0.0),
            ("XZPLANE", 0.0),
            ("XYPLANE", 0.5*czs),
            ("XYPLANE", -0.5*czs))

    def calculateCrackRadiusBeforeTransformation(self):
        """
        """
        a = self.getCrackParameters()["a"]
        b = self.getCrackParameters()["b"]
        transformationType = self.getMeshTransformationType()

        minorAxis = min(a, b)
        crackRadiusForAdvancedScale = math.sqrt(a/2.0 * b/2.0)

        crackRadii = {
            "elliptic": minorAxis/2.0,
            "simpleScale": minorAxis/2.0,
            "advancedScale": crackRadiusForAdvancedScale,
            "none": minorAxis}
        self.dataStr["input"]["geometricParameters"][
            "crackRadius"] = crackRadii[transformationType]

    def calculateCrackZoneSide(self, scale=1.0):
        """
        """
        crackRadius = self.getGeometricParameters()["crackRadius"]
        self.dataStr["input"]["geometricParameters"][
                "crackZoneSide"] = crackRadius * scale

    def calculateCrackTipSide(self, scale=0.3):
        """
        """
        crackZoneSide = self.getGeometricParameters()["crackZoneSide"]
        self.dataStr["input"]["geometricParameters"][
                "crackTipSide"] = crackZoneSide * scale

    def calculateMdbGeometricParameters(self):
        """
        """
        geometricParameters = self.getGeometricParameters()

        self.dataStr["mdb"]["geometricParameters"] = {
            "radii": {
                "crackZoneInnerRadius":
                    geometricParameters["crackRadius"] -
                    0.5*geometricParameters["crackZoneSide"],

                "crackZoneOuterRadius":
                    geometricParameters["crackRadius"] +
                    0.5*geometricParameters["crackZoneSide"],

                "crackTipInnerRadius":
                    geometricParameters["crackRadius"] -
                    0.5*geometricParameters["crackTipSide"],

                "crackTipOuterRadius":
                    geometricParameters["crackRadius"] +
                    0.5*geometricParameters["crackTipSide"],

                "crackRadius":
                    geometricParameters["crackRadius"],

                "containerRadius":
                    geometricParameters["containerRadius"]},

            "verticalLevels": {
                "surface":
                    0.5*geometricParameters["containerHeight"],

                "crackZone":
                    0.5*geometricParameters["crackZoneSide"],

                "crackTip":
                    0.5*geometricParameters["crackTipSide"]},
            "nodeSelectionTolerance": 0.5,
            "mergeNodesTolerance": 0.1}

    def createPartsData(self):
        """
        """
        r = self.getRadiiParameters()
        vl = self.getVerticalLevelsParameters()

        self.dataStr["mdb"]["parts"] = {
            "sketchPoints": {
                "solidParts": {
                    "container": (
                        (0.0, -vl["surface"]),
                        (r["containerRadius"], vl["surface"])),
                    "crackZone": (
                        (r["crackZoneInnerRadius"], -vl["crackZone"]),
                        (r["crackZoneOuterRadius"], vl["crackZone"])),
                    "crackTip": (
                        (r["crackTipInnerRadius"], -vl["crackTip"]),
                        (r["crackTipOuterRadius"], vl["crackTip"]))},
                "shellParts": {
                    "crackZoneDiagonal": (
                        (r["crackZoneInnerRadius"], vl["crackZone"]),
                        (r["crackZoneOuterRadius"], -vl["crackZone"])),
                    "crackZoneAntidiagonal": (
                        (r["crackZoneInnerRadius"], -vl["crackZone"]),
                        (r["crackZoneOuterRadius"], vl["crackZone"])),
                    "containerAntidiagonalPartition": (
                        (r["crackZoneOuterRadius"], vl["crackZone"]),
                        (r["containerRadius"], vl["surface"])),
                    "containerDiagonalPartition": (
                        (r["crackZoneOuterRadius"], -vl["crackZone"]),
                        (r["containerRadius"], -vl["surface"])),
                    "innerCylinderPartition": (
                        (r["crackZoneInnerRadius"], -vl["surface"]),
                        (r["crackZoneInnerRadius"], vl["surface"]))}},
            "mergedPart": {
                "name": "mergedPart"},
            "orphanMeshPart": {
                "name": "orphanMesh"}}

    def createPartitionData(self):
        """
        """
        geometricParameters = self.getGeometricParameters()
        crackType = self.getCrackParameters()["crackType"]

        piePartitionsDatum = {
            "embedded": 4,
            "edge": 2,
            "surface": 3}
        self.dataStr["mdb"]["partitionData"] = {
            "innerCylinderPartitions": (
                {"cellPoint":
                    ((0.0, 0.0, geometricParameters["crackZoneSide"]),),
                 "datum": 4},
                {"cellPoint":
                    ((0.0, 0.0, -geometricParameters["crackZoneSide"]),),
                 "datum": 5}),
            "piePartitionsDatum": piePartitionsDatum[crackType]}

    def createPolarCoordinatesOfAPointOnEntityForASet(self):
        """
        """
        r = self.getRadiiParameters()
        vl = self.getVerticalLevelsParameters()

        self.dataStr["mdb"]["sets"]["pointsProjectedOnZeroDegreePlane"] = {
            "crossSectionEdges": {
                "crackZoneVerticalEdges": (
                    (0.0, 0.0, 0.5*vl["crackZone"]),
                    (r["crackZoneInnerRadius"], 0.0, 0.5*vl["crackZone"]),
                    (r["crackTipInnerRadius"], 0.0, 0.5*vl["crackTip"]),
                    (r["crackTipOuterRadius"], 0.0, 0.5*vl["crackTip"]),
                    (r["crackZoneOuterRadius"], 0.0, 0.5*vl["crackZone"]),
                    (r["containerRadius"], 0.0, 0.5*vl["surface"]),

                    (0.0, 0.0, -0.5*vl["crackZone"]),
                    (r["crackZoneInnerRadius"], 0.0, -0.5*vl["crackZone"]),
                    (r["crackTipInnerRadius"], 0.0, -0.5*vl["crackTip"]),
                    (r["crackTipOuterRadius"], 0.0, -0.5*vl["crackTip"]),
                    (r["crackZoneOuterRadius"], 0.0, -0.5*vl["crackZone"]),
                    (r["containerRadius"], 0.0, -0.5*vl["surface"])),

                "crackZoneHorizontalEdges": (
                    (r["crackRadius"], 0.0, vl["crackTip"]),
                    (r["crackRadius"], 0.0, vl["crackZone"]),
                    (r["crackRadius"], 0.0, vl["surface"]),

                    (r["crackRadius"], 0.0, -vl["crackTip"]),
                    (r["crackRadius"], 0.0, -vl["crackZone"]),
                    (r["crackRadius"], 0.0, -vl["surface"])),

                "crackZoneRefinementEdges": (
                    (0.5*r["crackZoneInnerRadius"] + 0.5*r["crackTipInnerRadius"], 0.0, 0.0),
                    (0.5*r["crackTipInnerRadius"] + 0.5*r["crackZoneInnerRadius"],
                     0.0,
                     0.5*vl["crackZone"] + 0.5*vl["crackTip"]),
                    (0.5*r["crackTipOuterRadius"] + 0.5*r["crackZoneOuterRadius"],
                     0.0,
                     0.5*vl["crackZone"] + 0.5*vl["crackTip"]),
                    (0.5*r["crackTipOuterRadius"] + 0.5*r["crackZoneOuterRadius"], 0.0, 0.0),
                    (0.5*r["crackTipInnerRadius"] + 0.5*r["crackZoneInnerRadius"],
                     0.0,
                     -0.5*vl["crackZone"] - 0.5*vl["crackTip"]),
                    (0.5*r["crackTipOuterRadius"] + 0.5*r["crackZoneOuterRadius"],
                     0.0,
                     -0.5*vl["crackZone"] - 0.5*vl["crackTip"])),

                "crackTipRefinementEdges": (
                    (0.5*r["crackRadius"] + 0.5*r["crackTipInnerRadius"], 0.0, 0.0),
                    (0.5*r["crackRadius"] + 0.5*r["crackTipInnerRadius"],
                     0.0,
                     0.5*vl["crackTip"]),
                    (0.5*r["crackRadius"] + 0.5*r["crackTipOuterRadius"],
                     0.0,
                     0.5*vl["crackTip"]),

                    (0.5*r["crackRadius"] + 0.5*r["crackTipOuterRadius"], 0.0, 0.0),
                    (0.5*r["crackRadius"] + 0.5*r["crackTipOuterRadius"],
                     0.0,
                     -0.5*vl["crackTip"]),
                    (0.5*r["crackRadius"] + 0.5*r["crackTipInnerRadius"],
                     0.0,
                     -0.5*vl["crackTip"])),

                "containerRefinementEdges": (
                    (0.0, 0.0, 0.5*vl["surface"] + 0.5*vl["crackZone"]),
                    (r["crackZoneInnerRadius"],
                     0.0,
                     0.5*vl["surface"] + 0.5*vl["crackZone"]),
                    (0.5*r["crackZoneOuterRadius"] + 0.5*r["containerRadius"],
                     0.0,
                     0.5*vl["surface"] + 0.5*vl["crackZone"]),

                    (0.5*r["crackZoneOuterRadius"] + 0.5*r["containerRadius"], 0.0, 0.0),

                    (0.5*r["crackZoneOuterRadius"] + 0.5*r["containerRadius"],
                     0.0,
                     -0.5*vl["surface"] - 0.5*vl["crackZone"]),
                    (r["crackZoneInnerRadius"],
                     0.0,
                     -0.5*vl["surface"] - 0.5*vl["crackZone"]),
                    (0.0, 0.0,
                     -0.5*vl["surface"] - 0.5*vl["crackZone"])),

                "innerCylinderHorizontalEdges": (
                    (0.5*r["crackZoneInnerRadius"], 0.0, vl["surface"]),
                    (0.5*r["crackZoneInnerRadius"], 0.0, vl["crackZone"]),

                    (0.5*r["crackZoneInnerRadius"], 0.0, 0.0),

                    (0.5*r["crackZoneInnerRadius"], 0.0, -vl["crackZone"]),
                    (0.5*r["crackZoneInnerRadius"], 0.0, -vl["surface"]))},

            "arcEdges": {
                "allArcEdges": (
                    (r["crackZoneInnerRadius"], 0.0, vl["surface"]),
                    (r["containerRadius"], 0.0, vl["surface"]),

                    (r["crackZoneInnerRadius"], 0.0, vl["crackZone"]),
                    (r["crackZoneOuterRadius"], 0.0, vl["crackZone"]),

                    (r["crackTipInnerRadius"], 0.0, vl["crackTip"]),
                    (r["crackTipOuterRadius"], 0.0, vl["crackTip"]),

                    (r["crackZoneInnerRadius"], 0.0, 0.0),
                    (r["crackTipInnerRadius"], 0.0, 0.0),
                    (r["crackRadius"], 0.0, 0.0),
                    (r["crackTipOuterRadius"], 0.0, 0.0),
                    (r["crackZoneOuterRadius"], 0.0, 0.0),
                    (r["containerRadius"], 0.0, 0.0),

                    (r["crackTipInnerRadius"], 0.0, -vl["crackTip"]),
                    (r["crackTipOuterRadius"], 0.0, -vl["crackTip"]),

                    (r["crackZoneInnerRadius"], 0.0, -vl["crackZone"]),
                    (r["crackZoneOuterRadius"], 0.0, -vl["crackZone"]),

                    (r["crackZoneInnerRadius"], 0.0, -vl["surface"]),
                    (r["containerRadius"], 0.0, -vl["surface"])),

                "crackFrontEdges": (
                    (r["crackRadius"], 0.0, 0.0),)},

            "cells": {
                "crackTipCells": (
                    (0.5*r["crackTipInnerRadius"] + 0.5*r["crackRadius"],
                     0.0,
                     0.25*vl["crackTip"]),
                    (r["crackRadius"], 0.0, 0.25*vl["crackTip"]),
                    (0.5*r["crackTipOuterRadius"] + 0.5*r["crackRadius"],
                     0.0,
                     0.25*vl["crackTip"]),

                    (0.5*r["crackTipOuterRadius"] + 0.5*r["crackRadius"],
                     0.0,
                     -0.25*vl["crackTip"]),
                    (r["crackRadius"], 0.0, -0.25*vl["crackTip"]),
                    (0.5*r["crackTipInnerRadius"] + 0.5*r["crackRadius"],
                     0.0,
                     -0.25*vl["crackTip"])),

                "innerCylinderCells": (
                    (0.5*r["crackZoneInnerRadius"],
                     0.0,
                     0.5*vl["surface"] + 0.5*vl["crackZone"]),
                    (0.5*r["crackZoneInnerRadius"], 0.0, 0.5*vl["crackZone"]),

                    (0.5*r["crackZoneInnerRadius"],
                     0.0,
                     -0.5*vl["crackZone"]),
                    (0.5*r["crackZoneInnerRadius"],
                     0.0,
                     -0.5*vl["surface"] - 0.5*vl["crackZone"]))},

            "faces": {
                "crackFlanks": (
                    (0.5*r["crackTipInnerRadius"] + 0.5*r["crackRadius"], 0.0, 0.0),
                    (0.5*r["crackTipInnerRadius"] + 0.5*r["crackZoneInnerRadius"], 0.0, 0.0),
                    (0.5*r["crackZoneInnerRadius"], 0.0, 0.0))}}

    def getInnerCylinderCellsSetName(self):
        """
        to be removed
        """
        return "innerCylinderCells"

    def createAnglesForAPointOnZeroDegreePlane(self):
        """
        """
        crackType = self.getCrackParameters()["crackType"]

        anglesByCrackType = {
            "crossSectionEdges": {
                "embedded": (0.0, 90.0, 180.0, 270.0),
                "edge": (0.0, 90.0),
                "surface": (0.0, 90.0, 180.0)},
            "arcEdgesAndCells": {
                "embedded": (45.0, 135.0, 225.0, 315.0),
                "edge": (45.0,),
                "surface": (45.0, 135.0)}}

        self.dataStr["mdb"]["sets"]["angles"] = {
            "crossSectionEdges": anglesByCrackType["crossSectionEdges"][crackType],
            "arcEdges": anglesByCrackType["arcEdgesAndCells"][crackType],
            "cells": anglesByCrackType["arcEdgesAndCells"][crackType],
            "faces": anglesByCrackType["arcEdgesAndCells"][crackType]}

    def createCompleteSetsData(self):
        """
        """
        self.createSetData("crossSectionEdges", "edges")
        self.createSetData("arcEdges", "edges")
        self.createSetData("cells", "cells")
        self.createSetData("faces", "faces")
        self.createElementSetData()
        self.createNodeSetData()

    def createElementSetData(self):
        """
        """
        radii = self.getRadiiParameters()
        verticalLevels = self.getVerticalLevelsParameters()

        self.dataStr["mdb"]["sets"]["elementsSetData"] = {
            "innerCylinderPositiveYElementSet": {
                "center1": (0.0, 0.0, 0.0),
                "center2": (
                    0.0,
                    0.0,
                    verticalLevels["surface"]),
                "radius": radii["crackZoneInnerRadius"]},
            "innerCylinderNegativeYElementSet": {
                "center1": (0.0, 0.0, 0.0),
                "center2": (
                    0.0,
                    0.0,
                    -verticalLevels["surface"]),
                "radius": radii["crackZoneInnerRadius"]}}

    def createNodeSetData(self):
        """
        """
        self.dataStr["mdb"]["sets"]["nodeSetsData"]["innerCylinderHoleNodes"] = {
            "innerCylinderPositiveYElementSet": "innerCylinderPositiveYNodeSet",
            "innerCylinderNegativeYElementSet": "innerCylinderNegativeYNodeSet"}

    def createSetData(self, entityType, setDataSection):
        """
        """
        setNames = self.dataStr["mdb"]["sets"][
            "pointsProjectedOnZeroDegreePlane"][entityType].keys()
        angles = self.dataStr["mdb"]["sets"]["angles"][entityType]

        for setName in setNames:

            self.dataStr["mdb"]["sets"]["setData"][setDataSection][setName] = ()
            polarPoints = self.dataStr["mdb"]["sets"][
                "pointsProjectedOnZeroDegreePlane"][entityType][setName]

            for polarPoint in polarPoints:

                for degreesAngle in angles:

                    pointOnEntity = self.calculateXYZCoordinates(
                        polarPoint, degreesAngle)
                    self.dataStr["mdb"]["sets"]["setData"][
                        setDataSection][setName] += pointOnEntity,

    def calculateXYZCoordinates(self, polarPoint, angle):
        """
        """
        (r, rho, height) = polarPoint
        angle = math.radians(angle)
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        z = height
        point = (x, y, z)
        return point

    def createSeedsData(self):
        """
        """
        seedParameters = self.getSeedInputParameters()

        self.dataStr["mdb"]["seeds"] = {
            "crackZoneVerticalEdges": (
                int(0.5*seedParameters["crackZoneMainSeeds"]),
                FREE),
            "crackZoneHorizontalEdges": (
                seedParameters["crackZoneMainSeeds"],
                FREE),
            "crackZoneRefinementEdges": (
                seedParameters["crackZoneRefinementSeeds"],
                FREE),
            "crackTipRefinementEdges": (
                1,
                FREE),
            "containerRefinementEdges": (
                seedParameters["containerRefinementSeeds"],
                FREE),
            "innerCylinderHorizontalEdges": (
                2, FREE),
            "allArcEdges": (
                seedParameters["arcSeeds"],
                FREE)}

    def createElementTypeData(self):
        """
        """
        elementType = self.getElementType()
        elementFamily = {
            "QuadraticFI": (
                mesh.ElemType(
                    elemCode=C3D20, elemLibrary=STANDARD,
                    kinematicSplit=AVERAGE_STRAIN, secondOrderAccuracy=False,
                    hourglassControl=STIFFNESS, distortionControl=False),
                mesh.ElemType(elemCode=C3D15, elemLibrary=STANDARD),
                mesh.ElemType(elemCode=C3D10M, elemLibrary=STANDARD)),
            "QuadraticRI": (
                mesh.ElemType(
                    elemCode=C3D20R, elemLibrary=STANDARD,
                    kinematicSplit=AVERAGE_STRAIN, secondOrderAccuracy=False,
                    hourglassControl=STIFFNESS, distortionControl=False),
                mesh.ElemType(elemCode=C3D15, elemLibrary=STANDARD),
                mesh.ElemType(elemCode=C3D10M, elemLibrary=STANDARD)),
            "LinearFI": (
                mesh.ElemType(
                    elemCode=C3D8, elemLibrary=STANDARD,
                    secondOrderAccuracy=False,
                    distortionControl=False),
                mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD),
                mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD)),
            "LinearRI": (
                mesh.ElemType(
                    elemCode=C3D8R, elemLibrary=STANDARD,
                    kinematicSplit=AVERAGE_STRAIN, secondOrderAccuracy=False,
                    hourglassControl=STIFFNESS, distortionControl=False),
                mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD),
                mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD))}

        self.dataStr["mdb"]["meshParameters"]["elementCodes"] = elementFamily[elementType]

    def setInnerCylinderHoleRadius(self, radius):
        """
        """
        self.dataStr["mdb"]["sets"]["nodeSetsData"]["radius"] = radius

    def getInnerCylinderHoleRadius(self):
        """
        """
        return self.dataStr["mdb"]["sets"]["nodeSetsData"]["radius"]

    def getMeshTransformationType(self):
        """
        """
        return self.dataStr["mdb"]["meshParameters"]["transformationType"]

    def getMeshTransformationAxis(self):
        """
        """
        return self.dataStr["mdb"]["meshParameters"]["transformationAxis"]

    def processTransformationInputData(self):
        """
        """
        transformationAxis = "X"
        stationaryAxis = "Y"
        crackParameters = self.getCrackParameters()
        a = crackParameters["a"]
        b = crackParameters["b"]

        if a < b:
            transformationAxis, stationaryAxis = stationaryAxis, transformationAxis
        self.dataStr["mdb"]["meshParameters"][
            "transformationAxis"] = transformationAxis
        self.dataStr["mdb"]["meshParameters"][
            "transformationType"] = self.dataStr["input"]["meshParameters"]["transformationType"]

    def getMergeNodesTolerance(self):
        """
        """
        return self.dataStr["mdb"]["geometricParameters"]["mergeNodesTolerance"]

    def getOrphanMeshPartName(self):
        """
        """
        return self.dataStr["mdb"]["parts"]["orphanMeshPart"]["name"]

    def getElementSetData(self):
        """
        """
        return self.dataStr["mdb"]["sets"]["elementsSetData"]

    def getNodeSetData(self):
        """
        """
        return self.dataStr["mdb"]["sets"]["nodeSetsData"]["innerCylinderHoleNodes"]

    def setModelType(self, modelType):
        """
        """
        self.dataStr["input"]["modelType"] = modelType



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
import regionToolset, displayGroupMdbToolset as dgm, mesh, load, job
import inpReader
import meshEdit

import baseDataStr

# testUtils.setBackwardCompatibility()


class XFEMbaseDataStr(baseDataStr.BaseDataStr):
    """
    """
    def __init__(self):
        """
        """
        baseDataStr.BaseDataStr.__init__(self)
        self.dataStr["input"]["analysisType"] = "XFEM"

    def createDatumsData(self):
        """
        """
        self.dataStr["mdb"]["datumsData"] = (
            ("XZPLANE", 0.0), ("YZPLANE", 0.0), ("XYPLANE", 0.0))

    def calculateMdbGeometricParameters(self):
        """
        """
        r = self.dataStr["input"]["geometricParameters"]["containerRadius"]
        h = self.dataStr["input"]["geometricParameters"]["containerHeight"]
        self.dataStr["mdb"]["geometricParameters"] = {
            "radii": {
                "containerRadius": r},
            "verticalLevels": {
                "surface": 0.5*h},
            "tolerance": 5,
            "nodeSelectionTolerance": 0.5}

    def createPartsData(self):
        """
        """
        r = self.getRadiiParameters()
        vl = self.getVerticalLevelsParameters()

        self.dataStr["mdb"]["parts"] = {
            "sketchPoints": {
                "solidParts": {
                    "crackDomain": (
                        (0.0, -vl["surface"]),
                        (r["containerRadius"], vl["surface"]))},
                "shellParts": {},
                "crack": {
                    "crackGeometry": {
                        "a": self.getCrackParameters()["a"],
                        "b": self.getCrackParameters()["b"]}},
                "partitionedPart": {}},
            "mergedPart": {
                "name": "crackDomain"}}

    def createCrackPartitionPartData(self):
        """
        """
        crackParameters = self.getCrackParameters()
        a = crackParameters["a"]
        b = crackParameters["b"]
        crackType = self.getCrackType()
        parameters = {
            "surface": {
                "lines": (
                    ((a, 0.0), (0.0, 0.0)),
                    ((0.0, 0.0), (-a, 0.0))),
                "trimPoint": (0.0, -b)},
            "edge": {
                "lines": (
                    ((a, 0.0), (0.0, 0.0)),
                    ((0.0, 0.0), (0.0, b))),
                "trimPoint": (0.0, -b)},
            "embedded": {
                "lines": (((), ()), ((), ())),
                "trimPoint": ()}}
        self.dataStr["mdb"]["parts"]["crackPartition"] = {
            "ellipse": ((a, 0.0), (0.0, b)),
            "lines": parameters[crackType]["lines"],
            "trimPoint": parameters[crackType]["trimPoint"],
            "name": "crackPartitionPart"}

    def getCrackPartitionData(self):
        """
        """
        return self.dataStr["mdb"]["parts"]["crackPartition"]

    def getCrackPartData(self):
        """
        """
        return self.dataStr["mdb"]["parts"]["sketchPoints"]["crack"]

    def createSeedsData(self):
        """
        """
        seedParameters = self.getSeedInputParameters()
        self.dataStr["mdb"]["seeds"] = {}

        for key in seedParameters.keys():
            self.dataStr["mdb"]["seeds"][key] = (
                seedParameters[key], FREE)

    def createElementTypeData(self):
        """
        """
        elementType = self.getElementType()
        print "--------------------"
        print elementType
        print "--------------------"

        elementFamily = {
            "LinearTet": mesh.ElemType(
                elemCode=C3D4, elemLibrary=STANDARD, distortionControl=OFF),
            "LinearHexFI2ndOrdAcc": mesh.ElemType(
                elemCode=C3D8, elemLibrary=STANDARD,
                kinematicSplit=AVERAGE_STRAIN, secondOrderAccuracy=ON,
                hourglassControl=DEFAULT, distortionControl=DEFAULT),
            "LinearHexRI2ndOrdAcc": mesh.ElemType(
                elemCode=C3D8R, elemLibrary=STANDARD,
                kinematicSplit=AVERAGE_STRAIN, secondOrderAccuracy=ON,
                hourglassControl=DEFAULT, distortionControl=DEFAULT),
            "LinearHexRI": mesh.ElemType(
                elemCode=C3D8R, elemLibrary=STANDARD,
                kinematicSplit=AVERAGE_STRAIN, secondOrderAccuracy=OFF,
                hourglassControl=DEFAULT, distortionControl=DEFAULT),
            "LinearHexFI": mesh.ElemType(
                elemCode=C3D8,
                elemLibrary=STANDARD)}

        self.dataStr["mdb"]["meshParameters"]["elementCodes"] = elementFamily[elementType]

    def createCompleteSetsData(self):
        """
        """
        crackParameters = self.getCrackParameters()
        geometricParameters = self.getMdbGeometricParameters()
        tolerance = geometricParameters["tolerance"]
        containerRadius = geometricParameters["radii"]["containerRadius"]
        surfaceLevel = geometricParameters["verticalLevels"]["surface"]
        radius = max(crackParameters["a"], crackParameters["b"])

        self.dataStr["mdb"]["sets"]["setData"] = {
            "edges": {
                "allEdges": {
                    "center1": (0.0, 0.0, surfaceLevel + tolerance),
                    "center2": (0.0, 0.0, -surfaceLevel - tolerance),
                    "radius": containerRadius + tolerance},
                "crackEdges": {
                    "center1": (0.0, 0.0, tolerance),
                    "center2": (0.0, 0.0, -tolerance),
                    "radius": radius + tolerance}},
            "faces": {
                "crackFlanks": {
                    "center1": (0.0, 0.0, tolerance),
                    "center2": (0.0, 0.0, -tolerance),
                    "radius": radius + tolerance}}}

    def setSingularityCalcRadius(self, radius):
        """
        """
        radius = float(radius)
        self.dataStr["input"]["interactionProperties"][
            "crack"]["singularityCalcRadius"] = radius

    def getSingularityCalcRadius(self):
        """
        """
        return self.dataStr["input"]["interactionProperties"][
            "crack"]["singularityCalcRadius"]



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

import xfemBaseDataStr


class XFEMdataStrMP(xfemBaseDataStr.XFEMbaseDataStr):
    """
    """
    def __init__(self):
        """
        """
        xfemBaseDataStr.XFEMbaseDataStr.__init__(self)
        self.dataStr["input"]["modelType"] = "multiplePartitions"

    def calculateMdbGeometricParameters(self):
        """
        """
        xfemBaseDataStr.XFEMbaseDataStr.calculateMdbGeometricParameters(self)
        crackParameters = self.getCrackParameters()

        self.dataStr["mdb"]["geometricParameters"][
            "verticalLevels"]["smallCrackContainer"] = self.dataStr[
                "input"]["geometricParameters"]["smallContainerHeight"]
        self.dataStr["mdb"]["geometricParameters"][
            "smallContainerAxes"] = {
                "a": crackParameters["a"]/2.0 + self.dataStr["input"][
                    "geometricParameters"]["crackFrontOffset"],
                "b": crackParameters["b"]/2.0 + self.dataStr["input"][
                    "geometricParameters"]["crackFrontOffset"]}

    def createPartsData(self):
        """
        """
        xfemBaseDataStr.XFEMbaseDataStr.createPartsData(self)

        crackType = self.getCrackType()
        radii = self.getRadiiParameters()
        verticalLevels = self.getVerticalLevelsParameters()
        smallContainerAxes = self.getMdbGeometricParameters()[
            "smallContainerAxes"]
        a = smallContainerAxes["a"]
        b = smallContainerAxes["b"]
        parameters = {
            "edge": {
                "lines": (
                    ((a, 0.0), (0.0, 0.0)),
                    ((0.0, 0.0), (0.0, b))),
                "trimPoint": (0.0, -b)},
            "surface": {
                "lines": (
                    ((a, 0.0), (0.0, 0.0)),
                    ((0.0, 0.0), (-a, 0.0))),
                "trimPoint": (0.0, -b)},
            "embedded": {
                "lines": None,
                "trimPoint": None}}

        self.dataStr["mdb"]["parts"]["sketchPoints"][
            "smallContainer"] = {
                "ellipse": ((a, 0.0), (0.0, b)),
                "lines": parameters[crackType]["lines"],
                "trimPoint": parameters[crackType]["trimPoint"],
                "name": "smallContainer",
                "extrusionDepth": verticalLevels["smallCrackContainer"]}

    def getSmallContainerPartData(self):
        """
        """
        return self.dataStr["mdb"]["parts"]["sketchPoints"]["smallContainer"]

    def createParametersForLoft(self):
        """
        """
        containerRadius = self.getRadiiParameters()["containerRadius"]
        containerHeight = self.getVerticalLevelsParameters()["surface"]

        internalEdgePointPos = self.calcCoordsOfCrackContainerEllipseEdges(
            angle=45, heightUnitVector=1.0)
        internalEdgePointNeg = self.calcCoordsOfCrackContainerEllipseEdges(
            angle=45, heightUnitVector=-1.0)

        externalEdgePointPos = (
            containerRadius*math.cos(math.radians(30.0)),
            containerRadius*math.sin(math.radians(30.0)),
            containerHeight)
        externalEdgePointNeg = (
            containerRadius*math.cos(math.radians(30.0)),
            containerRadius*math.sin(math.radians(30.0)),
            -containerHeight)
        self.dataStr["mdb"]["parts"]["sketchPoints"][
            "smallContainer"]["loft"] = {
                "edgePoints": (
                    (internalEdgePointPos, externalEdgePointPos),
                    (internalEdgePointNeg, externalEdgePointNeg))}

    def calcCoordsOfCrackContainerEllipseEdges(self, angle, heightUnitVector):
        """
        """
        if (angle > 90 and angle < 180) or (angle > 270 and angle < 360):
            signX = -1
        else:
            signX = 1

        angle = math.radians(float(angle))
        smallContainerPartData = self.getSmallContainerPartData()
        height = 0.5*smallContainerPartData["extrusionDepth"]
        parameters = self.getMdbGeometricParameters()["smallContainerAxes"]
        a = parameters["a"]
        b = parameters["b"]
        x = math.sqrt(abs(((a**2)*(b**2)) /
                          (b**2 + (a**2)*(math.tan(angle)))))
        x = signX*x
        y = x * math.tan(angle)
        z = height*heightUnitVector
        return (x, y, z)

    def createDatumsData(self):
        """
        """
        self.dataStr["mdb"]["datumsData"] = (
            ("YZPLANE", 0.0), ("XZPLANE", 0.0))

    def createAdditionalSetsData(self):
        """
        """
        crackType = self.getCrackType()
        geometricParameters = self.getMdbGeometricParameters()
        tolerance = geometricParameters["tolerance"]
        smallContainerPartData = self.getSmallContainerPartData()
        height = 0.5*smallContainerPartData["extrusionDepth"]
        parameters = self.getMdbGeometricParameters()["smallContainerAxes"]
        a = parameters["a"]
        b = parameters["b"]
        self.dataStr["mdb"]["sets"]["setData"][
            "selectByBoundingBoxEdges"] = {
                "ellipseContainerEdges": {
                    "xMin": -1.1*a,
                    "xMax": 1.1*a,
                    "yMax": 1.1*b,
                    "yMin": -1.1*b,
                    "zMax": height + tolerance,
                    "zMin": -height - tolerance}}

    def createSeedsData(self):
        """
        """
        seedParameters = self.getSeedInputParameters()
        self.dataStr["mdb"]["seeds"] = {
            "ellipseContainerEdges": (seedParameters["crackContEdges"], FINER),
            "allEdges": (seedParameters["allEdges"], FINER)}

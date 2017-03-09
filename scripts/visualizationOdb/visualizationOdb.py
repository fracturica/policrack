

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

import visualization
from odbAccess import *
from odbMaterial import *
from odbSection import *
import k2_offset_funcs as kof


class VisualizationOdbFromDbEntry:
    """
    """
    def __init__(self, dataStr):
        """
        """
        self.dataStr = dataStr
        self.data = {
            "vectors": {
                "small": 1,
                "large": 3},
            "nodeSetNamesK2": {
                "outerContourInnerRow": 1,
                "outerContourOuterRow": 3,
                "innerContourInnerRow": -3,
                "innerContourOuterRow": -1},
            "nodeSetNamesK1": {
                "upperContourLowerRow": 1,
                "upperContourUpperRow": 3,
                "lowerContourLowerRow": -3,
                "lowerContourUpperRow": -1}}
        self.odb = {
            "odb": None,
            "nodeLabels": {},
            "elementLabels": {},
            "elements": (),
            "sections": {}}

    def initializeAbaqusOdb(self):
        """
        """
        self.data["odbName"] = "visualization" + self.dataStr.getModelName()
        self.odb["odb"] = Odb(
            name=self.data["odbName"],
            analysisTitle="SIF visualization",
            description="crack SIF visualization",
            path=self.data["odbName"] + ".odb")
        self.odb["assembly"] = self.odb["odb"].rootAssembly

    def initializeViewport(self):
        """
        """
        self.odb["viewport"] = session.Viewport(name=self.data["odbName"])
        self.odb["viewport"].makeCurrent()
        self.odb["viewport"].maximize()
        self.odb["viewport"].viewportAnnotationOptions.setValues(
            compassPrivilegedPlane=XYPLANE)

    def setViewportViewingPoint(self):
        """
        """
        self.odb["viewport"].view.setViewpoint(
            viewVector=(1.0, 1.0, 1.0),
            cameraUpVector=(0.0, 0.0, 1.0))
        session.View(
            name='Iso', nearPlane=548.9, farPlane=1005.6,
            width=326.16, height=396.91, projection=PARALLEL,
            cameraPosition=(523.82, 547.21, 447.21),
            cameraUpVector=(0, 0, 1), cameraTarget=(76.603, 100, 0),
            viewOffsetX=0, viewOffsetY=0, autoFit=ON)
        self.odb["viewport"].view.setValues(session.views["Iso"])

    def setDisplayedObject(self):
        """
        """
        self.odb["viewport"].setValues(displayedObject=self.odb["odb"])
        self.odb["viewport"].odbDisplay.setFrame(
            step=self.odb["step"],
            frame=self.odb["frame"])

    def createMaterial(self):
        """
        """
        material = self.dataStr.getMaterialProperties()
        self.odb["material"] = self.odb["odb"].Material(name=material["name"])
        self.odb["material"].Elastic(
            type=ISOTROPIC,
            table=((material["E"], material["v"]),))

    def createSections(self):
        """
        """
        material = self.dataStr.getMaterialProperties()
        self.odb["sections"]["truss"] = self.odb["odb"].TrussSection(
            name="trussSection",
            material=material["name"],
            area=1.0)
        self.odb["sections"]["shell"] = self.odb["odb"].HomogeneousShellSection(
            name="shellSection",
            material=material["name"],
            thickness=2.0)

    def createPart(self):
        """
        """
        self.odb["crackPart"] = self.odb["odb"].Part(
            name="crackVisualization",
            embeddedSpace=THREE_D,
            type=DEFORMABLE_BODY)

    def createNodes(self):
        """
        """
        nodeCounter = 1
        nodeData = ()
        nodeData = self.createCrackFrontNodes(nodeData)

        for nodeSetName in sorted(self.data["nodeSetNamesK2"].keys()):
            nodeData = self.createK2Nodes(nodeSetName, nodeData)

        for nodeSetName in sorted(self.data["nodeSetNamesK1"].keys()):
            nodeData = self.createK1Nodes(nodeSetName, nodeData)

        self.odb["crackPart"].addNodes(
            nodeData=nodeData,
            nodeSetName="nodes")
        self.data["numberOfNodes"] = nodeData[-1][0]

    def createK1Nodes(self, nodeSetName, nodeData):
        """
        """
        vector = self.data["nodeSetNamesK1"][nodeSetName]
        crackCoordinates = self.dataStr.getSortedCrackCoordinates()
        self.odb["nodeLabels"][nodeSetName] = ()
        nodeCounter = nodeData[-1][0]

        for point in crackCoordinates:
            (x, y, z) = point
            z += vector
            nodeCounter += 1
            nodeData += (nodeCounter, x, y, z),
            self.odb["nodeLabels"][nodeSetName] += nodeCounter,
        return nodeData

    def createK2Nodes(self, nodeSetName, nodeData):
        """
        """
        vector = self.data["nodeSetNamesK2"][nodeSetName]
        crackCoordinates = self.dataStr.getSortedCrackCoordinates()
        nodeCounter = nodeData[-1][0]
        self.odb["nodeLabels"][nodeSetName] = ()

        for point in crackCoordinates:
            print point
            (x, y, z) = self.calculateCoordinatesK2EllipseNormal(point, vector)
            nodeCounter += 1
            nodeData += (nodeCounter, x, y, z),
            self.odb["nodeLabels"][nodeSetName] += nodeCounter,
        return nodeData

    def calculateCoordinatesK2EllipseNormal(self, coordinates, vector):
        crackParameters = self.dataStr.getCrackParameters()
        a = float(crackParameters["a"])/2.0
        b = float(crackParameters["b"])/2.0
        return kof.findOffsetForPoint(coordinates, vector, a, b)

    def createCrackFrontNodes(self, nodeData):
        """
        """
        self.odb["nodeLabels"]["crackFront"] = ()
        crackCoordinates = self.dataStr.getSortedCrackCoordinates()
        nodeCounter = 0
        for point in crackCoordinates:
            (x, y, z) = point
            nodeCounter += 1
            nodeData += (nodeCounter, x, y, z),
            self.odb["nodeLabels"]["crackFront"] += nodeCounter,
        return nodeData

    def createElements(self):
        """
        """
        elementCounter = 1
        (elementCounter, elementData) = self.createCrackFrontElements(elementCounter)
        self.odb["crackPart"].addElements(
            elementData=elementData,
            type="T3D2",
            elementSetName="K3-Elements")

        elementData = ()
        (elementCounter, elementData) = self.createOuterK2(elementCounter, elementData)

        self.odb["crackPart"].addElements(
            elementData=elementData,
            type="CPS4R",
            elementSetName="K2-Elements")

        elementData = ()
        (elementCounter, elementData) = self.createUpperK1(elementCounter, elementData)
        (elementCounter, elementData) = self.createLowerK1(elementCounter, elementData)
        self.odb["crackPart"].addElements(
            elementData=elementData,
            type="CPS4R",
            elementSetName="K1-Elements")

    def createOuterK2(self, elementCounter, elementData):
        """
        """
        self.odb["elementLabels"]["outerK2"] = ()
        outerNodeLabels = self.odb["nodeLabels"]["outerContourOuterRow"]
        innerNodeLabels = self.odb["nodeLabels"]["outerContourInnerRow"]

        for index in range(len(outerNodeLabels)-1):
            nodeLabel1 = innerNodeLabels[index]
            nodeLabel2 = innerNodeLabels[index+1]
            nodeLabel3 = outerNodeLabels[index+1]
            nodeLabel4 = outerNodeLabels[index]
            elementData += (elementCounter,
                            nodeLabel1, nodeLabel2,
                            nodeLabel3, nodeLabel4),
            self.odb["elementLabels"]["outerK2"] += elementCounter,
            elementCounter += 1

        return elementCounter, elementData

    def createInnerK2(self, elementCounter, elementData):
        """
        """
        self.odb["elementLabels"]["innerK2"] = ()
        outerNodeLabels = self.odb["nodeLabels"]["innerContourOuterRow"]
        innerNodeLabels = self.odb["nodeLabels"]["innerContourInnerRow"]

        for index in range(len(outerNodeLabels)-1):
            nodeLabel1 = outerNodeLabels[index]
            nodeLabel2 = outerNodeLabels[index+1]
            nodeLabel3 = innerNodeLabels[index+1]
            nodeLabel4 = innerNodeLabels[index]

            elementData += (elementCounter,
                            nodeLabel1, nodeLabel2,
                            nodeLabel3, nodeLabel4),
            self.odb["elementLabels"]["innerK2"] += elementCounter,
            elementCounter += 1
        return elementCounter, elementData

    def createUpperK1(self, elementCounter, elementData):
        """
        """
        elementData = ()
        self.odb["elementLabels"]["upperK1"] = ()
        upperNodeLabels = self.odb["nodeLabels"]["upperContourUpperRow"]
        lowerNodeLabels = self.odb["nodeLabels"]["upperContourLowerRow"]

        for index in range(len(upperNodeLabels)-1):
            nodeLabel1 = lowerNodeLabels[index]
            nodeLabel2 = upperNodeLabels[index]
            nodeLabel3 = upperNodeLabels[index+1]
            nodeLabel4 = lowerNodeLabels[index+1]

            elementData += (elementCounter,
                            nodeLabel1, nodeLabel2,
                            nodeLabel3, nodeLabel4),
            self.odb["elementLabels"]["upperK1"] += elementCounter,
            elementCounter += 1
        return elementCounter, elementData

    def createLowerK1(self, elementCounter, elementData):
        """
        """
        self.odb["elementLabels"]["lowerK1"] = ()
        upperNodeLabels = self.odb["nodeLabels"]["lowerContourUpperRow"]
        lowerNodeLabels = self.odb["nodeLabels"]["lowerContourLowerRow"]

        for index in range(len(upperNodeLabels)-1):
            nodeLabel1 = upperNodeLabels[index]
            nodeLabel2 = upperNodeLabels[index+1]
            nodeLabel3 = lowerNodeLabels[index+1]
            nodeLabel4 = lowerNodeLabels[index]

            elementData += (elementCounter,
                            nodeLabel1, nodeLabel2,
                            nodeLabel3, nodeLabel4),
            self.odb["elementLabels"]["lowerK1"] += elementCounter,
            elementCounter += 1

        return elementCounter, elementData

    def createCrackFrontElements(self, elementCounter):
        """
        """
        elementData = ()
        self.odb["elementLabels"]["crackFront"] = ()
        nodeLabels = self.odb["nodeLabels"]["crackFront"]

        for label in nodeLabels[:-1]:
            elementData += (elementCounter, label, label+1),
            self.odb["elementLabels"]["crackFront"] += elementCounter,
            elementCounter += 1
        return elementCounter, elementData

    def createStepFrame(self):
        """
        """
        self.odb["step"] = self.odb["odb"].Step(
            name="step-1",
            description="",
            domain=TIME,
            timePeriod=1.0)
        self.odb["frame"] = self.odb["step"].Frame(
            incrementNumber=1,
            frameValue=0.1,
            description="")

    def createInstance(self):
        """
        """
        self.odb["crackInstance"] = self.odb["assembly"].Instance(
            name="crackVisualization",
            object=self.odb["crackPart"])

    def createFieldOutput(self):
        """
        """
        labels = range(1, self.data["numberOfNodes"]+1)
        # create SIFs K1, K2, K3 visualization in one FieldOutput
        averagedSIFs = self.dataStr.getSortedAveragedSIFs()
        values = averagedSIFs["K3"] + 4*averagedSIFs["K2"] + 4*averagedSIFs["K1"]
        data = ()
        for n in values:
            data += (n,),
        self.odb["field"] = self.odb["frame"].FieldOutput(
            name="SIFs",
            description="K1, K2, K3",
            type=SCALAR)
        self.odb["field"].addData(
            position=NODAL,
            instance=self.odb["crackInstance"],
            labels=labels,
            data=data)

        # create K1, K2, K3, JKs, Cpd, J, T, C visualization in separate FieldOutputs
        valueKeys = ("K1", "K2", "K3", "JKs", "Cpd", "J", "T", "C")
        for valueKey in valueKeys:
            if valueKey in averagedSIFs.keys():
                values = ()
                values = 9*averagedSIFs[valueKey]
                data = ()
                fieldKey = valueKey + "_field"
                for n in values:
                    data += (n,),
                self.odb[fieldKey] = self.odb["frame"].FieldOutput(
                    name=valueKey,
                    description=valueKey,
                    type=SCALAR)
                self.odb[fieldKey].addData(
                    position=NODAL,
                    instance=self.odb["crackInstance"],
                    labels=labels,
                    data=data)

        # create vector visualization of Cpd and JKs
        valueKeys = ("Cpd", "JKs")
        crackNodeLabels = self.odb["nodeLabels"]["crackFront"]
        nodeTree = self.getNodeCoords(crackNodeLabels)
        data = ()
        crackParameters = self.dataStr.getCrackParameters()
        a = 0.5*max(float(crackParameters["a"]), float(crackParameters["b"]))
        b = 0.5*min(float(crackParameters["a"]), float(crackParameters["b"]))

        for nodeLabel in crackNodeLabels:
            magnitude = averagedSIFs["JKs"][nodeLabel - 1] * 2
            theta = math.radians(float(averagedSIFs["Cpd"][nodeLabel - 1]))
            z = magnitude * math.sin(theta)
            x_prime = magnitude * math.cos(theta)
            (globalX, globalY, globalZ) = nodeTree[str(nodeLabel)]

            tanAlpha = (a**2 * globalY) / (b**2 * globalX)
            alpha = math.atan(tanAlpha)

            deltaY = x_prime * math.sin(alpha)
            deltaX = x_prime * math.cos(alpha)

            x = math.copysign(deltaX, globalX)
            y = math.copysign(deltaY, globalY)

            vector = (x, y, z)
            data += vector,

        self.odb["cpd_vect"] = self.odb["frame"].FieldOutput(
            name="cpd_vect",
            description="cpd_vect",
            type=VECTOR,
            validInvariants=(MAGNITUDE,))
        self.odb["cpd_vect"].addData(
            position=NODAL,
            instance=self.odb["crackInstance"],
            labels=crackNodeLabels,
            data=data)

    def getNodeCoords(self, nodeLabels):
        """
        """
        nodeTree = {}
        for node in self.odb["crackInstance"].nodes:
            if node.label in nodeLabels:
                nodeTree[str(node.label)] = node.coordinates
        return nodeTree

    def setDefaultField(self):
        """
        """
        self.odb["step"].setDefaultField(self.odb["field"])

    def saveOdb(self):
        """
        """
        self.odb["odb"].save()
        self.odb["odb"].close()

    def reopenOdb(self):
        """
        """
        self.odb["odb"] = openOdb(
            path=self.data["odbName"] + ".odb",
            readOnly=False)

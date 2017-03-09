

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
import customKernel

import scripts.modelDb.baseCrack as baseCrack


class FEMcrackOrphanMesh(baseCrack.BaseCrackMdb):
    """
    """
    def __init__(self, inputData):
        """
        """
        baseCrack.BaseCrackMdb.__init__(self, inputData)

        self.mdb["sets"] = {
            "elementSets": {},
            "nodeSets": {"innerCylinder": {}}}

    def initializeAbaqusModel(self):
        """
        """
        modelName = self.inputData.getModelName()
        inputFileName = modelName + ".inp"
        Mdb()

        self.mdb["model"] = mdb.ModelFromInputFile(
            name=modelName,
            inputFileName=inputFileName)

        self.mdb["assembly"] = self.mdb["model"].rootAssembly
        del mdb.models["Model-1"]

    def clearImportedModel(self):
        """
        """
        self.deleteSets()
        self.renameInteractions()
        self.renamePart()
        self.assignVariableToPart()
        self.renameInstance()
        self.assignVariableToInstance()

    def deleteSets(self):
        """
        """
        setNames = ()
        setData = self.inputData.getSetData()

        for setType in setData.keys():
            for setName in setData[setType].keys():
                setNames += setName.upper(),

        for setName in setNames:
            self.mdb["assembly"].deleteSets(setNames=(setName,))

    def renameInteractions(self):
        """
        """
        self.renameCrack()
        self.renameContactProperty()
        self.renameHistoryOutput()
        self.updateHistoryOutput()
        self.deleteContactInteraction()

    def renameCrack(self):
        """
        """
        (currentCrackName,) = self.mdb["assembly"].engineeringFeatures.cracks.keys()
        crackName = self.inputData.getCrackInteractionProperties()["name"]

        self.mdb["assembly"].engineeringFeatures.cracks.changeKey(
            fromName=currentCrackName,
            toName=crackName)

    def renameContactProperty(self):
        """
        """
        (currentContactPropertyName,) = self.mdb["model"].interactionProperties.keys()
        contactProperties = self.inputData.getCrackContactProperties()
        crackContactPropertyName = contactProperties["crackContactPropertyName"]

        self.mdb["model"].interactionProperties.changeKey(
            fromName=currentContactPropertyName,
            toName=crackContactPropertyName)

    def renameHistoryOutput(self):
        """
        """
        (currentHistoryOutputName,) = self.mdb["model"].historyOutputRequests.keys()
        historyOutputName = self.inputData.getCrackInteractionProperties()["historyOutputName"]

        self.mdb["model"].historyOutputRequests.changeKey(
            fromName=currentHistoryOutputName,
            toName=historyOutputName)

    def updateHistoryOutput(self):
        """
        """
        crackProperties = self.inputData.getCrackInteractionProperties()
        historyOutputName = crackProperties["historyOutputName"]
        contourIntegralName = crackProperties["name"]

        self.mdb["model"].historyOutputRequests[historyOutputName].setValues(
            contourIntegral=contourIntegralName)

    def deleteContactInteraction(self):
        """
        """
        (currentContactInteractionName,) = self.mdb["model"].interactions.keys()
        del self.mdb["model"].interactions[currentContactInteractionName]

    def renamePart(self):
        """
        """
        (orphanMeshCurrentName,) = self.mdb["model"].parts.keys()
        orphanMeshPartName = self.inputData.getOrphanMeshPartName()

        self.mdb["model"].parts.changeKey(
            fromName=orphanMeshCurrentName,
            toName=orphanMeshPartName)


    def assignVariableToPart(self):
        """
        """
        (orphanMeshCurrentName,) = self.mdb["model"].parts.keys()
        self.mdb["orphanMeshPart"] = self.mdb["model"].parts[orphanMeshCurrentName]

    def renameInstance(self):
        """
        """
        (currentInstanceName,) = self.mdb["assembly"].instances.keys()
        orphanMeshPartName = self.inputData.getOrphanMeshPartName()

        self.mdb["assembly"].instances.changeKey(
            fromName=currentInstanceName,
            toName=orphanMeshPartName)

    def assignVariableToInstance(self):
        """
        """
        (instanceCurrentName,) = self.mdb["assembly"].instances.keys()
        self.mdb["orphanMeshInstance"] = self.mdb["assembly"].instances[instanceCurrentName]

    def createElementSets(self):
        """
        temporarily disabled for testing
        """
        elementSetData = self.inputData.getElementSetData()
        for setName in elementSetData.keys():
            setData = elementSetData[setName]
            self.createInnerCylinderElementSet(
                setName=setName,
                setData=setData)

    def createInnerCylinderElementSet(self, setName, setData):
        """
        """
        center1 = setData["center1"]
        center2 = setData["center2"]
        radius = setData["radius"]

        elements = self.mdb["orphanMeshPart"].elements.getByBoundingCylinder(
            center1=center1,
            center2=center2,
            radius=radius)

        self.mdb["sets"]["elementSets"][setName] = self.mdb[
            "orphanMeshPart"].Set(name=setName, elements=elements)

    def deleteCentralWedgeElements(self):
        """
        """
        labels = self.selectCentralWedgeElements()
        self.deleteElementsWithLabels(labels)

    def selectCentralWedgeElements(self):
        """
        """
        elementSetData = self.inputData.getElementSetData()
        elementLabels = ()

        for setName in elementSetData.keys():
            elements = self.mdb["sets"]["elementSets"][setName].elements
            for element in elements:
                if self.isWedgeElement(element):
                    elementLabels += element.label,
        return elementLabels

    def deleteElementsWithLabels(self, elementLabels):
        """
        """
        elementSequence = self.mdb[
            "orphanMeshPart"].elements.sequenceFromLabels(
                labels=elementLabels)

        self.mdb["orphanMeshPart"].deleteElement(
            elements=elementSequence,
            deleteUnreferencedNodes=True)

    def isWedgeElement(self, element):
        """
        """
        if (element.type == C3D15) or (element.type == C3D6):
            return True
        else:
            return False

    def createSetForExternalNodes(self):
        """
        """
        containerHeight = self.inputData.getVerticalLevelsParameters()["surface"]
        containerRadius = self.inputData.getRadiiParameters()["containerRadius"]
        tolerance = self.inputData.getNodeSelectionTolerance()
        nodeSelectionRadiusSquared = containerRadius**2 - tolerance
        externalNodeSetName = self.inputData.getExternalNodeSetName()

        nodeLabels = ()

        for node in self.mdb["orphanMeshPart"].nodes:
            (x, y, z) = node.coordinates

            if abs(z) == containerHeight:
                nodeLabels += node.label,

            if node.label not in nodeLabels:
                nodeRadiusSquare = x**2 + y**2

                if nodeRadiusSquare >= nodeSelectionRadiusSquared:
                    nodeLabels += node.label,

        nodeSequence = self.mdb['orphanMeshPart'].nodes.sequenceFromLabels(
            labels=nodeLabels)

        self.mdb['sets']['nodeSets'][externalNodeSetName] = self.mdb[
            'orphanMeshPart'].Set(
                name=externalNodeSetName,
                nodes=nodeSequence)

    def createSetFromInnerCylinderNodes(self):
        """
        to rename the method
        """
        self.findInnerCylinderElementSetWedgeElementsRadius()

        elementSetData = self.inputData.getElementSetData()

        for elementSetName in elementSetData.keys():
            self.createInnerCylinderNodeSetFromElementSet(elementSetName)

    def findInnerCylinderElementSetWedgeElementsRadius(self):
        """
        """
        radius = self.inputData.getRadiiParameters()["containerRadius"]
        elementSetData = self.inputData.getElementSetData()
        elementKey = elementSetData.keys()[0]
        elements = self.mdb["sets"]["elementSets"][elementKey].elements

        for element in elements:
            nodes = element.getNodes()
            for node in nodes:
                (x, y, z) = node.coordinates
                nodeRadius = (x**2 + y**2)**0.5
                if radius > nodeRadius:
                    radius = nodeRadius

        radius += self.inputData.getNodeSelectionTolerance()
        self.inputData.setInnerCylinderHoleRadius(radius)

    def createInnerCylinderNodeSetFromElementSet(self, elementSetName):
        """
        """
        nodeLabels = ()
        elements = self.mdb["sets"]["elementSets"][elementSetName].elements

        nodeSetName = elementSetName
        wedgeElementsRadius = self.inputData.getInnerCylinderHoleRadius()

        for element in elements:
            nodes = element.getNodes()

            for node in nodes:
                (x, y, z) = node.coordinates
                nodeRadius = math.sqrt(x**2 + y**2)

                if nodeRadius <= wedgeElementsRadius:
                    if node.label not in nodeLabels:
                        nodeLabels += node.label,

        nodeSequence = self.mdb["orphanMeshPart"].nodes.sequenceFromLabels(
            labels=nodeLabels)
        self.mdb["sets"]["nodeSets"]["innerCylinder"][nodeSetName] = self.mdb[
            "orphanMeshPart"].Set(name=nodeSetName, nodes=nodeSequence)

    def applyMeshTransformation(self):
        """
        """
        nodes = self.mdb["orphanMeshPart"].nodes
        transformationType = self.inputData.getMeshTransformationType()

        calculateCoordinates = {
            "elliptic": self.calculateEllipticCoordinates,
            "simpleScale": self.calculateSimpleScaleCoordinates,
            "advancedScale": self.calculateAdvancedScaleCoordinates}

        for node in nodes:
            newCoordinates = calculateCoordinates[transformationType](node)
            nodeLabel = node.label,
            nodeSequence = self.mdb["orphanMeshPart"].nodes.sequenceFromLabels(
                labels=nodeLabel)
            self.moveNode(nodeSequence, newCoordinates)

    def calculateEllipticCoordinates(self, node):
        """
        """
        (x, y, z) = node.coordinates
        crackParameters = self.inputData.getCrackParameters()
        a = max(crackParameters["a"], crackParameters["b"])/2.0
        b = min(crackParameters["a"], crackParameters["b"])/2.0
        transformationAxis = self.inputData.getMeshTransformationAxis()

        if transformationAxis == "X":
            x = x*math.sqrt(1 + (a**2 - b**2) / (x**2 + y**2))

        if transformationAxis == "Y":
            y = y*math.sqrt(1 + (a**2 - b**2) / (x**2 + y**2))

        return (x, y, z)

    def calculateSimpleScaleCoordinates(self, node):
        """
        """
        (x, y, z) = node.coordinates
        crackParameters = self.inputData.getCrackParameters()
        a = max(crackParameters["a"], crackParameters["b"])/2.0
        b = min(crackParameters["a"], crackParameters["b"])/2.0
        transformationAxis = self.inputData.getMeshTransformationAxis()
        scaleFactor = a / b

        if transformationAxis == "X":
            x = scaleFactor*x
        if transformationAxis == "Y":
            y = scaleFactor*y
        return (x, y, z)

    def calculateAdvancedScaleCoordinates(self, node):
        """
        """
        (x, y, z) = node.coordinates
        crackParameters = self.inputData.getCrackParameters()
        a = max(crackParameters["a"], crackParameters["b"])/2.0
        b = min(crackParameters["a"], crackParameters["b"])/2.0
        radius = self.inputData.getRadiiParameters()["crackRadius"]
        transformationAxis = self.inputData.getMeshTransformationAxis()

        expansionScaleFactor = a / radius
        contractionScaleFactor = b / radius

        if transformationAxis == "X":
            x = expansionScaleFactor * x
            y = contractionScaleFactor * y
        if transformationAxis == "Y":
            x = contractionScaleFactor * x
            y = expansionScaleFactor * y
        return (x, y, z)

    def moveNode(self, nodeSequence, coordinates):
        """
        """
        (x, y, z) = coordinates
        self.mdb["orphanMeshPart"].editNode(
            nodes=nodeSequence,
            coordinate1=x,
            coordinate2=y,
            coordinate3=z)

    def closeInnerCylinderHole(self):
        """
        """
        nodeSetNames = self.mdb["sets"]["nodeSets"]["innerCylinder"].keys()

        for nodeSetName in nodeSetNames:
            nodes = self.mdb["sets"]["nodeSets"]["innerCylinder"][nodeSetName].nodes
            self.moveInnerCylinderHoleNodesToPlane(nodes)

            self.mergeNodes(nodes)

        self.regenerateAssembly()

    def moveInnerCylinderHoleNodesToPlane(self, nodes):
        """
        """
        transformationAxis = self.inputData.getMeshTransformationAxis()

        if transformationAxis =="X":
            self.mdb["orphanMeshPart"].editNode(
                nodes=nodes,
                coordinate2=0.0)

        if transformationAxis == "Y":
            self.mdb["orphanMeshPart"].editNode(
                nodes=nodes,
                coordinate1=0.0)

    def mergeNodes(self, nodes):
        """
        """
        tolerance = self.inputData.getMergeNodesTolerance()
        self.mdb["orphanMeshPart"].mergeNodes(
            nodes=nodes,
            tolerance=tolerance)

    def adjustMidsideNodes(self, nodes):
        """
        """
        self.mdb["orphanMeshPart"].adjustMidsideNode(
            cornerNodes=nodes,
            parameter=0.5)

    def redefineCrackInteraction(self):
        """
        """
        crackName = self.inputData.getCrackInteractionProperties()["name"]
        del self.mdb["assembly"].engineeringFeatures.cracks[crackName]

        self.mdb["assembly"].engineeringFeatures.ContourIntegral(
            name=crackName,
            crackFront=self.mdb["assembly"].sets["ContInt-1-Front"],
            crackTip=self.mdb["assembly"].sets["ContInt-1-Front"],
            collapsedElementAtTip=NONE,
            crackNormal=(
                (0.0, 0.0, 0.0),
                (0.0, 0.0, -1.0)),
            extensionDirectionMethod=CRACK_NORMAL,
            symmetric=OFF)

    def getExternalNodes(self):
        """
        """
        externalNodeSetName = self.inputData.getExternalNodeSetName()
        return self.mdb["sets"]["nodeSets"][externalNodeSetName].nodes

    def getCrackContainerInstance(self):
        """
        """
        return self.mdb["orphanMeshInstance"]

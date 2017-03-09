

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

import config


class BaseCrackMdb:
    """
    """
    def __init__(self, inputData):
        """
        """
        self.inputData = inputData
        self.mdb = {}
        self.mdb["parts"] = {}

    def initializeAbaqusModel(self):
        """
        """
        modelName = self.inputData.getModelName()
        Mdb()
        self.mdb["model"] = mdb.Model(name=modelName)
        self.mdb["assembly"] = self.mdb["model"].rootAssembly
        del mdb.models["Model-1"]

    def writeCustomKernelInputData(self):
        """
        """
        data = self.inputData.getDataForPickling()
        mdb.customData.metadata = data

    def deleteModels(self):
        """
        """
        modelNames = mdb.models.keys()
        print modelNames

        for modelName in modelNames:
            del mdb.models[modelName]

    def initializeViewport(self):
        """
        """
        modelName = self.inputData.getModelName()
        self.mdb["viewport"] = session.Viewport(name=modelName)
        self.mdb["viewport"].makeCurrent()
        self.mdb["viewport"].maximize()
        self.mdb["viewport"].viewportAnnotationOptions.setValues(
            compassPrivilegedPlane=XYPLANE)

    def setViewportViewingPoint(self):
        """
        """
        self.mdb["viewport"].view.setViewpoint(
            viewVector=(1.0, 1.0, 1.0),
            cameraUpVector=(0.0, 0.0, 1.0))
        session.View(
            name='Iso', nearPlane=548.9, farPlane=1005.6,
            width=326.16, height=396.91, projection=PARALLEL,
            cameraPosition=(523.82, 547.21, 447.21),
            cameraUpVector=(0, 0, 1), cameraTarget=(76.603, 100, 0),
            viewOffsetX=0, viewOffsetY=0, autoFit=ON)
        self.mdb["viewport"].view.setValues(session.views["Iso"])

    def setDisplayedObject(self, objectToDisplay):
        """
        """
        self.mdb["viewport"].setValues(displayedobject=objectToDisplay)

    def createSolidParts(self):
        """
        """
        solidParts = self.inputData.getSolidPartsParameters()
        for name in solidParts.keys():
            partSketchPoints = solidParts[name]
            self.createASolidRevolvedPart(name, partSketchPoints)

    def createShellParts(self):
        """
        """
        shellParts = self.inputData.getShellPartsParameters()
        for name in shellParts.keys():
            partSketchPoints = shellParts[name]
            self.createAShellRevolvedPart(name, partSketchPoints)

    def createASolidRevolvedPart(self, partName, partSketchPoints):
        """
        """
        points = partSketchPoints
        sketchName = partName
        revolutionAngle = self.inputData.getMdbGeometricParameters()["revolutionAngle"]
        containerRadius = self.inputData.getRadiiParameters()["containerRadius"]

        crossSectionSketch = self.mdb["model"].ConstrainedSketch(
            name=sketchName,
            sheetSize=2*containerRadius,
            transform=(
                1.0, 0.0, 0.0,
                0.0, 0.0, -1.0,
                0.0, 1.0, 0.0,
                0.0, 0.0, 0.0))
        crossSectionSketch.rectangle(
            point1=points[0], point2=points[1])

        revolutionAxis = crossSectionSketch.ConstructionLine(
            point1=(0.0, 0.0),
            point2=(0.0, 1.0))
        crossSectionSketch.assignCenterline(line=revolutionAxis)

        self.mdb["parts"][partName] = self.mdb["model"].Part(
            name=partName,
            dimensionality=THREE_D,
            type=DEFORMABLE_BODY)
        self.mdb["parts"][partName].BaseSolidRevolve(
            sketch=crossSectionSketch,
            angle=revolutionAngle)
        self.createPartOrientation(self.mdb["parts"][partName])

    def createPartOrientation(self, part):
        """
        """
        part.DatumCsysByThreePoints(
            name='Datum csys-1',
            coordSysType=CARTESIAN,
            origin=(0.0, 0.0, 0.0),
            line1=(1.0, 0.0, 0.0),
            line2=(0.0, 1.0, 0.0))
        self.createMaterialOrientation(part)

    def createMaterialOrientation(self, part):
        """
        """
        region = regionToolset.Region(cells=part.cells)
        localCsys = part.datums[2]
        part.MaterialOrientation(
            region=region, orientationType=GLOBAL,
            axis=AXIS_1, additionalRotationType=ROTATION_NONE,
            localCsys=None, fieldName='',
            stackDirection=STACK_3)

    def createAShellRevolvedPart(self, partName, partSketchPoints):
        """
        """
        sketchName = partName
        points = partSketchPoints
        revolutionAngle = self.inputData.getMdbGeometricParameters()["revolutionAngle"]
        containerRadius = self.inputData.getRadiiParameters()["containerRadius"]

        crossSectionSketch = self.mdb["model"].ConstrainedSketch(
            name=sketchName,
            sheetSize=2*containerRadius,
            transform=(
                1.0, 0.0, 0.0,
                0.0, 0.0, -1.0,
                0.0, 1.0, 0.0,
                0.0, 0.0, 0.0))
        crossSectionSketch.Line(point1=points[0], point2=points[1])

        revolutionAxis = crossSectionSketch.ConstructionLine(
            point1=(0.0, 0.0),
            point2=(0.0, 1.0))
        crossSectionSketch.assignCenterline(line=revolutionAxis)

        self.mdb["parts"][partName] = self.mdb["model"].Part(
            name=partName,
            dimensionality=THREE_D,
            type=DEFORMABLE_BODY)
        self.mdb["parts"][partName].BaseShellRevolve(
            sketch=crossSectionSketch,
            angle=revolutionAngle)
        self.createPartOrientation(self.mdb["parts"][partName])

    def createMergedPart(self):
        """
        """
        allInstances = ()
        for instanceName in self.mdb["assembly"].instances.keys():
            instance = self.mdb["assembly"].instances[instanceName]
            allInstances += instance,

        partName = self.inputData.getMergedPartName()

        self.mdb["parts"][partName] = self.mdb["assembly"].PartFromBooleanMerge(
            name=partName,
            instances=allInstances,
            keepIntersections=True,
            domain=GEOMETRY)

        self.createPartOrientation(self.mdb["parts"][partName])

    def createDatums(self):
        """
        """
        datumsData = self.inputData.getDatumsData()
        for datumData in datumsData:
            principalPlane = eval(datumData[0])
            offset = datumData[1]
            self.mdb["assembly"].DatumPlaneByPrincipalPlane(
                principalPlane=principalPlane,
                offset=offset)

    def deleteAllInstances(self):
        """
        """
        for instanceName in self.mdb["assembly"].instances.keys():
            del self.mdb["assembly"].instances[instanceName]

    def createInstancesFromAllParts(self):
        """
        """
        for partName in self.mdb["parts"].keys():
            self.createInstance(partName)

    def createMergedPartInstance(self):
        """
        """
        mergedPartName = self.inputData.getMergedPartName()
        self.mdb["mergedInstance"] = self.createInstance(mergedPartName)

    def createInstance(self, partName):
        """
        """
        instanceName = partName
        instance = self.mdb["assembly"].Instance(
            name=instanceName,
            part=self.mdb["parts"][partName],
            dependent=False)
        return instance

    def createMaterial(self):
        """
        """
        material = self.inputData.getMaterialProperties()
        v = material["v"]
        E = material["E"]
        name = material["name"]
        self.mdb["model"].Material(name=name)
        self.mdb["model"].materials[name].Elastic(table=((E, v),))

    def createSection(self):
        """
        """
        materialName = self.inputData.getMaterialProperties()["name"]
        sectionName = self.inputData.getSectionName()
        self.mdb["model"].HomogeneousSolidSection(
            name=sectionName,
            material=materialName,
            thickness=1.0)

    def assignSectionToAllParts(self):
        """
        """
        sectionName = self.inputData.getSectionName()
        for partName in self.mdb["parts"].keys():
            part = self.mdb["parts"][partName]
            region = regionToolset.Region(cells=part.cells)
            part.SectionAssignment(region=region, sectionName=sectionName)

    def assignSectionToMergedPart(self):
        """
        """
        mergedPartName = self.inputData.getMergedPartName()
        self.assignSectionToPart(mergedPartName)

    def assignSectionToPart(self, partName):
        """
        """
        sectionName = self.inputData.getSectionName()
        region = regionToolset.Region(cells=self.mdb["parts"][partName].cells)
        self.mdb["parts"][partName].SectionAssignment(
            region=region,
            sectionName=sectionName)

    def regenerateAssembly(self):
        """
        """
        self.mdb["assembly"].regenerate()

    def createStep(self):
        """
        """
        stepName = self.inputData.getStepName()
        self.mdb["model"].StaticStep(
            name=stepName,
            previous="Initial",
            description="Apply Loads")

    def deleteHistoryOutputs(self):
        """
        """
        historyOutputs = self.mdb["model"].historyOutputRequests
        for historyOutputName in historyOutputs.keys():
            del historyOutputs[historyOutputName]

    def createHistoryOutput(self):
        """
        """
        stepName = self.inputData.getStepName()
        crackProperties = self.inputData.getCrackInteractionProperties()
        contourIntegralName = crackProperties["name"]
        numberOfContours = crackProperties["numberOfContours"]
        contourTypes = {
            "K_FACTORS": K_FACTORS,
            "J_INTEGRAL": J_INTEGRAL,
            "C_INTEGRAL": C_INTEGRAL,
            "T_STRESS": T_STRESS}
        for histOutName in crackProperties["historyOutputs"].keys():
            contourType = contourTypes[crackProperties["historyOutputs"][histOutName]]
            self.mdb["model"].HistoryOutputRequest(
                name=histOutName,
                createStepName=stepName,
                contourIntegral=contourIntegralName,
                numberOfContours=numberOfContours,
                contourType=contourType)

    def createContactInteractionProperty(self):
        """
        """
        contactProperties = self.inputData.getCrackContactProperties()
        contactPropertyName = contactProperties["crackContactPropertyName"]

        self.mdb["model"].ContactProperty(name=contactPropertyName)
        self.mdb["model"].interactionProperties[
            contactPropertyName].NormalBehavior(
                constraintEnforcementMethod=DEFAULT,
                pressureOverclosure=HARD,
                allowSeparation=True)

        self.mdb["model"].interactionProperties[
            contactPropertyName].TangentialBehavior(formulation=FRICTIONLESS)

    def createGeneralContact(self):
        """
        """
        contactProperties = self.inputData.getCrackContactProperties()
        crackContactName = contactProperties["crackContactName"]
        crackContactProperties = contactProperties["crackContactPropertyname"]

        self.mdb["model"].ContactStd(
            name=crackContactName,
            createStepName="Initial",
            useAllstar=ON,
            contactPropertyAssignments=(
                (GLOBAL, SELF, crackContactPropertyName),))

    def assignElementType(self):
        """
        """
        elementCodes = self.inputData.getElementCodes()
        regions = regionToolset.Region(cells=self.mdb["mergedInstance"].cells)
        self.mdb["assembly"].setElementType(
            regions=regions,
            elemTypes=elementCodes)

    def generateMesh(self):
        """
        """
        regions = self.mdb["mergedInstance"].cells
        self.mdb["assembly"].generateMesh(regions=regions)

    def seedEdges(self):
        """
        """
        seeds = self.inputData.getMdbSeedParameters()

        for edgesSetName in seeds.keys():

            seedsNumber = seeds[edgesSetName][0]
            seedsConstraint = seeds[edgesSetName][1]
            self.mdb["assembly"].seedEdgeByNumber(
                edges=self.mdb["sets"]["edges"][edgesSetName].edges,
                number=seedsNumber,
                constraint=seedsConstraint)

    def verifyMesh(self):
        """
        """
        meshQualityReport = self.mdb["assembly"].verifyMeshQuality(
            criterion=ANALYSIS_CHECKS)
        meshPrettyReport = {}
        meshPrettyReport["numElements"] = meshQualityReport["numElements"]

        for key in ('warningElements', 'failedElements', 'naElements'):
            value = len(meshQualityReport[key])
            meshPrettyReport[key] = value
        return meshPrettyReport

    def createBC(self):
        """
        """
        if self.inputData.getCreatePredefinedBCsFlag():
            applyBoundaryConditionsForCrackModel = {
                "embedded": self.createInfiniteCylinderBC,
                "edge": self.createInfiniteCylinderBC,
                "surface": self.createInfiniteCylinderBC}

            crackType = self.inputData.getCrackParameters()["crackType"]
            applyBoundaryConditionsForCrackModel[crackType]()

    def createInfiniteCylinderBC(self):
        """
        """
        counter = 0
        nodes = self.getExternalNodes()
        stepName = self.inputData.getStepName()
        datumKeys = self.mdb["assembly"].datums.keys()
        datumKeys.sort()
        datumNumber = datumKeys[-1]
        coordinateSystem = self.mdb["assembly"].datums[datumNumber]

        for node in nodes:
            counter += 1
            displacements = self.calculateInfiniteCylinderDisplacementForNode(node)
            self.mdb["model"].DisplacementBC(
                name="displacementBC-" + str(counter),
                createStepName=stepName,
                region=self.makeRegionForBCFromNode(node),
                distributionType=UNIFORM,
                amplitude=UNSET,
                u1=displacements[0],
                u2=displacements[1],
                u3=displacements[2],
                localCsys=coordinateSystem)

    def makeRegionForBCFromNode(self, node):
        """
        """
        instance = self.getCrackContainerInstance()
        nodeSeq = instance.nodes.sequenceFromLabels(labels=(node.label,))
        region = regionToolset.Region(nodes=nodeSeq)
        return region

    def calculateInfiniteCylinderDisplacementForNode(self, node):
        """
        """
        coords = node.coordinates
        crackType = self.inputData.getCrackParameters()["crackType"]
        transformedCoords = self.transformCoordsByRotationMatrix(coords)
        if crackType == "embedded":
            displacementBCs = self.calculateBCforEmbeddedCrack(transformedCoords)
        if crackType == "surface":
            displacementBCs = self.calculateBCforSurfaceCrack(transformedCoords)
        if crackType == "edge":
            displacementBCs = self.calculateBCforEdgeCrack(transformedCoords)
        revDisplacementBCs = self.reverseTransformCoordsRotMatrix(displacementBCs)
        return revDisplacementBCs

    def transformCoordsByRotationMatrix(self, coords):
        """
        """
        (x, y, z) = coords
        bcParameters = self.inputData.getBCParameters()
        gamma = math.radians(float(bcParameters["gamma"]))
        omega = math.radians(float(bcParameters["omega"]))
        xPrime = (
            x*math.cos(gamma)*math.cos(omega) +
            y*math.cos(gamma)*math.sin(omega) -
            z*math.sin(gamma))
        yPrime = (
            -x*math.sin(omega) +
            y*math.cos(omega))
        zPrime = (
            x*math.sin(gamma)*math.cos(omega) +
            y*math.sin(gamma)*math.sin(omega) +
            z*math.cos(gamma))
        return (xPrime, yPrime, zPrime)

    def reverseTransformCoordsRotMatrix(self, coords):
        """
        """
        (x, y, z) = coords
        bcParameters = self.inputData.getBCParameters()
        gamma = math.radians(float(bcParameters["gamma"]))
        omega = math.radians(float(bcParameters["omega"]))
        xRev = (
            x*math.cos(gamma)*math.cos(omega) -
            y*math.sin(omega) +
            z*math.sin(gamma)*math.cos(omega))
        yRev = (
            x*math.cos(gamma)*math.sin(omega) +
            y*math.cos(omega) +
            z*math.sin(gamma)*math.sin(omega))
        zRev = (
            -x*math.sin(gamma) +
            z*math.cos(gamma))
        return (xRev, yRev, zRev)

    def calculateBCforEmbeddedCrack(self, coords):
        """
        """
        (x, y, z) = coords
        bcParameters = self.inputData.getBCParameters()
        sigma = float(bcParameters["sigma"])
        E = float(bcParameters["E"])
        v = float(bcParameters["v"])

        dispZ = (sigma / E) * z
        dispX = - v * (sigma / E) * x
        dispY = - v * (sigma / E) * y
        return (dispX, dispY, dispZ)

    def calculateBCforSurfaceCrack(self, coords):
        """
        """
        (x, y, z) = coords
        bcParameters = self.inputData.getBCParameters()
        sigma = float(bcParameters["sigma"])
        E = float(bcParameters["E"])
        v = float(bcParameters["v"])

        nodes = self.getExternalNodes()
        maxY = 0
        for node in nodes:
            y1 = node.coordinates[1]
            if y1 > maxY:
                maxY = y1
        dispZ = (sigma / E) * z
        dispX = - v * (sigma / E) * x
        dispY = - v * (sigma / E) * (y - maxY)
        return (dispX, dispY, dispZ)

    def calculateBCforEdgeCrack(self, coords):
        """
        """
        (x, y, z) = coords
        bcParameters = self.inputData.getBCParameters()
        sigma = float(bcParameters["sigma"])
        E = float(bcParameters["E"])
        v = float(bcParameters["v"])

        nodes = self.getExternalNodes()
        maxY = 0
        maxX = 0
        for node in nodes:
            x1 = node.coordinates[0]
            y1 = node.coordinates[1]
            if y1 > maxY:
                maxY = y1
            if x1 > maxX:
                maxX = x1

        dispZ = (sigma / E) * z
        dispX = - v * (sigma / E) * (x - maxX)
        dispY = - v * (sigma / E) * (y - maxY)
        return (dispX, dispY, dispZ)

    def createJob(self):
        """
        """
        modelName = self.inputData.getModelName()
        self.mdb["Job"] = mdb.Job(
            name=modelName,
            model=modelName,
            type=ANALYSIS,
            description="Analysis Job",
            memory=config.memory,
            memoryUnits=GIGA_BYTES,
            numCpus=config.numCpus,
            multiprocessingMode=MPI,
            numDomains=config.numDomains)

    def submitJob(self):
        """
        """
        self.mdb["Job"].submit()
        self.mdb["Job"].waitForCompletion()

    def closeMdb(self):
        """
        """
        mdb.close()

    def saveMdb(self):
        """
        """
        modelName = self.inputData.getModelName()
        print "saveMdb", modelName
        mdb.saveAs(modelName)

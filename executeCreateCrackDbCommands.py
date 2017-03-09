

import sys
import scripts.dataStr.femDataStr as femDataStr
import scripts.dataStr.xfemTETdataStr as xfemTETdataStr
import scripts.dataStr.xfemDataStrMP as xfemDataStrMP
import scripts.dataStr.xfemSimpleDataStr as xfemSimpleDataStr
import scripts.mdb as mdb


def createCommands(**kargs):
    """
    """
    if kargs["analysisType"] == "FEM":
        femCrackMdb(kargs)
    elif kargs["analysisType"] == "XFEM":
        if kargs["xfemType"] == "simple":
            xfemSimpleCrackMdb(kargs)
        elif kargs["xfemType"] == "crackPartition":
            xfemCPcrackMdb(kargs)
        elif kargs["xfemType"] == "multiplePartitions":
            xfemMPcrackMdb(kargs)


def femCrackMdb(pars):
    """
    """
    dataStr = femDataStr.FEMdataStr()

    crackParameters = {
        "a": pars["a"],
        "b": pars["b"],
        "crackType": pars["crackType"]}
    analysisParameters = {
        "sigma": pars["sigma"],
        "gamma": pars["gamma"],
        "omega": pars["omega"]}
    meshParameters = {
        "elements": pars["femElements"].split(" ")[0],
        "transformationType": pars["meshTransform"]}
    seedParameters = {
        "crackZoneMainSeeds": pars["crackZoneSeeds"],
        "crackZoneRefinementSeeds": pars["crackZoneRefinementSeeds"],
        "arcSeeds": pars["arcSeeds"],
        "containerRefinementSeeds": pars["containerRefinementSeeds"]}
    geometricParameters = {
        "containerHeight": pars["containerH"],
        "containerRadius": pars["containerD"]/2.0}
    material = {
        "v": pars["vRatio"],
        "E": pars["eModulus"],
        "name": pars["materialName"]}

    crackTipSideScale = pars["crackTipScale"]
    crackZoneSideScale = pars["crackZoneScale"]
    midNodePosition = 0.27
    modelType = "crackNormal"
    modelName = pars["mdbName"]

    dataStr.setCreatePredefinedBCsFlag(pars["applyLoads"])

    dataStr.setMaterialProperties(material)
    dataStr.setCrackParameters(crackParameters)
    dataStr.setAnalysisParameters(analysisParameters)
    dataStr.setMeshParameters(meshParameters)

    dataStr.setSeedParameters(seedParameters)
    dataStr.setGeometricParameters(geometricParameters)
    dataStr.setMidNodePosition(midNodePosition)
    dataStr.setModelType(modelType)

    dataStr.setAnalysisCreationTimeStamp()
    dataStr.setModelName(modelName)

    dataStr.processTransformationInputData()
    dataStr.calculateCrackRadiusBeforeTransformation()
    dataStr.calculateCrackZoneSide(crackZoneSideScale)
    dataStr.calculateCrackTipSide(crackTipSideScale)

    createMdb(dataStr)


def xfemCPcrackMdb(pars):
    """
    """
    dataStr = xfemTETdataStr.XFEMtetDataStr()

    crackParameters = {
        "a": pars["a"],
        "b": pars["b"],
        "crackType": pars["crackType"]}
    analysisParameters = {
        "sigma": pars["sigma"],
        "gamma": pars["gamma"],
        "omega": pars["omega"]}
    meshParameters = {
        "elements": pars["xfemCPElements"].split(" ")[0]}
    seedParameters = {
        "crackEdges": pars["CPcrackSeeds"],
        "allEdges": pars["CPcontainerSeeds"]}
    geometricParameters = {
        "containerHeight": pars["containerH"],
        "containerRadius": pars["containerD"]/2.0}
    material = {
        "v": pars["vRatio"],
        "E": pars["eModulus"],
        "name": pars["materialName"]}
    singularityCalcRadius = pars["singularityRadius"]
    modelName = pars["mdbName"]

    dataStr.setCreatePredefinedBCsFlag(pars["applyLoads"])

    dataStr.setMaterialProperties(material)
    dataStr.setCrackParameters(crackParameters)
    dataStr.setAnalysisParameters(analysisParameters)
    dataStr.setMeshParameters(meshParameters)
    dataStr.setSeedParameters(seedParameters)
    dataStr.setGeometricParameters(geometricParameters)
    dataStr.setSingularityCalcRadius(singularityCalcRadius)

    dataStr.setAnalysisCreationTimeStamp()
    dataStr.setModelName(modelName)
    createMdb(dataStr)


def xfemMPcrackMdb(pars):
    """
    """
    dataStr = xfemDataStrMP.XFEMdataStrMP()

    crackParameters = {
        "a": pars["a"],
        "b": pars["b"],
        "crackType": pars["crackType"]}
    analysisParameters = {
        "sigma": pars["sigma"],
        "gamma": pars["gamma"],
        "omega": pars["omega"]}
    meshParameters = {
        "elements": pars["xfemMPElements"].split(" ")[0]}
    seedParameters = {
        "allEdges": pars["xfemMPcontainerSeeds"],
        "crackContEdges": pars["xfemMPsmallContainerSeeds"]}
    geometricParameters = {
        "containerHeight": pars["containerH"],
        "containerRadius": pars["containerD"]/2.0,
        "smallContainerHeight": pars["xfemMPheight"],
        "crackFrontOffset": pars["xfemMPoffset"]}
    material = {
        "v": pars["vRatio"],
        "E": pars["eModulus"],
        "name": pars["materialName"]}
    modelName = pars["mdbName"]
    singularityCalcRadius = pars["singularityRadius"]

    dataStr.setCreatePredefinedBCsFlag(pars["applyLoads"])

    dataStr.setMaterialProperties(material)
    dataStr.setCrackParameters(crackParameters)
    dataStr.setAnalysisParameters(analysisParameters)
    dataStr.setMeshParameters(meshParameters)
    dataStr.setSeedParameters(seedParameters)
    dataStr.setGeometricParameters(geometricParameters)
    dataStr.setSingularityCalcRadius(singularityCalcRadius)

    dataStr.setAnalysisCreationTimeStamp()
    dataStr.setModelName(modelName)

    createMdb(dataStr)


def xfemSimpleCrackMdb(pars):
    """
    """
    dataStr = xfemSimpleDataStr.XFEMsimpleDataStr()

    crackParameters = {
        "a": pars["a"],
        "b": pars["b"],
        "crackType": pars["crackType"]}
    analysisParameters = {
        "sigma": pars["sigma"],
        "gamma": pars["gamma"], "omega": pars["omega"]}
    meshParameters = {
        "elements": pars["xfemSimpleElements"].split(" ")[0]}
    seedParameters = {
        "allEdges": pars["simpleContainerSeeds"]}
    geometricParameters = {
        "containerHeight": pars["containerH"],
        "containerRadius": pars["containerD"]/2.0}
    material = {
        "v": pars["vRatio"],
        "E": pars["eModulus"],
        "name": pars["materialName"]}
    singularityCalcRadius = pars["singularityRadius"]
    modelName = pars["mdbName"]

    dataStr.setCreatePredefinedBCsFlag(pars["applyLoads"])

    dataStr.setMaterialProperties(material)
    dataStr.setCrackParameters(crackParameters)
    dataStr.setAnalysisParameters(analysisParameters)
    dataStr.setMeshParameters(meshParameters)
    dataStr.setSeedParameters(seedParameters)
    dataStr.setGeometricParameters(geometricParameters)
    dataStr.setSingularityCalcRadius(singularityCalcRadius)

    dataStr.setAnalysisCreationTimeStamp()
    dataStr.setModelName(modelName)

    createMdb(dataStr)


def createMdb(dataStr):
    """
    """
    parameters = {"saveMdb": ["yes", ]}
    crack = mdb.MdbCommands(dataStr, parameters)
    crack.createSingleMdb()

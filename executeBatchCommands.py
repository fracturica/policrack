

import sharedFunctions
import scripts.dataStr.femDataStr as femDataStr
import scripts.dataStr.xfemTETdataStr as xfemTETdataStr
import scripts.dataStr.xfemDataStrMP as xfemDataStrMP
import scripts.dataStr.xfemSimpleDataStr as xfemSimpleDataStr
import scripts.mdb as mdb


def batchCreateCrackDb(**kargs):
    """
    """
    batchConf = kargs["batchConf"]
    pars = sharedFunctions.parseInput(batchConf)

    analysisParameters = []
    if pars["loads"][0] == "infiniteBody":
        if pars["crackType"][0] == "embedded":
            for sigma in pars["sigma"]:
                for omega in pars["omega"]:
                    for gamma in pars["gamma"]:
                        analysisParameters += {
                            "sigma": sigma,
                            "omega": omega,
                            "gamma": gamma},
        elif pars["crackType"][0] == "surface":
            for sigma in pars["sigma"]:
                for gamma in pars["gamma"]:
                    analysisParameters += {
                        "sigma": sigma,
                        "gamma": gamma},
        elif pars["crackType"][0] == "edge":
            for sigma in pars["sigma"]:
                analysisParameters += {"sigma": sigma},
    else:
        analysisParameters += {"type": "custom"},

    material = {
        "name": pars["materialName"][0],
        "E": pars["E"][0],
        "v": pars["v"][0]}

    if pars["analysisType"][0] == "FEM":
        femLoop(pars, analysisParameters, material)
    elif pars["analysisType"][0] == "XFEM_cp":
        xfemCPloop(pars, analysisParameters, material)
    elif pars["analysisType"][0] == "XFEM_mp":
        xfemMPloop(pars, analysisParameters, material)
    elif pars["analysisType"][0] == "XFEM_simple":
        xfemSimpleLoop(pars, analysisParameters, material)


def femLoop(parameters, analysisParameters, material):
    """
    """
    counter = 0

    for a in parameters["a"]:
        for b in parameters["b"]:
            for loads in analysisParameters:
                for czms in parameters["czms"]:
                    for czrs in parameters["czrs"]:
                        for arcSeeds in parameters["arcs"]:
                            for crs in parameters["crs"]:
                                for elementType in parameters["elementType"]:
                                    for transformation in parameters["transformation"]:
                                        for containerH in parameters["containerH"]:
                                            for containerD in parameters["containerD"]:
                                                for crackTipSideScale in parameters["crackTipSideScaleFactor"]:

                                                    dataStr = femDataStr.FEMdataStr()

                                                    crackType = parameters["crackType"][0]
                                                    crackParameters = {
                                                        "a": a,
                                                        "b": b,
                                                        "crackType": crackType}

                                                    meshParameters = {
                                                            "elements": elementType,
                                                            "transformationType": transformation}

                                                    seedParameters = {
                                                            "crackZoneMainSeeds": int(czms),
                                                            "crackZoneRefinementSeeds": int(czrs),
                                                            "arcSeeds": int(arcSeeds),
                                                            "containerRefinementSeeds": int(crs)}

                                                    geometricParameters = {
                                                            "containerHeight": containerH,
                                                            "containerRadius": containerD/2.0}

                                                    dataStr.setMaterialProperties(material)
                                                    dataStr.setCrackParameters(crackParameters)
                                                    dataStr.setAnalysisParameters(loads)
                                                    dataStr.setMeshParameters(meshParameters)
                                                    dataStr.setSeedParameters(seedParameters)
                                                    dataStr.setGeometricParameters(geometricParameters)
                                                    dataStr.setMidNodePosition(parameters["midNodePosition"][0])
                                                    dataStr.setModelType(parameters["modelType"][0])

                                                    dataStr.setAnalysisCreationTimeStamp()
                                                    dataStr.createModelName()

                                                    dataStr.processTransformationInputData()
                                                    dataStr.calculateCrackRadiusBeforeTransformation()

                                                    dataStr.calculateCrackZoneSide()
                                                    dataStr.calculateCrackTipSide(crackTipSideScale)

                                                    createMdb(dataStr, parameters)
                                                    dataStr = None

                                                    counter += 1
                                                    print "simulation number {0}".format(counter)
    print "Total number of simulations = {0}".format(counter)


def xfemCPloop(parameters, analysisParameters, material):
    """
    """
    counter = 0

    for a in parameters["a"]:
        for b in parameters["b"]:
            for loads in analysisParameters:
                for crackEdges in parameters["crackSeeds"]:
                    for allEdges in parameters["containerSeeds"]:
                        for elementType in parameters["elementType"]:
                            for containerH in parameters["containerH"]:
                                for singularityCalcRadius in parameters["singularityRadius"]:
                                    for containerD in parameters["containerD"]:

                                        dataStr = xfemTETdataStr.XFEMtetDataStr()

                                        crackType = parameters["crackType"][0]
                                        crackParameters = {
                                            "a": a,
                                            "b": b,
                                            "crackType": crackType}
                                        meshParameters = {
                                            "elements": elementType}
                                        seedParameters = {
                                            "crackEdges": crackEdges,
                                            "allEdges": allEdges}
                                        geometricParameters = {
                                            "containerHeight": containerH,
                                            "containerRadius": containerD/2.0}

                                        dataStr.setMaterialProperties(material)
                                        dataStr.setCrackParameters(crackParameters)
                                        dataStr.setAnalysisParameters(loads)
                                        dataStr.setMeshParameters(meshParameters)
                                        dataStr.setSeedParameters(seedParameters)
                                        dataStr.setGeometricParameters(geometricParameters)
                                        dataStr.setSingularityCalcRadius(singularityCalcRadius)

                                        dataStr.setAnalysisCreationTimeStamp()
                                        dataStr.createModelName()

                                        createMdb(dataStr, parameters)
                                        dataStr = None

                                        counter += 1
                                        print "simulation number {0}".format(counter)
    print "Total number of simulations = {0}".format(counter)


def xfemMPloop(parameters, analysisParameters, material):
    """
    """
    counter = 0

    for a in parameters["a"]:
        for b in parameters["b"]:
            for loads in analysisParameters:
                for allEdges in parameters["containerSeeds"]:
                    for crackContEdges in parameters["partitionContainerSeeds"]:
                        for elementType in parameters["elementType"]:
                            for smallContainerHeight in parameters["meshPartitionHeight"]:
                                for crackFrontOffset in parameters["meshPartitionOffset"]:
                                    for containerH in parameters["containerH"]:
                                        for singularityCalcRadius in parameters["singularityRadius"]:
                                            for containerD in parameters["containerD"]:

                                                dataStr = xfemDataStrMP.XFEMdataStrMP()

                                                crackType = parameters["crackType"][0]
                                                crackParameters = {
                                                    "a": a,
                                                    "b": b,
                                                    "crackType": crackType}
                                                meshParameters = {
                                                    "elements": elementType}
                                                seedParameters = {
                                                    "allEdges": allEdges,
                                                    "crackContEdges": crackContEdges}
                                                geometricParameters = {
                                                    "containerHeight": containerH,
                                                    "containerRadius": containerD/2.0,
                                                    "smallContainerHeight": smallContainerHeight,
                                                    "crackFrontOffset": crackFrontOffset}

                                                dataStr.setMaterialProperties(material)
                                                dataStr.setCrackParameters(crackParameters)
                                                dataStr.setAnalysisParameters(loads)
                                                dataStr.setMeshParameters(meshParameters)
                                                dataStr.setSeedParameters(seedParameters)
                                                dataStr.setGeometricParameters(geometricParameters)
                                                dataStr.setSingularityCalcRadius(singularityCalcRadius)

                                                dataStr.setAnalysisCreationTimeStamp()
                                                dataStr.createModelName()

                                                createMdb(dataStr, parameters)
                                                dataStr = None
                                                counter += 1
                                                print counter
    print "Total number of simulations = {0}".format(counter)


def xfemSimpleLoop(parameters, analysisParameters, material):
    """
    """
    counter = 0

    for a in parameters["a"]:
        for b in parameters["b"]:
            for loads in analysisParameters:
                for allEdges in parameters["containerSeeds"]:
                    for elementType in parameters["elementType"]:
                        for containerHeight in parameters["containerH"]:
                            for singularityCalcRadius in parameters["singularityRadius"]:
                                for containerD in parameters["containerD"]:

                                    dataStr = xfemSimpleDataStr.XFEMsimpleDataStr()

                                    crackType = parameters["crackType"][0]
                                    crackParameters = {
                                        "a": a,
                                        "b": b,
                                        "crackType": crackType}
                                    meshParameters = {
                                        "elements": elementType}
                                    seedParameters = {
                                        "allEdges": allEdges}
                                    geometricParameters = {
                                        "containerHeight": containerHeight,
                                        "containerRadius": containerD/2.0}

                                    dataStr.setMaterialProperties(material)
                                    dataStr.setCrackParameters(crackParameters)
                                    dataStr.setAnalysisParameters(loads)
                                    dataStr.setMeshParameters(meshParameters)
                                    dataStr.setSeedParameters(seedParameters)
                                    dataStr.setGeometricParameters(geometricParameters)
                                    dataStr.setSingularityCalcRadius(singularityCalcRadius)

                                    dataStr.setAnalysisCreationTimeStamp()
                                    dataStr.createModelName()

                                    createMdb(dataStr, parameters)
                                    dataStr = None

                                    counter += 1
                                    print counter
    print "Total number of simulations = {0}".format(counter)


def createMdb(dataStr, parameters):
    """
    """
    crack = mdb.MdbCommands(dataStr, parameters)
    crack.setBatchMode()

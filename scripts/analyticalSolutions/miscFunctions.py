

import math
import shelve
import os

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


def Rfun(parameters):
    """
    A function required for
    SIF calculations
    """
    a = parameters["a"]
    b = parameters["b"]
    k = parameters["k"]
    v = parameters["v"]

    term1 = (k**2)
    term2a = (k**2 - v) * compEllipIntE(k)
    term2b = v * ((1-k**2)**2) * compEllipIntK(k)
    R = term1 / (term2a + term2b)
    return R


def Qfun(parameters):
    """
    A function required for
    SIF calculations
    """
    a = parameters["a"]
    b = parameters["b"]
    k = parameters["k"]
    v = parameters["v"]

    term1 = k**2
    term2a = (k**2 + v * (1-k**2)**2) * compEllipIntE(k)
    term2b = v * ((1-k**2)**2) * compEllipIntK(k)
    Q = term1 / (term2a - term2b)
    return Q


def compEllipIntK(k):
    """
    """
    K = readDbValues(k, "compEllipIntK")
    return K


def compEllipIntE(k):
    """
    """
    E = readDbValues(k, "compEllipIntE")
    return E


def readDbValues(k, integral):
    """
    """
    shelvePath = thisDir + "\\analyticValuesDb\\compIntValues"
    db = shelve.open(shelvePath)
    values = db[integral]
    db.close()
    if str(k) in values.keys():
        return float(values[str(k)])
    else:
        xVals = convertStrKeysToFloats(values.keys())
        xVals.append(k)
        xVals.sort()
        kIndex = xVals.index(k)
        xVal1 = xVals[kIndex-1]
        xVal2 = xVals[kIndex+1]
        intVal1 = float(values[str(xVal1)])
        intVal2 = float(values[str(xVal2)])
        intVal = 0.5*(intVal1 + intVal2)
        return intVal


def convertStrKeysToFloats(keys):
    """
    """
    values = []
    for key in keys:
        values += float(key),
    return values

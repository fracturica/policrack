

import shelve
import scipy
import scipy.special
import pylab
from numpy import *
import matplotlib.pyplot as plt

compIntValuesDb = "compIntValuesHash"


class EllipticIntegrals:
    """
    """
    def __init__(self):
        """
        """
        self.intVals = {
            "compEllipIntK": {},
            "compEllipIntE": {}}
        self.valueRange = ()
        self.activeShelve = compIntValuesDb

    def initializeValueRange(self, step):
        """
        """
        finalValue = int(1/step)
        values = range(0, finalValue, 1)
        for val in values:
            self.valueRange += val*step,

    def calcEllipIntK(self):
        """
        """
        for value in self.valueRange:
            self.intVals["compEllipIntK"][str(value)] = str(scipy.special.ellipkm1(1-value))

    def calcEllipIntE(self):
        """
        """
        for value in self.valueRange:
            self.intVals["compEllipIntE"][str(value)] = (scipy.special.ellipe(value))

    def writeToDb(self):
        """
        """
        db = shelve.open(self.activeShelve)
        for intType in self.intVals.keys():
            db[intType] = self.intVals[intType]
        db.close()


def calcIntValues(step):
    """
    """
    intVals = EllipticIntegrals()
    intVals.initializeValueRange(step)
    intVals.calcEllipIntE()
    intVals.calcEllipIntK()
    intVals.writeToDb()


def getDbValues():
    """
    """
    db = shelve.open(compIntValuesDb)
    intVals = {}
    for key in db.keys():
        intVals[key] = db[key]
    db.close()
    return intVals


def plotValues(intVals):
    """
    """
    for integral in intVals.keys():
        x = []
        y = []
        for xVal in intVals[integral].keys():
            x += float(xVal),
        x.sort()
        for xVal in x:
            y += float(intVals[integral][str(xVal)]),
        x = pylab.array(x)
        y = pylab.array(y)
        plt.plot(x, y, label=integral)
        plt.axis()
        plt.legend()
    plt.grid()
    plt.show()


def writeValuesToFile(intVals):
    """
    """
    for integral in intVals.keys():
        fileName = integral + ".txt"
        intFile = open(fileName, 'w')
        for xVal in intVals[integral].keys():
            yVal = intVals[integral][xVal]
            intFile.write("{0} {1}".format(xVal, yVal)+"\n")
        intFile.close()


def calcCompIntArgumentIncrement(minCrackRatio):
    """
    """
    kMax = sqrt(1.0 - minCrackRatio**2)
    increment = 1.0 - kMax
    argStep = 1.0
    while increment < argStep:
        argStep = argStep/10.0
    return argStep


if __name__ == "__main__":
    minCrackRatio = 0.01
    argStep = calcCompIntArgumentIncrement(minCrackRatio)
    print "minCrackRatio = ", minCrackRatio
    print "increment =", argStep
    calcIntValues(argStep)
    integral = getDbValues()
    writeValuesToFile(integral)
    plotValues(integral)

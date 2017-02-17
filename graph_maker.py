#!/usr/bin/env python
# -*- coding: utf-8 -*-

#This program creates a .png graph by using the csv file that was created while doing the experiments. It uses the same min and max settings for all the graphs in order to allow a direct comparison. It can also make a graph comparing the power directly out of all the graphs.

import matplotlib.pyplot as pyplot
import csv
import os

#The file dimensions (serves more as a proportion)
fileDimensions = [16, 9]
#Sets the DPI for the document (DPI*dimensions is the actual size in pixels)
fileDPI = 300
#If set to true,   
comparePower = False

#Add the files that are going to be made into graphs.
#files = ["graph_0", "graph_1 (wood floor)", "graph_2 (tapete)"]
#names = {"graph_0":"Aislado", "graph_1 (wood floor)":"Madera", "graph_2 (tapete)":"Tapete"}

if comparePower:
    files = ["graph_isolated", "graph_1 (wood)", "graph_2 (ceramic)", "graph_3 (carpet)"]
else:
    files = ["graph_isolated", "graph_1 (wood)", "graph_2 (ceramic)", "graph_3 (carpet)", "graph_5 (pressure)"]

#These are human friendly names for legends.
names = {"graph_isolated":"Isolated", "graph_1 (wood)":"Wood", "graph_2 (ceramic)":"Ceramic", "graph_3 (carpet)":"Rug"}

directory = os.path.expanduser("~/Documents/Colegio/Undécimo/Monografía/Datos/")

data = {}
dataMax = -1
dataMin = 0

for fileName in files:
    data[fileName] = {"name": fileName, "voltage":[], "average":[], "max":[], "power":[]}
    try: 
        data[fileName]["nice_name"] = names[fileName]
    except KeyError:
        data[fileName]["nice_name"] = fileName

    with open(directory + fileName + ".csv", "rb") as csvFile:
        csvReader = csv.reader(csvFile)
        for row in csvReader:
            if (row[0] != "Voltage (V)"):
                data[fileName]["voltage"].append(float(row[0]))
                data[fileName]["average"].append(float(row[1]))
                data[fileName]["max"].append(float(row[2]))
                data[fileName]["power"].append(float(row[3]))

    if not comparePower:
        if (min(data[fileName]["average"]) <= dataMin):
            dataMin = min(data[fileName]["average"])
        if (max(data[fileName]["average"]) >= dataMax):
            dataMax = max(data[fileName]["average"])

        if (min(data[fileName]["max"]) <= dataMin):
            dataMin = min(data[fileName]["max"])
        if (max(data[fileName]["max"]) >= dataMax):
            dataMax = max(data[fileName]["max"])

    if (min(data[fileName]["power"]) <= dataMin):
        dataMin = min(data[fileName]["power"])
    if (max(data[fileName]["power"]) >= dataMax):
        dataMax = max(data[fileName]["power"])

dataMin *= 1.1
dataMax *= 1.1

if not os.path.exists(directory + "graphs"):
    os.makedirs(directory + "graphs")

fig, ax = pyplot.subplots(figsize=(fileDimensions[0], fileDimensions[1]))

if comparePower:
    for individualData in data:
        ax.plot(data[individualData]["voltage"], data[individualData]["power"], marker='o', label=data[individualData]["nice_name"])
        ax.title.set_text("I-V Curve")
        ax.set_xlabel(r"Voltage (V) (Error: $\pm$9.14$\cdot$10$^{-3}$V)")
        ax.set_ylabel(r"Power (mW) (Error: $\pm$1.02$\cdot$10$^{-7}$mW)")
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.grid(which='both', alpha=0.3)
        #ax.set_ylim([dataMin, dataMax + 0.0005])
        ax.legend(loc='lower right', frameon=True)

    pyplot.savefig(directory + "graphs/power.png", bbox_inches='tight', dpi=fileDPI)

else:
    for individualData in data:
        ax.clear()
        ax.title.set_text("I-V Curve")
        ax.set_xlabel(r"Voltage (V) (Error: $\pm$9.14$\cdot$10$^{-3}$)")
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.plot(data[individualData]["voltage"], data[individualData]["average"], color='b', marker='o', label="Average Current (mA)\n" + r'(Error: $\pm$1.94$\cdot$10$^{-5}$mA)')
        ax.plot(data[individualData]["voltage"], data[individualData]["max"], color='r', marker='o', label="Maximum Current (mA)\n" + r'(Error: $\pm$1.94$\cdot$10$^{-5}$mA)')
        ax.plot(data[individualData]["voltage"], data[individualData]["power"], color='g', marker='o', label="Power (mW)\n" + r'(Error: $\pm$1.02$\cdot$10$^{-7}$mA)')
        ax.legend(loc='upper right', frameon=True)
        ax.grid(which='both', alpha=0.3)
        ax.set_ylim([dataMin, dataMax])

        pyplot.savefig(directory + "graphs/" + individualData + '.png', bbox_inches='tight', dpi=fileDPI)

        print("Saved: " + individualData)
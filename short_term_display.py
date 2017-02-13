#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This code sends a serial signal to a µC programmed with the ARDUINO program, receiving all the data continuosly, and plotting it accordingly. It also exports all the data to .csv for further analysis.

import serial
import os
import math
import matplotlib.pyplot as pyplot
import time
import csv

voltage = 4.68
resistorVoltage = voltage * (1005.0/(1005.0+273.0))
resistance = 470000
#For full resolution, it is better to use a combination of 4000ms and 20 steps per sample. More than that is overkill. For any tests, any above above and
#below, respectively, are appropiate.
#Time in ms
timePerSample = 4000
#How many steps to add for each sample
sampleStep = 20
initialStep = sampleStep
endStep = 4095
#The file dimensions (serves more as a proportion)
fileDimensions = [16, 9]
#Sets the window DPI
windowDPI = 80
#Sets the DPI for the document (DPI*dimensions is the actual size in pixels)
fileDPI = 300
#This is the directory where the image is saved
directory = os.path.expanduser("~/Documents/Colegio/Undécimo/Monografía/Datos/")

try:
    #Put the correct serial port in here
    ser = serial.Serial("/dev/tty.usbserial-A9CVNLL9", 115200, timeout=1)
    print("Serial port opened!")
except serial.serialutil.SerialException:
    print("Port is closed. Maybe it isn't connected?")
    quit()

print("Using the following settings:\nVoltage: " + str(voltage) + "V\nDivider Voltage: " + str(resistorVoltage) + "V\nCurrent Resistance: " + str(resistance) + " Ohms\nTime per sample: " + str(timePerSample) + "ms\nNumber of samples: " + str(4096/sampleStep) + "\nApproximate time of experiment: " + str(4096/sampleStep*(timePerSample+500)/1000) + "s\nInitial Voltage: " + str(resistorVoltage-(initialStep/4095.0*voltage)) + "V\nEnd Voltage: " + str(resistorVoltage-(endStep/4095.0*voltage)) + "V")

pyplot.ion()
fig, ax = pyplot.subplots(figsize=(fileDimensions[0], fileDimensions[1]), dpi=windowDPI)
fig.canvas.set_window_title('I-V Curve')

time.sleep(2)

#[0] = Voltage [1] = Average [2] = Max [3] = Average Power
plotList = [[], [], [], []]

for i in xrange(initialStep, endStep, sampleStep):
    ser.write(str(i)+"\n")
    ser.write(str(timePerSample))

    while(True):
        if(ser.inWaiting() != 0):
            serLine = ser.readline().rstrip()
            if(serLine == "START"):
                print "VOLTAGE: " + str(resistorVoltage-(i/4095.0*voltage)) + "V TIME: " + str(timePerSample) + "ms"
                break
            print serLine

    sampleList = []

    while(True):
        if(ser.inWaiting() != 0):
            serialNumber = ser.readline().rstrip()
            if(serialNumber == "END"):
                break
            elif(serialNumber != "START"):
                sampleList.append(float(serialNumber)/1023*voltage/resistance*1000)

    calculatedVoltage = resistorVoltage-(i/4095.0*voltage)
    averageCurrent = sum(sampleList)/float(len(sampleList))
    maxCurrent = max(sampleList)

    plotList[0].append(calculatedVoltage)
    plotList[1].append(averageCurrent)
    plotList[2].append(maxCurrent)
    plotList[3].append(calculatedVoltage*averageCurrent)
    ax.clear()
    ax.title.set_text("I-V Curve (Time per Sample: " + str(timePerSample) + "ms)")
    ax.set_xlabel("Voltage (V)")
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.plot(plotList[0], plotList[1], color='b', marker='o', label="Average Current (mA)")
    ax.plot(plotList[0], plotList[2], color='r', marker='o', label="Maximum Current (mA)")
    ax.plot(plotList[0], plotList[3], color='g', marker='o', label="Power (mW)")
    ax.legend(loc='upper right', frameon=True)
    ax.grid(which='both', alpha=0.3)
    pyplot.draw()
    pyplot.pause(0.00001)

ser.close()
print("Program ended")

with open(directory + "graph.csv", "wb") as csvFile:
    csvWriter = csv.writer(csvFile)
    csvWriter.writerow(["Voltage (V)", "Average Current (mA)", "Maximum Current (mA)", "Power (mW)"])
    for row in zip(plotList[0], plotList[1], plotList[2], plotList[3]):
        csvWriter.writerow(row)

pyplot.ioff()
pyplot.savefig(directory + "graph" + '.png', bbox_inches='tight', dpi=fileDPI)
pyplot.show()
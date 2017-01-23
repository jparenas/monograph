import matplotlib.pyplot as pyplot
from matplotlib.dates import date2num, DayLocator, HourLocator, DateFormatter
import datetime
import csv
import math
import os

#The file dimensions (serves more as a proportion)
fileDimensions = [16, 9]
#Sets the DPI for the document (DPI*dimensions is the actual size in pixels)
fileDPI = 300
#Sets the number of annotations on the graph. Default = 10
numberOfAnnotations = 10
#This enables the annotations on the graph
enableAnnotations = False
#Enables the annotation of the legend
annotateLegend = False
#Sets the maximum ammount of ticks in the "x" axis
maxTicks = 25.0
#Sets both the minimum and the maximum voltage to display on the graph
minVoltage = 0.0
maxVoltage = 2.72

#This sets the plots to plot. It takes the dictionry inputs "name" and "arguments", which are used for the file name and the arguments for the pyplot construct, respectively
plots = [
    {"name":"dots", "arguments":[[], {"ms":1}]}, 
    {"name":"lines", "arguments":[["b-"], {}]}
    ]

#These are the two directories for the files, it defaults to the ARDUINO directory and fallbacks to the Downloads directory (this was directory was arbitrary)
directory = "/Volumes/ARDUINO/"
secondaryDirectory = os.path.expanduser("~/Downloads/")

try:
    fSample = open(directory + "samples.txt", "r")
except IOError: 
    try:
        fSample = open(secondaryDirectory + "samples.txt", "r")
        directory = secondaryDirectory
    except IOError: 
        print "No file found. Aborting"
        quit()

print "Using the following directory:", directory

#Reads the file, it should return only one line
sample = fSample.read()

fSample.close()

#Declares the initial index for the string search
index = 0
lastIndex = -1
sampleList = [[], [], [], []]
averageVoltage = 0;

while (index != -1):
    index = sample.find(";", lastIndex+1)
    if (index != -1):
        #Retrieves the string that is going to be analyzed (using the index as the initial bound and the delimitator "&" as the final bound)
        sampleStr = sample[lastIndex+1:index]
        #Retrieves the sample from the string
        sampleNumber = int(sampleStr[sampleStr.find("&")+1:])
        #Calculates the voltage according to the voltage divider, voltage reference and range (formula has been simplified)
        #The error for this formula (accounting for the ADC resolution) is of +- 3.28*10^-3 V (0.00328V)
        sampleNumber = (419*float(sampleNumber))/157635
        #Appends the calculated sample to the sample list
        sampleList[0].append(sampleNumber)
        #Adds the voltage to the total voltage, which will be computed after finishing up this loop
        averageVoltage += sampleNumber
        #Extracts the date from the string and makes a datetime object using the data that is decoded from the file
        date = datetime.datetime(2016, int(sampleStr[:sampleStr.find("/")]), int(sampleStr[sampleStr.find("/")+1:sampleStr.find("-")]), int(sampleStr[sampleStr.find("-")+1:sampleStr.find(":")]), int(sampleStr[sampleStr.find(":")+1:sampleStr.find("#")]), int(sampleStr[sampleStr.find("#")+1:sampleStr.find("&")]))
        #Add the numerical representation of the datetime object
        sampleList[1].append(date2num(date))
        #Adds the datetime representation of the time to the list, which is used to construct the CSV
        sampleList[2].append(date)
        #Concatenates a string using the datetime object and adds it to the list
        minute = str(date.minute)
        if date.minute < 10: 
            minute = "0" + str(date.minute) 
        else: 
            minute = str(date.minute)
        second = str(date.second)
        if date.second < 10: 
            second = "0" + str(date.second) 
        else: 
            second = str(date.second)
        sampleList[3].append(str(date.day) + "/" + str(date.month) + " " + str(date.hour) + ":" + minute + ":" + second)
        lastIndex = index

averageVoltage /= len(sampleList[0])

timeDelta = max(sampleList[2]) - min(sampleList[2])

print "Number of Samples:", len(sampleList[0])
print "Run time:", max(sampleList[2]) - min(sampleList[2])
print "Initial Voltage: " + str(sampleList[0][0]) + "V"
print "Average Voltage: " + str(averageVoltage) + "V"
print "Total hours:", (timeDelta.days*24)+(timeDelta.seconds/3600)

#This simple algorithm calculates the interval that is going to be used in the graph for the "x" axis
graphInterval = int(math.ceil(((timeDelta.days*24.0)+(timeDelta.seconds/3600.0))/maxTicks))

print "Total interval:", graphInterval    

#Creates a CSV file, dropping the data gathered so far in case that Excel processing is needed
with open(directory + "data.csv", "wb") as csvFile:
    csvWriter = csv.writer(csvFile)
    for row in zip(sampleList[3], sampleList[0]):
        csvWriter.writerow(row)

for plot in plots:
    #Creates a subplot object, in which a figure and a plot object
    fig, ax = pyplot.subplots()
    #Sets the size of the image. This serves more as a proportion than as an actual size.
    fig.set_size_inches(*fileDimensions)
    #Sets labels for both the "x" and the "y"axis
    ax.set_xlabel("Time")
    ax.set_ylabel("Voltage (V)")
    ax.plot_date(sampleList[1], sampleList[0], *plot["arguments"][0], **plot["arguments"][1])
    #Sets the limits for both the "x" and the "y" axis.
    ax.axis([min(sampleList[1]), max(sampleList[1]), minVoltage, maxVoltage])
    #Sets the major and minor locator for the "x" axis
    ax.xaxis.set_major_locator(DayLocator())
    ax.xaxis.set_minor_locator(HourLocator(interval=graphInterval))
    #Set the formatter that sets the text in the "x" axis
    ax.xaxis.set_major_formatter(DateFormatter('%d/%m'))
    ax.xaxis.set_minor_formatter(DateFormatter('%H:00'))
    #Increases the pad in the major formatter in the "x" axis
    ax.xaxis.set_tick_params(which='major', pad=20)
    #Sets the number of ticks in the "y" axis
    ax.locator_params(axis='y',nbins=20)
    #Adds a grid using the ticks
    ax.grid(which='both', alpha=0.3)
    #Annotates the initial voltage, and the average voltage
    if annotateLegend:
        ax.annotate("Initial Voltage: " + "{0:.3f}".format(sampleList[0][0]) + "V\nAverage Voltage: " + "{0:.4f}".format(averageVoltage) + "V\nRun time: " + str(max(sampleList[2]) - min(sampleList[2])), 
            xy= (0.017, 0.97), ha="left", va="top",
            xycoords='axes fraction',
            bbox=dict(boxstyle="square, pad=0.5", fc="w")
            )
    #This creates the annotations in the graph, set using the variable enableAnnotations
    if enableAnnotations:
        zipList = zip(sampleList[3], sampleList[0], sampleList[1])
        annotateNumber = len(zipList)/(numberOfAnnotations+1)
        for currentIndex in xrange(1, numberOfAnnotations+1):
            #[0] = Date [1] = Voltage [2] = Numerical Date
            index = annotateNumber*currentIndex
            ax.annotate(zipList[index][0] + "\n" + "{0:.3f}".format(zipList[index][1]) + "V", 
                xy = (zipList[index][2], zipList[index][1]),
                xytext = (0, 20),
                textcoords = 'offset points', ha="center",
                arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0')
                )
    #Saves the plot as a PNG file in the specified directory with the specified name.
    pyplot.savefig(directory + plot["name"] + '.png', bbox_inches='tight', dpi=fileDPI)
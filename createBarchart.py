#Import Libraries

import numpy as np
import matplotlib.pyplot as plt
import pylab as pl

# Open file named Figure2.1.csv located in Working directory and read it's 
#contents into a list named 'content'. 

with open("Figure2.1.csv") as f:
  content = f.read()
  print content
#remove return and new line characters from the content
content = content.split('\r\n')

#remove empty value indicating eof file from the list
if content[-1]=='':
  content.pop()

#Split data divided by ',' into x and y lists (indicating the X axis values)
x = [row.split(',')[0] for row in content]
y = [row.split(',')[1] for row in content]

#Separate the first Item in each list as it is the title of the axis
xTitle = x[0]
yTitle = y[0]
x=x[1:]
y=y[1:]

#convert values in Y to Integers
y = [int(i) for i in y]

#Begin plotting the graph

#Define the plot areas
fig = pl.figure()
ax = pl.subplot()

#Set the bar graph data as the content from Y
ax.bar(range(len(y)), y)

#Set the labels for each axis
width = 1.0
ax.set_xlabel(xTitle)
ax.set_ylabel(yTitle)

ind = np.arange(len(y))

#Plotting the graph
plt.bar(ind, y)
plt.xticks(ind + width / 2, x)

#formatting the labels for x axis
ax.set_xticklabels(x, rotation=90)
fig.autofmt_xdate()

#Show the final image
pl.show(fig)


import matplotlib.pyplot as plt

# The Graph for the Time packet loss scenerio
x = [0, 1, 2, 3, 4, 5,6,7,8,9,10] #packey loss percentage in %
# y = [108044,107919,109085,107416,105896,109106,110829,105578,109945,111132,111933]#time
# z=[93314,93423,92424,93860,95207,92406,90969,95494,91701,90722,90072]#speed
a=[37652,39059,40594,41977,43506,45098,46582,48109,49651,50887,52386]
# Create a plot
plt.plot(x, a, marker='o')

# Add titles and labels
plt.title('time loss scenario- number of sent packets vs % packet loss')
plt.xlabel('% packet loss')
plt.ylabel('number of sent packets')

# Show the plot
plt.show()


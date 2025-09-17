import math

#a = (x, y)

# a[0]
a = (1, 2)
b = (3, 1)
def add(a, b):
    return math.sqrt(((a[0]-b[0])**2) + ((a[1]-b[1])**2))


print(round(add(a, b)))
cities = ['New Delhi', 'Paris', 'Rome', 'Brisbane', 'Berlin', 'Buenos Aires', 'London', 'New York']
citieslat = [28, 48, 41, 27, 52, -34, 51, 40]
distanceinfo = []
distfromeq = 0
print('*****        Welcome to the Latitude to distance from equator converter!********    ')

i=input("Enter the cities: ")
if i in list(cities):
    j=cities.index(i)
    k=citieslat[j]
    print(i,":",abs(k)*69,"miles from equator")
else:
    print("It is case sensitive or may not be in our list")
    exit()





    
  

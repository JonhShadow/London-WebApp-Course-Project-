from geopy import distance
import pandas as pd

def distanceToLondon(lat, long):
    london = (51.5085300, -0.1257400)
    house = (lat, long)
    dist = distance.distance(london, house).km
    return dist

def getCrime(code):
    c=code.split(' ')
    code = c[0]
    print(code)
    london = pd.read_csv('LondonFinalLable.csv')
      
    crime = london[london['PostalCode'].astype(str).str.contains(code)]
    return crime['NCrime'].iloc[0]

def distanceToHospital(lat,long):
    poi_hospital = pd.read_csv("POI_Hospital.csv")
    house = (lat, long)
    disToHosp = []
    for index, row in poi_hospital.iterrows():
        dis = distance.distance((row.lat, row.long), house).km
        disToHosp.append(dis)
    
    return min(disToHosp)

def distanceToSubway(lat,long):
    poi_subway = pd.read_csv("POI_Subway.csv")
    house = (lat, long)
    disToSub = []
    for index, row in poi_subway.iterrows():
        dis = distance.distance((row.lat, row.long), house).km
        disToSub.append(dis)
    
    return min(disToSub)

def distanceToSchool(lat,long):
    poi_school = pd.read_csv("POI_School.csv")
    house = (lat, long)
    disToSchool = []
    for index, row in poi_school.iterrows():
        dis = distance.distance((row.lat, row.long), house).km
        disToSchool.append(dis)
    
    return min(disToSchool)

def HouseTypeToLable(house):
    london = pd.read_csv('LondonFinalLable.csv')
    london = london[['HouseType', 'HouseTypeLabel']]
    london = london.dropna()
    london = london.drop_duplicates()
    label = london[london['HouseType'] == house]
    
    return label['HouseTypeLabel'].iloc[0]

def PostalCodeToLable(code):
    london = pd.read_csv('LondonFinalLable.csv')
    london = london[['PostalCodeLabel']]
    
    return max(london['PostalCodeLabel']+1)


#print(HouseTypeToLable('House'))
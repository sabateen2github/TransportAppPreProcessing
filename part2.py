import pandas as pd
import requests as req
import json
import os
import polyline as pl


# api_key = AIzaSyDjkfubHruUsci6lo410IOWSpT0KG1YCHQ


def send(origin, destination):
    r = req.get(
        'https://maps.googleapis.com/maps/api/directions/json?' + 'origin=' + origin + '&destination=' + destination + '&key=AIzaSyDjkfubHruUsci6lo410IOWSpT0KG1YCHQ')
    return r.json()


def read():
    return pd.read_excel("C:/Users/alaa2/OneDrive/Desktop/خطوط النقل.xlsx", sheet_name='Sheet1',
                         engine='openpyxl').to_dict(orient='records')

def decodePolylineofRoute(steps):
    array = ["sda"]
    for step in steps:
        polyline = pl.decode(step['polyline']['points'])
        if array[len(array) - 1] == polyline[0]:
            polyline.pop(0)
        for point in polyline:
            array.append(point)
    array.pop(0)
    return array


def saveResponses():
    entries = read()
    for row in entries:
        print(row['first'] + "    " + row['second'])
        response = send(row['firstloc'], row['secondloc'])
        file = open("C:/Users/alaa2/OneDrive/Desktop/routes/" + row['first'] + '-' + row['second'] + ".response",
                    mode='w')
        json.dump(response, file)
        file.close()
    for row in entries:
        print(row['second'] + "    " + row['first'])
        response = send(row['secondloc'], row['firstloc'])
        file = open("C:/Users/alaa2/OneDrive/Desktop/routes/" + row['second'] + '-' + row['first'] + ".response",
                    mode='w')
        json.dump(response, file)
        file.close()


def generatePaths():
    files = os.listdir('C:/Users/alaa2/OneDrive/Desktop/routes')
    for name in files:
        file = open('C:/Users/alaa2/OneDrive/Desktop/routes/' + name, 'r')
        contentS = file.read()
        file.close()
        content = json.loads(contentS)
        steps = content['routes'][0]['legs'][0]['steps']
        points = decodePolylineofRoute(steps)
        file = open('C:/Users/alaa2/OneDrive/Desktop/paths/' + name, 'w')
        json.dump(points, file)
        file.close()


if __name__ == '__main__':
    saveResponses()
    generatePaths()

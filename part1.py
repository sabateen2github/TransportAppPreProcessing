
import os
import json
from turfpy import measurement
from geojson import Point, Feature

threshold = 400


def checkPoint(stopPoint, start, end):
    dist1 = measurement.distance(start, stopPoint, 'm')
    dist2 = measurement.distance(start, end, 'm')
    if dist1 > dist2:
        return False
    return True


def generate_stop_stations(path):
    bearings = []
    stopStations = []
    for i in range(1, len(path) - 1):
        start = tuple(path[i - 1])
        end = tuple(path[i])
        start = Feature(geometry=Point(start))
        end = Feature(geometry=Point(end))
        bearings.append(measurement.bearing(start, end))

    currentPoint = Feature(geometry=Point(tuple(path[0])))
    remaining = -1
    stopStations.append(path[0])
    for i in range(0, len(bearings) - 1):
        end = Feature(geometry=Point(tuple(path[i + 1])))
        if remaining != -1:
            stopPoint = measurement.destination(currentPoint, remaining, bearings[i], {'units': 'm'})
            if checkPoint(stopPoint, currentPoint, end):
                stopStations.append(stopPoint['geometry']['coordinates'])
                remaining = -1
                currentPoint = stopPoint
            elif i + 1 == len(path) - 1:
                break
            else:
                remaining -= measurement.distance(currentPoint, end, 'm')
                currentPoint = end
                continue

        stopPoint = measurement.destination(currentPoint, threshold, bearings[i], {'units': 'm'})
        if checkPoint(stopPoint, currentPoint, end):
            stopStations.append(stopPoint['geometry']['coordinates'])
            currentPoint = stopPoint
        elif i + 1 == len(path) - 1:
            break
        else:
            remaining = threshold - measurement.distance(currentPoint, end, 'm')
            currentPoint = end
            continue
    last = Feature(geometry=Point(tuple(path[len(path) - 1])))
    if measurement.distance(stopStations[len(stopStations) - 1], last, 'm') > threshold * 0.70:
        stopStations.append(last['geometry']['coordinates'])
    return stopStations


def make_stop_stations():
    files = os.listdir('C:/Users/alaa2/OneDrive/Desktop/paths')
    for name in files:
        file = open('C:/Users/alaa2/OneDrive/Desktop/paths/' + name, 'r')
        contentS = file.read()
        file.close()
        content = json.loads(contentS)
        stopStations = generate_stop_stations(content)
        file = open('C:/Users/alaa2/OneDrive/Desktop/stopStations/' + name, 'w')
        json.dump(stopStations, file)
        file.close()




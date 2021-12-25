import json
from pyproj import CRS, Transformer
from shapely.geometry import shape
from shapely.geometry import LineString
import os


def canGo(busStopFrom, busStopTo, names):
    featureFrom = featuresGeo[busStopFrom["id"] - 1]
    featureTo = featuresGeo[busStopTo["id"] - 1]

    temp = names.copy()
    for id in temp:
        polyline = geoPaths[id]
        distFrom = polyline.project(featureFrom)
        distTo = polyline.project(featureTo)
        if distFrom > distTo:
            names.remove(id)
    return len(names) > 0


def generateTree(busStop, _busStops, depth):
    tree = {"node": busStop["id"], "children": []}
    busStops = _busStops.copy()
    if depth == 3:
        return tree
    i = len(busStops) - 1
    while i >= 0:
        canGo = busStopsAllowed[busStop["id"] - 1][busStops[i]["id"] - 1]
        if len(canGo) > 0:
            item = busStops.pop(i)
            child = generateTree(item, busStops, depth + 1)
            child["receivedAt"] = canGo
            tree["children"].append(child)
        i -= 1
    if len(tree["children"]) == 0:
        del tree["children"]
    return tree


if __name__ == '__masdin__':

    with open("C:/Users/alaa2/OneDrive/Desktop/point_to_point/final_schedule.json") as fp:
        global features
        features = json.load(fp)["features"]
        features.sort(key=lambda x: x["id"])
        global featuresGeo
        featuresGeo = []
        for feature in features:
            featuresGeo.append(shape(features[feature["id"] - 1]["geometry"]))

    filesNames = os.listdir("C:/Users/alaa2/OneDrive/Desktop/point_to_point/paths_proj/")
    global geoPaths
    global nameIds
    namesIds = {}
    geoPaths = []
    i = 0
    for fileName in filesNames:
        with open("C:/Users/alaa2/OneDrive/Desktop/point_to_point/routes_ids/{}.txt".format(i), "w") as fp:
            json.dump(fileName, fp)
            namesIds[fileName] = i
        with open("C:/Users/alaa2/OneDrive/Desktop/point_to_point/paths_proj/{}".format(fileName)) as fp:
            polyline = LineString(json.load(fp))
            geoPaths.append(polyline)
        i = i + 1

    crs = CRS.from_proj4(
        '+proj=tmerc +lat_0=31.977400791234 +lon_0=35.9141891981517 +k=1 +x_0=500000 +y_0=200000 +datum=WGS84 '
        '+units=m +no_defs')

    transformer = Transformer.from_crs(CRS.from_epsg(4326), crs)

    for feature in features:
        points = feature["geometry"]["coordinates"]
        feature["geometry"]["coordinates"] = transformer.transform(points[0], points[1])

    ids = []
    ids_content = []

    for busStop in features:
        id = busStop["id"]
        ids.append(id)
        with open("C:/Users/alaa2/OneDrive/Desktop/point_to_point/schedules/{}.json".format(id), "r") as content:
            ids_content.append(list(map(lambda item: namesIds[item], json.load(content)["names"])))
    busStops = []
    for i in range(len(ids)):
        dict = {"id": ids[i], "names": set(ids_content[i])}
        busStops.append(dict)
    global busStopsAllowed
    busStopsAllowed = [None] * len(busStops)
    for i in range(len(busStops)):
        busStopsAllowed[i] = [None] * len(busStops)
        for x in range(len(busStops)):
            if i == x:
                continue
            intersections = busStops[i]["names"].intersection(busStops[x]["names"])
            if len(intersections) > 0:
                canGo(busStops[i], busStops[x], intersections)
                busStopsAllowed[i][x] = list(intersections)
            else:
                busStopsAllowed[i][x] = list(intersections)
    print("Finished")
    for i in range(len(busStops)):
        BS = busStops.copy()
        item = BS.pop(i)
        tree = generateTree(item, BS, 0)
        with open(
                "C:/Users/alaa2/OneDrive/Desktop/point_to_point/generated_trees/{}.json".format(tree["node"]),
                "w") as fp:
            json.dump(tree, fp)
        print("Done {} out of {}".format(i, len(busStops)))

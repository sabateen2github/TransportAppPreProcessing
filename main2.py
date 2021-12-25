from pyproj import CRS
from pyproj import Transformer
import json
import os
from shapely.geometry import LineString, mapping, shape, Point, GeometryCollection
from shapely.ops import transform
from shapely.strtree import STRtree
from geojson import FeatureCollection, Feature
import random


def dummy():
    crs = CRS.from_proj4(
        '+proj=tmerc +lat_0=31.977400791234 +lon_0=35.9141891981517 +k=1 +x_0=500000 +y_0=200000 +datum=WGS84 '
        '+units=m +no_defs')

    transformer = Transformer.from_crs(CRS.from_epsg(4326), crs)

    files = os.listdir("C:/Users/alaa2/OneDrive/Desktop/paths")
    for file in files:
        with open("C:/Users/alaa2/OneDrive/Desktop/paths/" + file, 'r', encoding="utf-8") as f:
            path = json.load(f)
            for i in range(len(path)):
                path[i] = transformer.transform(path[i][1], path[i][0])
            with open("C:/Users/alaa2/OneDrive/Desktop/paths_proj/" + file, 'w') as ff:
                json.dump(path, ff)


def dummy2():
    crs = CRS.from_proj4(
        '+proj=tmerc +lat_0=31.977400791234 +lon_0=35.9141891981517 +k=1 +x_0=500000 +y_0=200000 +datum=WGS84 '
        '+units=m +no_defs')

    transformerInv = Transformer.from_crs(crs, CRS.from_epsg(4326))

    files = os.listdir("C:/Users/alaa2/OneDrive/Desktop/paths_proj")
    for file in files:
        with open("C:/Users/alaa2/OneDrive/Desktop/paths_proj/" + file, 'r', encoding="utf-8") as f:
            path = json.load(f)
            lineString = LineString(path).buffer(2)
            with open("C:/Users/alaa2/OneDrive/Desktop/polys_proj/" + file, 'w') as pol:
                json.dump(mapping(lineString), pol)
            if file == 'وادي السير-وسط البلد.response':
                with open("C:/Users/alaa2/OneDrive/Desktop/test.json", 'w') as test:
                    json.dump(mapping(transform(transformerInv.transform, lineString)), test)


def dumpTest2(geometriesCollection, name="test2.json", related_data=None):
    crs = CRS.from_proj4(
        '+proj=tmerc +lat_0=31.977400791234 +lon_0=35.9141891981517 +k=1 +x_0=500000 +y_0=200000 +datum=WGS84 '
        '+units=m +no_defs')

    transformerInv = Transformer.from_crs(crs, CRS.from_epsg(4326))

    collection = transform(transformerInv.transform, geometriesCollection)

    feat_arr = []
    for i in range(len(collection)):
        geom = collection[i]
        feature = Feature(geometry=geom)
        feature['properties'] = {
            "color": "blue",
            "names": related_data[i] if related_data is not None else None
        }
        feat_arr.append(feature)

    features = FeatureCollection(feat_arr)

    with open("C:/Users/alaa2/OneDrive/Desktop/" + name, "w") as f:
        json.dump(features, f)


def dumpTest3(geometricCollection, related_data=None):
    collection = geometricCollection

    feat_arr = []
    for i in range(len(collection)):
        geom = collection[i]
        feature = Feature(geometry=geom)
        feature['properties'] = {
            "color": "blue",
            "names": related_data[i] if related_data is not None else None

        }
        feat_arr.append(feature)

    features = FeatureCollection([feat_arr])

    with open("C:/Users/alaa2/OneDrive/Desktop/test3.json", "w") as f:
        json.dump(features, f)


def getIntersects(index, geom):
    q = index.query(geom)
    true = []
    for l in q:
        if l.intersects(geom):
            true.append(l)
    return true


def generateStopPoints():
    polys = []
    names = []

    files_polys = os.listdir("C:/Users/alaa2/OneDrive/Desktop/polys_proj")
    for poly_f in files_polys:
        with open("C:/Users/alaa2/OneDrive/Desktop/polys_proj/" + poly_f, "r", encoding="utf-8") as f:
            polys.append(shape(json.load(f)))
            names.append(poly_f)

    index = STRtree(polys)

    lines = []
    files_lines = os.listdir("C:/Users/alaa2/OneDrive/Desktop/paths_proj")
    for line_f in files_lines:
        with open("C:/Users/alaa2/OneDrive/Desktop/paths_proj/" + line_f, "r", encoding="utf-8") as f:
            lines.append(LineString(json.load(f)))
    collection = GeometryCollection([*lines])

    dumpTest2(collection, "test4.json")

    busStops = []

    lines_done = 0
    for line in lines:
        lines_done += 1
        num = line.length / 500
        for i in range(int(num)):
            point = line.interpolate(i * 500)
            busStops.append(point)

    busStopsIndex = STRtree(busStops)

    i = 0
    while i < len(busStops):
        print("{}   +   {}".format(i, len(busStops)))
        buffer = busStops[i].buffer(400)
        points = busStopsIndex.query(buffer)
        intersectsP = getIntersects(index, busStops[i])
        for point in points:
            if point != busStops[i]:
                intersects = getIntersects(index, point)
                if len(intersectsP) == len(intersects):
                    if all(x in intersectsP for x in intersects):
                        busStops.remove(point)
        busStopsIndex = STRtree(busStops)
        i += 1

    baked_busStops = []
    busStops_names = []

    i = 0
    while i < len(busStops):
        print("{}   +   {}".format(i, len(busStops)))
        buffer = busStops[i].buffer(150)
        points = busStopsIndex.query(buffer)
        common = GeometryCollection(points)
        c_x = (common.bounds[0] + common.bounds[2]) / 2
        c_y = (common.bounds[1] + common.bounds[3]) / 2
        c_point = Point(c_x, c_y)
        busStop_names = []
        for p in points:
            polygons = getIntersects(index, p)
            for polygon in polygons:
                rel_name = names[polys.index(polygon)]
                if rel_name not in busStop_names:
                    busStop_names.append(rel_name)
            busStops.remove(p)
        busStopsIndex = STRtree(busStops)
        baked_busStops.append(c_point)
        busStops_names.append(busStop_names)
        i += 1

    collection = GeometryCollection(baked_busStops)
    dumpTest2(collection, related_data=busStops_names)
    dumpTest3(collection, related_data=busStops_names)


def generateLocalStopSchedule(path_name, past=None):
    program1 = [{"name": path_name, "hours": 8, "minutes": 0, "count": 2},
                {"name": path_name, "hours": 8, "minutes": 15, "count": 1},
                {"name": path_name, "hours": 8, "minutes": 30, "count": 2},
                {"name": path_name, "hours": 8, "minutes": 45, "count": 1},
                {"name": path_name, "hours": 9, "minutes": 0, "count": 1},
                {"name": path_name, "hours": 9, "minutes": 30, "count": 1},
                {"name": path_name, "hours": 9, "minutes": 45, "count": 1},
                {"name": path_name, "hours": 10, "minutes": 20, "count": 1},
                {"name": path_name, "hours": 10, "minutes": 50, "count": 1},
                {"name": path_name, "hours": 11, "minutes": 35, "count": 1},
                {"name": path_name, "hours": 12, "minutes": 20, "count": 1},
                {"name": path_name, "hours": 12, "minutes": 50, "count": 1},
                {"name": path_name, "hours": 13, "minutes": 40, "count": 1},
                {"name": path_name, "hours": 14, "minutes": 15, "count": 1},
                {"name": path_name, "hours": 14, "minutes": 30, "count": 1},
                {"name": path_name, "hours": 14, "minutes": 45, "count": 1},
                {"name": path_name, "hours": 15, "minutes": 30, "count": 1},
                {"name": path_name, "hours": 15, "minutes": 50, "count": 2},
                {"name": path_name, "hours": 16, "minutes": 30, "count": 2},
                {"name": path_name, "hours": 16, "minutes": 40, "count": 1},
                {"name": path_name, "hours": 16, "minutes": 50, "count": 1},
                {"name": path_name, "hours": 17, "minutes": 0, "count": 1},
                {"name": path_name, "hours": 17, "minutes": 20, "count": 1},
                {"name": path_name, "hours": 17, "minutes": 40, "count": 2},
                {"name": path_name, "hours": 18, "minutes": 0, "count": 1},
                {"name": path_name, "hours": 18, "minutes": 30, "count": 1},
                {"name": path_name, "hours": 19, "minutes": 30, "count": 1},
                {"name": path_name, "hours": 20, "minutes": 0, "count": 1},
                {"name": path_name, "hours": 20, "minutes": 30, "count": 1},
                {"name": path_name, "hours": 21, "minutes": 0, "count": 1},
                {"name": path_name, "hours": 21, "minutes": 30, "count": 1},
                {"name": path_name, "hours": 22, "minutes": 0, "count": 1},
                ]

    if past is None:
        return program1.copy()
    else:
        schedule = past.copy()
        for stamp in schedule:
            if stamp["minutes"] >= 55:
                stamp["hours"] += 1
                if stamp["hours"] > 23:
                    stamp["hours"] = 0
                stamp["minutes"] = 5 - (60 - stamp["minutes"])
            else:
                stamp["minutes"] += 5
        return schedule


def generateSchedule():
    paths_files = os.listdir("C:/Users/alaa2/OneDrive/Desktop/paths_proj")
    with open("C:/Users/alaa2/OneDrive/Desktop/test3.json") as stops_file:
        features = json.load(stops_file)["features"][0]
        for feature in features:
            feature["pyGeo"] = shape(feature['geometry'])
            feature["schedule"] = []  # list of dict { "hours":int,"minutes":int,"count":int,"name":"string"}
    for path_file in paths_files:
        with open("C:/Users/alaa2/OneDrive/Desktop/paths_proj/" + path_file, "r", encoding="utf-8") as path_bin:
            path = LineString(json.load(path_bin))
            rel_stops = []
            for feature in features:
                if path_file in feature["properties"]["names"]:
                    rel_stops.append(feature)
            rel_stops.sort(key=lambda feature: path.project(feature["pyGeo"]))
            past = None
            for stop in rel_stops:
                schedule = generateLocalStopSchedule(path_file, past)
                for stamp in schedule:
                    stop["schedule"].append(stamp)
                past = schedule if random.randint(1, 10) <= 3 else None
    for feature in features:
        del feature["pyGeo"]
    with open("C:/Users/alaa2/OneDrive/Desktop/test15.json", "w") as f:
        json.dump(FeatureCollection(features), f)


def lastPahse():
    crs = CRS.from_proj4(
        '+proj=tmerc +lat_0=31.977400791234 +lon_0=35.9141891981517 +k=1 +x_0=500000 +y_0=200000 +datum=WGS84 '
        '+units=m +no_defs')

    transformerInv = Transformer.from_crs(crs, CRS.from_epsg(4326))
    with open("C:/Users/alaa2/OneDrive/Desktop/جدول مع نقاط مع كل اشي .json") as f:
        features = json.load(f)["features"]
    id = 0
    for feature in features:
        geometry = shape(feature["geometry"])
        schedule = feature["schedule"]
        geometry = transform(transformerInv.transform, geometry)
        feature["geometry"] = mapping(geometry)
        id += 1
        feature["id"] = id

        for stamp in schedule:
            name = stamp["name"][:-9]
            del stamp["name"]
            names = name.split("-")
            stamp["from"] = names[0]
            stamp["to"] = names[1]

        schedule.sort(key=lambda x: x["hours"] * 60 + x["minutes"])
        with open("C:/Users/alaa2/OneDrive/Desktop/schedules/{}.json".format(id), "w") as f:
            feature_props = {"schedule": schedule, "names": feature["properties"]["names"]}
            json.dump(feature_props, f)
            del feature["schedule"]
            del feature["properties"]

    def keyGen(feature):
        east_start = 35.485461
        east_end = 36.736622
        return (feature["geometry"]["coordinates"][0] - east_start) + (
                feature["geometry"]["coordinates"][1] - east_start) * (east_end - east_start)

    features.sort(key=keyGen)

    collection = FeatureCollection(features)
    with open("C:/Users/alaa2/OneDrive/Desktop/final_schedule.json", "w") as f:
        json.dump(collection, f)

"""
if __name__ == "__main__":

    arrays = [3, 2, 1, 9, 10]
    array = [1, 2, 3, 4, 5, 4, 3, 2, 1]

    for n in arrays:
        max = 0
        index = -1

        if n > len(array):
            summa = 0
            index = -1
            print("summa {}   index {}".format(summa, index))
            continue
        for i in range(0, len(array) - n):
            sum = 0
            for x in range(i, n + i):
                sum += array[x]
            if sum > max:
                max = sum
                index = x

        if index == -1:
            summa = 0
            index = -1
        else:
            summa = max
            index = index
        print("summa {}   index {}".format(summa, index))


"""

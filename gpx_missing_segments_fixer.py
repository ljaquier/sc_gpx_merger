#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import geopy.distance
import datetime

ET.register_namespace("", "http://www.topografix.com/GPX/1/1")
ET.register_namespace("gpxtpx", "http://www.garmin.com/xmlschemas/TrackPointExtension/v2")
ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

NS = {
    "gpx": "http://www.topografix.com/GPX/1/1",
    "gpxtpx": "http://www.garmin.com/xmlschemas/TrackPointExtension/v2"
}

def parse_gpx(gpx_file):
    tree = ET.parse(gpx_file)
    root = tree.getroot()
    trk = root.find("gpx:trk", NS)
    if trk is None:
        raise ValueError(f"{gpx_file} has no <trk>")
    return tree, trk

def get_point(trkpt):
    return {
        "lat": float(trkpt.get("lat")),
        "lon": float(trkpt.get("lon")),
        "ele": (
            float(trkpt.findtext("gpx:ele", namespaces=NS))
            if trkpt.find("gpx:ele", NS) is not None
            else None
        ),
        "time": (
            datetime.datetime.fromisoformat(trkpt.findtext("gpx:time", namespaces=NS))
            if trkpt.find("gpx:time", NS) is not None
            else None
        )
    }

def get_reference_route(reference_file):
    _, trk = parse_gpx(reference_file)
    route = []
    for trkseg in trk.findall("gpx:trkseg", NS):
        for trkpt in trkseg.findall("gpx:trkpt", NS):
            route.append(get_point(trkpt))
    return route

def get_distance(point1, point2):
    return geopy.distance.geodesic(
        (point1["lat"], point1["lon"]), 
        (point2["lat"], point2["lon"])
    ).meters

def has_missing_segment(trkseg1, trkseg2):
    if trkseg1 is None or trkseg2 is None:
        return None

    point1 = get_point(trkseg1[-1])
    point2 = get_point(trkseg2[0])

    if get_distance(point1, point2) > 100:
        return point1, point2

    return None

def get_missing_segment(reference_route, start_point, end_point):
    start_index, _ = min(enumerate(reference_route), key=lambda item: get_distance(start_point, item[1]))
    end_index, _ = min(enumerate(reference_route), key=lambda item: get_distance(end_point, item[1]))
    points = [start_point] + reference_route[start_index:end_index + 1] + [end_point]

    cumulative_distances = [0.0]
    for index in range(len(points) - 1):
        cumulative_distances.append(cumulative_distances[-1] + get_distance(points[index], points[index + 1]))
    total_distance = cumulative_distances[-1]

    start_ele_correction = start_point['ele'] - reference_route[start_index]['ele']
    end_ele_correction = end_point['ele'] - reference_route[end_index]['ele']
    delta_ele_correction = end_ele_correction - start_ele_correction

    start_time = start_point['time']
    end_time = end_point['time']
    total_duration = end_time - start_time

    trkseg = ET.Element("trkseg")
    last_point_index = len(points) - 1
    for index, point in enumerate(points):
        ratio = cumulative_distances[index] / total_distance
        trkpt = ET.SubElement(trkseg, "trkpt", lat=str(point['lat']), lon=str(point['lon']))
        ET.SubElement(trkpt, "ele").text = str(point['ele'] + (start_ele_correction + delta_ele_correction * ratio if index > 0 and index < last_point_index else 0.0))
        ET.SubElement(trkpt, "time").text = str(start_time + total_duration * ratio)

    return trkseg

def fix_missing_segments(output_file, input_file, reference_file):
    base_tree, base_trk = parse_gpx(input_file)
    _, trk = parse_gpx(input_file)
    reference_route = get_reference_route(reference_file)

    base_trk.clear()
    prev_trkseg = None
    for trkseg in trk.findall("gpx:trkseg", NS):
        if prev_trkseg is not None:
            missing_segment_boundaries = has_missing_segment(prev_trkseg, trkseg)
            if missing_segment_boundaries:
                start_point, end_point = missing_segment_boundaries
                missing_segment = get_missing_segment(reference_route, start_point, end_point)
                base_trk.append(missing_segment)

        base_trk.append(trkseg)
        prev_trkseg = trkseg

    ET.indent(base_tree, space="  ")
    base_tree.write(output_file, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Fix missing segments in GPX file')
    parser.add_argument('output_file', help='Output GPX file')
    parser.add_argument('input_file', help='Input GPX file')
    parser.add_argument('reference_file', help='Input GPX file')
    args = parser.parse_args()

    fix_missing_segments(args.output_file, args.input_file, args.reference_file)

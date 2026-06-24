#!/usr/bin/env python3
import xml.etree.ElementTree as ET

ET.register_namespace("", "http://www.topografix.com/GPX/1/1")
ET.register_namespace("gpxtpx", "http://www.garmin.com/xmlschemas/TrackPointExtension/v2")
ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

NS = {
    "gpx": "http://www.topografix.com/GPX/1/1",
    "gpxtpx": "http://www.garmin.com/xmlschemas/TrackPointExtension/v2"
}

def clean_trkpt(trkpt):
    ext = trkpt.find("gpx:extensions", NS)
    if ext is None:
        return

    dist_elem = ext.find("gpx:distance", NS)
    if dist_elem is not None:
        ext.remove(dist_elem)

    tpx = ext.find("gpxtpx:TrackPointExtension", NS)
    if tpx is not None:
        course_elem = tpx.find("gpxtpx:course", NS)
        if course_elem is not None:
            tpx.remove(course_elem)

        if len(tpx) == 0:
            ext.remove(tpx)

    if len(ext) == 0:
        trkpt.remove(ext)

def clean_gpx(output_file, input_file):
    base_tree = ET.parse(input_file)
    base_root = base_tree.getroot()
    base_trk = base_root.find("gpx:trk", NS)

    if base_trk is None:
        raise ValueError(f"{input_file} has no <trk>")

    for trkseg in base_trk.findall("gpx:trkseg", NS):
        for trkpt in trkseg.findall("gpx:trkpt", NS):
            clean_trkpt(trkpt)

    ET.indent(base_tree, space="  ")
    base_tree.write(output_file, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Clean GPX file')
    parser.add_argument('output_file', help='Output GPX file')
    parser.add_argument('input_file', help='Input GPX file')
    args = parser.parse_args()

    clean_gpx(args.output_file, args.input_file)

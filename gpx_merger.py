#!/usr/bin/env python3
import xml.etree.ElementTree as ET

ET.register_namespace("", "http://www.topografix.com/GPX/1/1")
ET.register_namespace("gpxtpx", "http://www.garmin.com/xmlschemas/TrackPointExtension/v2")
ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

NS = {
    "gpx": "http://www.topografix.com/GPX/1/1",
    "gpxtpx": "http://www.garmin.com/xmlschemas/TrackPointExtension/v2"
}

def merge_gpx(output_file, input_files):
    if not input_files:
        raise ValueError("No input files provided")

    # Base file
    base_tree = ET.parse(input_files[0])
    base_root = base_tree.getroot()
    base_trk = base_root.find("gpx:trk", NS)

    if base_trk is None:
        raise ValueError(f"{input_files[0]} has no <trk>")

    for file in input_files[1:]:
        tree = ET.parse(file)
        root = tree.getroot()
        trk = root.find("gpx:trk", NS)

        if trk is None:
            print(f"Warning: {file} has no <trk>, skipping")
            continue

        for trkseg in trk.findall("gpx:trkseg", NS):
            base_trk.append(trkseg)

    ET.indent(base_tree, space="  ")
    base_tree.write(output_file, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Merge GPX files')
    parser.add_argument('output_file', help='Output GPX file')
    parser.add_argument('first_file', help='First GPX files')
    parser.add_argument('next_files', nargs='+', help='Next GPX files')
    args = parser.parse_args()

    merge_gpx(args.output_file, [args.first_file] + args.next_files)

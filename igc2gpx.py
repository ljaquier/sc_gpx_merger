from xc_scorer.xc_scorer import XCScorer, IGCParser
from datetime import datetime, timezone
import utils.gpx


def get_score(tracklog):
    scoring_rules = {
        "flat": {"multiplier": 1.2},
        "FAI": {"multiplier": 1.4},
        "closedFAI": {"multiplier": 1.6},
        "closedFlat": {"multiplier": 1.4},
        "freeFlight": {"multiplier": 1.0},
        "outReturn": {"multiplier": 1.2}
    }
    return XCScorer(tracklog, scoring_rules).score_flight(track_optimization=True)

def get_type_name(score):
    return {
        "flat": "Flat triangle",
        "FAI": "FAI triangle",
        "closedFAI": "Closed FAI triangle",
        "closedFlat": "Closed flat triangle",
        "free_distance": "Free flight"
    }[score['triangle_type'] if score['type'] == 'triangle' else score['type']]

def get_title(score):
    return f"🪂 Paragliding / {get_type_name(score)}"

def get_description(igc_parser, tracklog, score):
    description = f"XC distance: {score['properties']['total_distance']:.2f} km\n"
    description += f"XC score: {score['score']:.2f} pts\n"
    if igc_parser.glider_type:
        description += f"Glider: {igc_parser.glider_type}\n"
    description += "\n"

    description += f"Takeoff: {tracklog[0].alt:.0f} m\n"
    description += f"Max alt.: {max(tracklog, key=lambda point: point.alt).alt:.0f} m\n"
    description += f"Min alt.: {min(tracklog, key=lambda point: point.alt).alt:.0f} m\n"
    description += f"Landing: {tracklog[-1].alt:.0f} m\n"
    description += "\n"

    max_climb = next((int(comment.split(":")[1])/100 for comment in igc_parser.comments if 'SKYDROP-CLIMB-MAX-cm' in comment), None)
    if max_climb:
        description += f"Max climb: {max_climb:.2f} m/s\n"
    max_sink = next((int(comment.split(":")[1])/100 for comment in igc_parser.comments if 'SKYDROP-SINK-MAX-cm' in comment), None)
    if max_sink:
        description += f"Max sink: {max_sink:.2f} m/s"

    return description.strip()

def get_gpx(igc_parser):
    tracklog = igc_parser.parse()
    score = get_score(tracklog)

    track_points = []
    for point in tracklog:
        track_points.append(
            utils.gpx.TrackPoint(
                point.lat,
                point.lon,
                point.alt,
                datetime.combine(igc_parser.date, point.time, timezone.utc)
            )
        )

    return utils.gpx.get_gpx(
        get_title(score),
        get_description(igc_parser, tracklog, score),
        'Workout',
        track_points
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Convert an activity from a paragliding flight (IGC file) to a GPX file')
    parser.add_argument('igc_file', help='IGC file')
    parser.add_argument('gpx_file', help='GPX file')
    args = parser.parse_args()

    igc_parser = IGCParser(args.igc_file)
    gpx = get_gpx(igc_parser)
    with open(args.gpx_file, "w", encoding="utf-8") as gpx_file:
        gpx_file.write(gpx)

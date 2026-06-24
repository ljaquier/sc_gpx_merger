from dataclasses import dataclass
from datetime import datetime
import gpxpy


@dataclass
class TrackPoint:
    latitude: float
    longitude: float
    elevation: float
    time: datetime

def get_gpx(name, description, sport_type, track_points):
    gpx = gpxpy.gpx.GPX()
    gpx.creator='creator with barometer'

    gpx_track = gpxpy.gpx.GPXTrack()
    gpx_track.name=name
    gpx_track.description=description
    gpx_track.type=sport_type
    gpx.tracks.append(gpx_track)

    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    for track_point in track_points:
        gpx_segment.points.append(
            gpxpy.gpx.GPXTrackPoint(
                latitude=track_point.latitude,
                longitude=track_point.longitude,
                elevation=track_point.elevation,
                time=track_point.time
            )
        )

    return gpx.to_xml()

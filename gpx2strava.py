import gpxpy
import requests
import utils.json

def get_access_token(config):
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "grant_type": "refresh_token",
            "refresh_token": config["refresh_token"],
        },
    ).json()

    if "access_token" not in response:
        raise Exception(f"Error refreshing token: {response}")

    config['refresh_token'] = response["refresh_token"]

    return response["access_token"]

def upload_to_strava(access_token, gpx_content):
    gpx_track = gpxpy.parse(gpx_content).tracks[0]
    return requests.post(
        "https://www.strava.com/api/v3/uploads",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        files={
            "file": ("activity.gpx", gpx_content, "application/gpx+xml")
        },
        data={
            "name": gpx_track.name,
            "description": gpx_track.description,
            "data_type": "gpx",
            "sport_type": gpx_track.type
        }
    )

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Create activity on Strava from a GPX file')
    parser.add_argument('config_file', help='Config file')
    parser.add_argument('gpx_files', nargs='+', help='GPX files')
    args = parser.parse_args()
    
    config = utils.json.load_json(args.config_file)
    access_token = get_access_token(config)
    for gpx_path in args.gpx_files:
        with open(gpx_path, encoding="utf-8") as gpx_file:
            response = upload_to_strava(access_token, gpx_file.read())
            print(f"{gpx_path} : {response.status_code} : {response.text}")
    utils.json.save_json(args.config_file, config)

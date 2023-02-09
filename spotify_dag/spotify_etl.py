import pandas as pd
import s3fs
import boto3
from datetime import timedelta, datetime
import requests
from secret import spotify_user_id, spotify_token, discover_weekly_id
from refresh import Refresh

def token_refresh():
    # API를 사용하기 위한 Token을 Refresh하여 재사용이 가능하도록 하는 함수입니다.
    refreshCaller = Refresh()

    new_token = refreshCaller.refresh()
    return new_token

def find_songs(year, month, day, hour, **_):

    # 유저의 2시간(DAG interval time)동안 쌓인 음악 데이터를 조회한 후 Transform하여, 저장소로 보내는 함수입니다.
    # DAG를 실행하는 시간 그대로 (정각으로) 설정하여 저장해둡니다. 해당 datetime은 아래에서 쓰일 예정입니다.
    now_time = f'{year}-{month}-{day} {hour}:00:00'
    run_time = datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S') + timedelta(hours=9)

    # spotify API를 주기적으로 실행하기 위한 함수를 불러와 새로운 토큰을 발급합니다. 이후 쿼리를 설정합니다.
    spotify_token = token_refresh()
    query = "https://api.spotify.com/v1/me/player/recently-played?limit=50"

    # API를 통해 받은 데이터를 json 형태로 조회 가능하도록 합니다.
    response = requests.get(query, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotify_token)})
    response_json = response.json()

    # 위에서 설정한 정각 시간(run_time)을 혹여나 초과한 음악 감상시간이 있는지 확인하고, 존재한다면 해당 json에서 제외합니다.
    # latest_scr : 가장 최근 들은 음악의 한국시간 (UTC+9)
    latest_scr = datetime.strptime(response_json["items"][0]["played_at"],'%Y-%m-%dT%H:%M:%S.%fZ') + timedelta(hours=9)
    if (latest_scr > run_time) == True :
        response_json["items"] = response_json["items"][1:]

    # 이어 'latest_scr'이 2시간 내에 들은 음악이 아니면 해당 DAG를 간단한 출력으로 끝마칩니다. > 'break_time' task
    if (timedelta(hours=2) >= run_time - latest_scr) == False :
        print("see you next interval")
        return "break_time"
    # 아니라면, 2시간 내에 들은 음악들을 Transform 이후, csv형태로 저장하여 저장소로 보냅니다. > 'etl_start' task
    else :
        song_list = []
        for f_song in response_json["items"] :
            # KST 기준 수정 + 해당 Interval내가 아닐 시, 'song_list'로의 저장을 멈춥니다.
            listened_time = datetime.strptime(f_song["played_at"],'%Y-%m-%dT%H:%M:%S.%fZ') + timedelta(hours=9)

            if (timedelta(hours=2) >= run_time - listened_time) == False :
                break

            listened_day = datetime.strftime(listened_time, '%Y-%m-%d')
            listened_hour = datetime.strftime(listened_time, '%H')
            track_id = f_song["track"]["id"]
            # 음악의 특성을 불러오는 함수는 api가 다르므로, 별도로 불러옵니다.
            query_2 = "https://api.spotify.com/v1/audio-features/{}".format(track_id)
            response_2 = requests.get(query_2, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotify_token)})
            features = response_2.json()

            results = {
                "day" : listened_day,
                "hour" : listened_hour,
                "track_id" : track_id,
                "track_name" : f_song["track"]["name"],
                "artist_id" : f_song["track"]["artists"][0]['id'],
                "artist_name" : f_song["track"]["artists"][0]['name'],
                "acousticness" : features["acousticness"],
                "danceability" : features["danceability"],
                "energy" : features["energy"],
                "liveness" : features["liveness"],
                "loudness" : features["loudness"],
                "instrumentalness" : features["instrumentalness"],
                "speechiness" : features["speechiness"],
                "tempo" : features["tempo"],
                "valence" : features["valence"],
                "duration(ms)" : features["duration_ms"],
                "mode" : features["mode"],
                "key" : features["key"]
                }

            song_list.append(results)

        # else문의 마지막으로, csv 형태로 해당 버킷 폴더에 저장합니다.
        df = pd.DataFrame(song_list)
        s3 = boto3.client('s3')
        str_nt = run_time.strftime('%Y%m%d_%H')
        file_path = str_nt + '.csv'
        bucket = 'airflow-nk'
        key = f'logs/{file_path}'
        file_s3 = df.to_csv(file_path, index=False)
        s3.upload_file(file_path, bucket, key)
        return "etl_start"

def GlueJobRun():
    # Glue Job을 Run하기 위한 함수입니다.
    client = boto3.client('glue',region_name='ap-northeast-2')

    response = client.start_job_run(
        JobName='SpotifyGlueJob'
    )

    print(response)

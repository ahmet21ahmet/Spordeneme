import os
import requests
import concurrent.futures

sakusezon = {
    32: '2010/2011', 
    30: '2011/2012',
    25: '2012/2013',
    34: '2013/2014',
    37: '2014/2015',
    24: '2015/2016',
    29: '2016/2017',
    23: '2017/2018',
    20: '2018/2019',
    994: '2019/2020',
    3189: '2020/2021',
    3308: '2021/2022',
    3438: '2022/2023',
    3580: '2023/2024',
    3746: '2024/2025',
    3853: '2025/2026', 
}

sezonhafta = {
    32: range(1, 35),
    30: range(1, 35),
    25: range(1, 35),
    34: range(1, 35),
    37: range(1, 35),
    24: range(1, 35),
    29: range(1, 35),
    23: range(1, 35),
    20: range(1, 35),
    994: range(1, 35),
    3189: range(1, 43),
}

sezona = {
    30: 2899,
}

os.makedirs('saku', exist_ok=True)

def fetch_and_parse(url_info):
    url, sezonss = url_info
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        events = data.get('Data', {}).get('events', [])
        result = []
        for event in events:
            home = event.get('homeTeam', {}).get('name', 'Ev')
            home_score = event.get('homeTeam', {}).get('matchScore', '-')
            away = event.get('awayTeam', {}).get('name', 'Deplasman')
            away_score = event.get('awayTeam', {}).get('matchScore', '-')
            video_url = event.get('highlightVideoUrl')
            logo = event.get('highlightThumbnail', '')
            match_id = event.get('matchId', '')

            if video_url:
                title = f"{home} {home_score}-{away_score} {away}"
                line1 = f'#EXTINF:-1 tvg-id="{match_id}" tvg-logo="{logo}" group-title="{sezonss}",{title}\n'
                line2 = f"{video_url}\n"
                result.append((sezonss, line1, line2))
        return result
    except Exception:
        return []

tmurlfull = []
for sezonss_id, sezonss_name in sakusezon.items():
    weeks = sezonhafta.get(sezonss_id, range(1, 39))
    st = sezona.get(sezonss_id, 0)
    for week in weeks:
        url = f"https://beinsports.com.tr/api/highlights/events?sp=1&o=18&s={sezonss_id}&r={week}&st={st}"
        tmurlfull.append((url, sezonss_name))

sezonssal_results = {}

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = executor.map(fetch_and_parse, tmurlfull)
    for result in futures:
        for sezonss, line1, line2 in result:
            if sezonss not in sezonssal_results:
                sezonssal_results[sezonss] = []
            sezonssal_results[sezonss].append((line1, line2))

all_lines = []

for sezonss, lines in sezonssal_results.items():
    folder_name = sezonss.replace('/', '-')
    folder_path = os.path.join('saku', folder_name)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f"{folder_name}.m3u")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n\n")
        for line1, line2 in lines:
            f.write(line1)
            f.write(line2)
            all_lines.append((line1, line2))

all_m3u_path = os.path.join('saku', 'all.m3u')
with open(all_m3u_path, 'w', encoding='utf-8') as f:
    f.write("#EXTM3U\n\n")
    for line1, line2 in all_lines:
        f.write(line1)
        f.write(line2)

print("Her sezon için klasör, M3U dosyaları ve all.m3u başarıyla oluşturuldu.")

#Sakultah tarafından yapılmıştır iyi kullanımlar :)

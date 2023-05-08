from yandex_music.exceptions import NotFoundError
from pypresence import DiscordNotFound
from exceptions import TokenNotFound
from yandex_music import Client
import configparser
import pypresence
import os.path
import psutil
import time


client_id = '1102205912640409704'


configCreate = configparser.ConfigParser()
if os.path.isfile("config.ini"):
    configCreate.read("config.ini")
    if not configCreate.sections():
        configCreate['token'] = {'token': 'None'}
        file = open("config.ini", "w")
        configCreate.write(file)
        file.close()
else:
    configCreate['token'] = {'token': 'None'}
    file = open("config.ini", "w")
    configCreate.write(file)
    file.close()


def get_token():
    config = configparser.ConfigParser()
    config.read('config.ini')
    if config.get('token', 'token') == 'None':
        raise TokenNotFound()
    else:
        print('[YMDS] -> Токен был успешно получен')
    return config.get('token', 'token')


class Presence:
    def __init__(self) -> None:
        self.token = get_token()
        self.client = None
        self.sTime = None
        self.rpc = None
        self.running = False
        self.currentTrack = {
            'success': None,
            'name': None,
            'artists': None,
            'album': None,
            'link': None,
            'time': None,
            'og-image': None
        }

    def start(self) -> None:
        self.start_time = time.time()
        try:
            if "Discord.exe" not in (p.name() for p in psutil.process_iter()):
                print("[YMDS] -> Discord не запущен")
                self.running = False
            else:
                self.currentTrack = self.get_track()
                self.rpc = pypresence.Presence(client_id)
                self.rpc.connect()
                self.client = Client(self.token).init()
                self.running = True
        except DiscordNotFound:
            pass
        while self.running:
            if "Discord.exe" not in (p.name() for p in psutil.process_iter()):
                print("[YMDS] -> Discord был закрыт")
                self.running = False
            elif self.currentTrack != (ongoing_track := self.get_track()):
                if (
                    self.currentTrack['name'] != ongoing_track['name'] or
                    self.currentTrack['artists'] != ongoing_track['artists']
                ):
                    self.start_time = int(time.time())
                    if self.last_queue.context.type == 'radio':
                        print(f"[YMDS]->{ongoing_track['name']}")
                    else:
                        print(f"[YMDS]->Текущий трек {ongoing_track['name']}")
                    if ongoing_track['success']:
                        self.rpc.update(
                            details=ongoing_track['name'],
                            state=ongoing_track['artists'],
                            large_image=f"{ongoing_track['og-image']}",
                            large_text=ongoing_track['album'],
                            small_image="og-image",
                            small_text=ongoing_track['time'],
                            buttons=[
                                {
                                    'label': 'Слушать',
                                    'url': ongoing_track['link']
                                }
                                    ]
                        )
                    elif not ongoing_track['success']:
                        self.rpc.update(
                            details=ongoing_track['name'],
                            large_image="https://i.gifer.com/3OUSF.gif",
                            small_image="og-image",
                            small_text='Прямой Эфир',
                        )
                self.currentTrack = ongoing_track
            elif not self.sTime:
                self.rpc.clear()

    def get_track(self) -> dict:
        try:
            currect_time = int(time.time())
            queues = self.client.queues_list()
            self.last_queue = self.client.queue(queues[0].id)
            track_id = self.last_queue.get_current_track()
            track = track_id.fetch_track()
            track_ms = track.duration_ms
            time_end_track = int(self.start_time)+track_ms//1000+30
            self.sTime = True if time_end_track > currect_time else False
        except AttributeError:
            return {
                'success': False,
                'name': "Ищет поток",
            }
        except NotFoundError:
            return {
                'success': False,
                'name': "Ищет поток",
            }
        except Exception:
            live_dict = {
                'genre': 'жанру',
                'user': 'плейлисту',
                'editorial': 'плейлисту',
                "mood": "настроению",
                'activity': "активности",
                'epoch': 'эпохе'
            }
            live = live_dict[self.last_queue.context.id.split(":")[0]]
            live_description = self.last_queue.context.description
            return {
                'success': False,
                'name': f'Поток по {live} "{live_description}"'
            }
        base_url = 'https://music.yandex.ru'
        trk_album_id = track['albums'][0]['id']
        return {
            'success': True,
            'name': f"{track.title}",
            'artists': f'{", ".join(track.artists_name())}',
            'album': f"{track['albums'][0]['title']}",
            'link': f"{base_url}/album/{trk_album_id}/track/{track['id']}/",
            'time': f'{track_ms//(60*1000)%60:02d}:{track_ms//1000%(60):02d}',
            'og-image': f"https://{track.og_image[:-2]}300x300",
        }


presence = Presence()
while True:
    presence.start()

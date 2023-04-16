import pypresence
from pypresence import DiscordNotFound
import configparser
import time
from yandex_music import Client
import psutil
import os.path


client_id = 'Discord-токен'


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


def getToken():
    config = configparser.ConfigParser()
    config.read('config.ini')
    if config.get('token', 'token') == 'None':
        token_ = input("[YMDS] -> Пожалуйста, введите ваш токен, который вы получили c файла get_yandex_token: ")
        config.set('token', 'token', token_)
        with open('config.ini', 'w') as f:
            config.write(f)
    else:
        print('[YMDS] -> Токен был успешно получен')
    return config.get('token', 'token')


class Presence:
    def __init__(self) -> None:
        self.token = getToken()
        self.client = None
        self.currentTrack = None
        self.rpc = None
        self.running = False

    def start(self) -> None:
        self.running = True
        try:
            if "Discord.exe" not in (p.name() for p in psutil.process_iter()):
                print("[YMDS] -> Discord не запущен")
                # return
                self.running = False
            self.currentTrack = self.getTrack()
            self.rpc = pypresence.Presence(client_id)
            self.rpc.connect()
            self.client = Client(self.token).init()
        except DiscordNotFound:
            pass
        while self.running:
            if "Discord.exe" not in (p.name() for p in psutil.process_iter()):
                print("[YMDS] -> Discord был закрыт")
                # return
                self.running = False
            if self.currentTrack != (ongoing_track := self.getTrack()):
                print(f"[YMDS] -> Текущий трек {ongoing_track['name']}")
                try:
                    if ongoing_track['success']:
                        self.rpc.update(
                            details=ongoing_track['name'],
                            state=ongoing_track['artists'],
                            large_image=f"{ongoing_track['og-image']}",
                            large_text=ongoing_track['album'],
                            small_image="https://music.yandex.com/blocks/meta/i/og-image.png",
                            small_text=ongoing_track['time'],
                            buttons=[{'label': 'Слушать', 'url': ongoing_track['link']}]
                        )
                    if ongoing_track['success'] == False:
                        self.rpc.update(
                            details=ongoing_track['name'],
                            large_image="https://i.gifer.com/3OUSF.gif",
                        )
                    self.currentTrack = ongoing_track
                except Exception:
                    pass

    def getTrack(self) -> dict:
        try:
            queues = self.client.queues_list()
            last_queue = self.client.queue(queues[0].id)
            track_id = last_queue.get_current_track()
            track = track_id.fetch_track()
        except AttributeError:
            return {
                'success': False,
                'name': "В потоке",
            }
        except Exception as ex:
            print(ex)
            return {
                'success': False,
                'name': "В потоке",
            }
        return {
            'success': True,
            'name': f"{track.title} ",
            'artists': f'{", ".join(track.artists_name())}',
            'album': f"{track['albums'][0]['title']}",
            'link': f"https://music.yandex.ru/album/{track['albums'][0]['id']}/track/{track['id']}/",
            'time': f'{0 if track.duration_ms // 60000 < 10 else ""}{track.duration_ms // 60000}'
                        f':{0 if track.duration_ms % 60000 // 1000 < 10 else ""}{track.duration_ms % 60000 // 1000}',
            'og-image': "https://" + track.og_image[:-2] + "300x300"
        }


presence = Presence()
while True:
    presence.start()
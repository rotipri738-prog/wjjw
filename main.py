import flet as ft
import yt_dlp
import random
import os
import glob
import re

def main(page: ft.Page):
    page.title = "Anti-Yandex Ultra"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.padding = 15
    
    playlist_data = []
    audio = ft.Audio(src="", autoplay=False)
    page.overlay.append(audio)

    # --- ЛОГИКА ИМПОРТА И ПОИСКА ---
    def fetch_music(e):
        query = search_input.value
        if not query: return
        
        search_input.disabled = True
        loading_bar.visible = True
        page.update()

        # Настройки для обхода ограничений и поиска по названиям
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': False,
            'default_search': 'ytsearch',
            # Если это ссылка на закрытый сервис, yt-dlp попробует вытащить метаданные
            'ignoreerrors': True, 
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Если это просто текст, ищем в сети
                # Если ссылка на Spotify/Яндекс - вытягиваем инфу
                info = ydl.extract_info(query, download=False)
                
                if 'entries' in info:
                    tracks = info['entries']
                else:
                    tracks = [info]

                for t in tracks:
                    if t:
                        playlist_data.append({
                            'title': t.get('title', 'Без названия'),
                            'url': t.get('url'),
                            'thumb': t.get('thumbnail', 'https://via.placeholder.com/150'),
                            'artist': t.get('uploader', 'Разные источники'),
                            'source': 'Stream'
                        })
                render_list()
            except Exception as ex:
                print(f"Ошибка импорта: {ex}")
        
        loading_bar.visible = False
        search_input.disabled = False
        search_input.value = ""
        page.update()

    def import_from_device(e):
        # Сканируем стандартные папки Android
        paths = ["/storage/emulated/0/Music/*.mp3", "/storage/emulated/0/Download/*.mp3"]
        files = []
        for p in paths:
            files.extend(glob.glob(p))
        
        for f in files:
            playlist_data.append({
                'title': os.path.basename(f),
                'url': f,
                'thumb': ft.icons.FILE_OPEN,
                'artist': "Устройство",
                'source': 'Local'
            })
        render_list()
        ft.SnackBar(ft.Text(f"Импортировано {len(files)} треков"), open=True).show()
        page.update()

    def play_track(idx):
        t = playlist_data[idx]
        audio.src = t['url']
        audio.update()
        audio.play()
        now_playing.value = f"▶️ {t['title']}"
        play_btn.icon = ft.icons.PAUSE_CIRCLE_FILLED
        page.update()

    def render_list():
        list_view.controls.clear()
        for i, t in enumerate(playlist_data):
            list_view.controls.append(
                ft.ListTile(
                    leading=ft.Image(src=t['thumb'], width=45, height=45, border_radius=5) if t['source'] == 'Stream' else ft.Icon(ft.icons.AUDIOTRACK, color="#ffcc00"),
                    title=ft.Text(t['title'], size=14, weight="bold", no_wrap=True),
                    subtitle=ft.Text(t['artist'], size=12, color="grey"),
                    on_click=lambda _, idx=i: play_track(idx),
                    bgcolor="#1e1e1e",
                    shape=ft.RoundedRectangleBorder(radius=10)
                )
            )
        page.update()

    # --- ЭЛЕМЕНТЫ UI ---
    search_input = ft.TextField(hint_text="Ссылка (VK, Spotify, Yandex, YT) или песня", expand=True, border_radius=20, bgcolor="#262626")
loading_bar = ft.ProgressBar(visible=False, color="#ffcc00")
    list_view = ft.ListView(expand=True, spacing=8)
    now_playing = ft.Text("Очередь пуста", size=14, color="#ffcc00", weight="500", no_wrap=True)
    play_btn = ft.IconButton(icon=ft.icons.PLAY_CIRCLE_FILLED, icon_size=55, icon_color="#ffcc00")

    # --- СБОРКА СТРАНИЦЫ ---
    page.add(
        ft.Row([
            ft.Text("Anti-Yandex", size=28, weight="bold", color="#ffcc00"),
            ft.Icon(ft.icons.WAVES, color="#ffcc00")
        ], alignment="center"),
        ft.Row([search_input, ft.IconButton(ft.icons.DOWNLOAD_FOR_OFFLINE, on_click=fetch_music, icon_color="#ffcc00", icon_size=35)]),
        loading_bar,
        ft.Row([
            ft.Text("Моя музыка", size=18, weight="bold"),
            ft.Row([
                ft.IconButton(ft.icons.SHUFFLE, on_click=lambda _: random.shuffle(playlist_data) or render_list()),
                ft.IconButton(ft.icons.FOLDER_OPEN, on_click=import_from_device)
            ])
        ], alignment="spaceBetween"),
        list_view,
        # ПЛЕЕР
        ft.Container(
            content=ft.Column([
                now_playing,
                ft.Row([
                    ft.IconButton(ft.icons.SKIP_PREVIOUS, icon_size=30),
                    play_btn,
                    ft.IconButton(ft.icons.SKIP_NEXT, icon_size=30)
                ], alignment="center")
            ]),
            padding=10, bgcolor="#1a1a1a", border_radius=20, border=ft.border.all(1, "#333")
        )
    )

ft.app(target=main)
import os
from pathlib import Path

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView, TreeViewLabel
from plexapi.exceptions import BadRequest, NotFound
from plexapi.server import PlexServer
from PyQt6.QtWidgets import QApplication

from ..utils.authentication import PlexAuthentication

media_conveyor_root = Path.home() / ".plex_cred"
project_root = Path(__file__).resolve().parent.parent.parent
os.environ["PLEX_CRED"] = str(project_root / "tests/.plex_cred")


class ScrollableTreeView(TreeView):
    def on_minimum_height(self, instance, value):
        self.height = value


class HelloWorldApp(App):
    def build(self):
        return Button(text="Hello World", on_press=self.print_hello)

    def print_hello(self, instance):
        print("Hello World")


class PlaylistApp(App):
    def __init__(self, plex_server, **kwargs):
        super(PlaylistApp, self).__init__(**kwargs)
        self.plex_server = plex_server

    def build(self):
        return PlaylistGUI(plex_server=self.plex_server)


class PlaylistGUI(BoxLayout):
    audio_button = ObjectProperty(None)
    video_button = ObjectProperty(None)
    photo_button = ObjectProperty(None)
    playlist_tree = ObjectProperty(None)
    plex_server = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PlaylistGUI, self).__init__(**kwargs)
        self.orientation = "horizontal"  # Set the orientation of the main layout to horizontal
        self.plex_server = kwargs.get("plex_server", None)
        self.playlists = self.get_playlists()
        self.playlist_audio_data = self.get_playlist_audio_data()

        # Create the buttons layout with vertical orientation
        buttons_layout = BoxLayout(orientation="vertical", size_hint=(0.3, 1))

        # Create the buttons with less height
        self.audio_button = Button(text="Audio", size_hint_y=0.3)
        self.audio_button.bind(on_press=self.update_playlist_tree)

        self.video_button = Button(text="Video", size_hint_y=0.3)
        self.video_button.bind(on_press=self.update_playlist_tree)

        self.photo_button = Button(text="Photo", size_hint_y=0.3)
        self.photo_button.bind(on_press=self.update_playlist_tree)

        # Add the buttons to the buttons layout
        buttons_layout.add_widget(self.audio_button)
        buttons_layout.add_widget(self.video_button)
        buttons_layout.add_widget(self.photo_button)

        # Create the playlist tree
        self.playlist_tree = TreeView(hide_root=True, size_hint_y=None)
        self.playlist_tree.bind(minimum_height=self.playlist_tree.setter("height"))

        # Create a ScrollView
        scroll_view = ScrollView(
            size_hint=(None, None), size=(500, 320), pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        # Add the TreeView to the ScrollView
        scroll_view.add_widget(self.playlist_tree)

        # Add the buttons layout and the scroll view to the main layout
        self.add_widget(buttons_layout)
        self.add_widget(scroll_view)

        # Populate the tree with audio playlists
        self.populate_audio_playlist_tree()

    def update_playlist_tree(self, instance):
        # Clear the tree
        while self.playlist_tree.root.nodes:
            self.playlist_tree.remove_node(self.playlist_tree.root.nodes[0])

        # Check which button is pressed and update the tree accordingly
        if instance == self.audio_button:
            self.populate_audio_playlist_tree()
        elif instance == self.video_button:
            self.populate_video_playlist_tree()
        elif instance == self.photo_button:
            self.populate_photo_playlist_tree()

    def populate_audio_playlist_tree(self):
        # Populate the tree with audio playlists
        for playlist in self.playlists["audio"]:
            self.playlist_tree.add_node(TreeViewLabel(text=playlist.title))

    def populate_video_playlist_tree(self):
        # Populate the tree with video playlists
        for playlist in self.playlists["video"]:
            self.playlist_tree.add_node(TreeViewLabel(text=playlist.title))

    def populate_photo_playlist_tree(self):
        # Populate the tree with photo playlists
        for playlist in self.playlists["photo"]:
            self.playlist_tree.add_node(TreeViewLabel(text=playlist.title))

    def get_playlists(self):
        # This method will get the playlists from the Plex server
        # The implementation of this method will depend on the Plex server API
        try:
            playlists = self.plex_server.playlists()
            categorized_playlists = {
                "audio": [playlist for playlist in playlists if playlist.playlistType == "audio"],
                "video": [playlist for playlist in playlists if playlist.playlistType == "video"],
                "photo": [playlist for playlist in playlists if playlist.playlistType == "photo"],
            }
            # print(f"Categorized playlists: {categorized_playlists}")  # Debug print
            return categorized_playlists
        except Exception as e:
            print(f"Failed to fetch playlists: {e}")
            return {"audio": [], "video": [], "photo": []}

    def get_playlist_audio_data(self):
        # This method will get the audio data for the playlists
        # The implementation of this method will depend on the Plex server API
        all_playlist_data = {}
        for playlist in self.playlists["audio"]:
            playlist_data = {
                playlist.title.strip(): {},
            }
            for item in playlist.items():
                artist = item.grandparentTitle.strip()
                album = item.parentTitle.strip()
                track = item.title.strip()
                track_number = item.trackNumber

                if artist not in playlist_data[playlist.title.strip()]:
                    playlist_data[playlist.title.strip()][artist] = {}

                if album not in playlist_data[playlist.title.strip()][artist]:
                    playlist_data[playlist.title.strip()][artist][album] = []

                playlist_data[playlist.title.strip()][artist][album].append((track_number, track))

            all_playlist_data.update(
                playlist_data
            )  # Add this playlist's data to the main dictionary
        # print(f"All playlist data: {all_playlist_data}")  # Debug print
        return all_playlist_data


def main():
    plex_auth = PlexAuthentication()
    plex_server = PlexServer(baseurl=plex_auth.baseurl, token=plex_auth.token)
    # HelloWorldApp().run()
    PlaylistApp(plex_server).run()

from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QMainWindow,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class PlaylistGUI(QMainWindow):
    def __init__(self, plex_server):
        super().__init__()
        self.plex_server = plex_server
        self.tree = QTreeWidget()
        self.combo = QComboBox()
        self.playlists = self.get_playlists()
        self.populate_combo()
        layout = QVBoxLayout()
        layout.addWidget(self.combo)
        layout.addWidget(self.tree)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.populate_tree()

    def get_playlists(self):
        try:
            playlists = self.plex_server.playlists()
            categorized_playlists = {
                "audio": [playlist for playlist in playlists if playlist.playlistType == "audio"],
                "video": [playlist for playlist in playlists if playlist.playlistType == "video"],
                "photo": [playlist for playlist in playlists if playlist.playlistType == "photo"],
            }
            return categorized_playlists
        except Exception as e:
            print(f"Failed to fetch playlists: {e}")
            return {"audio": [], "video": [], "photo": []}

    def playlist_data_dict(self, playlist):
        """Return a dictionary of playlist data"""
        if playlist.playlistType != "audio":
            return None

        playlist_data = {
            playlist.title: {},
        }
        for item in playlist.items():
            artist = item.grandparentTitle
            album = item.parentTitle
            track = item.title
            track_number = item.trackNumber  # assuming the item object has a trackNumber attribute

            if artist not in playlist_data[playlist.title]:
                playlist_data[playlist.title][artist] = {}

            if album not in playlist_data[playlist.title][artist]:
                playlist_data[playlist.title][artist][album] = []

            playlist_data[playlist.title][artist][album].append((track_number, track))

        return playlist_data

    def populate_playlist_combo(self):
        model = QStandardItemModel()
        for category, playlists in self.playlists.items():
            category_item = QStandardItem(category.capitalize())
            category_item.setEnabled(False)
            model.appendRow(category_item)
            for playlist in playlists:
                playlist_item = QStandardItem(playlist.title)
                model.appendRow(playlist_item)
        self.combo.setModel(model)

    def populate_tree(self):
        self.tree.clear()
        current_playlist = self.combo.currentText()
        if current_playlist in self.playlists["audio"]:
            self.populate_audio_playlist_tree(current_playlist)
        elif current_playlist in self.playlists["video"]:
            self.populate_video_playlist_tree(current_playlist)
        elif current_playlist in self.playlists["photo"]:
            self.populate_photo_playlist_tree(current_playlist)

    def populate_audio_playlist_tree(self, playlist):
        playlist_data = self.playlist_data_dict(playlist)
        if not playlist_data:
            return

        for artist, albums in playlist_data[playlist.title].items():
            artist_item = QTreeWidgetItem([artist])
            for album, tracks in albums.items():
                album_item = QTreeWidgetItem([album])
                for track in tracks:
                    track_item = QTreeWidgetItem(
                        [track[1]]
                    )  # assuming track is a tuple (track_number, track_name)
                    album_item.addChild(track_item)
                artist_item.addChild(album_item)
            self.tree.addTopLevelItem(artist_item)

    def populate_video_playlist_tree(self, playlist):
        # TODO: Implement this method
        pass

    def populate_photo_playlist_tree(self, playlist):
        # TODO: Implement this method
        pass

import os

from PyQt6.QtGui import QIcon, QPixmap, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class PlaylistGUI(QMainWindow):
    RESOURCES_PATH = "src/plex_playlist_manager/resources/"

    def __init__(self, plex_server):
        super().__init__()
        self.plex_server = plex_server
        self.playlists = self.get_playlists()
        self.playlist_audio_data = self.get_playlist_audio_data()

        # Create the buttons
        self.audio_button = QPushButton("Audio")
        self.audio_button.setCheckable(True)
        self.audio_button.setChecked(True)  # Set the audio button to be checked by default
        self.audio_button.clicked.connect(self.update_playlist_list)

        self.video_button = QPushButton("Video")
        self.video_button.setCheckable(True)
        self.video_button.clicked.connect(self.update_playlist_list)

        self.photo_button = QPushButton("Photo")
        self.photo_button.setCheckable(True)
        self.photo_button.clicked.connect(self.update_playlist_list)

        # Create a button group and add the buttons to it
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.audio_button)
        self.button_group.addButton(self.video_button)
        self.button_group.addButton(self.photo_button)
        self.button_group.setExclusive(True)  # Make the buttons in the group exclusive

        # Create a vertical layout and add the buttons to it
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.audio_button)
        button_layout.addWidget(self.video_button)
        button_layout.addWidget(self.photo_button)
        button_layout.addStretch(1)  # Add a stretchable space to the bottom of the layout

        # Create the playlist list title
        self.playlist_list_title = QLabel("Playlists")

        # Create the playlist list
        self.playlist_list = QListWidget()
        self.playlist_list.itemClicked.connect(self.update_playlist_contents)

        # Populate the list with audio playlists
        self.populate_audio_playlist_list()

        # Create a vertical layout and add the title and the list to it
        list_layout = QVBoxLayout()
        list_layout.addWidget(self.playlist_list_title)
        list_layout.addWidget(self.playlist_list)

        # Create the playlist contents title
        self.playlist_contents_title = QLabel("Playlist Contents")

        # Create the playlist contents tree
        self.playlist_contents_tree = QTreeWidget()
        self.playlist_contents_tree.setHeaderHidden(True)

        # Create a vertical layout and add the title and the tree to it
        tree_layout = QVBoxLayout()
        tree_layout.addWidget(self.playlist_contents_title)
        tree_layout.addWidget(self.playlist_contents_tree)

        # Create a horizontal layout and add the button layout, the list layout, and the tree layout to it
        layout = QHBoxLayout()
        layout.addLayout(button_layout)
        layout.addLayout(list_layout)
        layout.addLayout(tree_layout)

        # Set the stretch factors
        layout.setStretch(0, 1)  # button_layout
        layout.setStretch(1, 1)  # list_layout
        layout.setStretch(2, 2)  # tree_layout

        # Create a vertical layout for the combo box and the horizontal layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Main window setup
        # Set window size
        self.resize(800, 600)

        # Set window title
        self.setWindowTitle("Plex Playlist GUI")

        # Set window icon (assuming you have an icon file named 'icon.png' in the same directory)
        icon_path = PlaylistGUI.RESOURCES_PATH + "icons/plex_icon.png"
        print(f"Icon path: {icon_path}")
        self.setWindowIcon(QIcon(icon_path))

    def get_playlist_audio_data(self):
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

        return all_playlist_data

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

    def update_playlist_list(self):
        # Clear the list
        self.playlist_list.clear()

        # Check which button is checked and update the list accordingly
        if self.sender() == self.audio_button and self.audio_button.isChecked():
            self.populate_audio_playlist_list()
        elif self.sender() == self.video_button and self.video_button.isChecked():
            self.populate_video_playlist_list()
        elif self.sender() == self.photo_button and self.photo_button.isChecked():
            self.populate_photo_playlist_list()

    def update_playlist_contents(self, item):
        # Get the playlist title from the clicked item
        playlist_title = item.text()

        # Clear the tree
        self.playlist_contents_tree.clear()

        # Check which button is checked and update the tree accordingly
        if self.audio_button.isChecked():
            contents = self.playlist_audio_data.get(playlist_title, {})
            # Populate the tree with the contents of the playlist
            for artist, albums in contents.items():
                artist_item = QTreeWidgetItem(self.playlist_contents_tree)
                artist_item.setText(0, artist)
                for album, tracks in albums.items():
                    album_item = QTreeWidgetItem(artist_item)
                    album_item.setText(0, album)
                    for track_number, track in tracks:
                        track_item = QTreeWidgetItem(album_item)
                        track_item.setText(0, f"{track_number}. {track}")
        elif self.video_button.isChecked():
            # Populate the tree with dummy video playlist contents
            video_item = QTreeWidgetItem(self.playlist_contents_tree)
            video_item.setText(0, "Video1")
            video_item = QTreeWidgetItem(self.playlist_contents_tree)
            video_item.setText(0, "Video2")
            video_item = QTreeWidgetItem(self.playlist_contents_tree)
            video_item.setText(0, "Video3")
        elif self.photo_button.isChecked():
            # Populate the tree with dummy photo playlist contents
            photo_item = QTreeWidgetItem(self.playlist_contents_tree)
            photo_item.setText(0, "Photo1")
            photo_item = QTreeWidgetItem(self.playlist_contents_tree)
            photo_item.setText(0, "Photo2")
            photo_item = QTreeWidgetItem(self.playlist_contents_tree)
            photo_item.setText(0, "Photo3")

    def populate_audio_playlist_list(self):
        # Populate the list with audio playlists
        for playlist in self.playlists["audio"]:
            self.playlist_list.addItem(playlist.title)

    def populate_video_playlist_list(self):
        # Populate the list with video playlists
        for playlist in self.playlists["video"]:
            self.playlist_list.addItem(playlist.title)

    def populate_photo_playlist_list(self):
        # Populate the list with photo playlists
        for playlist in self.playlists["photo"]:
            self.playlist_list.addItem(playlist.title)

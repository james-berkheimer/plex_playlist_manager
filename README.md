# Plex Playlist Manager

This project is a web application providing a more robust method for managing playlists
on a Plex media server. It is built with Python and Flask, and uses the Plex API
to interact with the Plex server.

## Features

- **Playlist Organization**: The application categorizes playlists into their tree base hierarchy. This is in contrast to the Plex app method of listing an unsorted list of tracks, episodes, and movies. The hierarchy is organized as follows:

    ```
    └── playlist_type/
        └── playlist/
            ├── artist/
            │   └── album/
            │       └── song
            ├── show/
            │   └── season/
            │       └── episode
            ├── movie
            └── photo
    ```
- **Playlist Modification**: *NOT YET IMPLIMENTED* Allow the user to remove from, add to, and create Plex playlists

- **Authentication**: The application authenticates with the Plex server using the `PlexAuthentication` class in `src/plex_playlist_manager/plex/authentication.py`.

- **Web Interface**: The application provides a web interface for users to interact with their playlists. This is done using Flask and the templates in `src/plex_playlist_manager/templates/`.

## Running the Application

*NOT YET IMPLIMENTED*

The design goal is for this app to be run locally with installers created to work with most of the currently available platforms.
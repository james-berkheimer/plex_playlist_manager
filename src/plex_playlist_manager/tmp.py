#     for artist in playlist_data[playlist.title]:
#         print(f"\t{artist}")
#         for album in playlist_data[playlist.title][artist]:
#             print(f"\t\t{album}")
#             for track in playlist_data[playlist.title][artist][album]:
#                 print(f"\t\t\t{track[0]}: {track[1]}")

# for artist in playlist_data["Test"]:
#     print(artist)
#     for album in playlist_data["Test"][artist]:
#         print(f"\t{album}")
#         for track in playlist_data["Test"][artist][album]:
#             print(f"\t\t{track[0]}: {track[1]}")

# test_playlist = next((playlist for playlist in playlists if playlist.title == "Test"), None)
# playlist_data = playlist_data_dict(test_playlist)
# for artist in playlist_data["Test"]:
#     print(artist)
#     for album in playlist_data["Test"][artist]:
#         print(f"\t{album}")
#         for track in playlist_data["Test"][artist][album]:
#             print(f"\t\t{track[0]}: {track[1]}")

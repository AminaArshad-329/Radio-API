from django.urls import path
from .views import UploadCSVFileView, DownloadLogsView, DownloadPlaylistView
from . import views

urlpatterns = [
    path("hello/", views.hello, name="hello"),
    path("get_songs_data/", views.get_songs_data, name="get_songs_data"),
    path("get_file_name/", views.get_file_name, name="get_file_name"),
    # path("artist_bar_chart/", views.artist_bar_chart, name="artist_bar_chart"),
    path("upload_csv_file/", UploadCSVFileView.as_view(), name="upload_csv_file"),
    path("download-logs/", DownloadLogsView.as_view(), name="download_logs"),
    path("download-playlist/", DownloadPlaylistView.as_view(), name="download_playlist"),
    # path(
    #     "volume_added_overtime/",
    #     views.volume_added_overtime,
    #     name="volume_added_overtime",
    # ),
    path("analyse_csv/", views.analyse_csv, name="analyse_csv"),
]

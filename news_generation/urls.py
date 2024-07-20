from django.urls import path

from .views import GenerateAIStoryView, GenerateStoryFromInputView, ExportPlaylistView, VoicesView

urlpatterns = [
    path('generate_news_ai', GenerateAIStoryView.as_view(), name='generate_news_ai'),
    path('generate_news_from_script', GenerateStoryFromInputView.as_view(), name='generate_news_from_script'),
    path('export_playlist', ExportPlaylistView.as_view(), name='export_playlist'),
    path('get_voices', VoicesView.as_view(), name='get_voices'),
]

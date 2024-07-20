from rest_framework import serializers


class NewsGenerationSerializer(serializers.Serializer):
    stories = serializers.IntegerField(required=True)
    voice = serializers.CharField(required=True)
    newsbed = serializers.BooleanField(required=True)
    separator = serializers.BooleanField(required=True)


class AudioGenerationSerializer(serializers.Serializer):
    voice = serializers.CharField(required=True)
    script = serializers.CharField(required=True)


class ExportPlaylistSerializer(serializers.Serializer):
    files = serializers.ListField(child=serializers.FileField(allow_empty_file=False), required=True)
    audios = serializers.FileField(required=False)
    newsbed = serializers.BooleanField(required=True)
    separator = serializers.BooleanField(required=True)

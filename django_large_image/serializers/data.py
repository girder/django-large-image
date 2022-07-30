from rest_framework import serializers


class PixelSerializer(serializers.Serializer):
    r = serializers.IntegerField(
        help_text='Red channel',
        min_value=0,
        max_value=255,
        read_only=True,
    )
    g = serializers.IntegerField(
        help_text='Green channel',
        min_value=0,
        max_value=255,
        read_only=True,
    )
    b = serializers.IntegerField(
        help_text='Blue channel',
        min_value=0,
        max_value=255,
        read_only=True,
    )
    a = serializers.IntegerField(
        help_text='Alpha channel',
        min_value=0,
        max_value=255,
        read_only=True,
    )
    bands = serializers.DictField(
        child=serializers.FloatField(),
        help_text='Pixel data for each band',
        read_only=True,
    )


class HistogramSerializer(serializers.Serializer):
    pass

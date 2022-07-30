from rest_framework import serializers


class MetaDataSerializer(serializers.Serializer):
    pass


class MetaDataInternalSerializer(serializers.Serializer):
    pass


class BandSerializer(serializers.Serializer):
    min = serializers.FloatField(
        help_text='Minimum value',
        read_only=True,
        allow_null=True,
    )
    max = serializers.FloatField(
        help_text='Maximum value',
        read_only=True,
        allow_null=True,
    )
    stdev = serializers.FloatField(
        help_text='Standard deviation value',
        read_only=True,
        allow_null=True,
    )
    interpretation = serializers.CharField(
        help_text='interpretation of band/channel',
        read_only=True,
    )


class BandsSerializer(serializers.Serializer):
    bands = serializers.DictField(
        child=BandSerializer(),
    )


class FramesSerializer(serializers.Serializer):
    pass


class TiffdumpSerializer(serializers.Serializer):
    pass

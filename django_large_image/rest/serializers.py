from rest_framework import serializers


class TileMetadataSerializer(serializers.Serializer):

    levels = serializers.IntegerField(
        help_text='Number of zoom levels in the image.',
        min_value=1,
        read_only=True,
    )
    size_x = serializers.IntegerField(
        help_text='Image size in the X direction.',
        min_value=1,
        read_only=True,
        source='sizeX',
    )
    size_y = serializers.IntegerField(
        help_text='Image size in the Y direction.',
        min_value=1,
        read_only=True,
        source='sizeY',
    )
    tile_size = serializers.IntegerField(
        help_text='Size of the square tiles the image is composed of.',
        min_value=1,
        read_only=True,
        source='tileWidth',
    )
    geospatial = serializers.BooleanField(
        help_text='Whether the tile source is geospatial',
        read_only=True,
        source='dli_geospatial',
    )
    additional_metadata = serializers.JSONField(
        help_text='Any additional metadata on the tile source.',
        read_only=True,
        source='getMetadata',
    )

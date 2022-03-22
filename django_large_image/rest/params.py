from drf_yasg import openapi

z_param = openapi.Parameter(
    'z', openapi.IN_PATH, description='zoom level', type=openapi.TYPE_INTEGER
)
x_param = openapi.Parameter('x', openapi.IN_PATH, description='x', type=openapi.TYPE_INTEGER)
y_param = openapi.Parameter('y', openapi.IN_PATH, description='y', type=openapi.TYPE_INTEGER)
band_param = openapi.Parameter(
    'band', openapi.IN_PATH, description='band index', type=openapi.TYPE_INTEGER
)
left_param = openapi.Parameter(
    'left', openapi.IN_PATH, description='left', type=openapi.TYPE_NUMBER
)
right_param = openapi.Parameter(
    'right', openapi.IN_PATH, description='right', type=openapi.TYPE_NUMBER
)
top_param = openapi.Parameter('top', openapi.IN_PATH, description='top', type=openapi.TYPE_NUMBER)
bottom_param = openapi.Parameter(
    'bottom', openapi.IN_PATH, description='bottom', type=openapi.TYPE_NUMBER
)

from webplotlib.chart_builders import create_chart_as_png_str
chart_png_str = create_chart_as_png_str(
    'timeseries',
    {'data': [[1, 2, 3, 4]], 'names': 'MyDataLine'},
    labels_dct={'title': 'TheBigBoard', 'x': 'Data', 'y': 'Value'})

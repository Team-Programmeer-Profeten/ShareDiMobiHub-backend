import os
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, LabelSet, FactorRange
from bokeh.io import export_svgs
from bokeh.palettes import Category20
from datetime import datetime
from bokeh.transform import cumsum, factor_cmap
from bokeh.palettes import Viridis6 as palette

from math import pi

dir_path = os.path.dirname(os.path.realpath(__file__))
graph_path = os.path.join(dir_path, 'utils', 'graphs', 'SVG_')

def barchart_vertical(categories, data, width, height, name, x_axis_label, y_axis_label):
  color = colors(len(categories))
  source = ColumnDataSource(data=dict(x=categories, y=data, color=color))
  p = figure(x_range=categories, width=width, height=height, background_fill_color=None, border_fill_color=None)
  p.vbar(x="x", top="y", color="color", width=0.9, source=source)
  
  labels = LabelSet(x='x', y='y', text='y', level='glyph', text_font_size='8px', text_color='#0A1A29', y_offset=-20, source=source)
  p.add_layout(labels)

  p.xaxis.axis_label = x_axis_label
  p.yaxis.axis_label = y_axis_label

  p.xaxis.axis_label_text_font = "Poppins"
  p.xaxis.axis_label_text_color = "#0A1A29"
  p.yaxis.axis_label_text_font = "Poppins"
  p.yaxis.axis_label_text_color = "#0A1A29"

  p.output_backend = "svg"
  export_svgs(p, filename = graph_path + name + '.svg')

def barchart_horizontal(categories, data, width, height, name, y_axis_label):
  color = colors(len(categories))
  source = ColumnDataSource(data=dict(x=data, y=categories, color=color))
  p = figure(y_range=categories, width=width, height=height, background_fill_color=None, border_fill_color=None)
  p.hbar(y="y", right="x", color="color", height=0.9, source=source)
  
  labels = LabelSet(x='x', y='y', text='x', level='glyph', text_font_size='10px', text_color='#0A1A29', x_offset=-50, source=source)
  p.add_layout(labels)

  p.xaxis.axis_label = y_axis_label

  p.xaxis.axis_label_text_font = "Poppins"
  p.xaxis.axis_label_text_color = "#0A1A29"

  p.output_backend = "svg"
  export_svgs(p, filename = graph_path + name + '.svg')

def linechart(x, y, width, height, name, x_axis_label, y_axis_label):
  x = [datetime.strptime(date, '%Y-%m-%d %H:%M:%S%z') for date in x]

  p = figure(width=width, height=height, x_axis_type="datetime", background_fill_color=None, border_fill_color=None)
  p.line(x, y, line_width = 2)

  p.xaxis.axis_label = x_axis_label
  p.yaxis.axis_label = y_axis_label

  p.output_backend = "svg"
  export_svgs(p, filename = graph_path + name + '.svg')


def multi_linechart(data, width, height, name):
    x = data.pop("x")

    x = [datetime.strptime(date, '%Y-%m-%d %H:%M:%S%z') for date in x]


    # you can use another bokeh pallete here as long as it has enough colors
    colors = list(Category20[len(data)])
    
    p = figure(width=width, height=height, x_axis_type="datetime", background_fill_color=None, border_fill_color=None)  # Set x_axis_type to "datetime"

    for key, value in data.items():
      p.line(x, value, line_width = 2, legend_label=key, color=colors.pop())

    p.add_layout(p.legend[0], 'right')
    p.legend.background_fill_alpha = 0
    p.legend.border_line_color = None

    p.output_backend = "svg"
    export_svgs(p, filename=graph_path + name + '.svg')
    

def multi_barchart(data, width, height, name, x_axis_label, y_axis_label):
    dates = list(data.keys())
    companies = list(data[next(iter(data))].keys())
    palette_cycle = multi_bar_colors(len(companies))

    # Transform data for grouped bars
    x = [(date, company) for date in dates for company in companies]
    counts = [data[date][company] for date, company in x]

    source = ColumnDataSource(data=dict(x=x, counts=counts))

    p = figure(x_range=FactorRange(*x), width=width, height=height, toolbar_location=None, tools="", background_fill_color=None, border_fill_color=None)

    p.vbar(x='x', top='counts', width=0.9, source=source,
          line_color="white", fill_color=factor_cmap('x', palette=palette_cycle, factors=companies, start=1, end=2))

    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None

    p.xaxis.axis_label = x_axis_label
    p.yaxis.axis_label = y_axis_label

    p.output_backend = "svg"
    export_svgs(p, filename=graph_path + name + '.svg')


def piechart(data_dict, width, height, name):
    categories = list(data_dict.keys())
    data = list(data_dict.values())
    color = pie_colors(len(categories))

    data_dict = {'category': [f'{cat} ({val})' for cat, val in zip(categories, data)], 'value': data, 'angle': [value/sum(data) * 2*pi for value in data], 'color': color}
    source = ColumnDataSource(data=data_dict)

    p = figure(height=height, width=width, toolbar_location=None, tools="hover", tooltips="@category: @value", x_range=(-0.5, 1.0), background_fill_color=None, border_fill_color=None, outline_line_color=None)

    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='category', source=source)

    p.legend.location = "center_right"
    p.legend.padding = -10
    p.legend.background_fill_alpha = 0

    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None

    p.output_backend = "svg"
    export_svgs(p, filename = graph_path + name + '.svg')

def colors(length):
  colors = ["#f8a931", "#c0cccd", "#43bac3", "#31313d"]
  palette = colors
  while len(palette) < length:
    palette += colors
  return palette[0:length]

def pie_colors(length):
  colors = ["#f8a931", "#c0cccd", "#43bac3", "#31313d", "#3A8DDE", "#DE443A", "#65DE3A", "#BFC217"]
  palette = colors
  while len(palette) < length:
    palette += colors
  return palette[0:length]

def multi_bar_colors(length):
  colors = ["#43bac3", "#f8a931", "#31313d", "#2B5F3C", "#3A8DDE", "#DE443A"]
  palette = colors
  while len(palette) < length:
    palette += colors
  return palette[0:length]
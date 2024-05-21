from bokeh.plotting import figure, save
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.models import ColumnDataSource


def barchart_vertical(categories, data, width, height):
  color = colors(len(categories))
  source = ColumnDataSource(data=dict(x=categories, y=data, color=color))
  p = figure(x_range=categories, width=width, height=height)
  p.vbar(x="x", top="y", color="color", width=0.9, legend_field="x", source=source)
  return p

def barchart_horizontal(categories, data, width, height):
  color = colors(len(categories))
  source = ColumnDataSource(data=dict(x=data, y=categories, color=color))
  p = figure(y_range=categories, width=width, height=height)
  p.hbar(y="y", right="x", color="color", height=0.9, legend_field="y", source=source)
  return p

def colors(length):
  colors = ["#f8a931", "#c0cccd", "#43bac3", "#31313d"]
  palette = colors
  while len(palette) < length:
    palette += colors
  return palette[0:length]
  


# voertuigen = ["fiets", "auto", "brommer", "a", "b", "c"]
# data = [5, 3, 4, 2, 7, 4]
# save(barchart_horizontal(voertuigen, data, 800, 300))
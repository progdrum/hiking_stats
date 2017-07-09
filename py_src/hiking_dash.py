from datetime import datetime

import pandas as pd
import pymongo as pm
import update_functions as ufunc
from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import RadioGroup, PreText
from bokeh.plotting import figure

from process_trail_data import HikingProcess

# Process the data
hp = HikingProcess()
hp.read_and_store_mongo()

# Connect to the DB to retrieve data
client = pm.MongoClient("localhost", 27017)
db = client["trail_data"]
trail_stats = db["stats"]

def change_data_set(new):
    """
    Update function for the radio button data-changer

    :param new: The new selection to apply
    """
    if new == 1:
        new_records = list(trail_stats.find({'Solo': True}))
        distance_counts, _ = ufunc.update_distances(new_records)
        new_title = "Distribution of Distances for Solo Hikes"
        new_stats = ufunc.update_stats_box(pd.DataFrame(new_records))
    elif new == 2:
        new_records = list(trail_stats.find({'Solo': False}))
        distance_counts, _ = ufunc.update_distances(new_records)
        new_title = "Distribution of Distances for Group Hikes"
        new_stats = ufunc.update_stats_box(pd.DataFrame(new_records))
    elif new == 3:
        new_records = list(trail_stats.find({'After Work': True}))
        distance_counts, _ = ufunc.update_distances(new_records)
        new_title = "Distribution of Distances for After Work Hikes"
        new_stats = ufunc.update_stats_box(pd.DataFrame(new_records))
    else:
        new_records = list(trail_stats.find())
        distance_counts, _ = ufunc.update_distances(new_records)
        new_title = "Distribution of Distances for All Hikes"
        new_stats = ufunc.update_stats_box(pd.DataFrame(new_records))

    dist_source.data = dict(bins=distance_bins, counts=distance_counts)
    distances.title.text = new_title
    stats_box.text = new_stats
    lg_source.data = ufunc.update_line_graphs(new_records)


def selection_change(attrname, old, new):
    """
    Make changes to the data when a selection is made.

    :param attrname: Name of attribute
    :param old: Old data
    :param new: New data
    """
    print(attrname)
    print(old)
    print(new)


# Get a distribution plot together for distances
distances = figure(plot_height=300, plot_width=800,
                   title="Distribution of Distances for All Hikes")
distance_counts, distance_bins = ufunc.update_distances(list(trail_stats.find()))
dist_source = ColumnDataSource(data=dict(bins=distance_bins, counts=distance_counts))
distances.vbar(x='bins', bottom=0, top='counts', width=0.5, source=dist_source)

# Set up the radio buttons for switching between data sets
buttons = RadioGroup(labels=['All', 'Solo', 'Group', 'After Work'], active=0)
buttons.on_click(change_data_set)

# Read trail stats into pandas dataframe for text description
ts_frame = pd.DataFrame(list(trail_stats.find()))
stats_box = PreText(name="Summary", text=ts_frame.describe().to_string(), width=1200)

# Data source for all line_graphs
lg_source = ColumnDataSource(data=dict(distances=[trail['Distance'] for trail in list(trail_stats.find())],
                                       dates=sorted([datetime.strptime(trail['Date'], '%Y/%m/%d %H:%M')
                                              for trail in list(trail_stats.find())]),
                                       energy=[trail['Energy'] for trail in list(trail_stats.find())],
                                       min_altitude=[trail['Min altitude'] for trail in list(trail_stats.find())],
                                       max_altitude=[trail['Max altitude'] for trail in list(trail_stats.find())]))
lg_source.on_change('selected', selection_change)

# Line graphs for everything!
tools = 'pan,wheel_zoom,xbox_select,reset'
dist_time = figure(title="Distance vs. Time",
                   plot_height=250,
                   plot_width=1200,
                   x_axis_type='datetime',
                   tools=tools,
                   active_drag='xbox_select')
dist_time.line(x='dates', y='distances',
               source=lg_source,
               line_width=2,
               color='darkslategray')
dist_time.circle(x='dates', y='distances',
                 source=lg_source,
                 color='darkslategray',
                 selection_color='orange')
energy_time = figure(title="Energy vs. Time",
                     plot_height=250,
                     plot_width=1200,
                     x_axis_type='datetime',
                     tools=tools,
                     active_drag='xbox_select')
energy_time.x_range = dist_time.x_range
energy_time.line(x='dates', y='energy',
                 source=lg_source,
                 line_width=2,
                 color='firebrick')
energy_time.circle(x='dates', y='energy',
                   source=lg_source,
                   color='firebrick',
                   selection_color='orange')
altitudes = figure(title="Minimum/Maximum Altitude Over Time",
                   plot_height=250,
                   plot_width=1200,
                   x_axis_type='datetime',
                   tools=tools,
                   active_drag='xbox_select')
altitudes.x_range = dist_time.x_range
altitudes.line(x='dates', y='min_altitude',
               source=lg_source,
               line_width=2,
               color='violet')
altitudes.line(x='dates', y='max_altitude',
               source=lg_source,
               line_width=2,
               color='navy')
altitudes.circle(x='dates', y='min_altitude',
                 source=lg_source,
                 color='violet',
                 selection_color='orange')
altitudes.circle(x='dates', y='max_altitude',
                 source=lg_source,
                 color='navy',
                 selection_color='orange')

# Layouts
butt_overview = row(buttons, distances)
sbox = row(stats_box)
line_graphs = column(dist_time, energy_time, altitudes)

curdoc().add_root(column(butt_overview, sbox, line_graphs))

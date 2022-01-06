import pandas as pd
import datetime as dt
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models import CategoricalColorMapper
from bokeh.palettes import Spectral6
from bokeh.layouts import widgetbox, row, gridplot
from bokeh.models import DateRangeSlider, Select
from bokeh.models.widgets import Tabs, Panel

data = pd.read_csv('data/covid-variants.csv')
data['date']= pd.to_datetime(data['date']).dt.date


locations = data[['location','date','num_sequences', 'perc_sequences','num_sequences_total']].groupby(['location', 'date']).sum().reset_index()
ints = locations['location'].value_counts().sort_index().index.tolist()

variants = data[['variant','date','num_sequences', 'perc_sequences','num_sequences_total']].groupby(['variant', 'date']).sum().reset_index()
ints2 = variants['variant'].value_counts().sort_index().index.tolist()

source = ColumnDataSource(data={
    'location': locations[locations['location'] == 'Indonesia']['location'],
    'date': locations[locations['location'] == 'Indonesia']['date'],
    'num_sequences': locations[locations['location'] == 'Indonesia']['num_sequences'],
    'perc_sequences': locations[locations['location'] == 'Indonesia']['perc_sequences'],
    'num_sequences_total': locations[locations['location'] == 'Indonesia']['num_sequences_total'],
})

sourceVariant = ColumnDataSource(data={
    'variant': variants[variants['variant'] == 'Omicron']['variant'],
    'date': variants[variants['variant'] == 'Omicron']['date'],
    'num_sequences': variants[variants['variant'] == 'Omicron']['num_sequences'],
    'perc_sequences': variants[variants['variant'] == 'Omicron']['perc_sequences'],
    'num_sequences_total': variants[variants['variant'] == 'Omicron']['num_sequences_total'],
})

tooltips_location = [
            ('Location', '@location'),
            ('Date', '@date{%F}'),
            ('Num Sequences', '@num_sequences'),
            ('Perc Sequences', '@perc_sequences'),  
            ('Num Sequences Total', '@num_sequences_total'),  
           ]

tooltips_variant = [
            ('Variant', '@variant'),
            ('Date', '@date{%F}'),
            ('Num Sequences', '@num_sequences'),
            ('Perc Sequences', '@perc_sequences'),  
            ('Num Sequences Total', '@num_sequences_total'),  
           ]

fig_location = figure(x_axis_type='datetime',plot_height=500, plot_width=1000,title='location',x_axis_label='Date')
fig_location.add_tools(HoverTool(tooltips=tooltips_location, formatters={'@date': 'datetime'}))
fig_location.line('date', 'num_sequences', color='red', source=source, legend_label="Num Sequences", line_width = 2)
fig_location.line('date', 'perc_sequences', color='green', source=source, legend_label="Perc Sequences", line_width = 2)
fig_location.line('date', 'num_sequences_total', color='blue', source=source, legend_label="Num Sequences Total", line_width = 2)

fig_variant = figure(x_axis_type='datetime',plot_height=500, plot_width=1000,title='COVID Variants',x_axis_label='Date')
fig_variant.add_tools(HoverTool(tooltips=tooltips_variant, formatters={'@date': 'datetime'}))
fig_variant.line('date', 'num_sequences', color='red', source=sourceVariant, legend_label="Num Sequences", line_width = 2)

# fig_location.vbar('date', 'num_sequences', legend_label="Num Sequences", width=0.5, bottom=0, color="red")

def update_location(attr, old, new):

    [start, end] = slider.value
    date_from = dt.datetime.fromtimestamp(start/1000.0).date()
    date_until = dt.datetime.fromtimestamp(end/1000.0).date()

    location_cd = str(location_select.value)

    # new data
    location_date = locations[(locations['date'] >= date_from) & (locations['date'] <= date_until)]
    new_data = {
        'location': location_date[location_date['location'] == location_cd]['location'],
        'date': location_date[location_date['location'] == location_cd]['date'],
        'num_sequences': location_date[location_date['location'] == location_cd]['num_sequences'],
        'perc_sequences': location_date[location_date['location'] == location_cd]['perc_sequences'],
        'num_sequences_total': location_date[location_date['location'] == location_cd]['num_sequences_total'],
    }
    source.data = new_data

init_value = (data['date'].min(), data['date'].max())
slider = DateRangeSlider(start=init_value[0], end=init_value[1], value=init_value)
slider.on_change('value',update_location)

location_select = Select(
    options= [str(x) for x in ints],
    value= 'Indonesia',
    title='Location'
)
location_select.on_change('value', update_location)

def update_variant(attr, old, new):

    [start, end] = slider.value
    date_from = dt.datetime.fromtimestamp(start/1000.0).date()
    date_until = dt.datetime.fromtimestamp(end/1000.0).date()

    variant_cd = str(variant_select.value)

    # new data
    variant_date = variants[(variants['date'] >= date_from) & (variants['date'] <= date_until)]
    new_data = {
        'variant': variant_date[variant_date['variant'] == variant_cd]['variant'],
        'date': variant_date[variant_date['variant'] == variant_cd]['date'],
        'num_sequences': variant_date[variant_date['variant'] == variant_cd]['num_sequences'],
        'perc_sequences': variant_date[variant_date['variant'] == variant_cd]['perc_sequences'],
        'num_sequences_total': variant_date[variant_date['variant'] == variant_cd]['num_sequences_total'],
    }
    sourceVariant.data = new_data

variant_select = Select(
    options= [str(x) for x in ints2],
    value= 'Omicron',
    title='Variant'
)
variant_select.on_change('value', update_variant)


layout = row(widgetbox(location_select, slider), fig_location)
layout2 = row(widgetbox(variant_select), fig_variant)

panel1 = Panel(child=layout, title='Tracking COVID Cases')
panel2 = Panel(child=layout2, title='COVID Variants Cases')


tabs = Tabs(tabs=[panel1,panel2])

curdoc().add_root(tabs)
curdoc().title = "Visualisasi COVID"
# curdoc().theme = 'dark_minimal'
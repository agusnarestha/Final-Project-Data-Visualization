#Import Library
import pandas as pd
import datetime as dt
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models import CategoricalColorMapper
from bokeh.palettes import Category20b, Spectral6, magma
from bokeh.layouts import widgetbox, row, gridplot
from bokeh.models import DateRangeSlider, Select
from bokeh.models.widgets import Tabs, Panel
from bokeh.transform import factor_cmap

#Membaca dataset
data = pd.read_csv('app/data/covid-variants.csv')
data['date']= pd.to_datetime(data['date']).dt.date

#Grouping Data Berdasarkan Location dan Date
locations = data[['location','date','num_sequences', 'perc_sequences','num_sequences_total']].groupby(['location', 'date']).sum().reset_index()
list_location = locations['location'].value_counts().sort_index().index.tolist()

#Grouping Data Berdasarkan Variant dan Date
variants = data[['variant','date','num_sequences', 'perc_sequences','num_sequences_total']].groupby(['variant', 'date']).sum().reset_index()
list_variant = variants['variant'].value_counts().sort_index().index.tolist()

#Grouping Data Berdasarkan Location dan Variant
covidperloc = data[['location','variant','date','num_sequences', 'perc_sequences','num_sequences_total']].groupby(['location', 'variant']).sum().reset_index()
list_covidperloc = covidperloc['location'].value_counts().sort_index().index.tolist()

#Data untuk Location
sourceLocation = ColumnDataSource(data={
    'location': locations[locations['location'] == 'Indonesia']['location'],
    'date': locations[locations['location'] == 'Indonesia']['date'],
    'num_sequences': locations[locations['location'] == 'Indonesia']['num_sequences'],
    'perc_sequences': locations[locations['location'] == 'Indonesia']['perc_sequences'],
    'num_sequences_total': locations[locations['location'] == 'Indonesia']['num_sequences_total'],
})

#Data untuk Variant COVID
sourceVariant = ColumnDataSource(data={
    'variant': variants[variants['variant'] == 'Omicron']['variant'],
    'date': variants[variants['variant'] == 'Omicron']['date'],
    'num_sequences': variants[variants['variant'] == 'Omicron']['num_sequences'],
    'perc_sequences': variants[variants['variant'] == 'Omicron']['perc_sequences'],
    'num_sequences_total': variants[variants['variant'] == 'Omicron']['num_sequences_total'],
})

#Data untuk COVID per Location
sourceCovidperLoc = ColumnDataSource(data=dict(variant=covidperloc[covidperloc['location'] == 'Indonesia']['variant'], counts=covidperloc[covidperloc['location'] == 'Indonesia']['num_sequences'], color=magma(24)))

#Tooltips untuk Figure Location
tooltips_location = [
    ('Location', '@location'),
    ('Date', '@date{%F}'),
    ('Num Sequences', '@num_sequences'),
    ('Perc Sequences', '@perc_sequences'),  
    ('Num Sequences Total', '@num_sequences_total'),  
]

#Tooltips untuk Figure Variant COVID
tooltips_variant = [
    ('Variant', '@variant'),
    ('Date', '@date{%F}'),
    ('Num Sequences', '@num_sequences'),
    ('Perc Sequences', '@perc_sequences'),  
    ('Num Sequences Total', '@num_sequences_total'),  
]

#Tooltips untuk Figure Covid per Location
tooltips_covidperloc = [
    ('Variant', '@variant'),
    ('Num Sequences', '@counts'),
]

#Membuat Figure Location
fig_location = figure(x_axis_type='datetime',plot_height=500, plot_width=1000,x_axis_label='Date', title='Kasus COVID di Indonesia per Mei 2020 - Desember 2021')
fig_location.add_tools(HoverTool(tooltips=tooltips_location, formatters={'@date': 'datetime'}))
fig_location.line('date', 'num_sequences', color='red', source=sourceLocation, legend_label="Num Sequences", line_width = 2)
fig_location.line('date', 'perc_sequences', color='green', source=sourceLocation, legend_label="Perc Sequences", line_width = 2)
fig_location.line('date', 'num_sequences_total', color='blue', source=sourceLocation, legend_label="Num Sequences Total", line_width = 2)
fig_location.add_layout(fig_location.legend[0], 'right')

#Membuat Figure Variant COVID
fig_variant = figure(x_axis_type='datetime',plot_height=500, plot_width=1000,title='Variant COVID Omicron di Seluruh Dunia per Mei 2020 - Desember 2021',x_axis_label='Date')
fig_variant.add_tools(HoverTool(tooltips=tooltips_variant, formatters={'@date': 'datetime'}))
fig_variant.line('date', 'num_sequences', color='red', source=sourceVariant, legend_label="Num Sequences", line_width = 2)
fig_variant.add_layout(fig_variant.legend[0], 'right')

#Membuat Figure Covid per Location
fig_covidperloc = figure(x_range=list_variant,plot_height=800, plot_width=1600,title='Kasus Variant COVID di Indonesia per Mei 2020 - Desember 2021',x_axis_label='Variant')
fig_covidperloc.add_tools(HoverTool(tooltips=tooltips_covidperloc))
fig_covidperloc.vbar(x='variant',top ='counts',width = 0.5, source=sourceCovidperLoc, color='color', legend_field="variant")
fig_covidperloc.add_layout(fig_covidperloc.legend[0], 'right')

#Procedure untuk update figure location
def update_location(attr, old, new):
    #Slider date
    [start, end] = slider.value
    date_from = dt.datetime.fromtimestamp(start/1000.0).date()
    date_until = dt.datetime.fromtimestamp(end/1000.0).date()

    #Menampung value location yang dipilih
    location_new = str(location_select.value)

    #Menampung data terbaru
    location_date = locations[(locations['date'] >= date_from) & (locations['date'] <= date_until)]
    new_data = {
        'location': location_date[location_date['location'] == location_new]['location'],
        'date': location_date[location_date['location'] == location_new]['date'],
        'num_sequences': location_date[location_date['location'] == location_new]['num_sequences'],
        'perc_sequences': location_date[location_date['location'] == location_new]['perc_sequences'],
        'num_sequences_total': location_date[location_date['location'] == location_new]['num_sequences_total'],
    }
    sourceLocation.data = new_data
    fig_location.title.text = 'Kasus COVID di ' +location_select.value+ ' per Mei 2020 - Desember 2021'

#Slider date
init_value = (data['date'].min(), data['date'].max())
slider = DateRangeSlider(start=init_value[0], end=init_value[1], value=init_value)
slider.on_change('value',update_location)

#List location
location_select = Select(
    options= [str(x) for x in list_location],
    value= 'Indonesia',
    title='Location'
)
location_select.on_change('value', update_location)

#Procedure untuk update figure Variant COVID
def update_variant(attr, old, new):
    #Slider date
    [start, end] = slider.value
    date_from = dt.datetime.fromtimestamp(start/1000.0).date()
    date_until = dt.datetime.fromtimestamp(end/1000.0).date()

    #Menampung value Variant COVID yang dipilih
    variant_new = str(variant_select.value)

    #Menampung data terbaru
    variant_date = variants[(variants['date'] >= date_from) & (variants['date'] <= date_until)]
    new_data = {
        'variant': variant_date[variant_date['variant'] == variant_new]['variant'],
        'date': variant_date[variant_date['variant'] == variant_new]['date'],
        'num_sequences': variant_date[variant_date['variant'] == variant_new]['num_sequences'],
        'perc_sequences': variant_date[variant_date['variant'] == variant_new]['perc_sequences'],
        'num_sequences_total': variant_date[variant_date['variant'] == variant_new]['num_sequences_total'],
    }
    sourceVariant.data = new_data
    fig_variant.title.text = 'Variant COVID ' +variant_select.value+ ' di Seluruh Dunia per Mei 2020 - Desember 2021'

#List Variant COVID
variant_select = Select(
    options= [str(x) for x in list_variant],
    value= 'Omicron',
    title='Variant'
)
variant_select.on_change('value', update_variant)

#Procedure untuk update figure COVID per Location
def update_covidperloc(attr, old, new):
    #Menampung value COVID per Location yang dipilih
    covidperloc_new = str(covidperloc_select.value)

    #Menampung data terbaru
    new_data = dict(variant=covidperloc[covidperloc['location'] == covidperloc_new]['variant'], counts=covidperloc[covidperloc['location'] == covidperloc_new]['num_sequences'], color=magma(24))
    sourceCovidperLoc.data = new_data
    fig_covidperloc.title.text = 'Kasus Variant COVID di ' +covidperloc_select.value+ ' per Mei 2020 - Desember 2021'
    
#List COVID per Location
covidperloc_select = Select(
    options= [str(x) for x in list_covidperloc],
    value= 'Indonesia',
    title='Location'
)
covidperloc_select.on_change('value', update_covidperloc)

#Layout
layout = row(widgetbox(location_select, slider), fig_location)
layout2 = row(widgetbox(variant_select), fig_variant)
layout3 = row(widgetbox(covidperloc_select), fig_covidperloc)

#Panel
panel1 = Panel(child=layout, title='Kasus COVID di Seluruh Dunia')
panel2 = Panel(child=layout2, title='Kasus Variant COVID di Seluruh Dunia')
panel3 = Panel(child=layout3, title='Variant COVID per Negara')

tabs = Tabs(tabs=[panel1,panel2,panel3])

#Menampilkan di website
curdoc().add_root(tabs)
curdoc().title = "Visualisasi COVID"
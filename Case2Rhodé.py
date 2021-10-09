#!/usr/bin/env python
# coding: utf-8

# # Case 2: Blogpost

# In[1]:


project_title = 'Blogpost_ziekteverzuim'


# Namen: Vincent Kemme (500838439), Rhodé Rebel (500819128), Amber van der Pol (500803136) en Oussama Abou <font color = 'red'>(...)

# # 1 System setup

# **Credits:**  
# https://www.cbs.nl/nl-nl/onze-diensten/open-data/open-data-v4/snelstartgids-odata-v4

# **Working directory setup**
# * **/Data/** for all data related maps
# * **/Data/raw/** for all raw incoming data
# * **/Data/clean/** for all clean data to be used during analysis
# * **/Data/staging/** for all data save during cleaning 
# * **/Data/temp/** for all tempral data saving 
# * **/Figs/temp/** for all tempral data saving 
# * **/Docs/** reference documentation
# * **/Results/** reference documentation
# * **/Code/** reference documentation
# 
# 
# **References:**
# https://docs.python-guide.org/writing/structure/

# Import packages

# In[2]:


import pandas as pd
import os
import requests
import plotly.express as px
import plotly.graph_objects as go

# Verberg waarschuwingen om verwarring te voorkomen
import warnings
warnings.filterwarnings('ignore')


# Set working directories

# In[3]:


print("Current working directory: {0}".format(os.getcwd()))


# Create project structure

# In[4]:


arr_map_structure  = [os.getcwd() + map for map in   ['/Data','/Data/raw','/Data/clean','/Data/staging',
                      '/Data/temp','/Figs','/Figs/temp','/Docs','/Results','/Code'] ]

[os.makedirs(map) for map in arr_map_structure if  not os.path.exists( map)]


# # 2 Import data

# Functie get_odata wordt gedefinieerd.  
# Credits: https://www.cbs.nl/nl-nl/onze-diensten/open-data/open-data-v4/snelstartgids-odata-v4

# In[5]:


def get_odata(target_url):
    data = pd.DataFrame()
    while target_url:
        r = requests.get(target_url).json()
        data = data.append(pd.DataFrame(r['value']))
        
        if '@odata.nextLink' in r:
            target_url = r['@odata.nextLink']
        else:
            target_url = None
            
    return data


# ### 2.1 Ziekteverzuim volgens werknemers; beroep

# In[6]:


ziekteverzuim_url = "https://opendata.cbs.nl/ODataApi/odata/84437NED"

ziekteverzuim_api = get_odata(ziekteverzuim_url)
print(ziekteverzuim_api)


# Geef een beschrijving van de variabelen

# In[7]:


DataProperties_zv_url = ziekteverzuim_api.iloc[3, 1]

DataProperties_zv = get_odata(DataProperties_zv_url)[['Key', 'Description', 'Unit']]
DataProperties_zv


# Laad de UntypedDataSet in

# In[8]:


zv_uds_url = ziekteverzuim_api.iloc[1, 1]

zv_uds = get_odata(zv_uds_url)
zv_uds.head()


# In[9]:


print(zv_uds.info())


# Laad de TypedDataSet in

# In[10]:


zv_tds_url = ziekteverzuim_api.iloc[2, 1]

zv_tds = get_odata(zv_tds_url)
zv_tds.head()


# In[11]:


print(zv_tds.info())


# We zien dat de TypedDataSet alle 'objects' behalve die van de kolommen 'Beroep' en 'Perioden' heeft omgezet naar 'floats'. We kiezen daarom om gebruik te maken van de TypedDataSet.

# In[12]:


ziekteverzuim = zv_tds
ziekteverzuim.to_csv(arr_map_structure[1]+'_ziekteverzuim.csv', index=False) # Dataframe als csv opslaan als 'raw_ziekteverzuim'


# ### 2.1 Fysieke arbeidsbelasting werknemers; beroep

# In[13]:


fysiekearbeidsbelasting_url = "https://opendata.cbs.nl/ODataApi/odata/84435NED"

fysiekearbeidsbelasting_api = get_odata(fysiekearbeidsbelasting_url)
print(fysiekearbeidsbelasting_api)


# Geef een beschrijving van de variabelen

# In[14]:


DataProperties_fa_url = fysiekearbeidsbelasting_api.iloc[3, 1]

DataProperties_fa = get_odata(DataProperties_fa_url)[['Key', 'Description', 'Unit']]
DataProperties_fa


# Laad de TypedDataSet in

# In[15]:


fysiekearbeidsbelasting_url = fysiekearbeidsbelasting_api.iloc[2, 1]

fysiekearbeidsbelasting = get_odata(fysiekearbeidsbelasting_url)
fysiekearbeidsbelasting.head()


# In[16]:


print(fysiekearbeidsbelasting.info())


# In[17]:


# Dataframe als csv opslaan als 'raw_fysiekearbeidsbelasting'
fysiekearbeidsbelasting.to_csv(arr_map_structure[1]+'_fysiekearbeidsbelasting.csv', index=False)


# # 3 Exploratory Data Analysis

# ## 3.1 Inspectie van de variabelen

# In[18]:


whos


# ## 3.2 EDA per dataframe

# Kijken naar shape, veldnamen en datatypes.

# In[19]:


print("shape ziekteverzuim: " + str(ziekteverzuim.shape))
print("shape fysiekearbeidsbelasting: " + str(fysiekearbeidsbelasting.shape))


# In[20]:


ziekteverzuim.info()


# In[21]:


fysiekearbeidsbelasting.info()


# Beide datasets hebben de variabelen 'ID', 'Beroep' en 'Perioden'. We kunnen de datasets eventueel joinen op 'Beroep' en 'Perioden'.

# ### 3.2.1 Datasets samenvoegen

# In[22]:


df_merged = ziekteverzuim.merge(fysiekearbeidsbelasting, how = 'outer', on = ['Beroep', 'Perioden'], validate = 'one_to_one')
df_merged.columns


# ### 3.2.1 Kolommen splitsen / verwijderen / hernoemen

# Vervang de waarden van de kolom 'Beroep' met de namen van de beroepen.

# In[23]:


beroep_url = ziekteverzuim_api.iloc[5, 1]
r = requests.get(beroep_url)
beroep = r.json()
beroep = beroep.get('value')
beroep = pd.DataFrame.from_dict(beroep)
beroep = beroep[['Key', 'Title']]
beroep.head()


# In[24]:


df_beroep = df_merged.merge(beroep, left_on = 'Beroep', right_on = 'Key', validate = 'many_to_one')
title_beroep = df_beroep['Title']
df_beroep.drop(labels=['Beroep', 'Key', 'Title'], axis = 1, inplace = True)
df_beroep.insert(1, 'Beroep', title_beroep)
df_beroep.head()


# Vervang de waarden van de kolom 'Perioden' met jaartallen.

# In[25]:


perioden_url = ziekteverzuim_api.iloc[6, 1]
r = requests.get(perioden_url)
perioden = r.json()
perioden = perioden.get('value')
perioden = pd.DataFrame.from_dict(perioden)
perioden = perioden[['Key', 'Title']]
perioden.head()


# In[26]:


df_beroep_perioden = df_beroep.merge(perioden, left_on = 'Perioden', right_on = 'Key', validate = 'many_to_one')
title_perioden = df_beroep_perioden['Title']
df_beroep_perioden.drop(labels=['Perioden', 'Key', 'Title'], axis = 1, inplace = True)
df_beroep_perioden.insert(2, 'Perioden', title_perioden)
df_beroep_perioden.sort_values(by = ['ID_x'], inplace = True)
df_beroep_perioden.head()


# Verwijder de ID kolommen

# In[27]:


df_beroep_perioden.drop(labels = ['ID_x', 'ID_y'], axis = 1, inplace = True)


#  Waarden in de kolom 'Beroep' omzetten naar string

# In[28]:


df_beroep_perioden['Beroep'] = df_beroep_perioden['Beroep'].astype('string')


# Waarden in de kolom 'Perioden' omzetten naar integer

# In[29]:


df_beroep_perioden['Perioden'] = df_beroep_perioden['Perioden'].astype('int')


# In[30]:


df = df_beroep_perioden.reset_index(drop=True)
df.head()


# ### 3.2.2 Duplicates checken

# In[31]:


duplicate = df[["Beroep", "Perioden"]].duplicated() # checken voor duplicates (met dezelfde combinatie beroep en jaar)
true_count = sum(duplicate) # True values tellen
print(true_count)


# Er zijn geen duplicates in deze dataset.

# ### 3.2.3 Generieke verkenning

# **Missende waarden**

# In[32]:


print(df.isnull().sum()) # Missende waarden checken


# Er zijn aardig wat missende waarden te zien

# **Dataset opsplitsen**

# De kolom 'Beroep' bevat een soort levelsysteem.  
# Allereerst:
# - Per jaar wordt het totaal gegeven van alle beroepen
# - Per jaar wordt het totaal gegeven per beroepsniveau
#  
# Verder worden beroepen (aangeduid met een 4-digit cijfer) onderverdeeld in beroepssegment (aangeduid met een 3-digit cijfer). Beroepssegment wordt weer opgedeeld in beroepsklasse (aangeduid met een 2-digit cijfer).
# 
# We splitsen de data dus op in 5 datasets:
# - Totaal
# - Beroepsniveau
# - Beroepsklasse
# - Beroepssegment
# - Beroep

# In[33]:


# Index getallen per 'level' in een lijst zetten
id_totaal = list(map(int, df.index[df['Beroep'].str.contains('Totaal')]))
id_beroepsniveau = list(map(int, df.index[df['Beroep'].str.contains('Beroepsniveau')]))
id_beroepsklasse = list(map(int, df.index[df['Beroep'].str.contains('^\d{2}\s')]))
id_beroepssegment = list(map(int, df.index[df['Beroep'].str.contains('^\d{3}\s')]))
id_beroep = list(map(int, df.index[df['Beroep'].str.contains('^\d{4}\s')]))

# Dataframes aanmaken per 'level'
df_totaal = df.iloc[id_totaal]
df_beroepsniveau = df.iloc[id_beroepsniveau]
df_beroepsklasse = df.iloc[id_beroepsklasse]
df_beroepssegment = df.iloc[id_beroepssegment]
df_beroep = df.iloc[id_beroep]


# Ook maken we een dataset aan waarin zowel 'Beroep', 'Beroepssegment' als 'Beroepsklasse' een variabele is.

# In[34]:


# Verkrijg de eerste twee en eerste 3 cijfers uit de kolom 'Beroep' en stop deze in nieuwe kolommen
df_beroep['ID2'] = df_beroep['Beroep'].str.extract('(^\d{2})')
df_beroep['ID3'] = df_beroep['Beroep'].str.extract('(^\d{3})')

# Verkrijg de drie cijfers uit de kolom 'Beroepssegment' en stop deze in een nieuwe kolom
df_beroepssegment['ID3'] = df_beroepssegment['Beroep'].str.extract('(^\d{3})')

# Verkrijg de twee cijfers uit de kolom 'Beroepsklasse' en stop deze in een nieuwe kolom
df_beroepsklasse['ID2'] = df_beroepsklasse['Beroep'].str.extract('(^\d{2})')


# In[35]:


# Pak de kolommen Beroep en ID(2/3)
df_sm = df_beroepssegment[['Beroep','ID3']]
df_bk = df_beroepsklasse[['Beroep','ID2']]

# Drop duplicates om een dataframe te krijgen met unieke combinaties
df_sm.drop_duplicates(inplace = True)
df_bk.drop_duplicates(inplace = True)


# In[36]:


# Merge beroep met de unieke combinaties van beroepsklasse
df_beroep_klasse = df_beroep.merge(df_bk, on = 'ID2', validate = 'many_to_one', suffixes = ['', '_y'])
klasse = df_beroep_klasse['Beroep_y']
df_beroep_klasse.drop(labels=['Beroep_y', 'ID2'], axis = 1, inplace = True)
df_beroep_klasse.insert(1, 'Beroepsklasse', klasse)

# Merge de verkregen dataframe met de unieke combinaties van beroepssegment
df_beroep_segklas = df_beroep_klasse.merge(df_sm, on = 'ID3', validate = 'many_to_one', suffixes = ['', '_y'])
segment = df_beroep_segklas['Beroep_y']
df_beroep_segklas.drop(labels=['Beroep_y', 'ID3'], axis = 1, inplace = True)
df_beroep_segklas.insert(1, 'Beroepssegment', segment)

df_beroep_segklas.head(50) # Laat de eerste 50 waarnemingen zien


# In[37]:


df_beroep_segklas.columns


# ### 3.2.4 Visuele data-analyse

# Labels aanmaken voor een aantal variabelen

# In[38]:


labeldict = {'Perioden':'Jaar',
             'ZiekteverzuimpercentageWerknemers_1':'Ziekteverzuimpercentage',
             'AandeelWerknemersDatHeeftVerzuimd_2':'Aandeel werknemers dat heeft verzuimd',
             'GemiddeldeVerzuimfrequentie_3':'Gemiddelde verzuimfrequentie',
             'GemiddeldeVerzuimduur_4':'Gemiddelde verzuimduur (in werkdagen)',
             'k_1Tot5Werkdagen_5':'1 tot 5 werkdagen',
             'k_5Tot20Werkdagen_6':'5 tot 20 werkdagen',
             'k_20Tot210Werkdagen_7':'20 tot 210 werkdagen',
             'k_210WerkdagenOfMeer_8':'210 werkdagen of meer',
             'JaHoofdzakelijkGevolgVanMijnWerk_9':'Ja, hoofdzakelijk gevolg van mijn werk',
             'JaVoorEenDeelGevolgVanMijnWerk_10':'Ja, voor een deel gevolg van mijn werk',
             'NeeGeenGevolgVanMijnWerk_11':'Nee, geen gevolg van mijn werk',
             'WeetNiet_12':'Weet ik niet',
             'RegelmatigVeelKrachtZetten_1':'Percentage werknemers dat regelmatig veel kracht verzet',
             'RegelmatigHardPraten_2':'Percentage werknemers dat regelmatig hard moet praten',
             'RegelmatigTeMakenMetTrillingen_3':'Percentage werknemers dat te maken krijg met trillingen',
             'GevaarlijkWerkTot2018_4':'Percentage werknemers dat gevaarlijk werk uitvoert (tot 2018)',
             'GevaarlijkWerkVanaf2018_5':'Percentage werknemers dat gevaarlijk werk uitvoert (tot 2019)',
             'Vallen_6':'Percentage werknemers dat werk uitvoert met valgevaar',
             'Struikelen_7':'Percentage werknemers dat werk uitvoert met struikelgevaar',
             'Bekneld_8':'Percentage werknemers dat werk uitvoert met knelgevaar',
             'Snijden_9':'Percentage werknemers dat werk uitvoert met snijgevaar',
             'Botsen_10':'Percentage werknemers dat werk uitvoert met botsgevaar',
             'GevaarlijkeStoffen_11':'Percentage werknemers dat werk uitvoert met gevaarlijke stoffen',
             'Geweld_12':'Percentage werknemers dat werk uitvoert waarbij geweld kan ontstaan',
             'Verbranden_13':'Percentage werknemers dat werk uitvoert met verbrandingsgevaar',
             'Verstikking_14':'Percentage werknemers dat werk uitvoert met verstikkingsgevaar',
             'Anders_15':'Percentage werknemers dat werk uitvoert met een ander gevaarsoort',
             'WaterigeOplossingen_16':'Percentage werknemers dat werkt met waterige oplossingen',
             'StoffenOpHuid_17':'Percentage werknemers dat werk uitvoert waarbij stoffen op de huid komen',
             'AdemtStoffenIn_18':'Percentage werknemers dat tijdens het werk stoffen inademt',
             'BesmettePersonen_19':'Percentage werknemers dat tijdens het werk in contact komt met besmette personen',
             'InOngemakkelijkeWerkhoudingWerken_20':'Percentage werknemers dat in een ongemakkelijke werkhouding werkt',
             'TijdensWerkRepeterendeBewegingMaken_21':'Percentage werknemers dat tijdens het werk repeterende bewegingen maakt',
             'UurPerDagAanBeeldschermVoorWerk_22':'Gemiddeld aantal schermuren voor werk'}

labeldict_breaks = {'Perioden':'Jaar',
             'ZiekteverzuimpercentageWerknemers_1':'Ziekteverzuimpercentage',
             'AandeelWerknemersDatHeeftVerzuimd_2':'Aandeel werknemers dat heeft verzuimd',
             'GemiddeldeVerzuimfrequentie_3':'Gemiddelde verzuimfrequentie',
             'GemiddeldeVerzuimduur_4':'Gemiddelde verzuimduur (in werkdagen)',
             'k_1Tot5Werkdagen_5':'1 tot 5 werkdagen',
             'k_5Tot20Werkdagen_6':'5 tot 20 werkdagen',
             'k_20Tot210Werkdagen_7':'20 tot 210 werkdagen',
             'k_210WerkdagenOfMeer_8':'210 werkdagen of meer',
             'JaHoofdzakelijkGevolgVanMijnWerk_9':'Ja, hoofdzakelijk gevolg van mijn werk',
             'JaVoorEenDeelGevolgVanMijnWerk_10':'Ja, voor een deel gevolg van mijn werk',
             'NeeGeenGevolgVanMijnWerk_11':'Nee, geen gevolg van mijn werk',
             'WeetNiet_12':'Weet ik niet',
             'RegelmatigVeelKrachtZetten_1':'Percentage werknemers<br>dat regelmatig veel<br>kracht verzet',
             'RegelmatigHardPraten_2':'Percentage werknemers dat regelmatig hard moet praten',
             'RegelmatigTeMakenMetTrillingen_3':'Percentage werknemers dat te maken krijg met trillingen',
             'GevaarlijkWerkTot2018_4':'Percentage werknemers dat gevaarlijk werk uitvoert (tot 2018)',
             'GevaarlijkWerkVanaf2018_5':'Percentage werknemers dat gevaarlijk werk uitvoert (tot 2019)',
             'Vallen_6':'Percentage werknemers dat werk uitvoert met valgevaar',
             'Struikelen_7':'Percentage werknemers dat werk uitvoert met struikelgevaar',
             'Bekneld_8':'Percentage werknemers dat werk uitvoert met knelgevaar',
             'Snijden_9':'Percentage werknemers dat werk uitvoert met snijgevaar',
             'Botsen_10':'Percentage werknemers dat werk uitvoert met botsgevaar',
             'GevaarlijkeStoffen_11':'Percentage werknemers dat werk uitvoert met gevaarlijke stoffen',
             'Geweld_12':'Percentage werknemers dat werk uitvoert waarbij geweld kan ontstaan',
             'Verbranden_13':'Percentage werknemers dat werk uitvoert met verbrandingsgevaar',
             'Verstikking_14':'Percentage werknemers dat werk uitvoert met verstikkingsgevaar',
             'Anders_15':'Percentage werknemers dat werk uitvoert met een ander gevaarsoort',
             'WaterigeOplossingen_16':'Percentage werknemers dat werkt met waterige oplossingen',
             'StoffenOpHuid_17':'Percentage werknemers dat werk uitvoert waarbij stoffen op de huid komen',
             'AdemtStoffenIn_18':'Percentage werknemers dat tijdens het werk stoffen inademt',
             'BesmettePersonen_19':'Percentage werknemers dat tijdens het werk in contact komt met besmette personen',
             'InOngemakkelijkeWerkhoudingWerken_20':'Percentage werknemers<br>dat in een ongemakkelijke<br>werkhouding werkt',
             'TijdensWerkRepeterendeBewegingMaken_21':'Percentage werknemers dat tijdens het werk repeterende bewegingen maakt',
             'UurPerDagAanBeeldschermVoorWerk_22':'Gemiddeld aantal schermuren voor werk'}


# In[39]:


df_beroep_segklas_groupby = df_beroep_segklas.groupby(['Beroep', 'Beroepssegment', 'Beroepsklasse']).mean()

fig = px.scatter_matrix(df_beroep_segklas_groupby,
                        dimensions=["ZiekteverzuimpercentageWerknemers_1", "RegelmatigVeelKrachtZetten_1", "InOngemakkelijkeWerkhoudingWerken_20"],
                        color = df_beroep_segklas_groupby.index.get_level_values('Beroepsklasse'),
                        labels = labeldict_breaks)

fig.update_traces(diagonal_visible=False) # laat diagonale grafieken weg
fig.update_layout(width=1000, height=700, # Maak grafiek groter
                  legend_title = 'Beroepsklasse')

fig.show()


# <font color = 'red'> Trompetvorm tussen ziekteverzuimpercentage - ongemakkelijke werkhouding en ziekteverzuimpercentage - veel kracht verzetten. Ook sterke samenhang te zien tussen veel kracht verzetten en ongemakkelijke werkhouding.

# Tussen de beroepsklasse staat nu geen '02 Creatieve en taalkundige beroepen' meer, omdat deze geen specifieke beroepen bevatten in de dataset.
# <font color = 'red'> Hierdoor komen de kleuren niet overeen met de kleuren van het volgende plaatje in de legenda.

# In[40]:


fig = px.box(data_frame = df_beroepsklasse, x = 'Beroep', y = 'ZiekteverzuimpercentageWerknemers_1',
            color = 'Beroep')

fig.update_xaxes(title = 'Beroepsklasse')
fig.update_yaxes(range = [0, df_beroepsklasse['ZiekteverzuimpercentageWerknemers_1'].max() + 0.5],
                 title = 'Ziekteverzuimpercentage')
fig.update_layout(legend_title = 'Beroepsklasse')

fig.show()


# Het valt op dat de ziekteverzuimpergentages van 'Openbaar bestuur, veiligheid en justitie' en 'Zorg en welzijn' hoger liggen dan de rest. 'Zorg en welzijn' ligt het hoogst.

# In[41]:


# Credits: https://plotly.com/python/sliders/

fig = px.scatter(data_frame = df_beroep_segklas, x = 'Beroep', y = 'ZiekteverzuimpercentageWerknemers_1',
                color = 'Beroepsklasse',
                animation_frame = 'Perioden',
                labels = labeldict_breaks)

fig.update_xaxes(showticklabels=False)
fig.update_yaxes(range = [0, df_beroep_segklas['ZiekteverzuimpercentageWerknemers_1'].max() + 0.5],
                 title = 'Ziekteverzuimpercentage')

fig.show()


# Tussen de beroepsklasse staat nu geen '02 Creatieve en taalkundige beroepen' meer, omdat deze geen specifieke beroepen bevatten in de dataset.
# <font color = 'red'> Hierdoor komen de kleuren niet overeen met de kleuren van het vorige plaatje in de legenda.

# In[42]:


df19 = df_beroep_segklas[df_beroep_segklas['Perioden']==2019]
df20 = df_beroep_segklas[df_beroep_segklas['Perioden']==2020]
index_vals = df19['Beroepsklasse'].astype('category').cat.codes # maak categorieën van beroepsklassen (voor de markerkleur)

fig = go.Figure()

fig.add_trace(go.Bar(x = df19['Beroep'], y = df19['ZiekteverzuimpercentageWerknemers_1'],
                     name = '2019', marker={'color':index_vals, 'colorscale': px.colors.qualitative.Light24}))
fig.add_trace(go.Bar(x = df20['Beroep'], y = df20['ZiekteverzuimpercentageWerknemers_1'],
                     name = '2020', marker={'color':index_vals, 'colorscale': px.colors.qualitative.Light24}))

year_buttons = [{'label': '2019', 'method': 'update', 'args': [{'visible': [True, False]}]},
                {'label': '2020', 'method': 'update', 'args': [{'visible': [False, True]}]}]

fig.update_layout({'updatemenus':[{'active': True, 'type': 'buttons', 'buttons':year_buttons}]},
                  showlegend = False)

fig.update_xaxes(showticklabels=False)
fig.update_yaxes(range=[0, 8], title = 'Ziekteverzuimpercentage')

fig.show()


# <font color = 'red'> Een legenda maken per kleur (beroepsklasse) lukt me niet.

# In[43]:


df_beroepsklasse_groupby = df_beroepsklasse.groupby('Beroep').mean()
fysiekearbeid = df_beroepsklasse_groupby.columns.tolist()[13:-1]
fysiekearbeid_labels = list(labeldict.values())[13:-1]

fig = go.Figure()

j = 0
dropdown_buttons = []
for i in fysiekearbeid:
    fig.add_trace(go.Bar(x = df_beroepsklasse_groupby.index, y = df_beroepsklasse_groupby[i],
                        name = i, text=df_beroepsklasse_groupby[i]))

    dropdown_buttons.append({'label':fysiekearbeid_labels[j],
                             'method': 'update',
                             'args': [{"visible":[x==i for x in fysiekearbeid]},
                                      {'yaxis':{'title':fysiekearbeid_labels[j],
                                                'range':[0, df_beroepsklasse_groupby[fysiekearbeid].max().max()+10]}}]})
    j += 1

fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
fig.update_layout({'updatemenus':[{'active':True, 'buttons': dropdown_buttons,
                                   'x': 1, 'y': 1.2}]},
                  annotations = [{'text':"Fysiekse arbeidsbelasting", 'font_size':15,
                                'x': 1, 'xref':"paper", 'y':1.3, 'yref':"paper",
                                'showarrow':False}],
                  showlegend = False,
                  height = 800)

fig.show()


# In[44]:


DataProperties_fa.iloc[7,1]


# In[45]:


DataProperties_fa.iloc[9,1]


# In[46]:


df_groupby_beroep = df_beroep_segklas.groupby(['Beroep', 'Beroepssegment', 'Beroepsklasse']).mean()
df_transpose = df_groupby_beroep.transpose()
df_transpose.head()


# In[50]:


# beroepen = list(df_beroep_segklas['Beroep'].unique())
# beroepsklassen = list(df_beroep_segklas['Beroepsklasse'].unique())
# fig = go.Figure()

# j = 0
# dropdown_buttons = []
# for i in beroepen:
#     fig.add_trace(go.Bar(x = df_transpose.index, y = df_transpose[df_transpose['Beroep']==i]))
 
#     dropdown_buttons.append({'label':beroepen[j],
#                              'method': 'update',
#                              'args': [{"visible":[x==i for x in beroepen]}]})
#     j += 1

# fig.show()


# In[ ]:





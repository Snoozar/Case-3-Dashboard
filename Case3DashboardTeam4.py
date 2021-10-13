#!/usr/bin/env python
# coding: utf-8

# # Case 3: Laadpalen

# In[1]:


project_title = 'Elektrische_Laadpalen'


# Namen: Vincent Kemme (500838439), Rhodé Rebel (500819128), Amber van der Pol (500803136) en Oussama Abou (500803060)

# In[2]:


import pandas as pd
import os
import requests
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np
import plotly.figure_factory as ff


# In[3]:

st.set_page_config(page_title = 'Dashboard Case 3', layout = 'wide')
st.title("Test")
st.markdown('Namen: Vincent Kemme (500838439), Rhodé Rebel (500819128), Amber van der Pol (500803136) en Oussama Abou (500803060)')


# ## Data Inladen

# ### OpenChargeMap

# In[4]:


# API OpenChargeMap
urlocm = "https://api.openchargemap.io/v3/poi/?output=json&countrycode=NL&key=c2b5b38c-09f3-4304-bbdb-b184319acc70"
ocm = requests.get(urlocm).json()


# In[5]:


dfocm = pd.DataFrame.from_dict(ocm)
dfocm.info()
dfocm.head()


# In[6]:


# for i in range(100):
#     print(dfocm['Connections'][i][0]['CurrentType']['Title'])


# In[7]:


dic = dfocm.iloc[1][20][0]
dic


# In[8]:


# Versimpelde versie API OpenChargeMap
urlocm2 = "https://api.openchargemap.io/v3/poi/?output=json&countrycode=NL&compact=true&verbose=false&key=c2b5b38c-09f3-4304-bbdb-b184319acc70"
ocm2 = requests.get(urlocm2).json()


# In[9]:


dfocm2 = pd.DataFrame.from_dict(ocm2)
dfocm2.info()
dfocm2.head()


# In[10]:


add_dict = (dfocm2['AddressInfo'])
add_dict.head()
add_dict[0]


# In[11]:


dftest = dfocm2
#dftest.iloc[0]


# In[12]:


# De dictionary in AddressInfo wordt opgesplitst in verschillende kolommen
dfnew = pd.concat([dftest.drop(['AddressInfo'], axis = 1), dftest['AddressInfo'].apply(pd.Series)], axis = 1)
#dfnew.iloc[0]


# In[13]:


#dfnew.iloc[10][8]


# ### OpenData RDW

# In[14]:


# API OpenData RDW
urlrdw = "https://opendata.rdw.nl/resource/w4rt-e856.json"
rdw = requests.get(urlrdw).json()


# In[15]:


dfrdw = pd.DataFrame.from_dict(rdw)
dfrdw.info()
dfrdw.head()


# ### Laadpaaldata

# In[16]:


import warnings
warnings.filterwarnings('ignore')


# In[17]:


# Laadpaaldata csv importeren
dflpd = pd.read_csv('laadpaaldata.csv')


# In[18]:


dflpd.info()
dflpd.head()


# In[19]:


# Negatieve tijden verwijderen
dflpdpos = dflpd[dflpd['ChargeTime']>=0]

# Niet kloppende datum verwijderen
dflpdpos = dflpdpos[dflpdpos['Started'] != '2018-02-29 07:37:53']


# In[20]:


dflpdpos['CumConnected'] = dflpdpos["ConnectedTime"].cumsum()
dflpdpos['CumCharge'] = dflpdpos["ChargeTime"].cumsum()
dflpdpos['Vermogen'] = dflpdpos["TotalEnergy"]/dflpdpos["ChargeTime"]


# In[21]:


dflpdpos


# In[22]:


# De gemiddelde bezetting van een laadpaal
TotMean = dflpdpos['TotalEnergy'].mean()
ConMean = dflpdpos['ConnectedTime'].mean()
CharMean = dflpdpos['ChargeTime'].mean()
MaxMean = dflpdpos['MaxPower'].mean()
print(TotMean)
print(ConMean)
print(CharMean)
print(MaxMean)


# In[23]:


# Verschil tussen laden en bezetten van een laadpaal
figCon = go.Figure()

figCon.add_trace(go.Box(y = dflpdpos['ConnectedTime'], name = 'Connected Time'))
figCon.add_trace(go.Box(y = dflpdpos['ChargeTime'], name = 'Charge Time'))


# In[42]:


figConZoom = figCon
figConZoom.update_layout(yaxis_range=[-3,25])
figConZoom.show()
st.plotly_chart(figConZoom)


# In[41]:


# Verschil tussen laden en bezetten van een laadpaal
figConLine = go.Figure()

figConLine.add_trace(go.Scatter(y = dflpdpos['CumConnected'], name = 'Connected Time'))
figConLine.add_trace(go.Scatter(y = dflpdpos['CumCharge'], name = 'Charge Time'))
figConLine.show()
st.plotly_chart(figConLine)


# In[40]:


# Verdeling van vermogens
figVer = go.Figure()

figVer.add_trace(go.Histogram(x = dflpdpos['Vermogen']))

figVer.update_layout(xaxis_range=[-3,15000])
figVer.show()
st.plotly_chart(figVer)


# In[27]:


CharMean = dflpdpos['ChargeTime'].mean()
CharMedian = dflpdpos['ChargeTime'].median()
print(CharMean)
print(CharMedian)


# In[39]:


# Histogram laadtijd
hist_date = [dflpdpos['ChargeTime']]
group_labels = ['distplot']

figLaad = ff.create_distplot(hist_date, group_labels, bin_size=.2)

figLaad.update_layout(xaxis_range=[-0.2,10])
figLaad.add_annotation(x=CharMean, y=0.3,
            text="Gemiddelde (2.49)",
            showarrow=True,
            arrowhead=1,
                      yshift = -20)
figLaad.add_annotation(x=CharMedian, y=0.3,
            text="Mediaan (2.23)",
            showarrow=True)

figLaad.show()
st.plotly_chart(figLaad)
## Meerdere groepen met ChargeTime, waarschijnlijk meerdere verdelingen die met elkaar overlappen


# In[29]:


# StartTime = pd.to_datetime(dflpdpos['Started'], errors = 'coerce')
# StartTime = StartTime.dropna()
# StartTime = StartTime.apply(lambda x: x.time())
# StartTime


# In[30]:


dflpdpos['StartTime'] = pd.to_datetime(dflpdpos['Started'], errors = 'coerce')
dflpdpos['StartTime'] = dflpdpos['StartTime'].dropna()
dflpdpos['StartTime'] = dflpdpos['StartTime'].apply(lambda x: x.time())
dflpdpos['StartTime']


# In[31]:


sort = dflpdpos.sort_values('StartTime')
sort['StartTime']


# In[32]:


# Scatterplot van tijd en laadtijd
figTimeSca = go.Figure()

figTimeSca.add_trace(go.Scatter(x = sort['StartTime'], y = dflpdpos['ConnectedTime'], mode = 'markers', marker=dict(color='red'), opacity=0.2))


# In[43]:


figTimeSca = px.scatter(sort, x = 'StartTime', y = 'ConnectedTime', opacity=0.2)
figTimeSca.update_yaxes(range = [-1, 24])
figTimeSca.show()
st.plotly_chart(figTimeSca)

col1, col2 = st.columns(2)
col1.plotly_chart(figTimeSca)
col2.plotly_chart(figLaad)





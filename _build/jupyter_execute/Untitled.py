#!/usr/bin/env python
# coding: utf-8

# In[1]:


#-- SET ME   Tutorial should work with most binary black hole events
#-- Default is no event selection; you MUST select one to proceed.
eventname = ''
eventname = 'GW150914' 
#eventname = 'GW151226' 
#eventname = 'LVT151012'
#eventname = 'GW170104'

# want plots?
make_plots = 1
plottype = "png"
#plottype = "pdf"


# In[3]:


# Standard python numerical analysis imports:
import numpy as np
from scipy import signal
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt, iirdesign, zpk2tf, freqz
import h5py
import json

# the IPython magic below must be commented out in the .py file, since it doesn't work there.
get_ipython().run_line_magic('matplotlib', 'inline')
get_ipython().run_line_magic('config', "InlineBackend.figure_format = 'retina'")
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

# LIGO-specific readligo.py 
from ligotools import readligo as rl


# In[4]:


fnjson = "BBH_events_v3.json"

events = json.load(open(fnjson,"r"))


# In[6]:


event = events[eventname]
fn_H1 = event['fn_H1']


# In[7]:


strain_H1, time_H1, chan_dict_H1 = rl.loaddata(fn_H1, 'H1')


# In[ ]:





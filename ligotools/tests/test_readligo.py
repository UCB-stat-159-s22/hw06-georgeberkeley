import json
from ligotools import readligo as rl
fnjson = "BBH_events_v3.json"


    

def test_loaddata():
    events = json.load(open(fnjson,"r"))
    eventname = 'GW150914' 
    event = events[eventname]
    fn_H1 = event['fn_H1'] 
    output = rl.loaddata(fn_H1, 'H1')
    assert len(output) == 3
    
    
def test_segList():
    segList = rl.getsegs(842657792, 842658792, 'H1')
    
    assert segList is not None
    

def test_filelist():
    fl = rl.FileList(directory='/home/ligodata')
    assert fl is not None
    
    
def test_readhdf5():
    events = json.load(open(fnjson,"r"))
    eventname = 'GW150914' 
    event = events[eventname]
    fn_H1 = event['fn_H1'] 
    
    output = rl.read_hdf5(fn_H1,True)
    
    assert len(output) == 7
    
    

    

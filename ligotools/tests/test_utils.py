from ligotools import utils
from ligotools import readligo as rl
import json
from scipy import signal
from scipy.interpolate import interp1d
import matplotlib.mlab as mlab
from scipy.signal import butter, filtfilt, iirdesign, zpk2tf, freqz
fnjson = "BBH_events_v3.json"
import numpy as np
import os
import h5py
events = json.load(open(fnjson,"r"))
eventname = 'GW150914'
event = events[eventname]
fn_H1 = event['fn_H1']
tevent = event['tevent']
fs = 4096
NFFT = 4*fs
fband = event['fband'] 
bb, ab = butter(4, [fband[0]*2./fs, fband[1]*2./fs], btype='band')
normalization = np.sqrt((fband[1]-fband[0])/(fs/2))
strain, time,  channel_dict = rl.loaddata(fn_H1, 'H1')
dt = time[1] - time[0]
Pxx_H1, freqs = mlab.psd(strain, Fs = fs, NFFT = NFFT)
psd_H1 = interp1d(freqs, Pxx_H1)

def test_whiten():
	whitten_strain = utils.whiten(strain,psd_H1,dt)
	assert type(whitten_strain) == type(np.array([1,2]))

def test_write_wavefile():
	out_audio = np.sin(np.linspace(0, 3.14, 100))
	out_path = "audio/test_audio.wav"
	utils.write_wavfile(out_path,4096, out_audio)
	assert os.path.exists(out_path)	
def test_reqshift():
	arr = utils.reqshift(np.linspace(0,1, 20))
	assert arr[1] == 0.05263157894736854

def test_plotter():
	whiten_strain = utils.whiten(strain, psd_H1, dt)
	fn_L1 = event['fn_L1']  
	strain_L1, time_L1, chan_dict_L1 = rl.loaddata(fn_L1, 'L1')
	timemax = 1126259462.432373
	template_offset = 16.
	psd_window = np.blackman(NFFT)
	# and a 50% overlap:
	NOVL = NFFT/2
	fn_template = event['fn_template']
	f_template = h5py.File(fn_template, "r")
	template_p, template_c = f_template["template"][...]
	template = (template_p + template_c*1.j) 
	# We will record the time where the data match the END of the template.
	etime = time+template_offset
	# the length and sampling rate of the template MUST match that of the data.
	datafreq = np.fft.fftfreq(template.size)*fs
	df = np.abs(datafreq[1] - datafreq[0])

	# to remove effects at the beginning and end of the data stretch, window the data
	# https://en.wikipedia.org/wiki/Window_function#Tukey_window
	try:   dwindow = signal.tukey(template.size, alpha=1./8)  # Tukey window preferred, but requires recent scipy version 
	except: dwindow = signal.blackman(template.size)          # Blackman window OK if Tukey is not available

	# prepare the template fft.
	template_fft = np.fft.fft(template*dwindow) / fs
	data = strain_L1.copy()
	data_fft = np.fft.fft(data*dwindow) / fs
	
	
	data_psd, freqs = mlab.psd(data, Fs = fs, NFFT = NFFT, window=psd_window, noverlap=NOVL)
	power_vec = np.interp(np.abs(datafreq), freqs, data_psd)
	optimal = data_fft * template_fft.conjugate() / power_vec
	optimal_time = 2*np.fft.ifft(optimal)*fs
	sigmasq = 1*(template_fft * template_fft.conjugate() / power_vec).sum() * df
	sigma = np.sqrt(np.abs(sigmasq))
	peaksample = int(data.size / 2)
	SNR_complex = optimal_time/sigma
	SNR = abs(SNR_complex)
	pcolor = "y"
	det = "L1"
	plottype = "png"
	indmax = np.argmax(SNR)
	timemax = time[indmax]
	SNRmax = SNR[indmax]

	# Calculate the "effective distance" (see FINDCHIRP paper for definition)
	# d_eff = (8. / SNRmax)*D_thresh
	d_eff = sigma / SNRmax
	# -- Calculate optimal horizon distnace
	horizon = sigma/8

	# Extract time offset and phase at peak
	phase = np.angle(SNR_complex[indmax])
	offset = (indmax-peaksample)
	template_phaseshifted = np.real(template*np.exp(1j*phase))
	template_rolled = np.roll(template_phaseshifted,offset) / d_eff
	template_whitened = utils.whiten(template_rolled,interp1d(freqs, data_psd),dt)
	template_match = filtfilt(bb, ab, template_whitened) / normalization
	utils.plotter(time,timemax, SNR, pcolor, det, eventname,
		plottype,whiten_strain, template_match,tevent, datafreq, template_fft, fs, freqs, d_eff, data_psd)
	
	matchtime_plot_path = "figurs/"+eventname+"_"+det+"_matchtime."+plottype
	
	assert os.path.exists(matchtime_plot_path)
#These packages need to be installed to run this:
#pip3 install COVID19Py
#pip3 install requests
#pip3 install numpy
#pip3 install matplotlib
#pip3 install scipy

import matplotlib.pylab as pl
import numpy as np
from numpy import log, exp
from scipy.stats import poisson
from scipy.special import gammaln
from scipy.optimize import minimize
import pickle

country = 'SE'
#cache the results to not unnecessarily tax their server
if False:
	import COVID19Py
	covid19 = COVID19Py.COVID19(data_source="jhu") #Johns Hopkins University
	
	res = covid19.getLocationByCountryCode(country, timelines=True)

	#categories are: 'cofirmed', 'deaths', 'recovered'
	deathDict = {k:v for k,v in res[0]['timelines']['deaths']['timeline'].items() if 0<v}

	dates = sorted(deathDict.keys())
	datesSinceLatest = list(range(1-len(dates),1))
	deaths=[deathDict[d] for d in dates]
	pickle.dump( (dates, datesSinceLatest, deaths), open( "cache{}.p".format(country), "wb" ) )
else:
	dates, datesSinceLatest, deaths = pickle.load( open( "cache{}.p".format(country), "rb" ) )

print('Country: '+country)
print('Latest number of deaths: {}'.format(deaths[-1]))

#append today's number if it is not yet available on the server
append=0 #66
if append:
	dates.append('today')
	datesSinceLatest=list(range(1-len(dates),1))
	deaths.append(append)

def likelihood(v, l, dates, deathsPerDay):
	return sum(deathsPerDay[i]*(log(v)+dates[i]*l)-v*exp(dates[i]*l) for i in range(len(deathsPerDay)))  #removed constant terms
	#return sum(deaths[i]*(log(v)+dates[i]*l)-v*exp(dates[i]*l)-gammaln(deaths[i]+1) for i in range(len(deaths)))
	#return sum(np.log(poisson.pmf(deaths[i], v*np.exp(dates[i]*l))) for i in range(len(deaths))) #same but not numerically stable

deathsPerDay=np.diff(deaths, prepend=0)
res = minimize(lambda x: -likelihood(x[0], x[1], datesSinceLatest, deathsPerDay), [1,0], bounds=[(0,np.inf),(0,np.inf)]).x
print("Doubling time: {:.2f} days".format(log(2)/res[1]))
allDates = np.arange(datesSinceLatest[0], 45)
pl.plot(allDates, res[0]*exp(allDates*res[1])/res[1], label='Exponential growth, total deaths.')
pl.plot(allDates, res[0]*exp(allDates*res[1]), label='Exponential growth, deaths per day.')
pl.plot(datesSinceLatest, deaths, 'x', label='Covid19 total deaths in '+country)
pl.plot(datesSinceLatest, deathsPerDay, 'x', label='Covid19 deaths per day in '+country)
pl.yscale('log')
pl.xlabel('days after '+dates[-1][:10])
pl.ylabel('deaths')
pl.legend()
pl.grid()
pl.show()
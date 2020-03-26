#These packages need to be installed to run this:
#pip3 install COVID19Py
#pip3 install requests
#pip3 install numpy
#pip3 install matplotlib
#pip3 install scipy

import matplotlib.pylab as pl
from numpy import log, exp, diff, arange, inf
from scipy.special import gammaln
from scipy.optimize import minimize
import pickle

population = {'SE':10.12e6}

country = 'SE'
#cache the results to not unnecessarily tax their server
if True:
	import COVID19Py
	covid19 = COVID19Py.COVID19(data_source="jhu") #Johns Hopkins University
	
	res = covid19.getLocationByCountryCode(country, timelines=True)

	#categories are: 'cofirmed', 'deaths', 'recovered'
	deathDict = {k:v for k,v in res[0]['timelines']['deaths']['timeline'].items() if 0<v}

	dates = sorted(deathDict.keys())
	datesSinceLatest = arange(1-len(dates),1)
	deaths=[deathDict[d] for d in dates]
	pickle.dump( (dates, datesSinceLatest, deaths), open( "cache{}.p".format(country), "wb" ) )
else:
	dates, datesSinceLatest, deaths = pickle.load( open( "cache{}.p".format(country), "rb" ) )

#append today's number if it is not yet available on the server
append=78 #
if append:
	dates.append('today')
	datesSinceLatest=arange(1-len(dates),1)
	deaths.append(append)

print('Country: '+country)
print('Latest number of deaths: {}'.format(deaths[-1]))

# number of deaths per day ~ Pois( v*exp(day*l) )
def likelihood(v, l, dates, deathsPerDay):
	return sum(deathsPerDay[i]*(log(v)+dates[i]*l)-v*exp(dates[i]*l) for i in range(len(deathsPerDay)))
	#removed constant term -gammaln(deaths[i]+1)

deathsPerDay = diff(deaths, prepend=0)
res = minimize(lambda x: -likelihood(x[0], x[1], datesSinceLatest, deathsPerDay), [1,0], bounds=[(0,inf),(0,inf)]).x
print("Doubling time: {:.2f} days".format(log(2)/res[1]))
allDates = arange(datesSinceLatest[0], 45)
pl.title('Covid19 total deaths in '+country)
pl.plot(allDates, res[0]*exp(allDates*res[1])/res[1], label='MLE fit of exponential growth')
pl.plot(datesSinceLatest, deaths, 'x', label='Actual deaths')
pl.plot(allDates[[0,-1]], 2*[population[country]], '--', label='Population before Covid19')
# pl.plot(allDates, res[0]*exp(allDates*res[1]), label='Exponential growth, deaths per day.')
# pl.plot(datesSinceLatest, deathsPerDay, 'x', label='Covid19 deaths per day in '+country)
pl.yscale('log')
pl.xlabel('days after '+dates[-1][:10])
pl.ylabel('deaths')
pl.legend()
pl.grid()
pl.show()
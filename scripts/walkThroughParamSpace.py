import p1d_arxiv
import gp_emulator
import os
import numpy as np
import matplotlib.pyplot as plt

'''
Script to pick two random points in parameter space
and walk between them plotting the fractional error
along the way, with and without temperature rescalings
'''

numPoints=200
numPairs=50
k=0.5

## Use default repo, for now just 1806 thermal only
archive_no_rescalings=p1d_arxiv.ArxivP1D(drop_tau_rescalings=True,drop_temp_rescalings=True)
archive_with_rescalings=p1d_arxiv.ArxivP1D(max_arxiv_size=2000) ## Reduce size for computation time

## IGM only emulator
paramList=["Delta2_p","mF","sigT_Mpc","gamma","kF_Mpc"]

## Initialise emulators
emu_no_rescalings=gp_emulator.GPEmulator(paramList=paramList,
                                passArxiv=archive_no_rescalings,
                                train=True)
emu_with_rescalings=gp_emulator.GPEmulator(paramList=paramList,
                                passArxiv=archive_with_rescalings,
                                train=True)

def get_walk():
        ## Pick 2 random points in parameter space
        p1=np.random.randint(len(archive_no_rescalings.data))
        p2=np.random.randint(len(archive_no_rescalings.data))
        point1={}
        point2={}

        for par in paramList:
                point1[par]=archive_no_rescalings.data[p1][par]
                point2[par]=archive_no_rescalings.data[p2][par]

        delta_pars={}
        for par in paramList:
            delta_pars[par]=(point2[par]-point1[par])/numPoints

        stepModel=dict(point1)
        fracError=np.empty(numPoints)
        fracError_res=np.empty(numPoints)
        prediction,error=emu_no_rescalings.emulate_p1d_Mpc(point1,k,return_covar=True)
        fracError[0]=np.sqrt(error)/prediction
        prediction,error=emu_with_rescalings.emulate_p1d_Mpc(point1,k,return_covar=True)
        fracError_res[0]=np.sqrt(error)/prediction

        for point in range(1,numPoints):
                for par in paramList:
                        stepModel[par]=stepModel[par]+delta_pars[par]
                        prediction,error=emu_no_rescalings.emulate_p1d_Mpc(stepModel,k,return_covar=True)
                        fracError[point]=np.sqrt(error)/prediction
                        prediction,error=emu_with_rescalings.emulate_p1d_Mpc(stepModel,k,return_covar=True)
                        fracError_res[point]=np.sqrt(error)/prediction
        return fracError,fracError_res

paths=np.empty((numPairs,numPoints))
paths_res=np.empty((numPairs,numPoints))

for aa in range(numPairs):
      paths[aa],paths_res[aa]=get_walk()  

plt.figure()
#plt.errorbar(np.linspace(0,numPoints-1,numPoints),np.mean(paths,axis=0),
#        yerr=np.std(paths,axis=0),label="No rescalings")
#plt.errorbar(np.linspace(0,numPoints-1,numPoints),np.mean(paths_res,axis=0),
#        yerr=np.std(paths_res,axis=0),label="With rescalings")
plt.plot(np.linspace(0,numPoints-1,numPoints),np.mean(paths,axis=0),label="No rescalings")
plt.plot(np.linspace(0,numPoints-1,numPoints),np.mean(paths_res,axis=0),label="With rescalings")
plt.ylabel("Fractional error")
plt.xlabel("Step number")
plt.legend()
plt.show()    
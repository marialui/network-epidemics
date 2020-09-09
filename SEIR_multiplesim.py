# !/usr/bin/python
import os, sys
import sys
import re
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random
from random import randrange
import pandas as pd

#auxiliar functions
def repeat(N, f, *args): #FUNCTION TO REPEAT THE SIMULATION N TIMES
    for i in range(N):
         yield f(*args)

#here we create a function that, given a dataframe with the results of all the simulations, will plot the spreading
#and saving the figures in a specific directory.
def plotnicely(dataframe,dir_path):
    for col in dataframe.columns:
        comp=(dataframe[col].mean())
        x = np.arange(len(comp))
        st=(dataframe[col].apply(pd.Series).std())
        plt.errorbar(x,comp, yerr=st, uplims=True, lolims=True,
                 label='uplims=True, lolims=True')
        plt.savefig('%s/RESULT_%s' % (dir_path,col))
        plt.clf()

def SEIRmodel(n, m, f):
    ba = nx.barabasi_albert_graph(n,m)  # function that given an n number of nodes,  with m edges, and f number of initial infected:
                                        # produces a random graph using Barabási-Albert preferential attachment model.
    iterationcounter = 0

    a = {'susceptible': [], 'exposed': [],'infetti': [], 'recovered': []}  #we initialize an empty dictionary in which we will store
                                                                           #the list of nodes whose attribute is respectively susceptible,
                                                                           #exposed, infected or recovered
    for i in range(n):
        ba.node[i]["state"] = "S"                            # they all start in with the susceptible state S
        (a['susceptible']).append(i)                         # so at first the susceptible list in the dictionary contains all the nodes

    # iniziamo con l'inserimento di f focolai

    for k in range(f):
        spreader = randrange(n)
        a['infetti'].append(spreader)                         # infetti will be a list of f people that has been infected
        ba.node[spreader]["state"] = "I"                      # a number f of people will have the attribute I (infected)

    andamentoI = {iterationcounter: len(a['infetti']) / n}     # initialize a dictionary in which we store the number of infected
                                                               # person over the total for each iteration
    andamentoS= {iterationcounter: len(a['susceptible']) / n}  # we do the same for susceptible
    andamentoR= {iterationcounter: len(a['recovered']) / n}    # and the same for recovered
    andamentoE = {iterationcounter: len(a['exposed']) / n}     #and for exposed

    while iterationcounter <= 100:                              # for 100 iterations
        if len(a['infetti']) % 100 == 0:
            print(len(a['infetti']))

        for person in a['infetti']:                           # per ogni spreader (persona infetta)
            spreadercontacts = list(ba.neighbors(person))     # lista di individui che hanno avuto contatto con il singolo spreader
            tau = 3 / 100                                     # percentuale di infettività
            numbernew = int((len(spreadercontacts)) * tau)           # numero di persone infettate dal singolo spreader
            newifected = random.sample(spreadercontacts, numbernew)  # lista contenente i nuovi individui infetti
            #print(newifected)
            for j in newifected:                              # for each new infected pearson
                if ba.node[j]["state"] == "S":                # if it was in a susceptible state
                    #print('j is' ,j)
                    ba.node[j]["state"] = "E"                 # now it began infected, so its attribute is I
                    a['susceptible'].remove(j)                # and will be removed from the list of susceptible people in the dictionary
                    a['exposed'].append(j)                    # so we update the infected list in the dictionary with the new infected


        iterationcounter = iterationcounter + 1               # this is a counter of iterations that give us a sense of the
                                                              # period of time
        sigma = 1 / 14                                      #this is the latency rate
        ni = int((len(a['exposed'])) * sigma)                 # ni= number of infected people that are also infectious
        infectious = a['exposed'][:ni]
        for inf in infectious:
            ba.node[inf]["state"] = "I"                        #so we give the I attribute th the infected nodes that now are infectious
        a['infetti'].extend(infectious)                        #and we update the list of infected people in the dictionary
        a['exposed'] = a['exposed'][ni:]                       #we remove the first ni elements from the exposed list

        beta = 10 / 100                                       #this is a recovery rate
        r = int((len(a['infetti'])) * beta)                   # r= number of recovered people
        newrecovered = a['infetti'][:r]                       #earlier infected people are more likely to recover earlier
                                                              #so we put the first r element of the infected list in the recovered list

        for el in newrecovered:
            ba.node[el]["state"] = "R"                        #so we give the R attribute th the recovered nodes
        a['recovered'].extend(newrecovered)                   #and we update the list of recovered people in the dictionary
        a['infetti'] = a['infetti'][r:]                       #we remove the first r elements from the infected list

        andamentoI[iterationcounter] = len(a['infetti']) / n       # here we uptade the dictionary andamento we created with
                                                                   # the number of infected over the total
                                                                   # and the corrisponding iteration
        andamentoS[iterationcounter] = len(a['susceptible']) / n
        andamentoR[iterationcounter] = len(a['recovered']) / n
        andamentoE[iterationcounter] = len(a['exposed']) / n
#IMPORTANT>>>>>>> HERE WE CONVERT THE DICTIONARIES WE CREATED INTO ARRAYS
    andamentoI = np.array(list(andamentoI.values()))
    andamentoR = np.array(list(andamentoR.values()))
    andamentoE = np.array(list(andamentoE.values()))
    andamentoS = np.array(list(andamentoS.values()))

    return (andamentoI,andamentoR,andamentoE,andamentoS)

if __name__ == "__main__":
    path='/home/maria/Desktop/network epidemics/100sim'

    nodes = 10000  # Number of nodes
    links = 25  # Number of initial links
    focolai = 3  # numero di focolai
    #SEIRmodel(nodes, links, focolai)
    N=100 #times the simulation will run

    res=list(repeat(N, SEIRmodel, nodes, links, focolai) )#HERE WE ARE DOING THE SIMULATION 100 TIMES and we store the result in res
    res=pd.DataFrame(res) #here we store the result of the simulation in a dataframe re and we set the columns name
    res.columns = ['I', 'R','E','S']
    plotnicely(res,path)



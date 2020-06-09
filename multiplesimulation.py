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

#function needed to plot, takes a range of values for which we are testing m
#takes X that can be either E,R,I or S
def plotnicely(X,num):
    nc=[]
    w={'E':'exposed','R':'recovered','I':'infected','S':'susceptible'}
    #for each simulation (num=number of simulations)
    for v in range (num):
        list = globals()['andamento%s_ %s' % (X,v)].items()
    #we extraxt the coordinates for the spreading of X
        x, y = zip(*list)
    #create an array y containing all the y coordinates for a specific simulation
        y=np.asarray(y)
    #append all the arrays of all the simulations in a single bigger array
        nc.append(y)
    #extract the mean line
    mean_y = np.mean(nc, axis=0)
    #and the standard deviation
    yerr = np.std(nc, axis=0)

    #so we plot the mean line
    plt.plot(x, mean_y, label="mean spreading over 30 simulations")
    plt.xlabel('Time')
    plt.legend(bbox_to_anchor=(0, 1), loc='upper left', ncol=3)
    plt.suptitle("%s curve" %(w[X]))
    plt.savefig('%s_mean_spreading.png'%(w[X]))
    plt.clf()

    #plot the line in form of error bar
    plt.errorbar(x, mean_y, label="mean spreading over 30 simulations", yerr=yerr, linestyle='None', marker='^')
    plt.xlabel('Time')
    plt.legend(bbox_to_anchor=(0, 1), loc='upper left', ncol=3)
    plt.suptitle("%s curve" %(w[X]))
    plt.savefig('%s_mean_spreading1.png' % (w[X]))
    plt.clf()

    return(mean_y) #return the the associated mean y values for the compartment X

######    SEIR model :    ######
# In this category of models, individuals experience a long incubation duration (the “exposed” category),
# such that the individual is infected but not yet infectious.
# The incubation rate, sigma, is the rate of latent individuals becoming infectious
# (average duration of incubation is 1/sigma).

# Barabási-Albert --> A graph of n nodes is grown by attaching new nodes each with m edges
# that are preferentially attached to existing nodes with high degree.

def SEIRmodel(n, m, f,simulations):
 #---> this is the file where we will store the resulting tables
    for l in range(simulations): #it iterates over the number of simulation
        ba = nx.barabasi_albert_graph(n,m)
        # function that given an n number of nodes,  with m edges, and f number of initial infected:
        # produces a random graph using Barabási-Albert preferential attachment model.
        iterationcounter = 0


        # we initialize an empty dictionary in which we will store
        # the list of nodes whose attribute is respectively susceptible,
        # exposed, infected or recovered
        a = {'susceptible': [], 'exposed': [], 'infetti': [], 'recovered': []}

        # they all start in with the susceptible state S
        # so at first the susceptible list in the dictionary contains all the nodes:
        for i in range(n):
            ba.node[i]["state"] = "S"
            (a['susceptible']).append(i)


        # iniziamo con l'inserimento di f focolai
        for k in range(f):
            spreader = randrange(n)
            a['infetti'].append(spreader)     # infetti will be a list of f people that has been infected
            ba.node[spreader]["state"] = "I"  # a number f of people will have the attribute I (infected)


        # initialize a dictionary in which we store the number of infected
        # person over the total for each iteration
        globals()['andamentoI_ %s' % (l)] = {iterationcounter: len(a['infetti']) / n}

        # we do the same for susceptible
        globals()['andamentoS_ %s' % (l)] = {iterationcounter: len(a['susceptible']) / n}

        # and the same for recovered
        globals()['andamentoR_ %s' % (l)] = {iterationcounter: len(a['recovered']) / n}

        # and for exposed
        globals()['andamentoE_ %s' % (l)] = {iterationcounter: len(a['exposed']) / n}


# for 100 iterations (epoche)
        while iterationcounter <= 100:
            if len(a['infetti']) % 100 == 0:
                print(len(a['infetti']))

            for person in a['infetti']:                         # per ogni spreader (persona infetta)
                spreadercontacts = list(ba.neighbors(person))   # lista di individui che hanno avuto contatto
                                                                                      # con il singolo spreader
                tau = 3 / 100                                                         # percentuale di infettività
                numbernew = int((len(spreadercontacts)) * tau)                        # numero di persone infettate dal singolo spreader
                newifected = random.sample(spreadercontacts, numbernew)               # lista contenente i nuovi individui infetti

                for j in newifected:                             # for each new infected pearson
                    if ba.node[j]["state"] == "S":               # if it was in a susceptible state
                        ba.node[j]["state"] = "E"                # now it began infected, so its attribute is I
                        a['susceptible'].remove(j)               # and will be removed from the list of susceptible
                                                                 # people in the dictionary
                        a['exposed'].append(j)                   # so we update the infected list in the dictionary
                                                                 # with the new infected


            # this is a counter of iterations that give us a sense of the period of time
            iterationcounter = iterationcounter + 1
            sigma = 1 / 14                                      # this is the latency rate
            ni = int((len(a['exposed'])) * sigma)               # ni= number of infected people that are also infectious
            infectious = a['exposed'][:ni]
            for inf in infectious:
                ba.node[inf]["state"] = "I"                     # so we give the I attribute th the infected nodes that
                                                                # now are infectious
            a['infetti'].extend(infectious)                     # and we update the list of infected people in the dictionary
                                                                # we remove the first ni elements from the exposed list
            a['exposed'] = a['exposed'][ni:]

            beta = 10 / 100                                     # this is a recovery rate
            r = int((len(a['infetti'])) * beta)                 # r= number of recovered people
            newrecovered = a['infetti'][:r]                     # earlier infected people are more likely to recover earlier
                                                                # so we put the first r element of the infected list in the
                                                                #recovered list

            for el in newrecovered:
                ba.node[el]["state"] = "R"                      # so we give the R attribute th the recovered nodes
            a['recovered'].extend(newrecovered)                 # and we update the list of recovered people in the dictionary
                                                                # we remove the first r elements from the infected list
            a['infetti'] = a['infetti'][r:]

            # here we uptade the dictionary andamento we created with
            # the number of infected over the total and the corrisponding iteration:
            globals()['andamentoI_ %s' % (l)][iterationcounter]= len(a['infetti']) / n
            globals()['andamentoS_ %s' % (l)][iterationcounter]= len(a['susceptible']) / n
            globals()['andamentoR_ %s' % (l)][iterationcounter]= len(a['recovered']) / n
            globals()['andamentoE_ %s' % (l)][iterationcounter]= len(a['exposed']) / n

    data={}

 # let's plot the spreading of the epidemics over time:
    COMPARTMENTS=['I','E','R','S']
    for comp in COMPARTMENTS:
         data[comp]= plotnicely(comp,simulations) # this dictionary will be updated in a way that we have
 #{'I': mean values array, 'E': mean values array....and so on}
 #we will finally collect all these informations in a single dataframe df
    df = pd.DataFrame(data)

    return(df)  #----------> so at the end of the story the function will return the dataframe collecting
                             #all the mean values for each compartment (the mean has been computed over 30 simulations)


if __name__ == "__main__":
    nodes = 10000  # Number of nodes
    links = (20)  # Number range of number of links to test
    focolai = 3  # numero di focolai
    k = 30
    print(SEIRmodel(nodes, links, focolai,k))
    #number of simulations


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
def plotnicely(start,end,X) :
    w={'E':'exposed','R':'recovered','I':'infected','S':'susceptible'}
    for v in range (start,end+1):
        list = globals()['andamento%s_ %s' % (X,v)].items()
        x, y = zip(*list)
        plt.plot(x, y, label="m= %s" % (v))
        plt.xlabel('Time')
    plt.legend(bbox_to_anchor=(0, 1), loc='upper left', ncol=3)
    plt.suptitle("%s curves" %(w[X]))
    plt.savefig('%s.png'%(w[X]))
    plt.clf()
######    SEIR model :    ######
# In this category of models, individuals experience a long incubation duration (the “exposed” category),
# such that the individual is infected but not yet infectious.
# The incubation rate, sigma, is the rate of latent individuals becoming infectious
# (average duration of incubation is 1/sigma).

# Barabási-Albert --> A graph of n nodes is grown by attaching new nodes each with m edges
# that are preferentially attached to existing nodes with high degree.

def SEIRmodel(n, contacts, f):
    Result= open('/home/maria/Desktop/network epidemics/RESULT.txt','a') #---> this is the file where we will store the resulting tables
    for m in range(contacts[0], contacts[1]+1):
        Result.write('\n\nm is --> %s\n\n' % (m))

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
        globals()['andamentoI_ %s' % (m)] = {iterationcounter: len(a['infetti']) / n}

        # we do the same for susceptible
        globals()['andamentoS_ %s' % (m)] = {iterationcounter: len(a['susceptible']) / n}

        # and the same for recovered
        globals()['andamentoR_ %s' % (m)] = {iterationcounter: len(a['recovered']) / n}

        # and for exposed
        globals()['andamentoE_ %s' % (m)] = {iterationcounter: len(a['exposed']) / n}


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
            globals()['andamentoI_ %s' % (m)][iterationcounter]= len(a['infetti']) / n
            globals()['andamentoS_ %s' % (m)][iterationcounter]= len(a['susceptible']) / n
            globals()['andamentoR_ %s' % (m)][iterationcounter]= len(a['recovered']) / n
            globals()['andamentoE_ %s' % (m)][iterationcounter]= len(a['exposed']) / n


        #here we create the table containing the values referring to a specific m.
        #the values we are reporting are :
        # the number of susceptible over the total for each iteration (column S)
        # the number of exposed over the total for each iteration (column E)
        # the number of recovered over the total for each iteration (column R)
        # the number of infected over the total for each iteration (column I)

        df= pd.DataFrame.from_dict(globals()['andamentoS_ %s' % (m)], orient='index',columns=['S'])
        df1 = pd.DataFrame.from_dict(globals()['andamentoE_ %s' % (m)], orient='index',columns=['E'])
        df2 = pd.DataFrame.from_dict(globals()['andamentoI_ %s' % (m)], orient='index',columns=['I'])
        df3 = pd.DataFrame.from_dict(globals()['andamentoR_ %s' % (m)], orient='index', columns=['R'])

        #so firstly we create the column (df stands for susceptible, df1 for exposed, df2 for infected and df3 for recoverd)
        #then we join all the columns in a single table
        table= ((df.join(df1)).join(df2)).join(df3)

        #and we writ the table on Result that is a txt file
        table.to_csv(Result, index=True, header=True, sep=' ')


# let's plot the spreading of the epidemics over time:
    COMPARTMENTS=['I','E','R','S']
    for comp in COMPARTMENTS:
        plotnicely(contacts[0],contacts[1],comp)

if __name__ == "__main__":
    nodes = 10000  # Number of nodes
    links = (5, 25)  # Number range of number of links to test
    focolai = 3  # numero di focolai
    SEIRmodel(nodes, links, focolai)

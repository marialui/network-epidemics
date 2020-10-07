import os, sys
import sys
import re
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random
from random import randrange
import pandas as pd


def gen_age(
        statistics):  # this is a function that given a csv file with stat information on gender and age on population, returns a table
    # Of percentage defining each class of subjects
    p_df = pd.read_csv("%s" % statistics)
    p_df = p_df.set_index('Age')
    # p_df['perc-M']=round((p_df['M']/p_df['M'].sum())*100,2)
    # p_df['perc-F'] = round(p_df['F'] / p_df['F'].sum()*100,2)
    # p_df=p_df.reindex(p_df.index.values.tolist() + ['Total'])
    # total= p_df['M'].sum()+p_df['F'].sum()
    total = (p_df['F'].sum() + p_df['M'].sum())
    p_df['M'] = round((p_df['M'] / total) * 100, 2)
    p_df['F'] = round((p_df['F'] / total) * 100, 2)
    p_df.at['95-99','F']=p_df.at['95-99','F'] +p_df.at['100+','F'] #eliminate last row
    p_df=p_df.iloc[:-1]
    p_df.rename(index={'95-99': '90-105'}, inplace=True)

    return p_df

def covid_statistics(tabella,nodes):      #it takes in input the number of nodes and, using the statistics from the table
                                            #gives in output the number of death and case for each age and gender
    p_df1 = pd.read_csv("%s" %tabella)
    p_df1 = p_df1.set_index('age_classes')
    total1 = (p_df1['total_cases'].sum())
    p_df1['M']=p_df1['male_deaths'].div(p_df1['male_cases'])
    p_df1['F'] = p_df1['female_deaths'].div(p_df1['female_cases'])

    new=round(p_df1*100)
    new.rename(index={'>90': '90-105'}, inplace=True)
    new.loc[ '90-105',:]=(new.tail(2)).sum()
    new=new.iloc[:-1]

    return new


# this function should assign the attibute of age and gender to the network on the basis of the percentages
# derived from the previous function.

def population_attribute(table, network,table1):
    t = len(network)
    print(t)
    table1=table1[table1.columns[-2:]]
    df2 = table1.replace(table1, 0)
   # df2 = pd.DataFrame().reindex_like(table)
    diz=df2.to_dict('index')

    nodi_tmp = {i: object() for i in range(t)}  # temporary dictionary containing all the nodes
    nodi = {}  # final dictionary will contain: node number: [sex,age]
    # total number of nodes
    for age in (list(table.index.values)):
        for sex in (list(table.columns)):
            perc = table.loc[age][
                sex]  # this is the fraction (percentage) of population that will have a specific sex and age
            # rows= age , col= sex
            n = int(round(perc * t / 100))
            while n != 0:  # finchè non avremmo aggiunto tutti gli n nodi di una categoria
                nodo = randrange(t)  # estrai random un nodo
                if nodo in nodi_tmp:  # se è presente sul dizionario con tutti i nodi
                    n = n - 1
                    e=re.findall(r'\d+',age)
                    età=randrange(int(e[0]),int(e[1]))
                    nodi[str(nodo)] = [sex, età, 'S']  # assegna sesso e età al nodo al dizionario definitivo
                    # note: we added the susceptible state since all of them start in this compartmet
                    del nodi_tmp[nodo]  # cancella il nodo dal dizionario provvisorio
                    for anno in diz:
                        anno1=anno.split('-')
                        if int(anno1[0]) <= età <= int(anno1[1]):
                            if diz[anno][sex]==0:
                                lista=[str(nodo)]
                                diz[anno][sex]=lista
                            else:
                                (diz[anno][sex]).append(str(nodo))

    print(len(nodi))
    return (nodi, diz )  #dictionary contains the age range: sex:[list of nodes] , is a dictionary of dictionaries


def fight_or_flight(diz, prob):
    died ={} #this will be the dictionaries in which we will store the survivedor the dead ones (D)
    tabella=prob[prob.columns[-2:]]  #tabella contains the death percentage for male and female for each range of age.
    for ages in diz:
        for sex in diz[ages]:
            f=tabella.loc[ages][sex] #frequency of death
            total=len(diz[ages][sex]) # total number for a category
            n=int((total/100)*f)
            #print(total, )
            lista=random.sample(range(0,total), n) #index of the death node in the list that has to be deleted from the list and added to the
            for i in (lista):
                died[diz[ages][sex][i]]=0            #died dictionary will finally contain all the nodes that will die
    return died


def SEIRmodel(n, m, f, path):
    a = {'susceptible': [], 'exposed': [], 'infetti': [],'recovered': []}  # we initialize an empty dictionary in which we will store
    # the list of nodes whose attribute is respectively susceptible,
    # exposed, infected or recovered

    ba = nx.barabasi_albert_graph(n,m)  # function that given an n number of nodes,  with m edges, and f number of initial infected:
    # produces a random graph using Barabási-Albert preferential attachment model.
    iterationcounter = 0
    tab = gen_age(path+"Italy-2019.csv")
    covid_tab=covid_statistics(path+"covid_gender_age.csv",n)
    D_result=population_attribute(tab, ba,covid_tab)
    dizionario=D_result[0]
    diz2=D_result[1]
    will_die=fight_or_flight(diz2, covid_tab) ############################# THIS IS A DICTIONARY CONTAINING THE NODE
    print(will_die)                                                                       #NUMBER THAT WILL DIE
    lista_attributi = ['gender', 'age', 'state']
    #print(dizionario)
    # we can add network attributes from the dictionary dizionario we just created
    for key in dizionario:
        for j in range(len(lista_attributi)):
            ba.node[int(key)][lista_attributi[j]] = dizionario[key][j]  # per ogni attributo della lista, prende il valore dal dizionario
        (a['susceptible']).append(int(key))
    #print(dizionario, len(a['susceptible']))
        # they all start in with the susceptible state S
        # so at first the susceptible list in the dictionary contains all the nodes

    # iniziamo con l'inserimento di f focolai

    for k in range(f):
        spreader = randrange(n)
        a['infetti'].append(spreader)  # infetti will be a list of f people that has been infected
        ba.node[spreader]["state"] = "I"  # a number f of people will have the attribute I (infected)


    andamentoI = {iterationcounter: len(a['infetti']) / n}  # initialize a dictionary in which we store the number of infected
    # person over the total for each iteration
    andamentoS = {iterationcounter: len(a['susceptible']) / n}  # we do the same for susceptible
    andamentoR = {iterationcounter: len(a['recovered']) / n}  # and the same for recovered
    andamentoE = {iterationcounter: len(a['exposed']) / n}  # and for exposed

    while iterationcounter <= 100:  # for 100 iterations
        if len(a['infetti']) % 100 == 0:
            print(len(a['infetti']))

        for person in a['infetti']:  # per ogni spreader (persona infetta)
            spreadercontacts = list(
                ba.neighbors(person))  # lista di individui che hanno avuto contatto con il singolo spreader
            tau = 3 / 100  # percentuale di infettività
            numbernew = int((len(spreadercontacts)) * tau)  # numero di persone infettate dal singolo spreader
            newifected = random.sample(spreadercontacts, numbernew)  # lista contenente i nuovi individui infetti
            # print(newifected)
            for j in newifected:  # for each new infected pearson
                if ba.node[j]["state"] == "S":  # if it was in a susceptible state
                    # print('j is' ,j)
                    ba.node[j]["state"] = "E"  # now it began infected, so its attribute is I
                    a['susceptible'].remove(
                        j)  # and will be removed from the list of susceptible people in the dictionary
                    a['exposed'].append(j)  # so we update the infected list in the dictionary with the new infected

        iterationcounter = iterationcounter + 1  # this is a counter of iterations that give us a sense of the
        # period of time
        sigma = 1 / 14  # this is the latency rate
        ni = int((len(a['exposed'])) * sigma)  # ni= number of infected people that are also infectious
        infectious = a['exposed'][:ni]
        for inf in infectious:
            ba.node[inf]["state"] = "I"  # so we give the I attribute th the infected nodes that now are infectious
        a['infetti'].extend(infectious)  # and we update the list of infected people in the dictionary
        a['exposed'] = a['exposed'][ni:]  # we remove the first ni elements from the exposed list

        beta = 10 / 100  # this is a recovery rate
        r = int((len(a['infetti'])) * beta)  # r= number of recovered people
        newrecovered = a['infetti'][:r]  # earlier infected people are more likely to recover earlier
        # so we put the first r element of the infected list in the recovered list

        for el in newrecovered:
            ba.node[el]["state"] = "R"  # so we give the R attribute th the recovered nodes
        a['recovered'].extend(newrecovered)  # and we update the list of recovered people in the dictionary
        a['infetti'] = a['infetti'][r:]  # we remove the first r elements from the infected list

        andamentoI[iterationcounter] = len(a['infetti']) / n  # here we uptade the dictionary andamento we created with
        # the number of infected over the total
        # and the corrisponding iteration
        andamentoS[iterationcounter] = len(a['susceptible']) / n
        andamentoR[iterationcounter] = len(a['recovered']) / n
        andamentoE[iterationcounter] = len(a['exposed']) / n

    #print(andamentoI,andamentoR, andamentoS,andamentoE)
    # let's plot the spreading of the epidemics over time

    #list1 = andamentoI.items()  # return a list of tuples : (infected,iteration)
    #x, y = zip(*list1)  # unpack a list of pairs into two tuples
    #list2 = andamentoS.items()
    #x, y2 = zip(*list2)
    #list3 = andamentoR.items()
    #x, y3 = zip(*list3)
    #list4 = andamentoE.items()
    #x, y4 = zip(*list4)




    plt.xlabel('Time')
    plt.plot(x, y,label="Infected")
    plt.plot(x, y2,label="Susceptible")
    plt.plot(x, y3,label="Recovered")
    plt.plot(x, y4, label="Exposed")


    leg = plt.legend(loc='best', ncol=2, mode="expand", shadow=True, fancybox=True)
    leg.get_frame().set_alpha(0.5)
    infezione = plt.show()
    return (infezione)  # the function returns the plot of the epidemic spreading


if __name__ == "__main__":
    nodes = 10000  # Number of nodes
    links = 25  # Number of initial links
    focolai = 3  # numero di focolai
    path = "/home/maria/Desktop/network epidemics/"

    SEIRmodel(nodes, links, focolai, path)

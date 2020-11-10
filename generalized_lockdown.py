from networkx.generators.degree_seq import expected_degree_graph
import datetime
import matplotlib.dates as mdates
from datetime import date, timedelta
import collections
import os, sys
import sys
import re
import numpy as np
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import random
from random import randrange
import pandas as pd
import pylab
import seaborn as sns
import bisect

def quarantine_period(sdate,edate):       #this function takes 2 argouments: starting date of a lockdown and ending date
    delta_ = edate - sdate  # as timedelta
    lock={}
    for i in range(delta_.days + 1):
        day = sdate + timedelta(days=i)
        lock[day]=0
    return lock

def network_creation (path,t):     #t number of nodes
    lista_attributi = ['gender', 'age', 'state']
    w = []
    p_df= covid_statistics(path+"covid_gender_age.csv")
    p_df1 = p_df[p_df.columns[-2:]]
    p_df1 = p_df1.replace(p_df1, 0)
    diz = p_df1.to_dict('index')
    df_con = pd.read_csv(path+"contacts_agegroups.csv", index_col=0, names=['contacts'], header=None)
    df_con = round(df_con.sort_values(by=['contacts']))
    print('The number of daily contat for each age group is:\n',df_con)
    table= gen_age(path+"Italy-2019.csv")
    #print(diz)
    nodi = {}  # final dictionary will contain: node number: [sex,age,State]
    ind= -1
    for age in (list(table.index.values)):
        e = re.findall(r'\d+', age)
        età = randrange(int(e[0]), int(e[1]))
        for sex in (list(table.columns)):

            perc = table.loc[age][sex]  # this is the fraction (percentage) of population that will have a specific sex and age
                                        # rows= age , col= sex
            n = int(round(perc * t / 100))
            for i in range(len(df_con)):
                N=df_con.index[i].split('-')
                if int(N[0]) <= età <= int(N[1]):
                    w1 = [df_con.iloc[i][0] for k in range(n)]
                    for el in w1:
                        ind=ind+1
                        nodi[ind]=[sex,età, 'S']
                        for ages in diz:
                            ages1=ages.split('-')
                            if int(ages1[0]) <=età<= int(ages1[1]):
                                if diz[ages][sex]==0:
                                    diz[ages][sex]=[ind]
                                else:
                                    diz[ages][sex].append(ind)

                    w.extend(w1)

    #HERE WE CREATED W THAT IS A LIST CONTAINING THE NUMBER OF CONTACTS FOR EACH NODE
    G = expected_degree_graph(w)  # configuration model
    print("Degree histogram")
   # dh = nx.degree_histogram(G)
    #print(dh)
    #print("degree (#nodes) ****")
    #for i, d in enumerate(dh):
     #   print(f"{i:2} ({d:2}) {'*'*d}")
    degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # degree sequence
    degreeCount = collections.Counter(degree_sequence)
    deg, cnt = zip(*degreeCount.items())

    #fig, ax = plt.subplots()
    #plt.bar(deg, cnt, width=0.80, color="b")

    #plt.title("Degree Histogram")
    #plt.ylabel("Count")
    #plt.xlabel("Degree")
    #ax.set_xticks([d + 0.4 for d in deg])
    #ax.set_xticklabels(deg)
    #plt.show()
    #HERE WE ASSIGN ALL THE ATTRIBUTES (AGE, GENDER, AND STATE) FOR EACH NODE OF THE NETWORK
    for key in nodi:
        for j in range(len(lista_attributi)):
            G.nodes[int(key)][lista_attributi[j]] = nodi[key][j]  # per ogni attributo della lista, prende il valore dal dizionario
    return(G,diz,p_df)

def gen_age(statistics):  # this is a function that given a csv file with stat information on gender and age on population, returns a table
    # Of percentage defining each class of subjects
    p_df = pd.read_csv("%s" % statistics)
    p_df = p_df.set_index('Age')
    total = (p_df['F'].sum() + p_df['M'].sum())
    p_df['M'] = round((p_df['M'] / total) * 100, 2)
    p_df['F'] = round((p_df['F'] / total) * 100, 2)
    p_df.at['95-99','F']=p_df.at['95-99','F'] +p_df.at['100+','F'] #eliminate last row
    p_df=p_df.iloc[:-1]
    p_df.rename(index={'95-99': '90-105'}, inplace=True)
    return (p_df)


def fight_or_flight(diz, prob):
    died ={} #this will be the dictionaries in which we will store the survivedor the dead ones (D)
    tabella=prob[prob.columns[-2:]]  #tabella contains the death percentage for male and female for each range of age.
    for ages in diz:
        for sex in diz[ages]:
            f=tabella.loc[ages][sex] #frequency of death
            total=len(diz[ages][sex]) # total number for a category
            n=int((total/100)*f)
            lista=random.sample(range(0,total), n) #index of the death node in the list that has to be deleted from the list and added to the
            for i in (lista):
                died[diz[ages][sex][i]]=0            #died dictionary will finally contain all the nodes that will die
   # print('died are', died)
    return died

def covid_statistics(tabella):  # it takes in input the number of nodes and, using the statistics from the table
# gives in output the number of death and case for each age and gender
    p_df1 = pd.read_csv("%s" % tabella)
    p_df1 = p_df1.set_index('age_classes')
    p_df1['M'] = p_df1['male_deaths'].div(p_df1['male_cases'])
    p_df1['F'] = p_df1['female_deaths'].div(p_df1['female_cases'])

    new = round(p_df1 * 100)
    new.rename(index={'>90': '90-105'}, inplace=True)
    new.loc['90-105', :] = (new.tail(2)).sum()
    new = new.iloc[:-1]
    return new


def SEIRmodel(n, f, path,lockdays):
    net=network_creation(path, n)
    ba=net[0]

    a = {'susceptible': [], 'exposed': [], 'infetti': [],'recovered': [],'died':[]}  # we initialize an empty dictionary in which we will store
    # the list of nodes whose attribute is respectively susceptible,
    # exposed, infected , recovered or died
    for i in range(n):               # they all start in with the susceptible state S
        (a['susceptible']).append(i)                         # so at first the susceptible list in the dictionary contains all the nodes

    diz2 = net[1]
    covid_tab=net[2]
    will_die=fight_or_flight(diz2, covid_tab) ############################# THIS IS A DICTIONARY CONTAINING THE NODE

    for k in range(f):
        spreader = randrange(n)
        a['infetti'].append(spreader)  # infetti will be a list of f people that has been infected
        ba.nodes[spreader]["state"] = "I"  # a number f of people will have the attribute I (infected)

    start_date = datetime.date(2020, 1, 30)
    end_date = date.today()  #datetime.date(year, month, day)
    delta = datetime.timedelta(days=1)
    andamentoI = {start_date: len(a['infetti']) / n}  # initialize a dictionary in which we store the number of infected
    # person over the total for each iteration
    andamentoS = {start_date: len(a['susceptible']) / n}  # we do the same for susceptible
    andamentoR = {start_date: len(a['recovered']) / n}  # and the same for recovered
    andamentoE = {start_date: len(a['exposed']) / n}  # and for exposed
    andamentoD = {start_date: len(a['died']) / n}  # and for death


    while start_date <= end_date:  # for 100 iterations
        if len(a['infetti']) % 100 == 0:
            print(len(a['infetti']))

        for person in a['infetti']:  # per ogni spreader (persona infetta)
            if start_date in lockdays:
                spreadercontacts_= list(ba.neighbors(person))
                random.shuffle(spreadercontacts_)
                spreadercontacts=spreadercontacts_[int(len(spreadercontacts_) * .70): int(len(spreadercontacts_) * 1)]

            else:
                spreadercontacts = list(ba.neighbors(person))  # lista di individui che hanno avuto contatto con il singolo spreader
            tau = 7/ 100  # percentuale di infettività
            numbernew = int((len(spreadercontacts)) * tau)  # numero di persone infettate dal singolo spreader
            newifected = random.sample(spreadercontacts, numbernew)  # lista contenente i nuovi individui infetti
            #
            #print(newifected)
            for j in newifected:  # for each new infected pearson
                if ba.nodes[j]["state"] == "S":  # if it was in a susceptible state
                    # print('j is' ,j)
                    ba.nodes[j]["state"] = "E"  # now it began infected, so its attribute is I
                    a['susceptible'].remove(j)  # and will be removed from the list of susceptible people in the dictionary
                    a['exposed'].append(j)  # so we update the infected list in the dictionary with the new infected

        start_date += delta  # this is a counter of iterations that give us a sense of the
        # period of time
        sigma = 1 / 14  # this is the latency rate
        ni = int((len(a['exposed'])) * sigma)  # ni= number of infected people that are also infectious
        infectious = a['exposed'][:ni]
        for inf in infectious:
            ba.nodes[inf]["state"] = "I"  # so we give the I attribute th the infected nodes that now are infectious
        a['infetti'].extend(infectious)  # and we update the list of infected people in the dictionary
        a['exposed'] = a['exposed'][ni:]  # we remove the first ni elements from the exposed list

        beta = 10 / 100  # this is a recovery rate
        r = int((len(a['infetti'])) * beta)  # r= number of recovered people
        newrecovered = a['infetti'][:r]  # earlier infected people are more likely to recover earlier
        # so we put the first r element of the infected list in the recovered list

        for el in newrecovered:
            if el in will_die:
                ba.nodes[el]["state"] = "D"
                a['died'].append(el)
            else:
                ba.nodes[el]["state"] = "R"  # so we give the R attribute th the recovered nodes
                a['recovered'].append(el)  # and we update the list of recovered people in the dictionary
        a['infetti'] = a['infetti'][r:]  # we remove the first r elements from the infected list
        andamentoD[start_date] = len(a['died']) / n
        andamentoI[start_date] = len(a['infetti']) / n  # here we uptade the dictionary andamento we created with
                                                                # the number of infected over the total
                                                                # and the corrisponding iteration
        andamentoS[start_date] = len(a['susceptible']) / n
        andamentoR[start_date] = len(a['recovered']) / n
        andamentoE[start_date] = len(a['exposed']) / n
        #print('inf,death',len(a['infetti']),len(a['died']))
    # let's plot the spreading of the epidemics over time

    list1 = andamentoI.items()  # return a list of tuples : (infected,iteration)
    x, y = zip(*list1)  # unpack a list of pairs into two tuples
    list2 = andamentoS.items()
    x, y2 = zip(*list2)
    list3 = andamentoR.items()
    x, y3 = zip(*list3)
    list4 = andamentoE.items()
    x, y4 = zip(*list4)
    list5 = andamentoD.items()
    x, y5 = zip(*list5)

    datatable= pd.DataFrame((list(zip(y, y2, y3,y4,y5))),columns = ['I', 'S', 'R','E','D'],index=x)
    print(datatable)
    datatable.to_csv(r'/Users/marilu/PycharmProjects/networkepidemics/generalized_lockdown_results.csv', index=True, header=True)
    fig = plt.figure()
    plt.xlabel('Time')
    plt.plot(x, y,label="Infected")
    plt.plot(x, y2,label="Susceptible")
    plt.plot(x, y3,label="Recovered")
    plt.plot(x, y4, label="Exposed")
    plt.plot(x, y5, label="Death")
    leg = plt.legend(loc='upper left'	, ncol=2, mode="expand", shadow=True, fancybox=True)
    leg.get_frame().set_alpha(0.5)
    ax = plt.gca()
    ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    fig.autofmt_xdate()
    fig.savefig(path+'generalized_lockdown', dpi=fig.dpi)

    plt.axis([datetime.date(2020, 1, 30), date.today(), 0, 0.4])
    plt.savefig(path+'generalized_lockdown(zoomin)')

if __name__ == "__main__":
    Nodes = 100000  # Number of nodes
    #links = 25  # Number of initial links
    focolai = 100 # numero di focolai
    path = "/Users/marilu/PycharmProjects/networkepidemics/"
    start= date(2020, 4, 9)  # start date
    stop = date(2020, 5, 18)  # end date
    lockdown=quarantine_period(start,stop)
    SEIRmodel(Nodes,focolai,path,lockdown)


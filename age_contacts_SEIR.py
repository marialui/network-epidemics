import os, sys
import sys
import re
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random
from random import randrange
import pandas as pd
import pylab
import seaborn as sns
import bisect


def common_data(list1, list2):
    x=list1.split('-')[1]
    y=list2.split('-')[0]
    result = False

    # traverse in the 1st list
   # for x in list1:

        # traverse in the 2nd list
    #    for y in list2:

            # if one common
    if x == y:
        result = True
        return result

    return result
def nothing_in_common(list1,list2, misch):
    lista1=list1.split('-')
    lista2=list2.split('-')
    result = True
    # traverse in the 1st list
    for x in lista1:

    # traverse in the 2nd list
        for y in lista2:

    # if one common
            if x == y:
                result = False
    if result:
        misch.append(list1)
    return misch



def find_key(input_dict, value):
    return next((k for k, v in input_dict.items() if v == value), None)

def range_f(lista):
    out=[]
    for e in range(len (lista)):
        if e < len(lista)-1:
            stringa= str(lista[e])+'-'+str(lista[e+1])
            out.append(stringa)
    return(out)

def contact_population(contacts,ba):  #it gives a statistics on the number of contacts for each groups of different ages
    df_con = pd.read_csv("%s" %contacts,index_col=0, names=['contacts'], header=None)
    df_con=df_con.sort_values(by=['contacts'])
    max_c=0
    min_c=10000
     #contains respectively few edges nodes, mid edges nodes, and many edges nodes

    lista=[]
    for node in ba.nodes():
        bisect.insort(lista, len(ba.edges(int(node))))

        if len(ba.edges(int(node))) > max_c:
            max_c=len(ba.edges(int(node)))

        if len(ba.edges(int(node))) < min_c:
            min_c=len(ba.edges(int(node)))

    edges_numb=[]
    for j in range (0,len(lista),int(len(lista)/3)):
        edges_numb.append(lista[j])




    edges_number= range_f(edges_numb) # in gives 3 intervals of contact numbers that characterized the network
    #print('edges',edges_number)
                                           #so that we can divide the nodes with just few nodes, from the ones that  have a mid number of edges or a lor

    cont_dicts = {}
    for el in edges_number:
        cont_dicts[el] = {}
    contatti=[list(df_con.index[:3]),list(df_con.index[3:7]),list(df_con.index[7:])]
    print('contatti is', contatti)
    d={}                                 ######here it will be a dictionary containint 'age group' : number of edges of the node

    for m in range (len(contatti)):
        c = {k:(edges_number[m] )for k in contatti[m]}
        d.update(c)

    for node in ba.nodes():

        for key in cont_dicts:
            #print('the key we are examining is ', key)
            if int(key.split('-')[0])<=len(ba.edges(int(node))) <= int(key.split('-')[1]):
                #print('the number of node contacts is smaller than',key, 'so we update the dictionary')
                cont_dicts[key][node]=0
                break


    return (d, cont_dicts)


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

def covid_statistics(tabella):      #it takes in input the number of nodes and, using the statistics from the table
                                            #gives in output the number of death and case for each age and gender
    p_df1 = pd.read_csv("%s" %tabella)
    p_df1 = p_df1.set_index('age_classes')
    p_df1['M']=p_df1['male_deaths'].div(p_df1['male_cases'])
    p_df1['F'] = p_df1['female_deaths'].div(p_df1['female_cases'])

    new=round(p_df1*100)
    new.rename(index={'>90': '90-105'}, inplace=True)
    new.loc[ '90-105',:]=(new.tail(2)).sum()
    new=new.iloc[:-1]

    return new


# this function should assign the attibute of age and gender to the network on the basis of the percentages
# derived from the previous function.

def population_attribute(table, network,table1,Diz,contact_dict):
    mischaracterized=[]
    t = len(network)
    print(t)
    table1=table1[table1.columns[-2:]]
    df2 = table1.replace(table1, 0)
    diz=df2.to_dict('index')
    print('diz is', diz)

    nodi_tmp = {i: object() for i in range(t)}  # temporary dictionary containing all the nodes
    nodi = {}  # final dictionary will contain: node number: [sex,age]
    # total number of nodes
    for age in (list(table.index.values)):
        e = re.findall(r'\d+', age)
        età = randrange(int(e[0]), int(e[1]))
        for sex in (list(table.columns)):
            perc = table.loc[age][sex]  # this is the fraction (percentage) of population that will have a specific sex and age
                        # rows= age , col= sex
            n = int(round(perc * t / 100))
            while n != 0:  # finchè non avremo aggiunto tutti gli n nodi di una categoria
               # print('n is', n)
                for k in Diz:
                    N = k.split('-')
                    if int(N[0]) <= età <= int(N[1]):
                         #this is the dictionary containig the names of the nodes (numbers) hat have a number of edges < Diz[k]
                                                #so to say the maximum number of edges a node of a cerain age can have

                        if contact_dict[Diz[k]]:
                            D = contact_dict[Diz[k]]
                        else:
                            for j in reversed(list(contact_dict.keys())):
                                print('D is empty', 'Diz[k] is',Diz[k],'j', j)
                                print('dict has length',len(contact_dict[j].keys()))

                                if contact_dict[j]:
                                    print(len(contact_dict[j].keys()))
                                    D = contact_dict[j]

                                    if (common_data(Diz[k],j)==True) :

                                        print(Diz[k], j)
                                        D = contact_dict[j]
                                        #LAST=False
                                        print('lunghezza,',len (D))
                                    break


                        nodo= random.choice(list(D.keys())) #number of maximum contact that the desidered node can have
                            #print('node is ' ,nodo, 'diz lunghezza', len(D.keys()))

                        mischaracterized=nothing_in_common(Diz[k],find_key(contact_dict,D),mischaracterized)
                        if nodo in nodi_tmp:  # se è presente sul dizionario con tutti i nodi
                            n = n - 1
                            D.pop(nodo)

                            nodi[str(nodo)] = [sex, età, 'S']  # assegna sesso e età al nodo al dizionario definitivo
                    # note: we added the susceptible state since all of them start in this compartmet
                            del nodi_tmp[nodo]  # cancella il nodo dal dizionario provvisorio
                            #print('nodi rimasti',len(nodi_tmp))
                            for anno in diz:
                                anno1=anno.split('-')
                                if int(anno1[0]) <= età <= int(anno1[1]):
                                    if diz[anno][sex]==0:
                                        lista=[str(nodo)]
                                        #print(lista)

                                        diz[anno][sex]=lista
                                        #print(diz[anno][sex])
                                    else:
                                        #print(diz[anno][sex])
                                        (diz[anno][sex]).append(str(nodo))

    print('mischaracterized are', mischaracterized, len(mischaracterized))
    for h in contact_dict:
        print('lunghezza diz shoud be zero',len(list(contact_dict[h].keys())))
    return (nodi, diz )  #dictionary contains the age range: sex:[list of nodes] , is a dictionary of dictionaries


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
    return died


def SEIRmodel(n, m, f, path):
    a = {'susceptible': [], 'exposed': [], 'infetti': [],'recovered': [],'died':[]}  # we initialize an empty dictionary in which we will store
    # the list of nodes whose attribute is respectively susceptible,
    # exposed, infected , recovered or died

    ba = nx.barabasi_albert_graph(n,m)  # function that given an n number of nodes,  with m edges, and f number of initial infected:
    # produces a random graph using Barabási-Albert preferential attachment model.
    iterationcounter = 0
    tab= gen_age(path+"Italy-2019.csv")
    dizionari=contact_population(path+"contacts_agegroups.csv",ba)
    diz=dizionari[0]
    cont_dic=dizionari[1]
    covid_tab=covid_statistics(path+"covid_gender_age.csv")
    D_result=population_attribute(tab, ba,covid_tab,diz,cont_dic)
    dizionario=D_result[0]
    diz2=D_result[1]
    will_die=fight_or_flight(diz2, covid_tab) ############################# THIS IS A DICTIONARY CONTAINING THE NODE
                                                                         #NUMBER THAT WILL DIE
    lista_attributi = ['gender', 'age', 'state']
    #print(dizionario)
    # we can add network attributes from the dictionary dizionario we just created
    for key in dizionario:
        for j in range(len(lista_attributi)):
            ba.node[int(key)][lista_attributi[j]] = dizionario[key][j]  # per ogni attributo della lista, prende il valore dal dizionario
        (a['susceptible']).append(int(key))

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
    andamentoD = {iterationcounter: len(a['died']) / n}  # and for death

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
                    a['susceptible'].remove(j)  # and will be removed from the list of susceptible people in the dictionary
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
            if str(el) in will_die:
                ba.node[el]["state"] = "D"
                a['died'].append(el)
            else:
                ba.node[el]["state"] = "R"  # so we give the R attribute th the recovered nodes
                a['recovered'].append(el)  # and we update the list of recovered people in the dictionary
        a['infetti'] = a['infetti'][r:]  # we remove the first r elements from the infected list
        andamentoD[iterationcounter] = len(a['died']) / n
        andamentoI[iterationcounter] = len(a['infetti']) / n  # here we uptade the dictionary andamento we created with
                                                                # the number of infected over the total
                                                                # and the corrisponding iteration
        andamentoS[iterationcounter] = len(a['susceptible']) / n
        andamentoR[iterationcounter] = len(a['recovered']) / n
        andamentoE[iterationcounter] = len(a['exposed']) / n
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

    plt.xlabel('Time')
    plt.plot(x, y,label="Infected")
    plt.plot(x, y2,label="Susceptible")
    plt.plot(x, y3,label="Recovered")
    plt.plot(x, y4, label="Exposed")
    plt.plot(x, y5, label="Death")
    leg = plt.legend(loc='upper left'	, ncol=2, mode="expand", shadow=True, fancybox=True)
    leg.get_frame().set_alpha(0.5)
    #infezione = plt.show()
    plt.savefig(path+'SEIR-D')
    plt.clf()
    #return (infezione)  # the function returns the plot of the epidemic spreading


if __name__ == "__main__":
    nodes = 10000  # Number of nodes
    links = 25  # Number of initial links
    focolai = 3  # numero di focolai
    path = "/home/maria/Desktop/network epidemics/"
    SEIRmodel(nodes, links, focolai, path)

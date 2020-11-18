from networkx.generators.degree_seq import expected_degree_graph
import datetime
import matplotlib.dates as mdates
from datetime import date, timedelta
import re
import numpy as np
import matplotlib.pyplot as plt
import random
from random import randrange
import pandas as pd
from pathlib import Path


##this code does everything at once ---> it runs multiple simulation changing the lockdown type and the parapetres we want to test

def lockdown_simulation(locks_types,n, f, path,lockdays,lock_p, mostc_p):
    #here we iterate among the percentages of contacts reduction [0.75,0.80,0.85,0.90]
    for lockp in lock_p:
        #and we create the respective directory : es lock_0.75 in which we will store the results
        Path(path+"lock_%s" % (lockp)).mkdir(parents=True, exist_ok=True)
        path_ = path +"lock_%s" % (lockp)
        #here we iterate on the different lockdowns we want to test: ['generalized', 'mostconnected', 'seniores']
        for lock in locks_types:
            #while simulating the most connected lock down we also want to test another parametre (number of superspreaders)
            if lock == 'mostconnected':
                #so we iterate among the quartile percentage we want to test : [0.60,0.65,0.70,0.75]
                for most in mostc_p:
                    #and we create the respective directory : es 0.60_connections
                    Path(path_+'/%s_connections'%(most)).mkdir(parents=True, exist_ok=True)
                    path_1=path_+'/%s_connections'%(most)
                    try:
                        datatable= SEIRmodel(lock,lockp,most,n,f,path,lockdays)
                        datatable.to_csv(r'%s/%s_results.csv'%(path_1,lock), index=True, header=True)  #using try and except we will skip errors
                    except Exception:
                        print('exeption encountered with ' + lock + ' '+str(lockp))
                        pass
            else:
                try:
                    datatable = SEIRmodel(lock,lockp,0.80,n,f,path,lockdays)
                    datatable.to_csv(r'%s/%s_results.csv'%(path_,lock), index=True, header=True)       #using try and except we will skip errors
                except Exception:
                    print('exeption encountered with'+lock+str(lockp))
                    pass



def lockdown(lock,lock_P,rete,nodo,most_connected):
    if lock== 'generalized':
        contacts_ = list(rete.neighbors(nodo))
        random.shuffle(contacts_)
        contacts = contacts_[int(len(contacts_) * lock_P): int(len(contacts_) * 1)]
    if lock== 'mostconnected':
        if nodo in most_connected:
            contacts_ = list(rete.neighbors(nodo))
            random.shuffle(contacts_)
            contacts = contacts_[int(len(contacts_) * lock_P): int(len(contacts_) * 1)]
        else:
            contacts = list(rete.neighbors(nodo))
    if lock=='seniores':
        if rete.nodes[nodo]['age']>14:
            contacts_ = list(rete.neighbors(nodo))
            random.shuffle(contacts_)
            contacts = contacts_[int(len(contacts_) * lock_P): int(len(contacts_) * 1)]
        else:
            contacts = list(rete.neighbors(nodo))
    return contacts




def quarantine_period(sdate,edate):       #this function takes 2 argouments: starting date of a lockdown and ending date
    delta_ = edate - sdate  # as timedelta
    lock={}
    for i in range(delta_.days + 1):
        day = sdate + timedelta(days=i)
        lock[day]=0
    return lock

def network_creation (path,t,percentage):     #t number of nodes
    lista_attributi = ['gender', 'age', 'state']
    w = []
    p_df= covid_statistics(path+"covid_gender_age.csv")
    p_df1 = p_df[p_df.columns[-2:]]
    p_df1 = p_df1.replace(p_df1, 0)
    diz = p_df1.to_dict('index')
    df_con = pd.read_csv(path+"contacts_agegroups.csv", index_col=0, names=['contacts'], header=None)
    df_con = round(df_con.sort_values(by=['contacts']))
    df_con.rename(index={'70-100': '70-105'}, inplace=True)
   # print('The number of daily contat for each age group is:\n',df_con)
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

    G = expected_degree_graph(w)
    degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # degree sequence
    q3=np.quantile(degree_sequence, percentage)
    #HERE WE ASSIGN ALL THE ATTRIBUTES (AGE, GENDER, AND STATE) FOR EACH NODE OF THE NETWORK
    most_connected={}
    for key in nodi:
        if len(G.edges(int(key))) >= q3:
            most_connected[key]=0
        for j in range(len(lista_attributi)):
            G.nodes[int(key)][lista_attributi[j]] = nodi[key][j]  # per ogni attributo della lista, prende il valore dal dizionario
    return(G,diz,p_df,most_connected)

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


def SEIRmodel(lock_type, lock_p, mostc_p, n, f, path,lockdays):
    net=network_creation(path, n,mostc_p)
    ba=net[0]
    a = {'susceptible': [], 'exposed': [], 'infetti': [],'recovered': [],'died':[]}  # we initialize an empty dictionary in which we will store
    # the list of nodes whose attribute is respectively susceptible,
    # exposed, infected , recovered or died
    for i in range(n):               # they all start in with the susceptible state S
        (a['susceptible']).append(i)                         # so at first the susceptible list in the dictionary contains all the nodes

    diz2 = net[1]
    covid_tab=net[2]
    will_die=fight_or_flight(diz2, covid_tab) ############################# THIS IS A DICTIONARY CONTAINING THE NODE
    most_connected=net[3]  #we introduced this dictionary that contains the node with ne most contact in the network
    for k in range(f):
        spreader = random.choice(list(ba.nodes()))
        a['infetti'].append(spreader)  # infetti will be a list of f people that has been infected
        if spreader in ba.nodes():
            ba.nodes[spreader]["state"] = "I"  # a number f of people will have the attribute I (infected)
            #print('hello')
        else:
            print('spreader is' ,spreader)

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
       # if len(a['infetti']) % 100 == 0:
        #    print(len(a['infetti']))

        for person in a['infetti']:  # per ogni spreader (persona infetta)
            if start_date in lockdays :
                spreadercontacts= lockdown(lock_type,lock_p,ba,person,most_connected)
            else:
                spreadercontacts = list(ba.neighbors(person))
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
    return datatable



if __name__ == "__main__":
    Nodes = 100000  # Number of nodes
    #links = 25  # Number of initial links
    focolai = 100 # numero di focolai
    path = "/Users/marilu/PycharmProjects/networkepidemics/"
    start= date(2020, 4, 9)  # start date
    stop = date(2020, 5, 18)  # end date
    lockdown_=quarantine_period(start,stop)
    lock_types = ['generalized', 'mostconnected', 'seniores']
    lock_percentage=[0.75,0.80,0.85,0.90]
    mostconnected_percentage=[0.60,0.65,0.70,0.75]
    lockdown_simulation(lock_types,Nodes,focolai,path,lockdown_,lock_percentage,mostconnected_percentage)


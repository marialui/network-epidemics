import os, sys
import sys
import re
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random
from random import randrange
import pandas as pd


def gen_age(statistics): #this is a function that given a csv file with stat information on gender and age on population, returns a table
                        #Of percentage defining each class of subjects
    p_df = pd.read_csv("%s"%statistics)
    p_df=p_df.set_index('Age')
    #p_df['perc-M']=round((p_df['M']/p_df['M'].sum())*100,2)
    #p_df['perc-F'] = round(p_df['F'] / p_df['F'].sum()*100,2)
    #p_df=p_df.reindex(p_df.index.values.tolist() + ['Total'])
    #total= p_df['M'].sum()+p_df['F'].sum()
    total = (p_df['F'].sum() + p_df['M'].sum())
    p_df['M']=round((p_df['M']/total)*100,2)
    p_df['F']=round((p_df['F']/total)*100,2)
    return p_df


#this function should assign the attibute of age and gender to the network on the basis of the percentages
#derived from the previous function.

def population_attribute(table):
    network = nx.barabasi_albert_graph(10000, 25)
    t = len(network)
    nodi_tmp = {i: object() for i in range(t)}  # temporary dictionary containing all the nodes
    nodi = {}  # final dictionary will contain: node number: [sex,age]
     #total number of nodes
    for age in (list(table.index.values)):
        for sex in (list(table.columns)):
            perc=table.loc[age][sex] #this is the fraction (percentage) of population that will have a specific sex and age
                                    #rows= age , col= sex
            #print(perc,sex,age)
            n=int(round(perc*t/100))
            while n!=0:  #finchè non avremmo aggiunto tutti gli n nodi di una categoria
                nodo= randrange(t)  #estrai random un nodo
                if nodo in nodi_tmp: #se è presente sul dizionario con tutti i nodi
                    n=n-1
                    nodi[str(nodo)]=[sex,age] # assegna sesso e età al nodo al dizionario definitivo
                    del nodi_tmp[nodo]        #cancella il nodo dal dizionario provvisorio



            #take n different nodes randomly, that will take the name of node

    return nodi




if __name__ == "__main__":
    nodes = 10 # Number of nodes
    links = 2  # Number of initial links
    focolai = 3  # numero di focolai
    path="/home/maria/Desktop/network epidemics/Italy-2019.csv"
    table=gen_age(path)
    res=population_attribute(table)
    print(table)
    print(res)
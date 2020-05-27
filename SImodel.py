import os, sys
import sys
import re
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random
from random import randrange


def SImodel(n, m, f):
    ba = nx.barabasi_albert_graph(n, m)
    iterationcounter = 0
    for i in range(n):
        ba.node[i]["state"] = "S"

    infetti = []
    for k in range(f):
        spreader = randrange(n)
        infetti.append(spreader)
        ba.node[spreader]["state"] = "I"

    andamento = {iterationcounter: len(infetti) / n}

    while iterationcounter <=10:
        if len(infetti) % 100 == 0:
            print(len(infetti))
        for person in infetti:
            tmp_infetti = []
            spreadercontacts = list(ba.neighbors(person))
            tau = 1.5 / 100
            numbernew = int((len(spreadercontacts)) * tau)
            newinfected = random.sample(spreadercontacts, numbernew)

            for j in newinfected:
                if ba.node[j]["state"] == "S":
                    ba.node[j]["state"] = "I"
                    tmp_infetti.append(j)
            infetti.extend(tmp_infetti)

        iterationcounter = iterationcounter + 1
        andamento[iterationcounter] = len(infetti) / n
    print(andamento)

    lists = andamento.items()
    x, y = zip(*lists)
    plt.ylabel('Infected')
    plt.xlabel('Time')
    plt.plot(x, y)
    infezione = plt.show()

    return (infezione)


if __name__ == "__main__":
    nodes = 10000  # Number of nodes
    links = 50# Number of initial links
    focolai = 3  # numero di focolai
    SImodel(nodes, links, focolai)
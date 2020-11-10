import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


def plot_lockdowns(generalized,seniores,most_connected):
    gen=pd.read_csv("%s" % generalized)
    sen=pd.read_csv("%s" % seniores)
    most_con=pd.read_csv("%s" % most_connected)
    D = {'INFECTED': 'I', 'EXPOSED': 'E'}
    for compartment in D:
        _gen=gen[D[compartment]]
        _sen=sen[D[compartment]]
        _most_con=most_con[D[compartment]]
        x= pd.to_datetime(gen.iloc[:,0], format='%Y-%m-%d')
        fig = plt.figure()
        plt.xlabel('Time')
        plt.plot(x, _gen, label="generalized lockdown")
        plt.plot(x, _sen, label="Seniores lockdown")
        plt.plot(x, _most_con, label="most connected lockdown")
        leg = plt.legend(loc='upper left', ncol=2, mode="expand", shadow=True, fancybox=True)
        leg.get_frame().set_alpha(0.5)
        ax = plt.gca()
        ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
        fig.autofmt_xdate()
        fig.savefig('/Users/marilu/PycharmProjects/networkepidemics/lockdown_summary_'+compartment, dpi=fig.dpi)

if __name__ == "__main__":
    path = "/Users/marilu/PycharmProjects/networkepidemics/"
    generalized_csv=path+'generalized_lockdown_results.csv'
    seniores_csv=path+'seniores_lockdown_results.csv'
    mostconnected_csv=path+'mostconnected_lockdown_results.csv'
    plot_lockdowns(generalized_csv,seniores_csv,mostconnected_csv)
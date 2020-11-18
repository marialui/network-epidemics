import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd



def summary_plot(lock_p, mostc_p, Path):
    for perc in lock_p:
        gen_sen_path= Path+'%s/'%(perc)
        for m_perc in mostc_p:
            most_path= gen_sen_path+'%s_connections/'%(m_perc)
            plot_lockdowns(gen_sen_path,most_path)



def plot_lockdowns(path1,path2):
    gen=pd.read_csv(path1 + 'generalized_results.csv')
    sen=pd.read_csv(path1 +  'seniores_results.csv')
    most_con=pd.read_csv(path2 +'mostconnected_results.csv')
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
        fig.savefig(path2+'lockdown_summary_'+compartment ,dpi=fig.dpi)
        plt.close()

if __name__ == "__main__":
    path = "/Users/marilu/PycharmProjects/networkepidemics/lock_"
    lock_percentage = [0.75, 0.80, 0.85, 0.90]
    mostconnected_percentage = [0.60, 0.65, 0.70, 0.75]
    summary_plot(lock_percentage,mostconnected_percentage,path)

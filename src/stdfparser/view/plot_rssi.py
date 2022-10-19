import pandas as pd
import matplotlib.pyplot as plt


if __name__ == '__main__':
    df = pd.read_csv(r"c:\tmp\out.csv")
    df1 = df[(df["pdt"] == "rssi") & (df["suite"] == "a_gainXrx_11axmcs0_5825_x_x__6dbgstepbw20")]
    s1 = df1[(df1["site"] == 1) & (df1["tag"] == 1.15)]
    s2 = df1[(df1["site"] == 2) & (df1["tag"] == 1.15)]
    fig, ax = plt.subplots()

    ax.scatter(x=s1["power"], y=s1["result"])
    ax.scatter(x=s2["power"], y=s2["result"])
    plt.savefig(r"c:\tmp\cc.dat")
    plt.show()

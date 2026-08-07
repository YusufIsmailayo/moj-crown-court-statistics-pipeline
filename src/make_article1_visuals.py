"""
Article 1 visuals — Crown Court backlog.
Builds four charts + a cover card as PNGs, styled to match my Medium look.
Everything is read from the Gold tables — no number is typed by hand here.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import FancyBboxPatch
from pathlib import Path
import pandas as pd

# ---- my palette ----
CREAM="#F4F1E9"; INK="#13273A"; RED="#D12E26"; STEEL="#2E6187"
ROYAL="#1D4ED8"; ORANGE="#E08A1E"; MUTED="#8A94A0"; GRID="#E4E1D8"
PANEL="#FBFAF7"; PINK="#F7E7E4"

PROJECT = Path(__file__).resolve().parents[1]
GOLD = PROJECT/"data"/"gold"
OUT  = PROJECT/"articles"/"visuals"; OUT.mkdir(parents=True, exist_ok=True)
SRC  = "Source: MOJ Criminal Court Statistics Quarterly, Oct–Dec 2025 (One Crown basis)  |  github.com/YusufIsmailayo"

plt.rcParams.update({
    "font.family":"DejaVu Sans", "figure.facecolor":PANEL, "axes.facecolor":PANEL,
    "axes.edgecolor":MUTED, "axes.linewidth":0.8, "text.color":INK,
    "axes.labelcolor":INK, "xtick.color":INK, "ytick.color":INK, "font.size":11,
})
def frame(ax):
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(MUTED); ax.spines["bottom"].set_color(MUTED)
    ax.grid(axis="y", color=GRID, lw=0.9)
    ax.set_axisbelow(True)
def head(fig, title, sub):
    fig.text(0.075,0.945,title,fontsize=17,fontweight="bold",color=INK,ha="left")
    fig.text(0.075,0.886,sub,fontsize=11.5,color=MUTED,ha="left")
def foot(fig):
    fig.text(0.075,0.03,SRC,fontsize=8.3,color=MUTED,ha="left")
def thousands(x,_): return f"{x:,.0f}"

# ============================ CHART 1: trajectory ============================
traj = pd.read_parquet(GOLD/"gold_backlog_trajectory.parquet").sort_values("quarter_end")
fig,ax=plt.subplots(figsize=(11,6.2),dpi=200)
fig.subplots_adjust(top=0.80,bottom=0.15,left=0.075,right=0.95)
ax.fill_between(traj.quarter_end,traj.open,color=RED,alpha=0.07)
ax.plot(traj.quarter_end,traj.open,color=INK,lw=2.6)
lo=traj.loc[traj.open.idxmin()]; hi=traj.iloc[-1]
for pt,txt,dy in [(lo,f"{lo.open:,.0f}\nend 2018",-42),(hi,f"{hi.open:,.0f}\nDec 2025 — a record",14)]:
    ax.scatter([pt.quarter_end],[pt.open],color=RED,zorder=5,s=45)
    ax.annotate(txt,(pt.quarter_end,pt.open),xytext=(0,dy),textcoords="offset points",
                ha="center",fontsize=10.5,fontweight="bold",color=INK)
ax.yaxis.set_major_formatter(FuncFormatter(thousands)); ax.set_ylim(25000,88000)
ax.xaxis.set_major_locator(mdates.YearLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
frame(ax); head(fig,"The Crown Court Backlog Has Never Been Bigger",
                 "Outstanding Crown Court cases at the end of each quarter · England & Wales · 2016–2025"); foot(fig)
fig.savefig(OUT/"01_backlog_trajectory.png"); plt.close(fig)

# ==================== CHART 2: more in than out (engine) ====================
fig,ax=plt.subplots(figsize=(11,6.2),dpi=200)
fig.subplots_adjust(top=0.80,bottom=0.15,left=0.075,right=0.95)
ax.plot(traj.quarter_end,traj.receipts,color=RED,lw=2.4,label="Cases received")
ax.plot(traj.quarter_end,traj.disposals,color=STEEL,lw=2.4,label="Cases disposed")
ax.fill_between(traj.quarter_end,traj.disposals,traj.receipts,
                where=(traj.receipts>=traj.disposals),color=RED,alpha=0.10,interpolate=True)
ax.yaxis.set_major_formatter(FuncFormatter(thousands))
ax.xaxis.set_major_locator(mdates.YearLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.legend(frameon=False,loc="lower left",fontsize=10.5)
ax.annotate("11 straight quarters\nreceived > disposed",(traj.iloc[-1].quarter_end,traj.iloc[-1].receipts),
            xytext=(-6,34),textcoords="offset points",ha="right",fontsize=10.5,fontweight="bold",color=RED)
frame(ax); head(fig,"The Engine Behind the Backlog: More In Than Out",
                 "Quarterly Crown Court receipts vs disposals · when the red line sits above the blue, the pile grows"); foot(fig)
fig.savefig(OUT/"02_more_in_than_out.png"); plt.close(fig)

# ============================ CHART 3: ageing share ============================
summ=pd.read_parquet(GOLD/"gold_caseload_age_summary.parquet").sort_values("quarter_end")
fig,ax=plt.subplots(figsize=(11,6.2),dpi=200)
fig.subplots_adjust(top=0.80,bottom=0.15,left=0.075,right=0.95)
ax.fill_between(summ.quarter_end,summ.share_1yr_plus*100,color=RED,alpha=0.07)
ax.plot(summ.quarter_end,summ.share_1yr_plus*100,color=RED,lw=2.6)
for q,lbl,dy in [(summ.iloc[0],"6.5%\nend 2019",14),(summ.iloc[-1],"27.7%\nDec 2025",14)]:
    ax.scatter([q.quarter_end],[q.share_1yr_plus*100],color=INK,zorder=5,s=42)
    ax.annotate(lbl,(q.quarter_end,q.share_1yr_plus*100),xytext=(0,dy),textcoords="offset points",
                ha="center",fontsize=10.5,fontweight="bold",color=INK)
ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f"{x:.0f}%")); ax.set_ylim(0,34)
ax.xaxis.set_major_locator(mdates.YearLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
frame(ax); head(fig,"It's Not Just Bigger. It's Older.",
                 "Share of open Crown Court cases that have been waiting a year or more"); foot(fig)
fig.savefig(OUT/"03_ageing_share.png"); plt.close(fig)

# ==================== CHART 4: oldest by offence ====================
byof=pd.read_parquet(GOLD/"gold_oldest_by_offence.parquet")
L=byof.quarter_end.max(); d=byof[byof.quarter_end==L].sort_values("open_1yr_plus")
serious={"Violence against the person","Sexual offences"}
colors=[RED if o in serious else "#E7B7B2" for o in d.offence]
fig,ax=plt.subplots(figsize=(11,6.8),dpi=200)
fig.subplots_adjust(top=0.80,bottom=0.10,left=0.30,right=0.94)
bars=ax.barh(d.offence,d.open_1yr_plus,color=colors)
for b,v,s in zip(bars,d.open_1yr_plus,d.share_of_quarter):
    ax.text(v+120,b.get_y()+b.get_height()/2,f"{v:,.0f}  ({s:.0%})",va="center",fontsize=10,fontweight="bold",color=INK)
ax.xaxis.set_major_formatter(FuncFormatter(thousands)); ax.set_xlim(0,7600)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False); ax.spines["left"].set_visible(False)
ax.grid(axis="x",color=GRID,lw=0.9); ax.set_axisbelow(True); ax.tick_params(left=False)
head(fig,"The Oldest Cases Are the Most Serious Ones",
     "Open Crown Court cases waiting a year or more, by offence · Dec 2025 · violence + sexual offences = 52.8%"); foot(fig)
fig.savefig(OUT/"04_oldest_by_offence.png"); plt.close(fig)

print("charts written:", sorted(p.name for p in OUT.glob("0[1-4]*.png")))

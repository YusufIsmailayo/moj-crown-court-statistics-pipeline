"""Article 3 visuals — geography. Charts + cover card, my Medium style, from Gold cuts."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import FancyBboxPatch, Rectangle
from pathlib import Path
import pandas as pd

CREAM="#F4F1E9"; INK="#13273A"; RED="#D12E26"; STEEL="#2E6187"
ROYAL="#1D4ED8"; ORANGE="#E08A1E"; MUTED="#8A94A0"; LABEL="#9AA1AC"
GRID="#E4E1D8"; PANEL="#FBFAF7"; PINK="#F7E7E4"; WHITE="#FFFFFF"
SERIF="DejaVu Serif"; MONO="DejaVu Sans Mono"; SANS="DejaVu Sans"
P=Path(__file__).resolve().parents[1]; GOLD=P/"data"/"gold"; OUT=P/"articles"/"visuals"; OUT.mkdir(parents=True,exist_ok=True)
SRC="Source: MOJ Criminal Court Statistics Quarterly, Oct–Dec 2025 (One Crown basis)  |  github.com/YusufIsmailayo"
plt.rcParams.update({"font.family":"DejaVu Sans","figure.facecolor":PANEL,"axes.facecolor":PANEL,
    "axes.edgecolor":MUTED,"axes.linewidth":0.8,"text.color":INK,"axes.labelcolor":INK,
    "xtick.color":INK,"ytick.color":INK,"font.size":11})
def barefr(ax):
    for sp in ["top","right","left"]: ax.spines[sp].set_visible(False)
    ax.grid(axis="x",color=GRID,lw=0.9); ax.set_axisbelow(True); ax.tick_params(left=False)
def head(fig,t,s):
    fig.text(0.075,0.945,t,fontsize=16.5,fontweight="bold",color=INK,ha="left")
    fig.text(0.075,0.886,s,fontsize=11.5,color=MUTED,ha="left")
def foot(fig): fig.text(0.075,0.03,SRC,fontsize=8.3,color=MUTED,ha="left")

# ---- Chart 1: region timeliness (median days) ----
tr=pd.read_parquet(GOLD/"gold_timeliness_by_region.parquet")
L=tr.quarter_end.max(); t=tr[(tr.quarter_end==L)&(tr.geo_level=="region")].sort_values("offence_to_completion_median")
cols=[RED if r=="South East" else STEEL if r=="Wales" else "#B9C4CC" for r in t.region]
fig,ax=plt.subplots(figsize=(11,6.0),dpi=200); fig.subplots_adjust(top=0.80,bottom=0.12,left=0.20,right=0.94)
bars=ax.barh(t.region,t.offence_to_completion_median,color=cols,height=0.62)
for b,v in zip(bars,t.offence_to_completion_median): ax.text(v+4,b.get_y()+b.get_height()/2,f"{v:.0f} days",va="center",fontsize=11,fontweight="bold",color=INK)
ax.set_xlim(0,470); barefr(ax)
head(fig,"The Wait Depends on the Region: 240 Days in Wales, 411 in the South East",
     "Median days from offence to final verdict, by region · Crown Court · Dec 2025"); foot(fig)
fig.savefig(OUT/"a3_01_region_timeliness.png"); plt.close(fig)

# ---- Chart 2: region share 1yr+ ----
ob=pd.read_parquet(GOLD/"gold_oldest_by_region.parquet")
o=ob[(ob.quarter_end==ob.quarter_end.max())&(ob.geo_level=="region")].sort_values("share_1yr_plus")
cols=[RED if r in ("South East","London") else STEEL if r=="Wales" else "#B9C4CC" for r in o.region]
fig,ax=plt.subplots(figsize=(11,6.0),dpi=200); fig.subplots_adjust(top=0.80,bottom=0.12,left=0.20,right=0.94)
bars=ax.barh(o.region,o.share_1yr_plus*100,color=cols,height=0.62)
for b,v in zip(bars,o.share_1yr_plus*100): ax.text(v+0.4,b.get_y()+b.get_height()/2,f"{v:.1f}%",va="center",fontsize=11,fontweight="bold",color=INK)
ax.set_xlim(0,38); barefr(ax)
head(fig,"A Third of London's Caseload Has Waited a Year. In Wales, One in Seven.",
     "Share of open Crown Court cases waiting a year or more, by region · Dec 2025"); foot(fig)
fig.savefig(OUT/"a3_02_region_1yr_share.png"); plt.close(fig)

# ---- Chart 3: court backlog ratio (top + bottom) ----
cb=pd.read_parquet(GOLD/"gold_court_backlog_ratio.parquet")
sel=pd.concat([cb.head(8), cb.tail(4)]).sort_values("years_of_backlog")
cols=[RED if r in ("London","South East") else STEEL for r in sel.region]
fig,ax=plt.subplots(figsize=(11,6.6),dpi=200); fig.subplots_adjust(top=0.80,bottom=0.10,left=0.24,right=0.94)
bars=ax.barh(sel.court,sel.years_of_backlog,color=cols,height=0.66)
for b,v in zip(bars,sel.years_of_backlog): ax.text(v+0.015,b.get_y()+b.get_height()/2,f"{v:.2f} yrs",va="center",fontsize=10.5,fontweight="bold",color=INK)
ax.set_xlim(0,1.5); barefr(ax)
head(fig,"Backlog Pressure by Court: Some Carry Three Times the Load",
     "Open caseload ÷ annual disposals — 'years to clear at today's pace' · busiest & lightest courts · 2025\n(red = London / South East)"); foot(fig)
fig.savefig(OUT/"a3_03_court_ratio.png"); plt.close(fig)

# ---- cover / social cards ----
def rrect(ax,x,y,w,h,fc,rad=0.6,z=1):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f"round,pad=0,rounding_size={rad}",fc=fc,ec="none",lw=0,zorder=z,mutation_aspect=0.55))
def card(square=False):
    if square: fig=plt.figure(figsize=(9,9),dpi=170); W,H=100,100
    else:      fig=plt.figure(figsize=(12,6.3),dpi=200); W,H=100,52.6
    ax=fig.add_axes([0,0,1,1]); ax.axis("off"); ax.set_xlim(0,W); ax.set_ylim(0,H)
    ax.add_patch(Rectangle((0,0),W,H,fc=CREAM,zorder=0)); top=H-6
    ax.text(W-3,4,"171d",fontsize=95 if square else 78,fontweight="bold",color="#ECE7DB",ha="right",va="bottom",family=SERIF)
    ax.text(6,top,"MOJ DATA ENGINEERING",fontsize=12,color=ROYAL,family=MONO,fontweight="bold",va="center")
    ax.text(6+(30 if square else 26),top,"· MEDIUM · AUGUST 2026",fontsize=12,color=MUTED,family=MONO,va="center")
    ax.add_patch(Rectangle((6,top-3.2),7,0.5,fc=RED,zorder=2)); ty=top-9
    ax.text(6,ty,"Justice Has a",fontsize=38 if square else 32,color=INK,family=SERIF,fontweight="bold",va="top")
    ax.text(6,ty-(11 if square else 8.5),"Postcode.",fontsize=38 if square else 32,color=RED,family=SERIF,fontweight="bold",style="italic",va="top")
    if square: cx,cw,ys,ch=6,88,[42,28,14],12
    else:      cx,cw,ys,ch=54,42,[34,20,6],12
    for (num,col,l1,l2),cy in zip([("411 days",RED,"SLOWEST REGION","SOUTH EAST"),("240 days",STEEL,"FASTEST REGION","WALES"),
        ("3.6×",ORANGE,"COURT BACKLOG GAP","WORST vs BEST")],ys):
        rrect(ax,cx,cy,cw,ch,WHITE,rad=0.7,z=2); ax.add_patch(Rectangle((cx+0.8,cy+ch-0.55),cw-1.6,0.55,fc=col,zorder=3))
        ax.text(cx+3,cy+ch/2,num,fontsize=23,color=col,family=SERIF,fontweight="bold",va="center",zorder=4)
        ax.text(cx+cw*0.46,cy+ch/2,f"{l1}\n{l2}",fontsize=10.5 if square else 10,color=LABEL,family=SANS,fontweight="bold",va="center",linespacing=1.4,zorder=4)
    qx,qy,qw,qh=(6,2.5,88,9) if square else (6,7,44,14)
    rrect(ax,qx,qy,qw,qh,PINK,rad=0.6,z=1); ax.add_patch(Rectangle((qx,qy),0.7,qh,fc=RED,zorder=3))
    ax.text(qx+3,qy+qh*0.62,"Same charge. Same country.",fontsize=12 if square else 12.5,color=INK,style="italic",family=SERIF,va="center")
    ax.text(qx+3,qy+qh*0.30,"A different wait by region.",fontsize=12.5 if square else 13,color=RED,fontweight="bold",family=SERIF,va="center")
    if not square:
        ax.text(6,2.6,"Yusuf Ismail",fontsize=12,color=INK,fontweight="bold",family=SANS,va="bottom")
        ax.text(6,1.2,"medium.com/@yusufismail_91982",fontsize=9.5,color=ROYAL,family=MONO,va="bottom")
        rrect(ax,84,1.2,12,3.2,INK,rad=0.5,z=3)
        ax.text(90,2.8,"READ ON MEDIUM →",fontsize=8.5,color=WHITE,fontweight="bold",family=MONO,ha="center",va="center",zorder=4)
    tag="social_square" if square else "cover_landscape"
    fig.savefig(OUT/f"a3_{tag}.png",facecolor=CREAM); plt.close(fig)
card(False); card(True)
print("article 3 visuals:", sorted(p.name for p in OUT.glob("a3_*.png")))

"""Article 4 visuals — the One Crown pause. Publication-gap timeline + cover card."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch, Rectangle
from datetime import datetime as D
from pathlib import Path

CREAM="#F4F1E9"; INK="#13273A"; RED="#D12E26"; STEEL="#2E6187"
ROYAL="#1D4ED8"; ORANGE="#E08A1E"; MUTED="#8A94A0"; LABEL="#9AA1AC"
GRID="#E4E1D8"; PANEL="#FBFAF7"; PINK="#F7E7E4"; WHITE="#FFFFFF"
SERIF="DejaVu Serif"; MONO="DejaVu Sans Mono"; SANS="DejaVu Sans"
P=Path(__file__).resolve().parents[1]; OUT=P/"articles"/"visuals"; OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({"font.family":"DejaVu Sans","figure.facecolor":PANEL,"axes.facecolor":PANEL,
    "text.color":INK,"font.size":11})

# --- Chart: the publication gap (quarterly Crown Court statistics releases) ---
# (publication dates from the GOV.UK Criminal court statistics collection)
rel=[("2023-12-14","Q3 2023",True),("2024-03-28","Q4 2023",True),
     ("2024-06-15","Q1 2024",False),("2024-09-15","Q2 2024",False),
     ("2024-12-12","Q3 2024",True),("2025-03-27","Q4 2024",True),
     ("2025-06-26","Q1 2025",True),("2025-09-30","Q2 2025",True),
     ("2025-12-18","Q3 2025",True),("2026-03-26","Q4 2025",True)]
fig,ax=plt.subplots(figsize=(12,5.2),dpi=200); fig.subplots_adjust(top=0.74,bottom=0.16,left=0.05,right=0.97)
# pause band
ax.axvspan(D(2024,4,1),D(2024,12,1),color=RED,alpha=0.08)
ax.axhline(0,color=MUTED,lw=1.2,zorder=1)
for d,lab,pub in rel:
    dt=D.fromisoformat(d)
    if pub:
        ax.scatter([dt],[0],s=120,color=STEEL,zorder=3)
        ax.annotate(lab,(dt,0),xytext=(0,-22),textcoords="offset points",ha="center",fontsize=9.5,color=INK,rotation=0)
    else:
        ax.scatter([dt],[0],s=140,facecolors="none",edgecolors=RED,linewidths=2,zorder=3,marker="X")
        ax.annotate("skipped",(dt,0),xytext=(0,16),textcoords="offset points",ha="center",fontsize=9.5,color=RED,fontweight="bold")
ax.annotate("Last release before the pause",(D(2024,3,28),0),xytext=(-6,40),textcoords="offset points",ha="right",fontsize=10,color=INK)
ax.annotate("Resumed — figures rebuilt\n(73,105, Sept 2024)",(D(2024,12,12),0),xytext=(6,40),textcoords="offset points",ha="left",fontsize=10,color=INK,fontweight="bold")
ax.text(D(2024,8,1),-0.62,"Crown Court caseload\nwithheld for ~9 months",ha="center",fontsize=10,color=RED,fontweight="bold")
ax.set_ylim(-0.9,0.9); ax.set_yticks([])
ax.xaxis.set_major_locator(mdates.YearLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
for s in ["top","right","left"]: ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(MUTED); ax.tick_params(left=False)
fig.text(0.05,0.92,"The Nine Months the Number Wasn't Published",fontsize=17,fontweight="bold",color=INK)
fig.text(0.05,0.855,"Quarterly Crown Court statistics releases · two 2024 releases were skipped during the One Crown rebuild",fontsize=11.5,color=MUTED)
fig.text(0.05,0.03,"Source: GOV.UK Criminal court statistics collection (publication dates)  |  github.com/YusufIsmailayo",fontsize=8.3,color=MUTED)
fig.savefig(OUT/"a4_01_publication_gap.png"); plt.close(fig)

# --- cover / social cards ---
def rrect(ax,x,y,w,h,fc,rad=0.6,z=1):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f"round,pad=0,rounding_size={rad}",fc=fc,ec="none",lw=0,zorder=z,mutation_aspect=0.55))
def card(square=False):
    if square: fig=plt.figure(figsize=(9,9),dpi=170); W,H=100,100
    else:      fig=plt.figure(figsize=(12,6.3),dpi=200); W,H=100,52.6
    ax=fig.add_axes([0,0,1,1]); ax.axis("off"); ax.set_xlim(0,W); ax.set_ylim(0,H)
    ax.add_patch(Rectangle((0,0),W,H,fc=CREAM,zorder=0)); top=H-6
    ax.text(W-3,4,"9mo",fontsize=95 if square else 78,fontweight="bold",color="#ECE7DB",ha="right",va="bottom",family=SERIF)
    ax.text(6,top,"MOJ DATA ENGINEERING",fontsize=12,color=ROYAL,family=MONO,fontweight="bold",va="center")
    ax.text(6+(30 if square else 26),top,"· MEDIUM · AUGUST 2026",fontsize=12,color=MUTED,family=MONO,va="center")
    ax.add_patch(Rectangle((6,top-3.2),7,0.5,fc=RED,zorder=2)); ty=top-9
    ax.text(6,ty,"The Number",fontsize=38 if square else 32,color=INK,family=SERIF,fontweight="bold",va="top")
    ax.text(6,ty-(11 if square else 8.5),"That Vanished.",fontsize=38 if square else 32,color=RED,family=SERIF,fontweight="bold",style="italic",va="top")
    if square: cx,cw,ys,ch=6,88,[42,28,14],12
    else:      cx,cw,ys,ch=54,42,[34,20,6],12
    for (num,col,l1,l2),cy in zip([("9 months",RED,"CASELOAD","WITHHELD IN 2024"),("2",STEEL,"VERSIONS OF THE","SAME NUMBER"),
        ("73,105",ORANGE,"REBUILT FIGURE","SEPT 2024")],ys):
        rrect(ax,cx,cy,cw,ch,WHITE,rad=0.7,z=2); ax.add_patch(Rectangle((cx+0.8,cy+ch-0.55),cw-1.6,0.55,fc=col,zorder=3))
        ax.text(cx+3,cy+ch/2,num,fontsize=24,color=col,family=SERIF,fontweight="bold",va="center",zorder=4)
        ax.text(cx+cw*0.44,cy+ch/2,f"{l1}\n{l2}",fontsize=10.5,color=LABEL,family=SANS,fontweight="bold",va="center",linespacing=1.4,zorder=4)
    qx,qy,qw,qh=(6,2.5,88,9) if square else (6,7,44,14)
    rrect(ax,qx,qy,qw,qh,PINK,rad=0.6,z=1); ax.add_patch(Rectangle((qx,qy),0.7,qh,fc=RED,zorder=3))
    ax.text(qx+3,qy+qh*0.62,"Reproducible is not",fontsize=12 if square else 12.5,color=INK,style="italic",family=SERIF,va="center")
    ax.text(qx+3,qy+qh*0.30,"the same as true.",fontsize=12.5 if square else 13,color=RED,fontweight="bold",family=SERIF,va="center")
    if not square:
        ax.text(6,2.6,"Yusuf Ismail",fontsize=12,color=INK,fontweight="bold",family=SANS,va="bottom")
        ax.text(6,1.2,"medium.com/@yusufismail_91982",fontsize=9.5,color=ROYAL,family=MONO,va="bottom")
        rrect(ax,84,1.2,12,3.2,INK,rad=0.5,z=3)
        ax.text(90,2.8,"READ ON MEDIUM →",fontsize=8.5,color=WHITE,fontweight="bold",family=MONO,ha="center",va="center",zorder=4)
    tag="social_square" if square else "cover_landscape"
    fig.savefig(OUT/f"a4_{tag}.png",facecolor=CREAM); plt.close(fig)
card(False); card(True)
print("article 4 visuals:", sorted(p.name for p in OUT.glob("a4_*.png")))

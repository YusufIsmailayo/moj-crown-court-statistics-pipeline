"""Cover / social card for article 1 — matplotlib, styled to my Medium cards."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from pathlib import Path

CREAM="#F4F1E9"; INK="#13273A"; RED="#D12E26"; ROYAL="#1D4ED8"
ORANGE="#E08A1E"; MUTED="#8A94A0"; LABEL="#9AA1AC"; WHITE="#FFFFFF"; PINK="#F7E7E4"
OUT=Path(__file__).resolve().parents[1]/"articles"/"visuals"

SERIF="DejaVu Serif"; MONO="DejaVu Sans Mono"; SANS="DejaVu Sans"

def rrect(ax,x,y,w,h,fc,ec="none",lw=0,rad=0.6,z=1):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f"round,pad=0,rounding_size={rad}",
                                fc=fc,ec=ec,lw=lw,zorder=z,mutation_aspect=0.55))

def build(square=False):
    if square:
        fig=plt.figure(figsize=(9,9),dpi=170); W,H=100,100
    else:
        fig=plt.figure(figsize=(12,6.3),dpi=200); W,H=100,52.6
    ax=fig.add_axes([0,0,1,1]); ax.axis("off"); ax.set_xlim(0,W); ax.set_ylim(0,H)
    ax.add_patch(Rectangle((0,0),W,H,fc=CREAM,zorder=0))
    top=H-6
    # watermark
    ax.text(W-3,4,"80,203",fontsize=95 if square else 78,fontweight="bold",color="#ECE7DB",
            ha="right",va="bottom",family=SERIF,zorder=0)
    # kicker
    ax.text(6,top,"MOJ DATA ENGINEERING",fontsize=12,color=ROYAL,family=MONO,fontweight="bold",va="center")
    ax.text(6+ (30 if square else 26),top,"· MEDIUM · AUGUST 2026",fontsize=12,color=MUTED,family=MONO,va="center")
    ax.add_patch(Rectangle((6,top-3.2),7,0.5,fc=RED,zorder=2))
    # title
    ty=top-9
    ax.text(6,ty,"The Backlog",fontsize=40 if square else 34,color=INK,family=SERIF,fontweight="bold",va="top")
    ax.text(6,ty-(11 if square else 8.5),"Won't Stop.",fontsize=40 if square else 34,color=RED,
            family=SERIF,fontweight="bold",style="italic",va="top")
    # stat cards
    if square:
        cx,cw=6,88; ys=[42,28,14]; ch=12; num_fs=26; lab_fs=11
    else:
        cx,cw=54,42; ys=[34,20,6]; ch=12; num_fs=25; lab_fs=10.5
    stats=[("80,203",RED,"OPEN CASES","A RECORD"),
           ("21,002",ROYAL,"WAITING","OVER A YEAR"),
           ("52.8%",ORANGE,"OF THE OLDEST ARE","SEXUAL OR VIOLENT")]
    for (num,col,l1,l2),cy in zip(stats,ys):
        rrect(ax,cx,cy,cw,ch,WHITE,rad=0.7,z=2)
        ax.add_patch(Rectangle((cx+0.8,cy+ch-0.55),cw-1.6,0.55,fc=col,zorder=3))
        ax.text(cx+3,cy+ch/2,num,fontsize=num_fs,color=col,family=SERIF,fontweight="bold",va="center",zorder=4)
        ax.text(cx+cw*0.42,cy+ch/2,f"{l1}\n{l2}",fontsize=lab_fs,color=LABEL,family=SANS,
                fontweight="bold",va="center",linespacing=1.4,zorder=4)
    # pull-quote (landscape: left column; square: below stats)
    if square:
        qx,qy,qw,qh=6,2.5,88,9
    else:
        qx,qy,qw,qh=6,7,44,14
    rrect(ax,qx,qy,qw,qh,PINK,rad=0.6,z=1)
    ax.add_patch(Rectangle((qx,qy),0.7,qh,fc=RED,zorder=3))
    ax.text(qx+3,qy+qh*0.62,"Same courts. More work than ever.",fontsize=12 if square else 12.5,
            color=INK,style="italic",family=SERIF,va="center")
    ax.text(qx+3,qy+qh*0.30,"A bigger backlog than ever.",fontsize=12.5 if square else 13,
            color=RED,fontweight="bold",family=SERIF,va="center")
    # footer
    ax.text(6,2.6 if not square else -0.5,"Yusuf Ismail",fontsize=12,color=INK,fontweight="bold",family=SANS,va="bottom") if not square else None
    if not square:
        ax.text(6,1.2,"medium.com/@yusufismail_91982",fontsize=9.5,color=ROYAL,family=MONO,va="bottom")
        rrect(ax,84,1.2,12,3.2,INK,rad=0.5,z=3)
        ax.text(90,2.8,"READ ON MEDIUM →",fontsize=8.5,color=WHITE,fontweight="bold",family=MONO,ha="center",va="center",zorder=4)
    else:
        ax.text(6,-3.0,"Yusuf Ismail   ·   medium.com/@yusufismail_91982",fontsize=11,color=INK,family=SANS,va="bottom")
    tag="social_square" if square else "cover_landscape"
    fig.savefig(OUT/f"05_{tag}.png",facecolor=CREAM); plt.close(fig)
    return f"05_{tag}.png"

print("cards:",build(False),build(True))

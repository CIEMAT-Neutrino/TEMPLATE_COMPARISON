import scipy as sc
import numpy as np
import pandas as pd
import plotly.express as px

import plotly.graph_objects as go
from scipy.optimize import curve_fit

def unicode(x):
    unicode_greek  = {"Delta":"\u0394","mu":"\u03BC","pi":"\u03C0","gamma":"\u03B3","Sigma":"\u03A3","Lambda":"\u039B","alpha":"\u03B1","beta":"\u03B2","gamma":"\u03B3","delta":"\u03B4","epsilon":"\u03B5","zeta":"\u03B6","eta":"\u03B7","theta":"\u03B8","iota":"\u03B9","kappa":"\u03BA","lambda":"\u03BB","mu":"\u03BC","nu":"\u03BD","xi":"\u03BE","omicron":"\u03BF","pi":"\u03C0","rho":"\u03C1","sigma":"\u03C3","tau":"\u03C4","upsilon":"\u03C5","phi":"\u03C6","chi":"\u03C7","psi":"\u03C8","omega":"\u03C9"}
    unicode_symbol = {"PlusMinus":"\u00B1","MinusPlus":"\u2213","Plus":"\u002B","Minus":"\u2212","Equal":"\u003D","NotEqual":"\u2260","LessEqual":"\u2264","GreaterEqual":"\u2265","Less":"\u003C","Greater":"\u003E","Approximately":"\u2248","Proportional":"\u221D","Infinity":"\u221E","Degree":"\u00B0","Prime":"\u2032","DoublePrime":"\u2033","TriplePrime":"\u2034","QuadruplePrime":"\u2057","Micro":"\u00B5","PerMille":"\u2030","Permyriad":"\u2031","Minute":"\u2032","Second":"\u2033","Dot":"\u02D9","Cross":"\u00D7","Star":"\u22C6","Circle":"\u25CB","Square":"\u25A1","Diamond":"\u25C7","Triangle":"\u25B3","LeftTriangle":"\u22B2","RightTriangle":"\u22B3","LeftTriangleEqual":"\u22B4","RightTriangleEqual":"\u22B5","LeftTriangleBar":"\u29CF","RightTriangleBar":"\u29D0","LeftTriangleEqualBar":"\u29CF","RightTriangleEqualBar":"\u29D0","LeftRightArrow":"\u2194","UpDownArrow":"\u2195","UpArrow":"\u2191","DownArrow":"\u2193","LeftArrow":"\u2190","RightArrow":"\u2192","UpArrowDownArrow":"\u21C5","LeftArrowRightArrow":"\u21C4","LeftArrowLeftArrow":"\u21C7","UpArrowUpArrow":"\u21C8","RightArrowRightArrow":"\u21C9","DownArrowDownArrow":"\u21CA","LeftRightVector":"\u294E","RightUpDownVector":"\u294F","DownLeftRightVector":"\u2950","LeftUpDownVector":"\u2951","LeftVectorBar":"\u2952","RightVectorBar":"\u2953","RightUpVectorBar":"\u2954","RightDownVectorBar":"\u2955"}
    unicode_dict = {**unicode_greek,**unicode_symbol}
    return unicode_dict[x]

def update_legend(fig,dict):
    fig.for_each_trace(lambda t: t.update(name = dict[t.name],legendgroup = dict[t.name],hovertemplate = t.hovertemplate.replace(t.name, dict[t.name])))
    return fig

def format_coustom_plotly(fig,fontsize=16,figsize=None,ranges=(None,None),tickformat=(",.2s",",.2s"),tickmode=("auto","auto"),log=(False,False),facet_titles=None):
    fig.update_layout(template="presentation",font=dict(size=fontsize)) # font size and template
    fig.update_xaxes(showline=True,mirror="ticks",showgrid=True,minor_ticks="inside",tickformat=tickformat[0],tickmode=tickmode[0],range=ranges[0]) # tickformat=",.1s" for scientific notation
    fig.update_yaxes(showline=True,mirror="ticks",showgrid=True,minor_ticks="inside",tickformat=tickformat[1],tickmode=tickmode[1],range=ranges[1]) # tickformat=",.1s" for scientific notation
    
    if figsize != None:
        fig.update_layout(width=figsize[0],height=figsize[1])
    
    if log[0]:
        fig.update_xaxes(type="log",tickmode=tickmode[0])
    if log[1]:
        fig.update_yaxes(type="log",tickmode=tickmode[1])
    
    if facet_titles is not None:
        try:
            for i,title in enumerate(facet_titles):
                fig.layout.annotations[i].text = title
        except IndexError:
            for title in fig.layout.annotations:
                title.text = title.text.split("=")[1]
        except TypeError:
            for title in fig.layout.annotations:
                title.text = title.text.split("=")[1]

    return fig
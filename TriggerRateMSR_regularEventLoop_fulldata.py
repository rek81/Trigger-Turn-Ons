import os
import ROOT
from ROOT import *
from array import array
import math
from math import *
import sys
import csv
import numpy

RDF = ROOT.ROOT.RDataFrame
ROOT.ROOT.EnableImplicitMT()


def quickplot(File, tree, plot, var, Cut, Weight):
    temp = plot.Clone("temp")
    chain = TChain(tree)
    for i in File:
        chain.Add(i)
    chain.Draw(var + ">>" + "temp", "(" + Weight + ")*(" + Cut + ")", "goff")
    plot.Add(temp)

def MakeNBinsFromMinToMax(N,Min,Max):
    BINS = []
    for i in range(N+1):
        BINS.append(Min+(i*(Max-Min)/N))
    return BINS

Xbins = [900.,1000.,1100.,1200.,1300.,1400.,1500.,1750.,2000.,5000.]
abins = MakeNBinsFromMinToMax(10, 15., 115.)
abins += MakeNBinsFromMinToMax(3, 130., 200.)
HTbins = MakeNBinsFromMinToMax(300, 500., 3500.)

dataweight = "1."

masscuts900 = "evt_HT>900. && J1pt>300. && J2pt>300. && J1eta<2.4 && J2eta<2.4"
masscuts1200 = "evt_HT>1200. && J1pt>300. && J2pt>300. && J1eta<2.4 && J2eta<2.4"
HTcuts = "evt_HT>0."


HT = ["evt_HT", "Jet HT (GeV)", HTcuts, HTbins, "HT900"]
X = ["evt_XM", "Dijet Mass (GeV)", masscuts900, Xbins, "HT900"]
a = ["evt_aM", "Averege Jet Mass (GeV)", masscuts900, abins, "HT900"]

var = [HT, X, a]



num = ROOT.TFile("/cms/xaastorage/PicoTrees/2016/April2020v6/SingleMuon_2016Bv1_numTrig_October14_2020/SingleMuon_2016FullDataset_numTrig_October14_2020.root")
den = ROOT.TFile("/cms/xaastorage/PicoTrees/2016/April2020v6/SingleMuon_2016Bv2_denTrig_October9_2020/SingleMuon_2016FullDataset_denTrig_October9_2020.root")

for v in var:


    TrigNum = TH1F("Num", v[0], len(v[3])-1, numpy.array(v[3]))
    TrigDen = TH1F("Den", v[0], len(v[3])-1, numpy.array(v[3]))

    FNum = num.Get("tree_nominal")
    FDen = den.Get("tree_nominal")


    entNum = FNum.GetEntries()
    entDen = FDen.GetEntries()

    for e in range(entNum):
        FNum.GetEntry(e)
        if e % 30:
            print "numerator e is " + str(e)
        for e in FNum:
            if v[0] is HT:
                TrigNum.Fill(FNum.evt_HT)
            if v[0] is X:
                if FNum.evt_HT>900. and FNum.J2pt>300. and abs(FNum.J2eta)<2.4:
                    TrigNum.Fill(FNum.evt_XM)
            if v[0] is a:
                if FNum.evt_HT>900. and FNum.J2pt>300. and abs(FNum.J2eta)<2.4:
                    TrigNum.Fill(FNum.evt_aM)

    for e in range(entDen):
        FDen.GetEntry(e)
        if e % 30:
            print "denominator e is " + str(e)
        for e in FDen:
            if v[0] is HT:
                TrigDen.Fill(FDen.evt_HT)
            if v[0] is X:
                if FDen.evt_HT>900. and FDen.J2pt>300. and abs(FDen.J2eta)<2.4:
                    TrigDen.Fill(FDen.evt_XM)
            if v[0] is a:
                if FDen.evt_HT>900. and FDen.J2pt>300. and abs(FDen.J2eta)<2.4:
                    TrigDen.Fill(FDen.evt_aM)

#    print "for "+v[0]+" numerator integral is "+str(TrigNum.Integral()) + " in run " + i[1]
#    print "for "+v[0]+" denominator integral is "+str(TrigDen.Integral()) + " in run " + i[1]
                
    TrigNum.Sumw2()
    TrigDen.Sumw2()
                
    newNum = TrigNum.Clone("nnew")
    newNum.SetStats(0)
    newNum.GetYaxis().SetTitle("Trigger Efficiency (%)")
    newNum.SetLineColor(kBlue)
    newNum.SetMarkerStyle(20)
    newNum.SetMarkerColor(9)

    print "new num integral " + str(newNum.Integral())
    print "old num integral " + str(TrigNum.Integral())
    print "den integral " + str(TrigDen.Integral())
    
    newNum.Divide(TrigDen)
    
    newNum.Scale(100)
    newNum.Scale(100)
    
    TrigNum.Scale(1000./TrigNum.Integral())
    TrigDen.Scale(1000./TrigDen.Integral())
    
    TrigNum.SetLineColor(kRed)
    TrigNum.SetMarkerStyle(20)
    TrigNum.SetMarkerColor(2)
    
    TrigDen.SetLineColor(kGreen)
    TrigDen.SetMarkerStyle(20)
    TrigDen.SetMarkerColor(3)
    
    
    Box = TBox(v[3][0], 100.01, v[3][-1], 110.)
    Box.SetLineColor(kWhite)
    Box.SetFillColor(kWhite)
    
    Flat = TLine(v[3][0], 100, v[3][-1], 100)
    Flat.SetLineColor(kBlack)
    
    if v[4] is "HT900":
        Tall = TLine(900, 5, 900, 100)
    if v[4] is "HT1200":
        Tall = TLine(1200, 5, 1200, 100)
    Tall.SetLineColor(kOrange+5)
    Tall.SetLineWidth(2)
    Tall.SetLineStyle(3)
    
    L = TLegend(0.35, 0.25, 0.89, 0.45)
    L.SetLineColor(0)
    L.SetFillColor(0)
    L.AddEntry(newNum, "2016 SingleMuon (HLT_Mu50 Ref. Trigger)", "P")
    L.AddEntry(TrigNum, "Numerator, Scale: 1000)", "P")
    L.AddEntry(TrigDen, "Denominator, Scale: 1000", "P")
    
    
    C = TCanvas()
    C.cd()
    newNum.Draw("histe p")
    TrigNum.Draw("histsamee p")
    TrigDen.Draw("histsamee p")
    Flat.Draw("same")
    Box.Draw("same")
    if v[0] is "evt_HT":
        Tall.Draw("same")
                    #        L.Draw("same")
    gPad.SetTicks(1, 1)
    gPad.RedrawAxis()
    if "900" in v[4]:
        C.Print("2016_"+v[0]+"_TrigTurnOn_"+v[4]+"_Oct16_2020.png")
    if "1200" in v[4]:
        C.Print("2016_"+v[0]+"_TrigTurnOn_"+v[4]+"_Oct16_2020.png")

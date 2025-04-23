#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 13:58:33 2025

@author: Alexander.Morano
"""

import os 
import pandas as pd
import matplotlib.pyplot as plt


def SearchMyCells(CellList, GeneList, PathToFolder):
    
    celllist = CellList
    genelist = GeneList
    os.chdir(PathToFolder)
   
    df = pd.read_csv('TPM.csv')

    #rename columns to remove numbers and just have the gene name
    df.columns = df.columns.str.split(' ').str[0].str.strip()
    gene_names = df.columns.tolist()

    namesmapfull = pd.read_csv("Model.csv")

    namesmap = namesmapfull[["ModelID","StrippedCellLineName"]]

    namesmap=namesmap.rename(columns={"ModelID":"Unnamed:", "StrippedCellLineName":"CellLine"})

    conditions = [(namesmap['CellLine'] == cell ) for cell in celllist]

 
    combined_condition = conditions[0]
    for condition in conditions [1:]:
        combined_condition |= condition


    cellsIhave = namesmap[combined_condition]
    print(len(cellsIhave))

    ModelList = cellsIhave['Unnamed:']

    conditions2 = [(df['Unnamed:'] == model ) for model in ModelList]

    combined_condition2 = conditions2[0]
    for condition2 in conditions2 [1:]:
        combined_condition2 |= condition2


    filteredbycl = df[combined_condition2]
    filteredbycl = filteredbycl.merge(namesmap, on=["Unnamed:"], how='outer').dropna()
    
    finalcolumns = ["CellLine"] + genelist
    finaldf = filteredbycl[finalcolumns]
    print(len(filteredbycl))
    
    csv_path = os.path.join(PathToFolder,r'results.csv')
    finaldf.to_csv(csv_path, index=True, encoding='utf-8-sig')
 
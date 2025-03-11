#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 12:20:49 2025

@author: Alexander.Morano
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 10:05:01 2025

@author: Alexander.Morano
"""

import os 
import pandas as pd
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import time

"""
Before running this function: 
1: download this data set from DepMap (https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap+Public+24Q4&filename=OmicsExpressionProteinCodingGenesTPMLogp1.csv); rename to 'TPM.csv' and move it to a specific folder.
2: download the correlative cell line name data set from DepMap (https://depmap.org/portal/data_page/?tab=allData&releasename=DepMap%20Public%2024Q4&filename=Model.csv);  move it to the same folder as 'TPM.csv' 

Inputs are 2 lists and one directory path; one list of genes that you want to ALL be highly expressed in your cell lines (it will select for cell lines where all of the genes in the list are expressed highly)
the other list is a list of genes that you want an additional one of any of these to be expressed highly. 
For example, if I wanted cell lines that express all 3 neurexins highly and any of the 3 neuroligins highly, I would type: 

The third input is just the path to the folder where you stored TPM.csv and Model.csv    
Usually the path looks like this: '/Users/Alexander.Morano/Desktop/python and fiji scripts/DepMap/' 
You can copy the path name from the finder window if you're on a Mac.

ATCC_Has_It_For_You(["NRXN1", "NRXN2", "NRXN3"], ["NLGN1", NLGN2". "NLGN3"])
The resulting cell lines would have ALL of NRXN1/2/3 expressed highly, AND ANY ONE of NLGN1/2/3 expressed highly, filtering on 4 total genes.

"""


def ATCC_Has_It_For_You(andGenes, orGenes, PathToFolder):
    
    gene_list = andGenes + orGenes
 
    os.chdir(PathToFolder)
    df = pd.read_csv('TPM.csv')

#rename columns to remove numbers and just have the gene name
    df.columns = df.columns.str.split(' ').str[0].str.strip()
    gene_names = df.columns.tolist()

    print(len(df))
    conditions = [(df[gene] > 2.5) for gene in andGenes]
   
    combined_condition = conditions[0]
    
    for condition in conditions [1:]:
       combined_condition &= condition
   
    filt1 = df[combined_condition]
    print(len(filt1))
    
   
    conditions2 = [(df[gene] > 2.5) for gene in orGenes]
   
    combined_condition2 = conditions2[0]
    
    for condition2 in conditions2 [1:]:
       combined_condition2 |= condition2
       
    combined_condition2_filt1 = combined_condition2.loc[filt1.index]   
   
    filt2 = filt1[combined_condition2_filt1]
    print(len(filt2))
                
    
    namesmapfull = pd.read_csv("Model.csv")

    namesmap = namesmapfull[["ModelID","StrippedCellLineName"]]

    namesmap=namesmap.rename(columns={"ModelID":"Unnamed:", "StrippedCellLineName":"CellLine"})

    hits = filt2.merge(namesmap, on=["Unnamed:"], how='outer').dropna()

    cell_lines = hits["CellLine"]
    
    print(cell_lines)

    driver = webdriver.Chrome()
    driver.implicitly_wait(10)

    driver.get("https://www.atcc.org")

    driver.find_element("xpath", '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]').click()  

    cellinfo = []

    for cell in cell_lines:
        driver.get(f"https://www.atcc.org/search#q={cell}&sort=relevancy&numberOfResults=24")
        time.sleep(8)
        
        try:
            element = driver.find_element("xpath", '/html[1]/body[1]/main[1]/div[4]/div[1]/div[1]/div[1]/div[2]/div[2]/div[3]/div[2]/div[1]/div[5]/div[1]/div[1]/div[1]/h3[1]/a[1]')
            link = element.get_attribute('href')
            x = (link)

        except NoSuchElementException:
           x = ("Element is not present in the database")
           
           y_cleaned = ("Complete medium info not found")
           tissue_cleaned = ("tissue not found")
           disease_cleaned = ("disease not found")
        else:
            
            try: 
                
                driver.find_element("xpath", '/html[1]/body[1]/main[1]/div[4]/div[1]/div[1]/div[1]/div[2]/div[2]/div[3]/div[2]/div[1]/div[5]/div[1]/div[1]/div[1]/h3[1]/a[1]').click()
                time.sleep(8)
                
                handling_info_section = driver.find_element("xpath", "//div[@class='generic-accordion__item-title']//h3[contains(text(), 'Handling information')]")
                handling_info_section.click()

               
                time.sleep(2)
               
                try:
                   complete_medium_element = driver.find_element(
                        "xpath", "//dt[contains(text(), 'Complete medium')]/following-sibling::dd"
                    )
                   y = complete_medium_element.get_attribute("innerHTML")  # Capture the content with HTML tags
                   y_cleaned = BeautifulSoup(y, "html.parser").get_text()
                   
                except NoSuchElementException:
                   y_cleaned = "Complete medium info not found"
                   
                try:
                    tissue_element = driver.find_element("xpath", "//dt[contains(text(), 'Tissue')]/following-sibling::dd")
                    tissue = tissue_element.get_attribute("innerHTML")
                    tissue_cleaned = BeautifulSoup(tissue, "html.parser").get_text()
                
                except:
                    tissue_cleaned = "Tissue not found"
                
                try:
                    disease_element = driver.find_element("xpath", "//dt[contains(text(), 'Disease')]/following-sibling::dd")
                    disease = disease_element.get_attribute("innerHTML")
                    disease_cleaned = BeautifulSoup(disease, "html.parser").get_text()
                
                except:
                    disease_cleaned = "Disease not found"
              
            except NoSuchElementException:
                y_cleaned = "Element is not present in the database"
                tissue_cleaned = "tissue not found"
                disease_cleaned = "disease not found"

        print(x)
        print(y_cleaned)
        print(tissue_cleaned)
        print(disease_cleaned)
        
        cellinfo.append({'Cell Line': cell, 'ATCC': x, 'Media': y_cleaned, 'Tissue': tissue_cleaned, 'Disease': disease_cleaned})
        continue
       

    CI = pd.DataFrame(cellinfo)
    CI['Media'] = CI['Media'].apply(lambda x: x.strip() if isinstance(x, str) else x)
    csv_path = os.path.join(PathToFolder,r'results.csv')
    CI.to_csv(csv_path, index=True, encoding='utf-8-sig')

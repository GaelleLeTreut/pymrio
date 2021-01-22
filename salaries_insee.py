# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""
import os
import pandas as pd
import statistics as stat
import numpy as np
from dbf_into_csv import *

data_dir = 'data'

exec(open("Inc_Based.py").read())

#convertir le fichier dbf de l'insee en csv pour le traiter avec pandas
#faire attention de bien disposer du module dans le répertoire

#Ne convertir le fichier dBase en csv que s'il ne l'est pas déjà
#bien vérifier la présence du module dbf_to_csv.py dans le répertoire
if os.path.isfile(data_dir +os.sep + 'salaries15.csv')==True:
    print('le fichier salaries est déjà disponible au format csv')
else:
    dbf_to_csv(data_dir +os.sep + 'salaries15.dbf')
    print('Le fichier salaries15 est maintenant disponible au format csv')


#Methode 1 pour le calcul des contenus en émissions
# emis_cont_fr => from inc_based.py  

#Importer base salaires15 INSEE (euro 2015)
full_insee_table = pd.read_csv(data_dir + os.sep + 'salaries15.csv',sep=',',index_col=0, low_memory=False)
dict_TRNNETO_to_salary = {0 : stat.mean([0,200]),1 : stat.mean([200,500]),2 : stat.mean([500,1000]),3 : stat.mean([1000,1500]),4 : stat.mean([1500,2000]),5 : stat.mean([2000,3000]),6 : stat.mean([3000,4000]),7 : stat.mean([4000,6000]),8 : stat.mean([6000,8000]),9 : stat.mean([8000,10000]),10 : stat.mean([10000,12000]), 11 : stat.mean([12000,14000]),12 : stat.mean([14000,16000]), 13 : stat.mean([16000,18000]), 14 : stat.mean([18000,20000]), 15 : stat.mean([20000,22000]), 16 : stat.mean([22000,24000]), 17 : stat.mean([24000,26000]), 18 : stat.mean([26000,28000]),19 : stat.mean([28000,30000]),20 : stat.mean([30000,35000]), 21 : stat.mean([35000,40000]), 22 : stat.mean([40000,50000]),23 : 60000 }
full_insee_table['salary_value']=full_insee_table['TRNNETO'].replace(dict_TRNNETO_to_salary)
#Pas trouver d'infos sur l'INSEE concernant les secteurs non référencés (NaN), donc je les attribue au secteur AZ
full_insee_table['A38']=full_insee_table['A38'].fillna('AZ')

insee_classification_to_passage_classification={"AZ":"AZ","BZ":"BZ","CA":"CA","CB":"CB","CC":"CC","CD":"CD","CE":"CE_CF","CF":"CE_CF","CG":"CG","CH":"CH","CI":"CI","CJ":"CJ","CK":"CK","CL":"CL","CM":"CM","DZ":"DZ","EZ":"EZ","FZ":"FZ","GZ":"GZ","HZ":"HZ","IZ":"IZ","JA":"JA","JB":"JB","JC":"JC","KZ":"KZ","LZ":"LZ","MA":"MA_MC","MB":"MB","MC":"MA_MC","NZ":"NZ","OZ":"OZ","PZ":"PZ","QA":"QA_QB","QB":"QA_QB","RZ":"RZ","SZ":"SZ","TZ":"TZ","UZ":"UZ"}


def create_dic_from_sector_to_emission_content(sector_table,emission_content_table, passage_dic = insee_classification_to_passage_classification, sector_label_in_sector_table = 'A38', sector_label_in_emission_content_label='sector', emission_content_label='emission content'):
    """
    Return a dictionary that associates each sector of sector_table to their emission content given by emission_content_label
    by default, assume that sector column in sector_table is labeled by 'A38', that sector column in emission_content_sector is labeled by 'Code_Sector', that emission content column in emission_content sector is labeled by 'emission content'. Finally, it assumes that the dictionary from sector_table nomenclature of sectors to emission_content_table nomenclature is insee_classification_to_passage_classifcation
    """
    dic_to_emission_content = {}
    for x in sector_table[sector_label_in_sector_table].unique():
        try:
            passage_sector = insee_classification_to_passage_classification[x]
            emission_content = emission_content_table[emission_content_table[sector_label_in_emission_content_label]==passage_sector][emission_content_label].reset_index(drop=True)[0]
            dic_to_emission_content[x] = emission_content
        except KeyError:
            print('Impossible to retrieve emission content of sector ' +x)
            dic_to_emission_content[x]= np.nan
    return dic_to_emission_content

#rajouter les émissions au tableau
#ne marche pas pour l'instant

#rajoute la colonne Emissions (en t de CO2) à chaque individu référencé
# emis_cont_fr from inc_based.py
Scaling_factor=10**(-6)
dic_to_emission_content = create_dic_from_sector_to_emission_content(full_insee_table, emis_cont_fr) 
full_insee_table['income-based_emissions']= full_insee_table['salary_value'] * full_insee_table['A38'].replace(dic_to_emission_content)*Scaling_factor

#Total des emissions
#depuis la base des salaires,  MtCO2 
Emissions_insee_tot=sum(full_insee_table['income-based_emissions']*full_insee_table['POND'])*1e-6
print('France emissions from salaries insee: ',Emissions_insee_tot,'Mt de CO2')

#depuis inc_based.py, total income-based emission, MtCO2 
inc_based_emis_mrio_FR_tot=np.sum(income_based_emis_FR.values)*1e-6
print('France total income-based emissions from mrio database: ',inc_based_emis_mrio_FR_tot,'Mt de CO2')

#depuis inc_based.py, labour factor income-based emission, MtCO2 
inc_based_emis_mrio_FR_lab=np.sum(income_based_emis_FR.xs('Labour', axis=1, level=1, drop_level=False).values)*1e-6
print('France labour factor income-based emissions from mrio database: ',inc_based_emis_mrio_FR_lab,'Mt de CO2')

#comparaison: moins d'un tiers des Income-Basedemissions de la France seraient attribués aux salaires
comparaison=Emissions_insee_tot/inc_based_emis_mrio_FR_tot
print("Insee/Mrio income-based emissions ratio:",comparaison)
print("Insee/Mrio 'labour'based emissions ratio:",Emissions_insee_tot/inc_based_emis_mrio_FR_lab)


def ratio_of_mass(lower_bound, higher_bound, label_to_sum, label_of_bound, data):
    low_mass = np.sum( data[data[label_of_bound]<lower_bound][label_to_sum])
    high_mass = np.sum( data[data[label_of_bound]>higher_bound][label_to_sum])
    return high_mass / low_mass
    
def ratio_of_mass2(lower_bound, higher_bound, label_to_sum, label_of_bound, data):
    low_mass = np.sum( data[data[label_of_bound]<=lower_bound][label_to_sum])
    high_mass = np.sum( data[data[label_of_bound]>higher_bound][label_to_sum])
    return high_mass / low_mass

#Statistiques Descriptives
#base salaire
mean_salary=round(stat.mean(full_insee_table['salary_value']))
stdev_salary=stat.stdev(full_insee_table['salary_value'])
median_salary=stat.median(full_insee_table['salary_value'])
decile1_salary=np.percentile(full_insee_table['salary_value'],10)
decile9_salary=np.percentile(full_insee_table['salary_value'],90)
interdecile_salary=decile9_salary/decile1_salary
masses_salary = ratio_of_mass( decile1_salary, decile9_salary, 'salary_value', 'salary_value', full_insee_table)

#France Emissions
mean_emissions=stat.mean(full_insee_table['income-based_emissions'])
stdev_emissions=stat.stdev(full_insee_table['income-based_emissions'])
median_emissions=stat.median(full_insee_table['income-based_emissions'])
decile1_emissions=np.percentile(full_insee_table['income-based_emissions'],10)
decile9_emissions=np.percentile(full_insee_table['income-based_emissions'],90)
interdecile_emissions=decile9_emissions/decile1_emissions
masses_emissions = ratio_of_mass( decile1_salary, decile9_salary, 'income-based_emissions', 'salary_value', full_insee_table)

#Comparaison
dispersion=interdecile_emissions>interdecile_salary
if dispersion:
    print("Il y a plus d'inégalités d'émissions que de salaires")
else:
    print("Il y a plus d'inégalités de salaires que d'émissions")
import pandas as pd

def xls_to_base(fname:str)->list:
    df = pd.read_excel(fname,skipfooter=161,names=['row'+str(i) for i in list(range(25))]).fillna('none')
    df = (df[['row1','row2','row3','row4','row5','row6','row7','row8','row9','row11','row18','row19','row21']]
        .rename(columns={'row1':'protocol','row2':'ip','row3':'hostname','row4':'model','row5':'dev_ios',
                        'row6':'serial_n','row7':'building','row8':'room','row9':'place','row11':'inv_n',
                        'row18':'description','row19':'power_type','row21':'power'})
        .dropna(how='all'))
    result_list = df.to_dict('records')
    for each in result_list:
        for param in each:
            each[param]=str(each[param]).strip()            
        if not each['power'].isdigit():
            each['power']=0
    return result_list
import pandas as pd
def xls_to_base(fname:str)->list:
    df = pd.read_excel(fname,skipfooter=161,names=['row'+str(i) for i in list(range(25))]).fillna('none')
    df = (df[['row2','row3','row4','row5','row6','row7','row8','row9']]
        .rename(columns={'row2':'ip','row3':'hostname','row4':'model','row5':'ios',
                        'row6':'serial','row7':'building','row8':'room','row9':'place'})
        .dropna(how='all'))
    result_dict = df.to_dict('records')
    return result_dict
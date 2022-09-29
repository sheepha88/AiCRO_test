import numpy as np
import pandas as pd
import datetime
import warnings
import openpyxl
warnings.filterwarnings("ignore")



#baeline에서 PCBSLD , PCNSLD , SUMBLD , SUMNLD 등은 np.nan값으로 바꿔주는 함수
# ex)makevalue(df , "SCRN_CT", "PCBSLD" , np.nan)
# baelineNAME : baeline이름(bl or SCRN_CT,,,) , colname : 컬럼이름 , value: 변경 후 값 (여기서는 np.nan)
# dataframe copy를 썼기 때문에 선언해줘야 한다 ex)df.loc[0,"PCBSLD"] = makevalue(df ,0 , "SCRN_CT", "PCBSLD" , 3)

def makevalue(dataframe, baselineNAME , colname , value):
    
    new_dataframe = dataframe.copy(deep = True)
    
    for i in range(len(dataframe)):

        if new_dataframe.loc[i , "VISIT"]==baselineNAME:
            new_dataframe.loc[i , colname] = value
    
    return new_dataframe





#map develop 함수 -> dictionary에 없는 값은 원래의 값을 출력
# ex) map_dict(df , "LAGRADE",LAGRADE_dict ).unique()
def map_dict(dataframe, col , dict_name):
    func = lambda x : dict_name.get(x,x)
    dataframe_new = dataframe[col].map(func , na_action = None)
    
    return dataframe_new
    
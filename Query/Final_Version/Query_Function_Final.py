import numpy as np
import pandas as pd
import datetime
import warnings
import openpyxl
warnings.filterwarnings("ignore")


###조정자 pick 오류 검토 함수
#ADJ_PICK(df , "01S306" , "Baseline (1st scan)" , "ADJUDICATOR" , "Analyst#1" , "Analyst#2" , ["TRGOC_1","TRGOCOT_1","TRGLD_1"])
# 1. raw_dataframe에서 해당 대상자의 baseline에서 columns를 기준으로 ADJ와 Analyst를 비교하여 ADJ가 누굴 택했는지 확인(인자 = ADJ_Pick_Analayst)
# 2. ADJ 와 선택된 Analyst들만 있는 테이블을 뽑아내고 , 조정자 행과 선택된 Analyst행의 columns값들을 비교하여 하나라도 틀린 행이 있으면 출력

def ADJ_PICK(dataframe, USUBJID , Baselinename , ADJUDICATOR , Analyst_1 , Analyst_2 , columns):
    
    #해당 대상자의 baseline만 뽑아낸 테이블
    baseline_Dataframe = dataframe[ (dataframe["USUBJID"]==USUBJID) & (dataframe["VISIT"]==Baselinename)].reset_index(drop=True)
    
    #해당 대상자의 전체 visit 뽑아낸 테이블
    visit_Dataframe = dataframe[ (dataframe["USUBJID"]==USUBJID)].reset_index(drop=True)
    
  
    # 조정자의 columns값과 Analyst#1의 columns값이 baseline에서 같다면 analyst#1을 출력해라
    if baseline_Dataframe.loc[list(baseline_Dataframe[baseline_Dataframe["READER"]==ADJUDICATOR].index)[0] , columns].equals\
        (baseline_Dataframe.loc[list(baseline_Dataframe[baseline_Dataframe["READER"]==Analyst_1].index)[0] , columns]):
            ADJ_Pick_Analayst = Analyst_1
            
    
    elif baseline_Dataframe.loc[list(baseline_Dataframe[baseline_Dataframe["READER"]==ADJUDICATOR].index)[0] , columns].equals\
        (baseline_Dataframe.loc[list(baseline_Dataframe[baseline_Dataframe["READER"]==Analyst_2].index)[0] , columns]):
            ADJ_Pick_Analayst = Analyst_2
    
    
    #baseline에서 조정자가 pick한 Analyst와 조정자값만으로 이루어진 테이블 생성
    visit_Dataframe = visit_Dataframe[visit_Dataframe["READER"].isin([ADJUDICATOR ,ADJ_Pick_Analayst ])].reset_index(drop=True)
    
    
    #반복문으로 격수로 (ADJ , Analyst#) 비교해서 컬럼중 데이터값이 하나라도 틀리면 조정자 , Analyst행 출력
    result = pd.DataFrame()
    for i in range(0,len(visit_Dataframe),2):
        if not visit_Dataframe.loc[i,columns].equals(visit_Dataframe.loc[i+1,columns]):
            result = result.append([visit_Dataframe.loc[i,:] ,visit_Dataframe.loc[i+1,:] ])
            
        else:
            pass
        
    return result 
    
    
        



#map develop 함수 -> dictionary에 없는 값은 원래의 값을 출력
# ex) map_dict(df , "LAGRADE",LAGRADE_dict ).unique()
def map_dict(dataframe, col , dict_name):
    func = lambda x : dict_name.get(x,x)
    dataframe_new = dataframe[col].map(func , na_action = None)
    
    return dataframe_new
    


# # 배치리스트와 export한 data 일치하는지 확인-배치리스트의 각 대상자 visit정보 리스트화 시키는 과정
# ex) visit_extract(df_list , "Subject No","S32-13013")
# 
# 1)
def visit_extract(dataframe_batchlist , col ,  subjectNO ):
    
    #dataframe_batchlist_column_list 중 Baseline~EOT까지 범위설정 , 보통 0번쨰가 USUBJID라 1번째 부터 시작
    dataframe_batchlist_column_list = dataframe_batchlist.columns[1:]  
    
    #return 결과 담을 list 생성
    visit_result = []
    
    for z in dataframe_batchlist_column_list:
        if pd.notnull(dataframe_batchlist[dataframe_batchlist[col] ==subjectNO].reset_index(drop = True).loc[0,z]):
            visit_result.append(z)
                
    return visit_result

# 4) 사용방법
# dict_list = {}
# for i in list(df_batch["USUBJID"].unique()):
#     dict_list[i] = visit_extract(df_batch , "USUBJID", i )
    
# dict_list


# 2) 대상자와 각 대상장의 visit정보를 dict형식으로 묶는다
# ex) {'S32-01002': ['Baseline', 'W08(±7D)', 'W16(±7D)', 'W24(±7D)', 'W32(±7D)'],
#      'S32-01006': ['Baseline', 'W08(±7D)', 'W16(±7D)']}

# 반복문으로 각 여러대상자의 visit 정보를 dict형식을 묶어줌
# dict_list = {}
# for i in list(df_list["Subject No"]):
#     dict_list[i] = visit_extract(df_list , "Subject No", i )

# 3) export data 의 각 대상자의 visit 정보 중 dict_list의 visit정보의 개수가 맞는지 확인하면 끝!
# ex)for i in list(df_list["Subject No"]):
#   print(i, len(df_raw[(df_raw["SubjectNo"] ==i) & (df_raw["Visit"].isin(dict_list[i]))]))


    

#----------------------------------------------------------------
# # Lesion(TRGOC)가 있는데, TRGOC, TRGOCOT가 둘 다 없는 경우
# # Lesion(TRGOC)가 있는데, TRGOC 또는 TRGOCOT가  없는 경우

# In[13]:


#kwargs 의 value값은 and, or로 지정, ex) operator = and

def andor(range1, range2, dataframe,*args, **kwargs):
     
    #df_TL에 DM_CMT 컬럼 추가
    new_list = list(dataframe.columns)
    new_list.append("DM_CMT")
    
    #col1 = string
    #col2 = string

    #범위 지정->string으로 받는다
    list_range = [str(i) for i in list(range(range1, range2))]
    
    #kwargs의 key값, value값을 리스트로 받고 인덱싱 한다 -> 나오는 결과괎: ex."TRGMET"
    key = [keys for keys in kwargs.keys()][0]
    value = [values for values in kwargs.values()][0]
    
    #변수가 3개일때
    #operator가 and 일때 , -> TRGOCOT도 없고, TRGOCOSIT도 없는경우
    if len(args)==3:
        if value=="and":
            #빈 데이터프레임 생성
            df_empty = pd.DataFrame( columns = new_list)
            df_append = pd.DataFrame( columns = new_list)
            for numlist in list_range:
                df_empty = dataframe[(dataframe[args[0]+"_"+numlist].notnull()) & ( (dataframe[args[1]+"_"+numlist].isnull()) & (dataframe[args[2]+"_"+numlist].isnull()) )]
                df_empty["DM_CMT"] = args[0]+"_"+numlist+"가 value가 있는데, "+args[1]+"_"+numlist+"이 없고,"+args[2]+"_"+numlist+"도 없는 경우"
                df_append = df_append.append(df_empty)
                
        if value=="or":
            #빈 데이터프레임 생성
            df_empty = pd.DataFrame( columns = new_list)
            df_append = pd.DataFrame( columns = new_list)
            for numlist in list_range:
                df_empty = dataframe[(dataframe[args[0]+"_"+numlist].isnull()) & ( (dataframe[args[1]+"_"+numlist].notnull()) | (dataframe[args[2]+"_"+numlist].notnull()) )]
                df_empty["DM_CMT"] = args[0]+"_"+numlist+"가 NA인데, "+args[1]+"_"+numlist+"이 있거나,"+args[2]+"_"+numlist+"이 있는 경우"
                df_append = df_append.append(df_empty)
    
    
    

    return df_append
    


# # NA, Value_v2

# In[56]:


def valuena(range1, range2, dataframe, *args, **kwargs):
    
    #df_TL에 DM_CMT 컬럼 추가
    new_list = list(dataframe.columns)
    new_list.append("DM_CMT")

    #범위 지정->string으로 받는다
    list_range = [str(i) for i in list(range(range1, range2))]
    
    #kwargs의 key값, value값을 리스트로 받고 인덱싱 한다 -> 나오는 결과괎: ex."TRGMET"
    key = [keys for keys in kwargs.keys()]
    value = [values for values in kwargs.values()]
    
    #TRGOC값이 TRGLD가 없는 경우
    #response 중 NE, CR이 포함된 경우는 제외 , tumor길이는 상관없음
    #valuena(1,6,df_TL,"TRGOC","TRGLD", response="TRGRESP",exclude=["NE","CR"])
    if "response" in key:
        #빈 데이터프레임 생성
        df_empty = pd.DataFrame( columns = new_list)
        df_append = pd.DataFrame( columns = new_list)

        for numlist in list_range:
            df_empty = dataframe[(dataframe[args[0]+"_"+numlist].notnull())  &  (dataframe[args[1]+"_"+numlist].isnull())]
            df_empty = df_empty[-df_empty[kwargs["response"]].isin(kwargs["exclude"])]
            df_empty["DM_CMT"] = args[0]+"_"+numlist+"가 value가 있는데,"+args[1]+numlist+"가 na인 경우"
            df_append = df_append.append(df_empty)
    
    
    #tumor길이에 따라 달라지는 경우, response가 상관없는 경우
    elif "length" in key:
        #튜머길이가 없을 경우        
        if kwargs["length"] == "NA":
            #빈 데이터프레임 생성
            df_empty = pd.DataFrame( columns = new_list)
            df_append = pd.DataFrame( columns = new_list)

            for numlist in list_range:
                df_empty = dataframe[dataframe[args[0]+"_"+numlist].notnull()  &  dataframe[args[1]+"_"+numlist].isnull()]
                df_empty["DM_CMT"] = args[0]+"_"+numlist+"가 value가 있는데,"+args[1]+numlist+"가 na인 경우"
                df_append = df_append.append(df_empty)
                

        
        #튜머길이가 있을 경우
        if kwargs["length"] != "NA":
            #빈 데이터프레임 생성
            df_empty = pd.DataFrame( columns = new_list)
            df_append = pd.DataFrame( columns = new_list)

            for numlist in list_range:
                df_empty = dataframe[dataframe[args[0]+"_"+numlist].notnull()  &  dataframe[args[1]+"_"+numlist].isnull()]
                df_empty = df_empty[df_empty[kwargs["length"]+"_"+numlist]!=0]
                df_empty["DM_CMT"] = args[0]+"_"+numlist+"가 value가 있는데,"+args[1]+"_"+numlist+"가 na인 경우"
                df_append = df_append.append(df_empty)
        
    return df_append





#lenth = tumor 길이
# lenght = "NA" -> 매개변수 기본값 설정 -> 함수에 lenght값을 기입하지 않으면 기본값(여기에서는 NA)값이 기입됨
# length 기입 X -> 매칭이 안됨 -> 기본값 NA를 가지고 있기 때문에 NA로 기입됨 -> tumor길이를 고려하지 않고 함수적용
# length 기입 O -> 매칭        -> 기입한 컬럼으로 기입됨 -> tumor길이가 0이 아닌 경우 query내용 보여줌

def navalue(range1, range2, dataframe, col1, col2, length="NA"):
    
    #df_TL에 DM_CMT 컬럼 추가
    new_list = list(dataframe.columns)
    new_list.append("DM_CMT")
    
    #빈 데이터프레임 생성
    df_empty = pd.DataFrame( columns = new_list)
 
    #범위 지정->string으로 받는다
    list_range = [str(i) for i in list(range(range1, range2))]
    
    if length == "NA":
        #빈 데이터프레임 생성
        df_empty = pd.DataFrame( columns = new_list)
        df_append = pd.DataFrame( columns = new_list)
        for numlist in list_range:
            df_empty = dataframe[dataframe[col1+"_"+numlist].isnull()  &  dataframe[col2+"_"+numlist].notnull()]
            df_empty["DM_CMT"] = col1+"_"+numlist+"가 na이지만,"+col2+numlist+"가 value가 있는 경우"
            df_append = df_append.append(df_empty)
            
    if length != "NA":
        #빈 데이터프레임 생성
        df_empty = pd.DataFrame( columns = new_list)
        df_append = pd.DataFrame( columns = new_list)
        for numlist in list_range:
            df_empty = dataframe[dataframe[col1+"_"+numlist].isnull()  &  dataframe[col2+"_"+numlist].notnull()]
            df_empty = df_empty[df_empty[length+"_"+numlist]!=0]
            df_empty["DM_CMT"] = col1+"_"+numlist+"가 na이지만,"+col2+numlist+"가 value가 있는 경우"
            df_append = df_append.append(df_empty)
             
    return df_append


# # NA, Value TRGDL_SE, TRGDL_IM

# In[9]:


def valuenaseim(range1, range2, dataframe, *args, **kwargs):
    
    #df_TL에 DM_CMT 컬럼 추가
    new_list = list(dataframe.columns)
    new_list.append("DM_CMT")

    #범위 지정->string으로 받는다
    list_range = [str(i) for i in list(range(range1, range2))]
    
    #kwargs의 key값, value값을 리스트로 받고 인덱싱 한다 -> 나오는 결과괎: ex."TRGMET"
    key = [keys for keys in kwargs.keys()]
    value = [values for values in kwargs.values()]
    
    
#col2 가 TRGDL_SE일 때
#length=0, Response가 "NE","CR"이면 제외

    #TRGOC 일때(Target Lesion 일때)
    #valuenaseim(1,2,df_TL, "TRGOC","TRGDL_SE",length = "TRGLDIAM" ,response = "TRGRESP",  exclude =  ["CR","NE"])
    if args[0]=="TRGOC":
        if "SE" in args[1].split("_"):
            #튜머길이가 있을 경우, 
            #Response가 CR 또는 NE일경우 제외
            if kwargs["length"] != "NA":
                if "response" in key:
                    #빈 데이터프레임 생성
                    df_empty = pd.DataFrame( columns = new_list)
                    df_append = pd.DataFrame( columns = new_list)

                    for numlist in list_range:
                        df_empty = dataframe[(dataframe[args[0]+"_"+numlist].notnull())  &  (dataframe[args[1]+numlist].isnull())]
                        df_empty = df_empty[df_empty[kwargs["length"]+"_"+numlist]!=0]
                        df_empty = df_empty[-df_empty[kwargs["response"]].isin(kwargs["exclude"])]
                        df_empty["DM_CMT"] = args[0]+"_"+numlist+"가 value가 있는데,"+args[1]+numlist+"가 na인 경우"
                        df_append = df_append.append(df_empty)

            # length가 NA인 경우는 없을것으로 판단하여 주석처리
            # if kwargs["length"] == "NA":
            #     if "response" in key:
            #         #빈 데이터프레임 생성
            #         df_empty = pd.DataFrame( columns = new_list)
            #         df_append = pd.DataFrame( columns = new_list)

            #         for numlist in list_range:
            #             df_empty = dataframe[(dataframe[args[0]+"_"+numlist].notnull())  &  (dataframe[args[1]+numlist].isnull())]
            #             df_empty = df_empty[-df_empty[kwargs["response"]].isin(kwargs["exclude"])]
            #             df_empty["DM_CMT"] = args[0]+"_"+numlist+"가 value가 있는데,"+args[1]+numlist+"가 na인 경우"
            #             df_append = df_append.append(df_empty)


        #valuenaseim(1,2,df_TL, "TRGOC","TRGDL_IM",length = "TRGLDIAM" ,response = "TRGRESP",  exclude =  ["CR","NE"])
        #col2 가 TRGDL_IM일 때
        if "IM" in args[1].split("_"):
            #튜머길이가 있을 경우, 
            #Response가 CR 또는 NE일경우 제외
            if kwargs["length"] != "NA":
                if "response" in key:
                    #빈 데이터프레임 생성
                    df_empty = pd.DataFrame( columns = new_list)
                    df_append = pd.DataFrame( columns = new_list)

                    for numlist in list_range:
                        df_empty = dataframe[dataframe[args[0]+"_"+numlist].notnull()  &  dataframe[args[1]+numlist].isnull()]
                        df_empty = df_empty[df_empty[kwargs["length"]+"_"+numlist]!=0]
                        df_empty = df_empty[-df_empty[kwargs["response"]].isin(kwargs["exclude"])]
                        df_empty["DM_CMT"] = args[0]+"_"+numlist+"가 value가 있는데,"+args[1]+numlist+"가 na인 경우"
                        df_append = df_append.append(df_empty)

            if kwargs["length"] == "NA":
                if "response" in key:
                    #빈 데이터프레임 생성
                    df_empty = pd.DataFrame( columns = new_list)
                    df_append = pd.DataFrame( columns = new_list)

                    for numlist in list_range:
                        df_empty = dataframe[(dataframe[args[0]+"_"+numlist].notnull())  &  (dataframe[args[1]+numlist].isnull())]
                        df_empty = df_empty[-df_empty[kwargs["response"]].isin(kwargs["exclude"])]
                        df_empty["DM_CMT"] = args[0]+"_"+numlist+"가 value가 있는데,"+args[1]+numlist+"가 na인 경우"
                        df_append = df_append.append(df_empty)
    
    #NTRGOC 일때(Non Target Lesion 일때)
    if args[0]=="NTRGOC":
        if "SE" in args[1].split("_"):
            #튜머길이가 있을 경우, 
            #Response가 CR 또는 NE일경우 제외
            if kwargs["length"] == "NA":
                if "response" in key:
                    #빈 데이터프레임 생성
                    df_empty = pd.DataFrame( columns = new_list)
                    df_append = pd.DataFrame( columns = new_list)

                    for numlist in list_range:
                        df_empty = dataframe[(dataframe[args[0]+"_"+numlist].notnull())  &  (dataframe[args[1]+numlist].isnull())]
                        df_empty = df_empty[-df_empty[kwargs["response"]+"_"+numlist].isin(kwargs["exclude"])]
                        df_empty["DM_CMT"] = args[0]+"_"+numlist+"가 value가 있는데,"+args[1]+numlist+"가 na인 경우"
                        df_append = df_append.append(df_empty)


        #col2 가 TRGDL_IM일 때
        if "IM" in args[1].split("_"):
            #튜머길이가 있을 경우, 
            #Response가 CR 또는 NE일경우 제외
            if kwargs["length"] == "NA":
                if "response" in key:
                    #빈 데이터프레임 생성
                    df_empty = pd.DataFrame( columns = new_list)
                    df_append = pd.DataFrame( columns = new_list)

                    for numlist in list_range:
                        df_empty = dataframe[(dataframe[args[0]+"_"+numlist].notnull())  &  (dataframe[args[1]+numlist].isnull())]
                        df_empty = df_empty[-df_empty[kwargs["response"]+"_"+numlist].isin(kwargs["exclude"])]
                        df_empty["DM_CMT"] = args[0]+"_"+numlist+"가 value가 있는데,"+args[1]+numlist+"가 na인 경우"
                        df_append = df_append.append(df_empty)
        
    #NTRGOC 일때(Non Target Lesion 일때)
    if args[0]=="NEWLOC":
        if "SE" in args[1].split("_"):
            #튜머길이가 있을 경우, 
            #Response가 CR 또는 NE일경우 제외
            if kwargs["length"] == "NA":
                #빈 데이터프레임 생성
                df_empty = pd.DataFrame( columns = new_list)
                df_append = pd.DataFrame( columns = new_list)

                for numlist in list_range:
                    df_empty = dataframe[(dataframe[args[0]+"_"+numlist].notnull())  &  (dataframe[args[1]+numlist].isnull())]
                    df_empty["DM_CMT"] = args[0]+"_"+numlist+"가 value가 있는데,"+args[1]+numlist+"가 na인 경우"
                    df_append = df_append.append(df_empty)


        #col2 가 TRGDL_IM일 때
        if "IM" in args[1].split("_"):
            #튜머길이가 있을 경우, 
            #Response가 CR 또는 NE일경우 제외
            if kwargs["length"] == "NA":
                #빈 데이터프레임 생성
                df_empty = pd.DataFrame( columns = new_list)
                df_append = pd.DataFrame( columns = new_list)

                for numlist in list_range:
                    df_empty = dataframe[(dataframe[args[0]+"_"+numlist].notnull())  &  (dataframe[args[1]+numlist].isnull())]
                    df_empty["DM_CMT"] = args[0]+"_"+numlist+"가 value가 있는데,"+args[1]+numlist+"가 na인 경우"
                    df_append = df_append.append(df_empty)
   
    return df_append


# # Other, Na, value

# In[8]:


#TRGMET 값이 Other인데 , TRGMETOT_n 이 없는 경우(TRGLD_n이 0이 아닌경우)

def otherna(range1, range2, dataframe,*args, **kwargs):
    
    #df_TL에 DM_CMT 컬럼 추가(df_TL에는 DM_CMT컬럼이 없기 때문에)
    new_list = list(dataframe.columns)
    new_list.append("DM_CMT")    
    
    #범위 지정->string으로 받는다
    list_range = [str(i) for i in list(range(range1, range2))]
    
    #kwargs의 key값, value값을 리스트로 받고 인덱싱 한다 -> 나오는 결과괎: ex."TRGMET"
    key = [keys for keys in kwargs.keys()][0]
    value = [values for values in kwargs.values()][0]
    
    
    #변수가 3개일때
    #tumor길이가 필요없을 때, 일반적인 상황 : if value=="NA" ->default값
    #ex) otherna(1,6,df_TL,"TRGOC","TRGOCOT","TRGOCSITE",length="NA")
    if len(args)==3:
        if value=="NA":
            #빈 데이터프레임 생성
            df_empty = pd.DataFrame( columns = new_list)
            df_append = pd.DataFrame( columns = new_list)
            for numlist in list_range:
                df_empty = dataframe[(dataframe[args[0]+"_"+numlist].isin(["Other","Others"])) & ( (dataframe[args[1]+"_"+numlist].isnull()) & (dataframe[args[2]+"_"+numlist].isnull()) )]
                df_empty["DM_CMT"] = args[0]+"_"+numlist+"가 Other인데 "+args[1]+"_"+numlist+"이 없고,"+args[2]+"_"+numlist+"도 없는 경우"
                df_append = df_append.append(df_empty)
                
                
    #변수가 2개일때
    #tumor길이가 필요할 때, 특수한 상황 : if value!="NA" ->tumor길이가 0이 아닌 경우
    #ex) otherna(1,6,df_TL,"TRGMET","TRGMETOT",length="TRGLD")
    if len(args)==2:
        if value!="NA":
            #빈 데이터프레임 생성
            df_empty = pd.DataFrame( columns = new_list)
            df_append = pd.DataFrame( columns = new_list)
            for numlist in list_range:
                #결과가 출력될 dataframe = df_NA : TRGOCSITE_1_NA
                df_empty = dataframe[(dataframe[args[0]+"_"+numlist].isin(["Other","Others"]))  & ( dataframe[args[1]+"_"+numlist].isnull() )]

                #value값(tumor길이)가 0인것은 제외 
                df_empty = df_empty[df_empty[value+"_"+numlist]!=0]
                df_empty["DM_CMT"] = args[0]+"_"+numlist+"값이 Other인데,"+args[1]+numlist+"가 없는 경우"
                df_append = df_append.append(df_empty)
                
        if value=="NA":
            #빈 데이터프레임 생성
            df_empty = pd.DataFrame( columns = new_list)
            df_append = pd.DataFrame( columns = new_list)
            for numlist in list_range:
                #결과가 출력될 dataframe = df_NA : TRGOCSITE_1_NA
                df_empty = dataframe[(dataframe[args[0]+"_"+numlist].isin(["Other","Others"]))  & ( dataframe[args[1]+"_"+numlist].isnull() )]
                df_empty["DM_CMT"] = args[0]+"_"+numlist+"값이 Other인데,"+args[1]+numlist+"가 없는 경우"
                df_append = df_append.append(df_empty)
    
    
    #최종 데이터프레임 산출
    return df_append



#Other가 아닌데, 값이 있는 경우(TRGOC값이 Others가 아닌데, TRGOCOT 이 있는 경우)
# ex)nothervalue(1,6,df_TL , "TRGOC","TRGOCOT" , length = "NA")
def nothervalue(range1, range2, dataframe,*args, **kwargs):
    
    #df_TL에 DM_CMT 컬럼 추가(df_TL에는 DM_CMT컬럼이 없기 때문에)
    new_list = list(dataframe.columns)
    new_list.append("DM_CMT")
    
    #범위 지정->string으로 받는다
    list_range = [str(i) for i in list(range(range1, range2))]
    
    #kwargs의 key값, value값을 리스트로 받고 인덱싱 한다 -> 나오는 결과괎: ex."TRGMET"
    key = [keys for keys in kwargs.keys()][0]
    value = [values for values in kwargs.values()][0]
                      
    #변수가 2개일때
        #tumor길이가 필요할 때, 일반적인 상황 : if value!="NA":
    if len(args)==2:
        if value=="NA":
            df_empty = pd.DataFrame( columns = new_list)
            df_append = pd.DataFrame( columns = new_list)
            for numlist in list_range:
                df_empty = dataframe[(-dataframe[args[0]+"_"+numlist].isin(["Other","Others"]))  & ( dataframe[args[1]+"_"+numlist].notnull() )]
                df_empty["DM_CMT"] = args[0]+"_"+numlist+"값이 Other가 아닌데,"+args[1]+numlist+"가 있는 경우"
                df_append = df_append.append(df_empty)
    
    #최종 데이터프레임 산출
    return df_append



#TRGRESP 판별 알고리즘
def TargetResponse(dataframe):
    #dataframe index 재정렬
    dataframe = dataframe.reset_index(drop=True)
    
    #index순으로 반복하여 TRGRESP산출
    for i in list(range(len(dataframe))):
        
        #PCNSLD가 20%보다 크고, 차이가 5보다 크면, PD
        if dataframe.loc[i,"PCNSLD"]>=20:
            if dataframe.loc[i,"ABS"]>=5:
                dataframe.loc[i,"TRGRESP_YJW"]="PD"
            
            #만약 차이가 5보다 작다면, SD
            elif dataframe.loc[i,"ABS"]<5:
                dataframe.loc[i,"TRGRESP_YJW"]="SD"
            
        elif -100<dataframe.loc[i,"PCBSLD"]<=-30:
            dataframe.loc[i,"TRGRESP_YJW"]="PR"
            
        elif dataframe.loc[i,"PCBSLD"]<=-100:
            dataframe.loc[i,"TRGRESP_YJW"]="CR"
            
        else:
            dataframe.loc[i,"TRGRESP_YJW"]="SD"
            
            
    #VISIT 이 screening 이면 TRGRESP 값이 NA 이다.
    dataframe["TRGRESP_YJW"][dataframe["VISIT"].isin(["Baseline","BL"])]=np.nan
    
    return dataframe



def TargetResponse_YN(dataframe):
    
    #판독자와 알고리즘 결과값이 다른 경우 표시       
    for i in list(range(len(dataframe))):
        if dataframe.loc[i, "TRGRESP"] != dataframe.loc[i, "TRGRESP_YJW"]:
            dataframe.loc[i,"YN"] = "N"
            
        if (pd.isnull(dataframe.loc[i, "TRGRESP"])) & (pd.isnull(dataframe.loc[i, "TRGRESP_YJW"])):
            dataframe.loc[i,"YN"] = "Y"
            


        if dataframe.loc[i, "TRGRESP"] == dataframe.loc[i, "TRGRESP_YJW"]:
            dataframe.loc[i,"YN"] = "Y"
                
    return dataframe



#------------------------------------------
# Overall Response logic

def OverallResponse(dataframe):
    for i in list(range(len(dataframe))):
        if dataframe.loc[i,"TRGIND"]=="Yes":                    
            if dataframe.loc[i,"TRGRESP"]=="PD":
                dataframe.loc[i,"OVRESP_YJW"]="PD"
            
            elif dataframe.loc[i,"NTRGRESP"]=="PD":
                dataframe.loc[i,"OVRESP_YJW"]="PD"
                
            elif dataframe.loc[i,"NEWLIND"]=="Yes":
                dataframe.loc[i,"OVRESP_YJW"]="PD"
                
                
            elif dataframe.loc[i,"TRGRESP"]=="CR":
                if dataframe.loc[i,"NTRGRESP"]=="CR":
                    if dataframe.loc[i,"NEWLIND"]=="No":
                        dataframe.loc[i,"OVRESP_YJW"]="CR"
                        
                elif dataframe.loc[i,"NTRGRESP"] in ["CR","Non-CR/Non-PD","Not evaluable","NE"]:
                    if dataframe.loc[i,"NEWLIND"]=="No":
                        dataframe.loc[i,"OVRESP_YJW"]="PR"
                        
            elif dataframe.loc[i,"TRGRESP"]=="PR":
                if dataframe.loc[i,"NTRGRESP"] in ["CR","Non-CR/Non-PD","Not evaluable","NE"]:
                    if dataframe.loc[i,"NEWLIND"]=="No":
                        dataframe.loc[i,"OVRESP_YJW"]="PR"
                        
            elif dataframe.loc[i,"TRGRESP"]=="SD":
                if dataframe.loc[i,"NTRGRESP"] in ["CR","Non-CR/Non-PD","Not evaluable","NE"]:
                        if dataframe.loc[i,"NEWLIND"]=="No":
                            dataframe.loc[i,"OVRESP_YJW"]="SD"
                        
            elif dataframe.loc[i,"TRGRESP"] in ["Not Evaluable","NE"]:
                if dataframe.loc[i,"NTRGRESP"] == "Non-CR/Non-PD":
                    if dataframe.loc[i,"NEWLIND"]=="No":
                        dataframe.loc[i,"OVRESP_YJW"]="NE"
                    
        elif dataframe.loc[i,"TRGIND"]=="No":
            if dataframe.loc[i,"NTRGRESP"]=="CR":
                if dataframe.loc[i,"NEWLIND"]=="No":
                    dataframe.loc[i,"OVRESP_YJW"]="CR"
                    
            elif dataframe.loc[i,"NTRGRESP"]=="Non-CR/Non-PD":
                if dataframe.loc[i,"NEWLIND"]=="No":
                    dataframe.loc[i,"OVRESP_YJW"]="non-CR/non-PD"
                    
            elif dataframe.loc[i,"NTRGRESP"] in ["Not evaluable","NE"]:
                if dataframe.loc[i,"NEWLIND"]=="No":
                    dataframe.loc[i,"OVRESP_YJW"]="NE"
                    
            elif dataframe.loc[i,"NTRGRESP"]=="PD":
                dataframe.loc[i,"OVRESP_YJW"]="PD"
                
            if dataframe.loc[i,"NEWLIND"]=="Yes":
                dataframe.loc[i,"OVRESP_YJW"]="PD"
        

        else:
            dataframe.loc[i,"OVRESP_YJW"]=np.nan
        
    return dataframe
        
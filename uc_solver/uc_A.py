import pulp as lp
import pandas as pd
import numpy as np
import random,os,json

"""
THIS MODEL WILL SOLVE (1) TIME STEP OF UC WITH ONLY ON/OFF BEING AVAILABLE.

"""


### https://stackoverflow.com/questions/77622453/helping-with-lp-timeseries-using-pulp

GENERATORS  = pd.read_csv('Generator_database.csv')
FUELS       = pd.read_csv('Fuels.csv',index_col='Fuel Name')
RAW_DEMAND  = pd.Series(data=[random.randint(13000,25000) for i in range(len(GENERATORS[GENERATORS.columns.tolist()[0]]))],
                       index = range(1,len(GENERATORS[GENERATORS.columns.tolist()[0]]) + 1) )

def minimize_cost(idx):
    """
    We want to minimize the :
        - Cost of generation subject to the production cost, startup costs, shut down costs, penalty costs 

    min SUM_all_t (SUM_all_gens (c_g^p(t) + C_g^R*ug(t) + c_g^SU(t) + c_g^SD(t)) + SUM_all_busses(C_LP * (s_n^+(t) + s_n^-(t)) + C_RP * s_R(t)))
    
    
    """
    
    sub_df  = GENERATORS.iloc[idx]
    hr      = sub_df['Heat Rate (MMBtu/MWh)']
    su_c    = sub_df['Start Up Costs ($/MW)']
    sd_c    = sub_df['Shut Down Costs ($/MW)']
    fuel    = sub_df['Energy Source Code']

    return FUELS.loc[fuel].values[0] * hr + su_c + sd_c

def get_capacity(gen_idx):
    """
    Returns the nameplate capacity for the generator referenced.
    """
    return GENERATORS.loc[gen_idx]['Nameplate Capacity (MW)']


prob        = lp.LpProblem('UnitCommitment',lp.LpMinimize)

# Creating a dict utilizing the indexes of the generators being the unique id's
UNITS           = lp.LpVariable.dicts('Units',[i for i in GENERATORS.index.tolist()],0,1,lp.LpInteger)  
#UNIT_CAPACITY   = lp.LpVariable('Unit_Capacity',[GENERATORS[GENERATORS.iloc[idx]]['Nameplate Capacity (MW)'] for idx in GENERATORS.index.tolist()],0,None,lp.LpInteger)


# NOTE: Adding the objective function to the LP solver.
# NOTE: THESE ARE THE UNIT VALUES....I.E. THE STATE VARIABLES. THE OUTPUT IS WHICH ONES ARE ON AND THE SUMMATION OF THE GENS MUST > DEMAND
prob += (
    lp.lpSum([UNITS[idx] * minimize_cost(idx) for idx in UNITS.keys()]), 
                f'Objective_fcn')

# NOTE: Adding constraint to ensure supply > demand
j = random.randint(0, len(RAW_DEMAND))
prob += (lp.lpSum([UNITS[idx] * get_capacity(idx) for idx in UNITS.keys()]) >= RAW_DEMAND[j],
         'Supply_>_Demand')


# NOTE: Adding generation min/max constraints
#-- state transition variables....how to.

prob.writeLP('uc.lp')
prob.solve()









# ===================================================================================
# ============================== Creates a dataframe of results =====================
df = pd.DataFrame()

for gen in UNITS:
    if len(df) == 0:
        #print(float([GENERATORS.iloc[gen]['Nameplate Capacity (MW)']][0]))
        data = {'Gen_id': [UNITS[gen]],'Value':[UNITS[gen].value()], 'Capacity': [float([GENERATORS.iloc[gen]['Nameplate Capacity (MW)']][0])] }
        df = pd.DataFrame(data)
    else:
        data = {'Gen_id': [UNITS[gen]],'Value':[UNITS[gen].value()], 'Capacity': [float([GENERATORS.iloc[gen]['Nameplate Capacity (MW)']][0])] }
        df = pd.concat([df,pd.DataFrame(data)])

df.to_csv('results.csv',index=False)


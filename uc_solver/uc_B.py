import pulp as lp
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt

### https://stackoverflow.com/questions/77622453/helping-with-lp-timeseries-using-pulp

GENERATORS  = pd.read_csv('Generator_database.csv')
FUELS       = pd.read_csv('Fuels.csv',index_col='Fuel Name')
#RAW_DEMAND  = pd.Series(data=[random.randint(13000,25000) for i in range(20)])

demand                      = pd.read_csv('systemload.csv',on_bad_lines='skip')
HOURLY_DEMAND:pd.Series     = demand[demand['Type'] == 'forecast']['Mw']


prob        = lp.LpProblem('UnitCommitment',lp.LpMinimize)

# Creating a dict utilizing the indexes of the generators being the unique id's
GEN_UNITS       = lp.LpVariable.dicts('Units',[f'unit_{i}_{t}' for i in GENERATORS.index.tolist() for t in range(len(HOURLY_DEMAND))],0,None,lp.LpInteger)  




# NOTE: Adding the objective function to the LP solver.
def minimize_cost(gen_index,lp_unit):
    """
    We want to minimize the :
        - Cost of generation subject to the production cost, startup costs, shut down costs, penalty costs 

    min SUM_all_t (SUM_all_gens (c_g^p(t) + C_g^R*ug(t) + c_g^SU(t) + c_g^SD(t)) + SUM_all_busses(C_LP * (s_n^+(t) + s_n^-(t)) + C_RP * s_R(t)))
    

    RETURNS:
        cost of generation ($/MWh)
    """
    sub_df  = GENERATORS.iloc[gen_index]
    hr      = sub_df['Heat Rate (MMBtu/MWh)']
    su_c    = sub_df['Start Up Costs ($/MW)']
    sd_c    = sub_df['Shut Down Costs ($/MW)']
    fuel    = sub_df['Energy Source Code']

    return (FUELS.loc[fuel].values[0] * lp_unit * hr) + su_c + sd_c

obj_fcn = 0
for time in range(len(HOURLY_DEMAND)):
    for unit in GENERATORS.index.tolist():
        unit_key = 'unit_' + str(unit) + '_' + str(time)
        obj_fcn += minimize_cost(gen_index=unit,lp_unit=GEN_UNITS[unit_key])
    print(f'{unit_key=} added.')
prob += (obj_fcn, 'Objective Fcn')
    
# NOTE: Adding constraint to ensure supply > demand
for t in range(len(HOURLY_DEMAND)):
    prob += (lp.lpSum([GEN_UNITS['unit_' + str(unit) + '_' + str(t)] for unit in GENERATORS.index.tolist()]) >= HOURLY_DEMAND[t],
            f'Supply_>_Demand_{t}')


# NOTE: Adding capacity constraints on the UNITS_CAPACITY
for time in range(len(HOURLY_DEMAND)):
    print(f'{time=} ADDING CAPACITY FOR GENS')
    for unit in GENERATORS.index.tolist():
        prob += (GENERATORS.iloc[unit]['Minimum Capacity (MW)'] <= GEN_UNITS['unit_' + str(unit) + '_' + str(time)] <= GENERATORS.iloc[unit]['Nameplate Capacity (MW)'] ,
                 f'{unit}_{time}_Capacity')


# NOTE: Adding ramping constraints...
for time in range(len(HOURLY_DEMAND)):
    if time > 0:
        for unit in GENERATORS.index.tolist():
            pass






prob.writeLP('uc.lp')
prob.solve()

# ===================================================================================
# ============================== Creates a dataframe of results =====================
df = pd.DataFrame()
# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


data:dict = {'Time id': [],
             'Generator Name':[],
             'Generator Id':[],
             'Dispatched Energy':[],
             'Max Capacity': [], 
             'Minimum Capacity':[],
             'Demand':[]
             }

progbar_idx = 0
for gen in GEN_UNITS:
    printProgressBar(progbar_idx,total=len(GEN_UNITS.keys()))
    u,gen_idx,time      = gen.split('_')
    gen_idx             = int(gen_idx)
    time                = int(time)
    gen_name            = GENERATORS.iloc[gen_idx]['Plant Name']
    gen_id              = GENERATORS.iloc[gen_idx]['Generator ID']
    generated_energy    = GEN_UNITS[gen].value()
    demand              = HOURLY_DEMAND[time]
    nameplate           = float([GENERATORS.iloc[gen_idx]['Nameplate Capacity (MW)']][0])
    min_cap             = float([GENERATORS.iloc[gen_idx]['Minimum Capacity (MW)']][0])

    val     = [time,gen_name,gen_id,generated_energy,nameplate,min_cap,demand]
    keys    = [i for i in data]
    for i in range(len(val)):
        data[keys[i]].append(val[i])
    progbar_idx +=1

df = pd.DataFrame(data)
df.to_parquet('RESULTS.parquet',index=False)
#df.to_csv('RESULTS.csv',index=False,compression='gzip')


HOURLY_DEMAND.to_csv('demand.csv',index = False, compression='gzip')


plt.figure(1)
plt.plot(HOURLY_DEMAND.tolist())
plt.show()
plt.savefig('demand.png')
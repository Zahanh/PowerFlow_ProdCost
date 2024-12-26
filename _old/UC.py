"""
MLR FORMULATION
    OBJECTIVE           (69)
    UP TIME/DOWN TIME   (2,3,4,5)
    GEN LIMITS          (20,21)
    RAMP LIMITS         (26,27)
    PIECEWISE PROD      (50)
    START UP COSTS      (54,55,56)
    SHUT DOWN COSTS     (62)
    SYSTEM CONSTRAINTS  (64,65,66,67)

VARS:
    ug, vg, wg, xg, p'g, _p'g, pw,fk, theta_n, sn+, sn-, sn, sR
"""
import pulp as lp
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import numpy as np

"""
NOTE: CHANGES MADE FROM THE PAPER...

- We want to use p(t) as the percentage of power (int from 0-100) of the nameplate maximum power. 
- Assumption of no reserves at the moment. 
- WE CANNOT DIVIDE A LP variable...idk why but we multiply the LP var by 0.01 to reduce it by 100 and give it the ability to change between 0-100
"""
# =================================== INPUTS
TIME        = 5
ACCURACY    = 10   # MUST BE ATLEAST 1
# ==========================================
#GENERATORS      = pd.read_parquet('Generator_Database.parquet')
GENERATORS      = pd.read_csv('Generator_Database.csv')
PLANT_STATES    = GENERATORS['Plant State'].unique().tolist() # This will be the basis of a general zonal model.
FUELS           = pd.read_csv('Fuels.csv',index_col='Fuel Name')
HOURLY_DEMAND   = pd.Series(data=[random.randint(13000,25000) for i in range(TIME)])

# =============================== CREATING THE MODEL
solver = lp.getSolver('SCIP_PY')
model  = lp.LpProblem('UnitCommitment',lp.LpMinimize)
# % of power produced by generator g at time t
G   = lp.LpVariable.dicts('gens',[f'{i}_{t}' for i in GENERATORS.index.tolist() for t in range(len(HOURLY_DEMAND))],0,ACCURACY,lp.LpInteger)  
_p  = lp.LpVariable.dicts('max_cap_at_t',[f'{i}_{t}' for i in GENERATORS.index.tolist() for t in range(len(HOURLY_DEMAND))],0,ACCURACY,lp.LpInteger)  

# ==================================== State transition variables.
print('adding u')
U   = lp.LpVariable.dicts('U',[f'{i}_{t}' for i in GENERATORS.index.tolist() for t in range(len(HOURLY_DEMAND))],0,1,lp.LpBinary)

"""
Variables:
- c_d = Shutdown cost of unit g for time t
- c_p = prod cost of unit g at time t
- c_u = startup cost of unit g for time t
- p_g = power output of unit g for time t
- t_off = number of periods unit g has been offline prior to the startup in period t
- u(t) = binary var representing 1 if unit is online, else 0
- del  = power produced in block l of piecewise linear prod cost function of unit g in period t
"""

def p_g(gen,time):
    """
    Returns the power output of generator g at time t
    """
    id = f'{gen}_{time}'
    return (G[id] * (ACCURACY ** -1)) * GENERATORS.iloc[gen]['Nameplate Capacity (MW)']

def c_d(gen):
    """
    Returns shutdown cost of unit g for time t
    """
    return GENERATORS.iloc[gen]['Shut Down Costs ($/MW)']

def determine_prod_cost_eq(x:list,y:list):
    p = np.polyfit(x,y,1)
    return p
    
def c_p(gen,time):
    """
    This should be a function like:

    c_p = a*u(t) + b*p_g + c*p_g**2
 
    """
    id = f'{gen}_{time}'
    heat_rate   = GENERATORS.iloc[gen]['Heat Rate (MMBtu/MWh)']
    fuel        = GENERATORS.iloc[gen]['Energy Source Code']
    c_f           = heat_rate * FUELS.loc[fuel].values[0]
    minGen      = GENERATORS.iloc[gen]['Minimum Capacity (MW)']
    maxGen      = GENERATORS.iloc[gen]['Nameplate Capacity (MW)']
    x = [minGen, maxGen]
    y = [minGen*c_f, maxGen*c_f]
    p = determine_prod_cost_eq(x,y)
    
    a = p[0]
    b = p[1]
    #c = p[2]
    return a * U[id] + b * p_g(gen,time) 

def c_u(gen,time):
    """
    Start up costs for generator g at time t. currently not dependent on time t
    """

    return GENERATORS.iloc[gen]['Start Up Costs ($/MW)']

def _P(gen,time):
    """
    Maximum available power output of unit g in period t
    """
    id = f'{gen}_{time}'
    return (_p[id] *( ACCURACY**-1)) * GENERATORS.iloc[gen]['Nameplate Capacity (MW)']

obj = 0
# NOTE: assumption:
    # -> Start up and Shut down costs are not a stair function, but rather a constant. 
for time in range(len(HOURLY_DEMAND)):
    print(f'{time=}')
    for gen in GENERATORS.index.tolist():
        id = f'{gen}_{time}'

        maxGen = GENERATORS.iloc[gen]['Nameplate Capacity (MW)']
        minGen = GENERATORS.iloc[gen]['Minimum Capacity (MW)']
        RU      = GENERATORS.iloc[gen]['Ramp Up Rate (MW/h)']
        SU      = GENERATORS.iloc[gen]['Start Up Rate (MW/h)']
        SD      = GENERATORS.iloc[gen]['Shut Down Rate (MW/h)']
        RD      = GENERATORS.iloc[gen]['Ramp Down Rate (MW/h)']


        # Thermal Constraints: Eq 16,17
        model += minGen * U[id] <= p_g(gen,time) <= _P(gen,time)
        model += 0 <= _P(gen,time) <= maxGen * U[id] 

        # Equation 18   start up ramp
        if time > 0:
            id_m1 = f'{gen}_{time-1}'
            model += _P(gen,time) <= p_g(gen,time-1) + RU * U[id_m1] + SU*(U[id] - U[id_m1]) + maxGen*(1-U[id]), f'startUp_{gen}_{time}'
        # Equation 19   shut down ramp
        if time < len(HOURLY_DEMAND) -2:
            id_p1 = f'{gen}_{time+1}'
            model += _P(gen,time) <= maxGen * U[id_p1] + SD * (U[id] - U[id_p1]), f'shut_down_{gen}_{time}'

        # Equation 20
        if time > 0:
            id_m1 = f'{gen}_{time-1}'
            model += p_g(gen,time-1) - p_g(gen,time) <= RD * U[id] + SD * (U[id_m1] - U[id]) + maxGen * (1-U[id_m1]), f'ramp_down_{gen}_{time}'

        # Equations 21-22 Minimum Uptime constraints


        obj += c_p(gen,time) + c_u(gen,time) + c_d(gen)
    
model += obj, 'Objective Function'

print('Adding Supply/demand')
for time in range(len(HOURLY_DEMAND)):    
    demand = HOURLY_DEMAND[time]
    model += lp.lpSum([p_g(gen_id,time) for gen_id in GENERATORS.index.tolist()]) >= demand, f'Supply>demand_{time}'

def run(save:bool = True) -> None:
    if save:
        model.writeLP('uc.lp')

    model.solve(solver)

if __name__ == '__main__':
    run()
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
                'Unit Status': [],
                'Ramp Down Rate (MW/h)': [],
                'Ramp Up Rate (MW/h)':[],
                'Max Capacity': [], 
                'Minimum Capacity':[],
                'Demand':[]
                }

    progbar_idx = 0
    for time in range(len(HOURLY_DEMAND)):
        for gen in GENERATORS.index.tolist():
            printProgressBar(progbar_idx,total=len(_p.keys()))
            id = f'{gen}_{time}'
            gen_name            = GENERATORS.iloc[gen]['Plant Name']
            gen_id              = GENERATORS.iloc[gen]['Generator ID']
            generated_energy    = _p[id].value()
            demand              = HOURLY_DEMAND[time]
            nameplate           = float([GENERATORS.iloc[gen]['Nameplate Capacity (MW)']][0])
            min_cap             = float([GENERATORS.iloc[gen]['Minimum Capacity (MW)']][0])
            RD                  = GENERATORS['Ramp Down Rate (MW/h)'].iloc[gen]
            RU                  = GENERATORS['Ramp Up Rate (MW/h)'].iloc[gen]
            U_                  = U[id].value()

            val     = [time,gen_name,gen_id,((generated_energy * (ACCURACY**(-1)))*nameplate),U_,RD,RU,nameplate,min_cap,demand]
            keys    = [i for i in data]
            for i in range(len(val)):
                data[keys[i]].append(val[i])
            progbar_idx +=1

    df = pd.DataFrame(data)
    #df.to_parquet('RESULTS.parquet')
    df.to_csv('RESULTS.csv',index=False)

    HOURLY_DEMAND.to_csv('demand.csv',index = False)

    plt.figure(1)
    plt.plot(HOURLY_DEMAND.tolist())
    plt.show()
    plt.savefig('demand.png')

    u_vals  = [U[i].value() for i in U]
    u_names = [i for i in U]


    d = {'u_name': u_vals,'u':u_names}

    print(pd.DataFrame(d))




import pandas as pd
import numpy as np
import os, random

"""
NOTE:
- Slack bus should be the bus with the largest generation capacity.

"""

class PowerFlow:
    """
    Class which will calculate the power flow across a line in a network given:


    lines: Dataframe for lines 

    nodes: Datafram for nodes
    """
    def __init__(self,lines:pd.DataFrame,nodes:pd.DataFrame,load:pd.Series):
        self.base_power = 1000 #MW
        # NOTE: actual value = present value / base value
            # We need to convert all the values in the P vector to per-unit basis.
            # https://electricalacademia.com/electric-power/per-unit-calculation-per-unit-system-examples/
        self.load = load / self.base_power
        self.nodes = nodes
        self.lines = lines
        self.slack_bus = ''
        self.__slack_bus()
        self.B = self.__B()
        self.B_ = self.__admittance_matrix()
        self.angles = self.__voltage_angles()
        self.pf = pd.DataFrame()
        self.__power_flow()

    def __slack_bus(self):
        nodal_gen_sum = (pd.read_csv('DB/Generator_Database.csv').groupby(['Plant State'])['Nameplate Capacity (MW)'].sum())
        idx = nodal_gen_sum.idxmax()
        self.slack_bus = idx

    def opf():
        '''
        NOTE: OPF (optimal power flow) utilizes the DC interpretation. 

        Steps:\n
        1. Determine the addmittance matrix (where y_kn = 1/Z_kn)
        2. Determine the susceptance matrix utilizing node 1 as a slack bus (i.e. reference node)
        3. Determine Voltage angles for every node (θ = B^-1 * P)
        4. Determine the power flow for each line given f_k(t) = B_k * Δθ    


        Required Information:
        - Reactance of the Line
        - Resistance of the line
        - Voltage of the node

        '''

        pass

    def __y(self,x:float) -> float:
        return -1 / x
    
    def __B(self) -> pd.DataFrame:
        '''
        Method to generate the susceptance matrix. will need later.
        
               NH     MA     RI     CT     VT     ME     NY     HQ     NB\n
        NH -300.0 -100.0    0.0 -100.0 -100.0    0.0    0.0    0.0    0.0\n
        MA    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0\n
        RI    0.0 -100.0 -100.0    0.0    0.0    0.0    0.0    0.0    0.0\n
        CT    0.0 -100.0 -100.0 -200.0    0.0    0.0    0.0    0.0    0.0\n
        VT    0.0 -100.0    0.0    0.0 -100.0    0.0    0.0    0.0    0.0\n
        ME -100.0    0.0    0.0    0.0    0.0 -100.0    0.0    0.0    0.0\n
        NY    0.0 -100.0    0.0    0.0 -100.0    0.0 -200.0    0.0    0.0\n
        HQ    0.0 -100.0    0.0    0.0 -100.0    0.0    0.0 -200.0    0.0\n
        NB    0.0    0.0    0.0    0.0    0.0 -100.0    0.0    0.0 -100.0\n
        
        '''
        N = {}
        idx =1
        for i in self.nodes.index.tolist():
            N[idx] = i
            idx +=1

        # Forming the suceptance matrix. (NOTE: we needed the dict of num to node to generate it.)
        B       = []
        B_num   = pd.DataFrame(columns=[N[i] for i in N])
        for i in N:
            row = []
            row_num = []
            for j in N:
                tmp = N[i] + '-' + N[j]
                if tmp in self.lines.index.tolist():
                    row_num.append(self.__y(self.lines.loc[tmp]['Reactance']))
                    row.append(tmp)
                else:
                    row.append(tmp)
                    row_num.append(0)
            B.append(row)
            row_num[i-1] = (sum(row_num))    # replacing B[i][j] with sum for all row
            B_num.loc[N[i]] = row_num

        return B_num

    def __admittance_matrix(self):
        '''
        returns -B^(-1)
        '''
        tmp:pd.DataFrame = self.B.copy()
        tmp.drop(self.slack_bus,inplace=True,axis=0)
        tmp.drop(self.slack_bus,inplace=True,axis=1)
        df = (tmp**(-1))

        return -1 * df.replace([np.inf,-np.inf],0)
    
    def __voltage_angles(self):
        '''
        Calculates the voltage angles in radians
        '''
        l = self.load.drop('MA').copy()
        angles = (self.B_.dot(l))
        angles.loc[self.slack_bus] = 0    # Adding in the slack bus
        return angles
    
    def __power_flow(self):

        temp = {}

        # eq -> P = B(theta_n - theta_m)
        for line in self.lines.index.tolist():
            to = self.lines.loc[line]['Node To']
            fr = self.lines.loc[line]['Node From']
            theta_n = self.angles[fr]
            theta_m = self.angles[to]
            b = -1/self.lines.loc[line]['Reactance']
            flow = ((b * (theta_m - theta_n)) * self.base_power)

            temp[line] = [flow]
        
        self.pf = pd.concat([self.pf,pd.DataFrame(temp)])



if __name__ == '__main__':
    lines = pd.read_csv('DB/Lines.csv',index_col='Name')
    nodes = pd.read_csv('DB/Nodes.csv',index_col='Name')

    load = pd.Series(index=nodes.index.tolist(),data=[random.randint(800,6256) for i in range(len(nodes.index.tolist()))])
    pf = PowerFlow(lines,nodes,load)


    # print(pf.B)
    # print(f"{pf.slack_bus=}")
    # print(f'{pf.B_}')
    # print(pf.angles)
    print(load)
    print(pf.pf.T)
















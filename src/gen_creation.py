import os,random,math
import pandas as pd

class CreateFauxGens:
    def __init__(self) -> None:
        self.columns = ['Entity ID', 'Entity Name', 'Plant ID', 'Plant Name', 
            'Google Map', 'Bing Map', 'Plant State', 
            'County', 'Balancing Authority Code', 'Sector', 
            'Generator ID', 'Unit Code', 'Nameplate Capacity (MW)', 
            'Net Summer Capacity (MW)', 'Net Winter Capacity (MW)', 'Technology', 
            'Energy Source Code', 'Prime Mover Code', 'Operating Month', 
            'Operating Year', 'Planned Retirement Month', 'Planned Retirement Year', 
            'Status', 'Nameplate Energy Capacity (MWh)', 'DC Net Capacity (MW)', 
            'Planned Derate Year', 'Planned Derate Month', 
            'Planned Derate of Summer Capacity (MW)', 'Planned Uprate Year', 
            'Planned Uprate Month', 'Planned Uprate of Summer Capacity (MW)', 
            'Latitude', 'Longitude', 'Minimum Duration (hr)', 'Heat Rate (MMBtu/MWh)', 
            'Ramp Up Duration (hr)', 'Ramp Down Duration (hr)', 'Start Up Costs ($/MW)', 
            'Shut Down Costs ($/MW)', 'Minimum Capacity (MW)']
        self.df = pd.DataFrame(columns=self.columns)
    
    def __fuels(self) -> list[str]:
        fuels = ['WAT', 'KER', 'DFO', 'NG', 'RFO', 'JF', 'NUC', 'WDS', 'MWH', 'BIT', 'SUN', 'WND', 'BLQ', 'MSW', 'OBG', 'LFG']
        return fuels

    def createDB(self,n:int,save:bool = False,savePath:os.path=None,printdf:bool = False):
        assert int(n)
        fuels = self.__fuels()

        for i in range(n):
            name    = f'{i}_gen'
            maxCap  = random.randint(250,2500)
            minCap  = math.floor(maxCap * 0.75)
            heatRate = random.randint(8000,12000)
            SU = random.randint(150,1500)
            SD = SU
            energySourceCode = fuels[random.randint(0,len(fuels)-1)]
            RU = random.randint(0,5)
            RD = random.randint(0,5)
            min_dur = random.randint(0,3)

            self.df.loc[len(self.df)] = [0,name,0,name,0,0,0,0,0,0,i,0,maxCap,0,0,0,energySourceCode,
                                0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,min_dur,heatRate,RU,RD,SU,SD,minCap]

        if save:
            self.df.to_parquet(os.path.join(savePath,'Generator_Database.parquet'))
            print(f'Generator Database saved to \n{savePath}')

        if printdf:
            print(self.df)


if __name__ == '__main__':
    db = CreateFauxGens()
    db.createDB(500,save=True,savePath='/home/alexander/Documents/Umbral/Unit_Commitment')
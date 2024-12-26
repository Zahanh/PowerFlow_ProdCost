import pandas as pd
import openpyxl as xl
import os
import matplotlib.pyplot as plt


# NORTH_EAST_STATES = ['CT','RI','MA','ME','NH','VT']
# BALANCING_AUTH = 'Balancing Authority Code'

# EXCEL = 'july_generator2024.xlsx'
# SHEET = 'Operating'
# wb = xl.load_workbook(EXCEL)
# print(wb.sheetnames)
# if 'ISNE.csv' not in os.listdir():
#     df = pd.read_excel(EXCEL,sheet_name=SHEET,header=2)
# else:
#     df = pd.read_csv('ISNE.csv')


# print(df)

# user_in = input('Choose regional (r) or state (s) for csv')

# if user_in.lower() == 's':
#     for state in NORTH_EAST_STATES:
#         tmp_df = (df[df['Plant State'] == state])
#         tmp_df.to_csv(f'{state}.csv',index=False)
# else:
#     tmp_df = df[df[BALANCING_AUTH] == 'ISNE']
#     tmp_df.to_csv('ISNE.csv',index=False)


# FUELS -------------------------------------------------------------------------------------------------------------------------------------------------

# Note; these fuels we do not have any data on. EIA may contain some but dont need for the testing. 
# FUELS = {'JF': 13.18,
#          'COAL': 8.00,
#          'KER':5.18}


DATA_PATH = r'SOURCE_DATA'
os.chdir(os.path.join(os.path.dirname(__file__),DATA_PATH))

# # pip install xlrd
# NG_PRICES = pd.read_excel('N3045US3m.xls',sheet_name= 1,header=2)
# NG_PRICES.rename({'U.S. Natural Gas Electric Power Price (Dollars per Thousand Cubic Feet)':'NG'},inplace=True,axis=1)
# print(NG_PRICES)


# def show_ng_price_graph():
#     plt.figure(1)
#     plt.grid(visible=True)
#     plt.plot(NG_PRICES['Date'].to_list(),NG_PRICES['NG'].to_list())
#     plt.show()

df = pd.read_csv('ISNE.csv')
print(df['Energy Source Code'].unique().tolist())

print(df.columns)
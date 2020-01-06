import pandas as pd 

if __name__ == '__main__':

    def clean_pluto(df):

        df_cleaned =  df.loc[pluto['CONDO COOP']!=1]\
                        .loc[pluto['GSF']>=800]\
                        .loc[pluto['# BLDG']!=0]\
                        .loc[pluto['# FLOORS']!=0]\
                        .loc[pluto['# UNITS']!=0]\
                        .loc[(pluto['COMM SF']<=0) & 
                             (pluto['OFFICE SF']<=0) & 
                             (pluto['RETAIL SF'])<=0]\
                        .reset_index()

        return df_cleaned


    pluto = pd.read_csv('../data/project/NPL-001 All_Properties [bylocation;address] PLUTO.csv', index_col=0)

    pluto_cleaned = clean_pluto(pluto)
    pluto_cleaned.to_csv('../data/project/All_Properties PLUTO_New_Data.csv')
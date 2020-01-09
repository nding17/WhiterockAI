import pandas as pd 

if __name__ == '__main__':

    def clean_pluto(df):

        drop_indices = pluto[(pluto['CONDO COOP']==1) |
                             (pluto['GSF']<800) |
                             (pluto['# BLDG']==0) |
                             (pluto['# FLOORS']==0) |
                             (pluto['# UNITS']==0) |
                             ((pluto['COMM SF']>0) & 
                              (pluto['OFFICE SF']>0) & 
                              (pluto['RETAIL SF']>0))].index

        df_cleaned =  df.drop(drop_indices)\
                        .astype(dtype={'ZIP': str}, 
                                errors='ignore')\
                        .reset_index()

        return df_cleaned


    pluto = pd.read_csv('../data/project/NPL-001 All_Properties [bylocation;address] PLUTO.csv', index_col=0)

    pluto_cleaned = clean_pluto(pluto)
    pluto_cleaned.to_csv('../data/project/All_Properties PLUTO_New_Data.csv', index=False)
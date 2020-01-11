import pandas as pd
from datetime import datetime
from datetime import date
import numpy as np

if __name__ == '__main__':

    def category_date(d):
        if date(2009,1,1) <= d <= date(2010,12,31):
            return 'p1'
        if date(2011,1,1) <= d <= date(2012,12,31):
            return 'p2'
        if date(2013,1,1) <= d <= date(2014,12,31):
            return 'p3'
        if date(2015,1,1) <= d <= date(2016,12,31):
            return 'p4'
        if date(2017,1,1) <= d <= date(2018,12,31):
            return 'p5'
        if d >= date(2019,1,1):
            return 'p6'
        return None

    dict_p = {
        'p1': '2009-2010',
        'p2': '2011-2012',
        'p3': '2013-2014',
        'p4': '2015-2016',
        'p5': '2017-2018',
        'p6': '2019'
    }

    def group_sales(period, df):
        df_sales_p = df[df['period']==period]
        df_sales_p = df_sales_p.drop_duplicates(keep='first')\
                               .reset_index(drop=True)\
                               .groupby(['ZIP'])\
                               .agg({'SALE PRICE': ['mean', 
                                                    'median', 
                                                    'count']})

        df_sales_p.columns = [f"average sales price {dict_p[period]}", 
                              f"median sales price {dict_p[period]}", 
                              f"number of transactions {dict_p[period]}"]
        
        df_sales_p = df_sales_p.reset_index()\
                               .astype(dtype={'ZIP': str})\
                               .reset_index(drop=True)
        
        return df_sales_p

    def export_sales_summary(df_sales, export_path):
        df_sales['SALE DATE'] = df_sales['SALE DATE'].apply(lambda x: datetime.strptime(x, '%m/%d/%Y'))
        df_sales['period'] = df_sales['SALE DATE'].apply(category_date)
        
        groups = [p for p in df_sales['period'].unique() if p is not None]
        
        for period in groups:
            df_sales_p = group_sales(period, df_sales)
            df_sales_p.to_csv(f'{export_path}/sales_summary_{period}.csv', index=False)

    data_path = '../data/project/NYC Residential Sales Master.csv'
    export_path = '../data/project/sales_summary'

    df_sales = pd.read_csv(data_path, index_col=0)
    export_sales_summary(df_sales, export_path)

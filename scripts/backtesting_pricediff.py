import xlrd
import os
import warnings
import pandas as pd
import numpy as np
from datetime import date

if __name__ == '__main__':

    warnings.filterwarnings("ignore")

    def get_content_list(root):
        content_list = []
        for file in os.listdir(root):
            if file.endswith(".xlsx") or file.endswith(".xls"):
                loc = "/".join([root,file])
                wb = xlrd.open_workbook(loc)
                sheet = wb.sheet_by_index(0)
                ZIP = sheet.cell_value(6,3)
                ADDRESS = sheet.cell_value(5,3)
                ASKING_PRICE = sheet.cell_value(28,3)
                WHITEROCK_PRICE = sheet.cell_value(32,3)
                content_list.append([ADDRESS,
                                     ZIP, 
                                     ASKING_PRICE, 
                                     WHITEROCK_PRICE])

        return content_list

    ## The file path where you store the Excel spreadsheets
    ## Remeber to change when testing
    def sales_backtesting(root):
        
        ## Make sure put the PHL New Sales and PHL New Sales Backtesting under the same root folder
        ## Otherwise you need to write absolute path of these two files
        df1 = pd.read_csv('/'.join([root, 'PHL New Sales Data.csv']))
        df2 = pd.read_csv('/'.join([root, 'PHL New Sales Backtesting.csv']))

        content_list = get_content_list(root)

        ## Calculate the price difference and stroe in a new dataframe
        price_diff = []
        for prop in content_list:
            try:
                ## Check whether the zip code match
                if str(df1[df1['ADDRESS']==prop[0]]['zip_code'].values[0])[:5]==prop[1]:
                    price_diff.append([prop[0],
                                       df1[df1['ADDRESS']==prop[0]]['zip_code'].values[0],
                                       prop[2], 
                                       prop[3],
                                       df2[df2['ADDRESS']==prop[0]]['SALE PRICE'].values[0] - prop[2],
                                       df2[df2['ADDRESS']==prop[0]]['SALE PRICE'].values[0] - prop[3],
                                       prop[2] - prop[3]])
                else:
                    print(prop[0]+"zip code does not match the one in PHL New Sales File")
            except:
                print(prop[0]+' does not in the PHL New Sales File')

        # Merging the dataframe to PHL New Sales Backtesting
        temp_df = pd.DataFrame(price_diff, columns=['ADDRESS',
                                                    'ZIP',
                                                    'ASKING PRICE',
                                                    'WHITEROCK PRICE',
                                                    'AD / AE DIFF', 
                                                    'AD / AF DIFF',
                                                    'AE / AF DIFF'])

        testdf = df2.set_index(['ADDRESS', 'ZIP']).combine_first(temp_df.set_index(['ADDRESS', 'ZIP']))
        testdf.reset_index(inplace=True)
        testdf = testdf.reindex(columns=df2.columns)
        testdf = testdf.drop(['Unnamed: 35','Unnamed: 36'], axis=1)
        # Save the new dataframe as cvs file
        testdf.to_csv('PHL Sold Assets Backtesting.csv')

    ## The file path where you store the Excel spreadsheets
    ## Remeber to change when testing
    def price_diff_analysis_part1(root):

        ## Make sure put the PHL New Sales and PHL New Sales Backtesting under the same root folder
        ## Otherwise you need to write absolute path of these two files
        df1 = pd.read_csv('/'.join([root, 'PHL New Sales Data.csv']))
        df2 = pd.read_csv('/'.join([root, 'PHL New Sales Backtesting.csv']))

        ## Create new columns in new data frame Sold Sales 
        for column in ['ASKING PRICE',
                       'WHITEROCK PRICE',
                       'AD / AE DIFF', 
                       'AD / AF DIFF',
                       'AE / AF DIFF']:

            df2[column] = np.NaN*len(df2)

        content_list = get_content_list(root)

        ## Calculate the price difference and stroe in a new dataframe
        price_diff = []
        for prop in content_list:
            try:
                ## Check whether the zip code matc
                if str(df1[df1['ADDRESS']== prop[0]]['zip_code'].values[0])[:5]==prop[1]:
                    price_diff.append([prop[0],df1[df1['ADDRESS']==prop[0]]['zip_code'].values[0],
                                       prop[2], 
                                       prop[3],
                                       1-prop[2]/df2[df2['ADDRESS']==prop[0]]['SALE PRICE'].values[0],
                                       1-prop[3]/df2[df2['ADDRESS']==prop[0]]['SALE PRICE'].values[0],
                                       (prop[2]-prop[3])/df2[df2['ADDRESS']==prop[0]]['SALE PRICE'].values[0]])
                else:
                    print(prop[0]+"zip code does not match the one in PHL New Sales File")
            except:
                print(prop[0]+' does not in the PHL New Sales File')

        # Merging the dataframe to PHL New Sales Backtesting 
        temp_df = pd.DataFrame(price_diff, columns=['ADDRESS', 
                                                    'ZIP', 
                                                    'ASKING PRICE', 
                                                    'WHITEROCK PRICE', 
                                                    'AD / AE DIFF', 
                                                    'AD / AF DIFF',
                                                    'AE / AF DIFF'])

        testdf = df2.set_index(['ADDRESS','ZIP']).combine_first(temp_df.set_index(['ADDRESS','ZIP']))
        testdf.reset_index(inplace=True)
        testdf = testdf.reindex(columns=df2.columns)

        # Save the new dataframe as cvs file 
        d = date.today().strftime("%m-%d-%Y")
        name = 'PHL Sold Assets Backtesting {}.csv'.format(d)
        testdf.to_csv(name)
        return name

    ## Pass the dataframe from above as argument
    def price_diff_analysis_part2(df_name, excel_root):
        
        df = pd.read_csv(df_name)

        ## Calculate the std, average, median value for each window range
        def get_windows_value(column_name, windows_range):
            std,avg,med = [[],[],[]], [[],[],[]], [[],[],[]]
            price_columns = ['AD / AE DIFF', 'AD / AF DIFF','AE / AF DIFF']
            for j in range(len(price_columns)):
                for i in range(len(windows_range)-1):
                    ## Please note the year built feature have mixed type of input, like '196Y', please
                    ## clean the data before run the following test
                    std[j].append(df[(df[column_name].astype(int)>=windows_range[i]) & \
                        (df[column_name].astype(int)<windows_range[i+1])][price_columns[j]].std())           
                    avg[j].append(df[(df[column_name].astype(int)>=windows_range[i]) & \
                        (df[column_name].astype(int)<windows_range[i+1])][price_columns[j]].mean())
                    med[j].append(df[(df[column_name].astype(int)>=windows_range[i]) & \
                        (df[column_name].astype(int)<windows_range[i+1])][price_columns[j]].median())

            return [std[0],std[1],std[2],avg[0],avg[1],avg[2],med[0],med[1],med[2]]

        ##Store the windows values as pandas dataframe
        def get_windows_df(column_name, windows_range):
            columns_name = []
            for i in range(len(windows_range)-1):
                columns_name.append('-'.join([str(windows_range[i]),str(windows_range[i+1])]))
            df = pd.DataFrame(data = get_windows_value(column_name,windows_range),
                index=['AD / AE DIFF STD','AD / AF DIFF STD','AE / AF DIFF STD',
                       'AD / AE DIFF AVG','AD / AF DIFF AVG','AE / AF DIFF AVG',
                       'AD / AE DIFF MEDIAN','AD / AF DIFF MEDIAN','AE / AF DIFF MEDIAN'],
                columns = columns_name)
            return df

        ## Generate the windows range for each column type
        year_range = [i for i in range(1850,2040,20)]
        gsf_range= [i for i in range(500,10200,200)]
        units_range = [i for i in range(1,25,1)]
        units_range+=[25,50,100,np.inf]
        
        ## Get the dataframe and save as Excel SpreadSheet
        ## Each sheet represent a certain column type
        df_year = get_windows_df('YEAR BUILT', year_range)
        df_gsf = get_windows_df('GSF', gsf_range)
        df_units = get_windows_df('# ROOMS', units_range)
        
        ## Remember to change the file path when tested
        file_path = f'{excel_root}/windows_value.xlsx'
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        df_year.to_excel(writer, sheet_name='YEAR BUILT')
        df_gsf.to_excel(writer,sheet_name='GSF')
        df_units.to_excel(writer,sheet_name='# UNITS')
        writer.save()

    # root of the two data files 
    root = '../data/project'
    sales_backtesting(root)

    df_name = price_diff_analysis_part1(root)

    # root of the excel sheets, might be a different root directory
    excel_root = '../data/project'
    price_diff_analysis_part2(df_name, excel_root)

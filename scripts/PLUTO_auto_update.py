import pandas as pd
import numpy as np
from datetime import datetime

class clean_instructions: 

    def __init__(self):
        pass

    ### new columns
    added_columns = [
        '# UNITS',
        'REIS Submarket',
        'CITY',
        'STATE',
        'RESI',
        'CONDO',
        'UNIT',
        'COMM',
        'TOT ASSD $',
        'RE TAXES',
    ]

    ### OVERWRITE instructions for the original data file
    ### these instructions could be manually altered  
    rename_dict = {
        'number_of_rooms': {
            'delete': 0,
            'new_name': '# ROOMS',
        },
        'assessment_date': {
            'delete': 0,
            'new_name': 'assessment_date',
        },
        'beginning_point': {
            'delete': 1,
        },
        'book_and_page': {
            'delete': 1,
        },
        'building_code': {
            'delete': 1,
        },
        'building_code_description': {
            'delete': 0,
            'new_name': 'BLDG CODE',
        },
        'category_code': {
            'delete': 1,
        },
        'category_code_description': {
            'delete': 0,
            'new_name': 'BLDG CAT',
        },
        'census_tract': {
            'delete': 1,
        },
        'central_air': {
            'delete': 0,
            'new_name': 'CENTRAL AIR',
        },
        'cross_reference': {
            'delete': 1,
        },
        'date_exterior_condition': {
            'delete': 0,
            'new_name': 'EXT CONDITION DATE',
        },
        'depth': {
            'delete': 0,
            'new_name': 'LOT DEPTH',
        },
        'exempt_building': {
            'delete': 0,
            'new_name': 'BLDG EXEMPT',
        },
        'exempt_land': {
            'delete': 0,
            'new_name': 'LAND EXEMPT',
        },
        'exterior_condition': {
            'delete': 0,
            'new_name': 'EXT CONDITION',
        },
        'fireplaces': {
            'delete': 0,
            'new_name': '# FIREPLACE',
        },
        'frontage': {
            'delete': 0,
            'new_name': 'LOT FRONTAGE',
        },
        'fuel': {
            'delete': 1,
        },
        'garage_spaces': {
            'delete': 0,
            'new_name': 'GARAGE',
        },
        'garage_type': {
            'delete': 0,
            'new_name': 'GARAGE TYPE',
        },
        'general_construction': {
            'delete': 1,
        },
        'geographic_ward': {
            'delete': 1,
        },
        'homestead_exemption': {
            'delete': 0,
            'new_name': 'homestead_exemption',
        },
        'house_extension': {
            'delete': 1,
        },
        'house_number': {
            'delete': 1,
        },
        'interior_condition': {
            'delete': 0,
            'new_name': 'INT CONDITION',
        },
        'location': {
            'delete': 0,
            'new_name': 'ADDRESS',
        },
        'mailing_address_1': {
            'delete': 1,
        },
        'mailing_address_2': {
            'delete': 1,
        },
        'mailing_care_of': {
            'delete': 1,
        },
        'mailing_city_state': {
            'delete': 0,
            'new_name': 'OWNER CITY',
        },
        'mailing_street': {
            'delete': 0,
            'new_name': 'OWNER ADDRESS',
        },
        'mailing_zip': {
            'delete': 0,
            'new_name': 'OWNER ZIP',
        },
        'market_value': {
            'delete': 0,
            'new_name': 'MARKET VALUE',
        },
        'market_value_date': {
            'delete': 1,
        },
        'number_of_bathrooms': {
            'delete': 0,
            'new_name': '# BATH',
        },
        'number_of_bedrooms': {
            'delete': 0,
            'new_name': '# BED',
        },
        'basements': {
            'delete': 0,
            'new_name': 'BASEMENT',
        },
        'number_stories': {
            'delete': 0,
            'new_name': '# FLOORS',
        },
        'off_street_open': {
            'delete': 0,
            'new_name': 'off_street_open'
        },
        'other_building': {
            'delete': 0,
            'new_name': 'BUILDING',
        },
        'owner_1': {
            'delete': 0,
            'new_name': 'OWNER',
        },
        'owner_2': {
            'delete': 1,
        },
        'parcel_number': {
            'delete': 0,
            'new_name': 'PARCEL ID',
        },
        'parcel_shape': {
            'delete': 0,
            'new_name': 'PARCEL SHAPE',
        },
        'quality_grade': {
            'delete': 1
        },
        'recording_date': {
            'delete': 0,
            'new_name': 'RECORDING DATE',
        },
        'registry_number': {
            'delete': 1
        },
        'sale_date': {
            'delete': 0,
            'new_name': 'SALE DATE',
        },
        'sale_price': {
            'delete': 0,
            'new_name': 'SALE PRICE',
        },
        'separate_utilities': {
            'delete': 1,
        },
        'sewer': {
            'delete': 1,
        },
        'site_type': {
            'delete': 1,
        },
        'state_code': {
            'delete': 1,
        },
        'street_code': {
            'delete': 1,
        },
        'street_designation': {
            'delete': 1,
        },
        'street_direction': {
            'delete': 1,
        },
        'street_name': {
            'delete': 1,
        },
        'suffix': {
            'delete': 1,
        },
        'taxable_building': {
            'delete': 0,
            'new_name': 'BLDG ASSD $',
        },
        'taxable_land': {
            'delete': 0,
            'new_name': 'LAND ASSD $',
        },
        'topography': {
            'delete': 0,
            'new_name': 'TOPOGRAPHY',
        },
        'total_area': {
            'delete': 0,
            'new_name': 'LAND SF',
        },
        'total_livable_area': {
            'delete': 0,
            'new_name': 'GSF',
        },
        'type_heater': {
            'delete': 1,
        },
        'unfinished': {
            'delete': 1,
        },
        'unit': {
            'delete': 0,
            'new_name': 'UNIT #',
        },
        'utility': {
            'delete': 1,
        },
        'view_type': {
            'delete': 0,
            'new_name': 'VIEW',
        },
        'year_built': {
            'delete': 0,
            'new_name': 'YEAR BUILT',
        },
        'year_built_estimate': {
            'delete': 1,
        },
        'zip_code': {
            'delete': 0,
            'new_name': 'ZIP',
        },
        'zoning': {
            'delete': 0,
            'new_name': 'ZONING',
        },
        'objectid': {
            'delete': 1,
        },
        'lat': {
            'delete': 0,
            'new_name': 'LATITUDE',
        },
        'lng': {
            'delete': 0,
            'new_name': 'LONGITUDE',
        },
    }

    instructions = {
        'added_columns': added_columns,
        'rename_dict': rename_dict,
    }

class cleaning_pipline:

    def __init__(self):
        pass

    def pre_clean_df(self, df, instructions):
        added_columns = instructions['added_columns']
        rename_dict = instructions['rename_dict']
        orig_columns = list(instructions['rename_dict'].keys())
        df_new = df.copy()[orig_columns]
        
        for column in orig_columns:
            if rename_dict[column]['delete'] == 1:
                df_new = df_new.drop([column], axis=1)
            if rename_dict[column]['delete'] == 0:
                df_new = df_new.rename(columns={column: rename_dict[column]['new_name']})
        
        df_new = df_new.reindex(df_new.columns.tolist()+added_columns, axis=1)\
                       .astype(dtype={'SALE DATE': str})
        
        df_new['SALE DATE'] = pd.to_datetime(df_new['SALE DATE'], errors='coerce')
    
        df_new = df_new.sort_values(by=['SALE DATE'], ascending=False)\
                       .drop(df_new[df_new['SALE DATE']==pd.NaT].index)\
                       .reset_index(drop=True)
        
        return df_new



if __name__ == '__main__':

    ci = clean_instructions()
    print(ci.added_columns)
    print(ci.rename_dict)




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
        
        df_new['SALE DATE'] = pd.to_datetime(df_new['SALE DATE'])
        df_new = df_new.sort_values(by=['SALE DATE'], ascending=False)\
                       .reset_index(drop=True)
        
        return df_new

    def subset_df_date(self, df_new, deltadays):
        delta = pd.Timedelta(deltadays)
        df_new = df_new.sort_values(by=['SALE DATE'], ascending=False)
        latest_date = df_new['SALE DATE'].iloc[0]
        earliest_date = latest_date-delta
        keep_index = df_new[(df_new['SALE DATE']>=earliest_date) & 
                            (df_new['SALE DATE']<=latest_date)].index
        df_sub = df_new.iloc[keep_index]\
                       .reset_index(drop=True)
        return df_sub

    def update_PLUTO(self, pluto, df_sub):
        pluto['SALE DATE'] = pd.to_datetime(pluto['SALE DATE'])
        pluto = pluto.sort_values(by=['SALE DATE'], ascending=False)

        pluto_addresses = pluto['ADDRESS'].tolist()
        sub_addresses = df_sub['ADDRESS'].tolist()
        pluto_update = pluto.copy()
        df_added = pd.DataFrame(columns=pluto.columns)
        df_sub = df_sub[pluto.columns]

        ### loop through all the addresses in the new data 
        ### to match the addresses in the PLUTO dataset 
        for address in sub_addresses:
            if address in pluto_addresses:
                added = df_sub[df_sub['ADDRESS']==address]['PARCEL ID']\
                            .values.tolist()
                original = pluto[pluto['ADDRESS']==address]['PARCEL ID']\
                            .values.tolist()
                
                # address in the PLUTO whose data need to be updated 
                if set(added) == set(original):
                    pluto_update.at[
                        pluto_update[pluto_update['ADDRESS']==address].index,
                        ['GSF', 'SALE PRICE', 'SALE DATE']
                    ] = df_sub[df_sub['ADDRESS']==address][['GSF', 'SALE PRICE', 'SALE DATE']]\
                          .values\
                          .tolist()
                else:
                    commons = set(added).intersection(set(original))
                    diffs = set(added) - set(original)

                    for pid in list(commons):
                        pluto_update.at[
                            pluto_update[(pluto_update['ADDRESS']==address) & 
                                         (pluto_update['PARCEL ID']==pid)].index,
                            ['GSF', 'SALE PRICE', 'SALE DATE']
                        ] = df_sub[(df_sub['ADDRESS']==address) & 
                                   (df_sub['PARCEL ID']==pid)][['GSF', 'SALE PRICE', 'SALE DATE']]\
                                  .values\
                                  .tolist()

                    if not diffs:
                        # to account for the addresses that have multiple properties
                        added_rows = df_sub.loc[(df_sub['ADDRESS']==address) &
                                                (df_sub['PARCEL ID'].isin(list(diffs)))]
                        for i in range(added_rows.shape[0]):
                            df_added = df_added.append(added_rows.iloc[i], 
                                                       ignore_index=True)
            else:
                added_row = df_sub[df_sub['ADDRESS']==address]
                df_added = df_added.append(added_row, ignore_index=True)
        
        pluto_conc = pd.concat([pluto_update, df_added], ignore_index=True)
        
        def int_to_datetime(date):
            if type(date) == int:
                return pd.to_datetime(date)
            elif type(date) == pd._libs.tslibs.timestamps.Timestamp:
                return date
            else:
                return 'nan'
        
        pluto_conc['SALE DATE'] = pluto_conc['SALE DATE'].apply(lambda x: int_to_datetime(x))
        
        pluto_conc = pluto_conc.sort_values(by='SALE DATE', ascending=False)\
                               .reset_index(drop=True)

        return pluto_conc

    ### fill in missed location data into the merged PLUTO
    def fill_loc(self, pluto_update):
        d_subm = dict(zip(pluto_update['ADDRESS'], pluto_update['REIS Submarket']))
        d_city = dict(zip(pluto_update['ADDRESS'], pluto_update['CITY']))
        d_state = dict(zip(pluto_update['ADDRESS'], pluto_update['STATE']))
        d_zip = dict(zip(pluto_update['ADDRESS'], pluto_update['ZIP']))
        
        p_subm = pd.DataFrame(d_subm.items(), columns=['ADDRESS', 'REIS Submarket'])
        p_city = pd.DataFrame(d_city.items(), columns=['ADDRESS', 'CITY'])
        p_state = pd.DataFrame(d_state.items(), columns=['ADDRESS', 'STATE'])
        p_zip = pd.DataFrame(d_zip.items(), columns=['ADDRESS', 'ZIP'])
        
        p_all = p_subm
        
        ps = [p_city, p_state, p_zip]
        for p_one in ps:
            p_all = pd.merge(p_all, p_one, on='ADDRESS', how='left')
        
        valid_cols = pluto_update.columns.difference(['REIS Submarket', 'CITY', 'STATE', 'ZIP'])
        pluto_loc_updated = pluto_update[valid_cols]
        
        pluto_loc_updated = pd.merge(pluto_loc_updated, p_all, on='ADDRESS', how='left')
        
        return pluto_loc_updated


if __name__ == '__main__':

    ci = clean_instructions()
    instructions = ci.instructions

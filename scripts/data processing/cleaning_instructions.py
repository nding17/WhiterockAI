import numpy as np

class ci:

    ### new columns
    PHL_COLS_ADD = [
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
    PHL_PLUTO_RENAME = {
        'number_of_rooms': {
            'delete': 0,
            'new name': '# ROOMS',
        },
        'assessment_date': {
            'delete': 0,
            'new name': 'assessment_date',
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
            'new name': 'BLDG CODE',
        },
        'category_code': {
            'delete': 1,
        },
        'category_code_description': {
            'delete': 0,
            'new name': 'BLDG CAT',
        },
        'census_tract': {
            'delete': 1,
        },
        'central_air': {
            'delete': 0,
            'new name': 'CENTRAL AIR',
        },
        'cross_reference': {
            'delete': 1,
        },
        'date_exterior_condition': {
            'delete': 0,
            'new name': 'EXT CONDITION DATE',
        },
        'depth': {
            'delete': 0,
            'new name': 'LOT DEPTH',
        },
        'exempt_building': {
            'delete': 0,
            'new name': 'BLDG EXEMPT',
        },
        'exempt_land': {
            'delete': 0,
            'new name': 'LAND EXEMPT',
        },
        'exterior_condition': {
            'delete': 0,
            'new name': 'EXT CONDITION',
        },
        'fireplaces': {
            'delete': 0,
            'new name': '# FIREPLACE',
        },
        'frontage': {
            'delete': 0,
            'new name': 'LOT FRONTAGE',
        },
        'fuel': {
            'delete': 1,
        },
        'garage_spaces': {
            'delete': 0,
            'new name': 'GARAGE',
        },
        'garage_type': {
            'delete': 0,
            'new name': 'GARAGE TYPE',
        },
        'general_construction': {
            'delete': 1,
        },
        'geographic_ward': {
            'delete': 1,
        },
        'homestead_exemption': {
            'delete': 0,
            'new name': 'homestead_exemption',
        },
        'house_extension': {
            'delete': 1,
        },
        'house_number': {
            'delete': 1,
        },
        'interior_condition': {
            'delete': 0,
            'new name': 'INT CONDITION',
        },
        'location': {
            'delete': 0,
            'new name': 'ADDRESS',
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
            'new name': 'OWNER CITY',
        },
        'mailing_street': {
            'delete': 0,
            'new name': 'OWNER ADDRESS',
        },
        'mailing_zip': {
            'delete': 0,
            'new name': 'OWNER ZIP',
        },
        'market_value': {
            'delete': 0,
            'new name': 'MARKET VALUE',
        },
        'market_value_date': {
            'delete': 1,
        },
        'number_of_bathrooms': {
            'delete': 0,
            'new name': '# BATH',
        },
        'number_of_bedrooms': {
            'delete': 0,
            'new name': '# BED',
        },
        'basements': {
            'delete': 0,
            'new name': 'BASEMENT',
        },
        'number_stories': {
            'delete': 0,
            'new name': '# FLOORS',
        },
        'off_street_open': {
            'delete': 0,
            'new name': 'off_street_open'
        },
        'other_building': {
            'delete': 0,
            'new name': 'BUILDING',
        },
        'owner_1': {
            'delete': 0,
            'new name': 'OWNER',
        },
        'owner_2': {
            'delete': 1,
        },
        'parcel_number': {
            'delete': 0,
            'new name': 'PARCEL ID',
        },
        'parcel_shape': {
            'delete': 0,
            'new name': 'PARCEL SHAPE',
        },
        'quality_grade': {
            'delete': 1
        },
        'recording_date': {
            'delete': 0,
            'new name': 'RECORDING DATE',
        },
        'registry_number': {
            'delete': 1
        },
        'sale_date': {
            'delete': 0,
            'new name': 'SALE DATE',
        },
        'sale_price': {
            'delete': 0,
            'new name': 'SALE PRICE',
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
            'new name': 'BLDG ASSD $',
        },
        'taxable_land': {
            'delete': 0,
            'new name': 'LAND ASSD $',
        },
        'topography': {
            'delete': 0,
            'new name': 'TOPOGRAPHY',
        },
        'total_area': {
            'delete': 0,
            'new name': 'LAND SF',
        },
        'total_livable_area': {
            'delete': 0,
            'new name': 'GSF',
        },
        'type_heater': {
            'delete': 1,
        },
        'unfinished': {
            'delete': 1,
        },
        'unit': {
            'delete': 0,
            'new name': 'UNIT #',
        },
        'utility': {
            'delete': 1,
        },
        'view_type': {
            'delete': 0,
            'new name': 'VIEW',
        },
        'year_built': {
            'delete': 0,
            'new name': 'YEAR BUILT',
        },
        'year_built_estimate': {
            'delete': 1,
        },
        'zip_code': {
            'delete': 0,
            'new name': 'ZIP',
        },
        'zoning': {
            'delete': 0,
            'new name': 'ZONING',
        },
        'objectid': {
            'delete': 1,
        },
        'lat': {
            'delete': 0,
            'new name': 'LATITUDE',
        },
        'lng': {
            'delete': 0,
            'new name': 'LONGITUDE',
        },
    }

    ### special instructions for data processing
    PHL_PLUTO_PROCESS = {
        'APT 2-4 UNITS': {
            '# UNITS': 3,
            'CONDO': 0,
            'BUILDING': 1,
            'UNIT': 0
        },
        'APTS 100+ UNITS': {
            '# UNITS': np.nan,
            'CONDO': 0,
            'BUILDING': 1,
            'UNIT': 0,
        },
        'APTS 51-100 UNITS': {
            '# UNITS': np.nan,
            'CONDO': 0,
            'BUILDING': 1,
            'UNIT': 0,
        },
        'APTS 5-50 UNITS': {
            '# UNITS': np.nan,
            'CONDO': 0,
            'BUILDING': 1,
            'UNIT': 0,
        },
        'DET CONV APT': {
            '# UNITS': np.nan,
            'CONDO': 0,
            'BUILDING': 1,
            'UNIT': 1,
        },
        'DETACHED SINGLE FAM': {
            '# UNITS': 1,
            'CONDO': 0,
            'BUILDING': 1,
            'UNIT': 1,
        },
        'ROW CONV/APT': {
            '# UNITS': 2,
            'CONDO': 0,
            'BUILDING': 1,
            'UNIT': 0,
        },
        'ROW SINGLE FAM': {
            '# UNITS': 1,
            'CONDO': 0,
            'BUILDING': 1,
            'UNIT': 1,
        },
        'S/D APT': {
            '# UNITS': np.nan,
            'CONDO': 0,
            'BUILDING': 1,
            'UNIT': 0,
        },
        'S-DETACHED SINGLE FAM': {
            '# UNITS': 1,
            'CONDO': 0,
            'BUILDING': 1,
            'UNIT': 1,
        }
    }

    ### some log instructions - status update messages 
    PHL_LOGGING = {
        'download_df': '==>Downloading new data... (takes a while, please be patient)',
        'pre_clean_df': '==>Pre-processing the downloaded data (delete redundant columns, rename some columns)',
        'subset_df_date': '==>Subsetting recent data from the downloaded data',
        'load_old_PLUTO': '==>Loading old PLUTO data...',
        'update_PLUTO': '==>Merging PLUTO with the new data... (takes a while, please be patient)',
        'process_PLUTO': '==>Final step: process the new pluto, almost ready',
        'export_data': '==>Exporting data',
        'export_addr_img': '==>Exporting images for each address',
    }

    NYC_SALES_CLEANING = {
        'BOROUGH': {
            'delete': 0,
            'new name': 'BOROUGH',
        },
        'NEIGHBORHOOD': {
            'delete': 0,
            'new name': 'NEIGHBORHOOD',
        },
        'BUILDING CLASS CATEGORY': {
            'delete': 1,
        },
        'TAX CLASS AT PRESENT': {
            'delete': 0,
            'new name': 'TAX CLASS',
        },
        'BLOCK': {
            'delete': 0,
            'new name': 'BLOCK',
        },
        'LOT': {
            'delete': 0,
            'new name': 'LOT',
        },
        'EASE-MENT': {
            'delete': 1
        },
        'BUILDING CLASS AT PRESENT': {
            'delete': 0,
            'new name': 'BLDG CLASS',
        },
        'ADDRESS': {
            'delete': 0,
            'new name': 'ADDRESS',
        },
        'APARTMENT NUMBER': {
            'delete': 0,
            'new name': 'APT #',
        },
        'ZIP CODE': {
            'delete': 0,
            'new name': 'ZIP',
        },
        'RESIDENTIAL UNITS': {
            'delete': 0,
            'new name': 'RESI UNITS',
        },
        'COMMERCIAL UNITS': {
            'delete': 0,
            'new name': 'COMM UNITS',
        },
        'TOTAL UNITS': {
            'delete': 0,
            'new name': '# UNITS',
        },
        'LAND SQUARE FEET': {
            'delete': 0,
            'new name': 'LAND SF',
        },
        'GROSS SQUARE FEET': {
            'delete': 0,
            'new name': 'GSF',
        },
        'YEAR BUILT': {
            'delete': 0,
            'new name': 'YEAR BUILT',
        },
        'TAX CLASS AT TIME OF SALE': {
            'delete': 0,
            'new name': 'TAX CLASS SALE',
        },
        'BUILDING CLASS AT TIME OF SALE': {
            'delete': 0,
            'new name': 'CLASS SALE',
        },
        'SALE PRICE': {
            'delete': 0,
            'new name': 'SALE PRICE',
        },
        'SALE DATE': {
            'delete': 0,
            'new name': 'SALE DATE',
        },
    }

    NYC_PLUTO_CLEANING = {
        'borough': {
            'delete': 0,
            'new name': 'BOROUGH',
        },
        'block': {
            'delete': 0,
            'new name': 'BLOCK',
        },
        'lot': {
            'delete': 0,
            'new name': 'LOT',
        },
        'cd': {
            'delete': 1,
        },
        'ct2010': {
            'delete': 1,
        },
        'cb2010': {
            'delete': 1,
        },
        'schooldist': {
            'delete': 0,
            'new name': 'SCHOOL DIS',
        },
        'council': {
            'delete': 0,
            'new name': 'COUNCIL',
        },
        'zipcode': {
            'delete': 0,
            'new name': 'ZIP',
        },
        'firecomp': {
            'delete': 0,
            'new name': 'FIRE COMP',
        },
        'policeprct': {
            'delete': 0,
            'new name': 'POLICE PRCT',
        },
        'healtharea': {
            'delete': 0,
            'new name': 'HEALTH AREA',
        },
        'sanitboro': {
            'delete': 0,
            'new name': 'SANIT BORO',
        },
        'sanitsub': {
            'delete': 1,
        },
        'address': {
            'delete': 0,
            'new name': 'ADDRESS',
        },
        'zonedist1': {
            'delete': 0,
            'new name': 'zonedist1',
        },
        'zonedist2': {
            'delete': 0,
            'new name': 'zonedist2',
        },
        'zonedist3': {
            'delete': 0,
            'new name': 'zonedist3',
        },
        'zonedist4': {
            'delete': 0,
            'new name': 'zonedist4',
        },
        'overlay1': {
            'delete': 0,
            'new name': 'overlay1',
        },
        'overlay2': {
            'delete': 0,
            'new name': 'overlay2',
        },
        'spdist1': {
            'delete': 0,
            'new name': 'spdist1',
        },
        'spdist2': {
            'delete': 0,
            'new name': 'spdist2',
        },
        'spdist3': {
            'delete': 0,
            'new name': 'spdist3',
        },
        'ltdheight': {
            'delete': 1,
        },
        'splitzone': {
            'delete': 1,
        },
        'bldgclass': {
            'delete': 0,
            'new name': 'BLDG CLASS NOW',
        },
        'landuse': {
            'delete': 0,
            'new name': 'LAND USE',
        },
        'easements': {
            'delete': 0,
            'new name': 'easements',
        },
        'ownertype': {
            'delete': 0,
            'new name': 'OWNER TYPE',
        },
        'ownername': {
            'delete': 0,
            'new name': 'OWNER',
        },
        'lotarea': {
            'delete': 0,
            'new name': 'LAND SF',
        },
        'bldgarea': {
            'delete': 0,
            'new name': 'GSF',
        },
        'comarea': {
            'delete': 0,
            'new name': 'COMM SF',
        },
        'resarea': {
            'delete': 0,
            'new name': 'RESI SF',
        },
        'officearea': {
            'delete': 0,
            'new name': 'OFFICE SF',
        },
        'retailarea': {
            'delete': 0,
            'new name': 'RETAIL SF',
        },
        'garagearea': {
            'delete': 0,
            'new name': 'GARAGE SF',
        },
        'strgearea': {
            'delete': 0,
            'new name': 'STORAGE SF',
        },
        'factryarea': {
            'delete': 0,
            'new name': 'FACTORY SF',
        },
        'otherarea': {
            'delete': 0,
            'new name': 'OTHER SF',
        },
        'areasource': {
            'delete': 1,
        },
        'numbldgs': {
            'delete': 0,
            'new name': '# BLDG',
        },
        'numfloors': {
            'delete': 0,
            'new name': '# FLOORS',
        },
        'unitsres': {
            'delete': 1,
        },
        'unitstotal': {
            'delete': 0,
            'new name': '# UNITS',
        },
        'lotfront': {
            'delete': 0,
            'new name': 'LOT FRONT',
        },
        'lotdepth': {
            'delete': 0,
            'new name': 'LOT DEPTH',
        },
        'bldgfront': {
            'delete': 0,
            'new name': 'BLDG FRONT',
        },
        'bldgdepth': {
            'delete': 0,
            'new name': 'BLDG DEPTH',
        },
        'ext': {
            'delete': 1,
        },
        'proxcode': {
            'delete': 1,
        },
        'irrlotcode': {
            'delete': 1, 
        },
        'lottype': {
            'delete': 0,
            'new name': 'LOT TYPE',
        },
        'bsmtcode': {
            'delete': 0,
            'new name': 'bsmtcode',
        },
        'assessland': {
            'delete': 0,
            'new name': 'assessland',
        },
        'assesstot': {
            'delete': 0,
            'new name': 'assesstot',
        },
        'exempttot': {
            'delete': 0,
            'new name': 'exempttot',
        },
        'yearbuilt': {
            'delete': 0,
            'new name': 'YEAR BUILT',
        },
        'yearalter1': {
            'delete': 0,
            'new name': 'yearalter1',
        },
        'yearalter2': {
            'delete': 0,
            'new name': 'yearalter2',
        },
        'histdist': {
            'delete': 1,
        },
        'landmark': {
            'delete': 1,
        },
        'builtfar': {
            'delete': 0,
            'new name': 'builtfar',
        },
        'residfar': {
            'delete': 0,
            'new name': 'residfar',
        },
        'commfar': {
            'delete': 0,
            'new name': 'commfar',
        },
        'facilfar': {
            'delete': 0,
            'new name': 'facilfar',
        },
        'borocode': {
            'delete': 1,
        },
        'bbl': {
            'delete': 1,
        },
        'condono': {
            'delete': 1,
        },
        'tract2010': {
            'delete': 1,
        },
        'xcoord': {
            'delete': 1,
        },
        'ycoord': {
            'delete': 1,
        },
        'latitude': {
            'delete': 0,
            'new name': 'LATITUDE',
        },
        'longitude': {
            'delete': 0,
            'new name': 'LONGITUDE',
        },
        'zonemap': {
            'delete': 1,
        },
        'zmcode': {
            'delete': 1,
        },
        'sanborn': {
            'delete': 1
        },
        'taxmap': {
            'delete': 1
        },
        'edesignum': {
            'delete': 0,
            'new name': 'edesignum',
        },
        'appbbl': {
            'delete': 0,
            'new name': 'appbbl',
        },
        'appdate': {
            'delete': 1,
        },
        'plutomapid': {
            'delete': 1,
        },
        'version': {
            'delete': 1,
        },
        'sanitdistrict': {
            'delete': 0,
            'new name': 'sanitdistrict',
        },
        'healthcenterdistrict': {
            'delete': 0,
            'new name': 'healthcenterdistrict',
        },
        'firm07_flag': {
            'delete': 0,
            'new name': 'firm07_flag',
        },
        'pfirm15_flag': {
            'delete': 0,
            'new name': 'pfirm15_flag',
        },
        'rpaddate': {
            'delete': 1,
        },
        'dcasdate': {
            'delete': 1,
        },
        'zoningdate': {
            'delete': 1,
        },
        'landmkdate': {
            'delete': 1,
        },
        'basempdate': {
            'delete': 1,
        },
        'masdate': {
            'delete': 1,
        },
        'polidate': {
            'delete': 1,
        },
        'edesigdate': {
            'delete': 0,
            'new name': 'edesigdate',
        },
        'geom': {
            'delete': 1,
        },
        'dcpedited': {
            'delete': 1,
        },
        'notes': {
            'delete': 1,
        },
    }

    NYC_REIS_RENAME = {
        'Property Type': 'PROPERTY TYPE',
        'Street Address': 'ADDRESS',
        'City': 'CITY',
        'State': 'STATE',
        'Zip': 'ZIP',
        'County': 'COUNTY',
        'Year Renovated': 'YEAR RENOVATED',
        'Asking Rent (Units)': 'ASKING RENT (UNITS)',
        'Asking Rent (SF)': 'ASKING RENT (SF)',
        'Vacancy': 'VACANCY',
        'Building Class': 'BLDG CLASS',
        'Cap Rate': 'CAP RATE',
        'Sale Price': 'SALE PRICE',
        'Sale Date': 'SALE DATE',
        'Transaction Type': 'TRANSACTION TYPE',
        'Buyer': 'BUYER',
        'Year Built': 'YEAR BUILT',
        'Seller': 'SELLER',
        'Construction Status': 'CONSTRUCTION STATUS',
        'Expected Completion': 'EXPECTED COMPLETION',
        'Expected Groundbreak': 'EXPECTED GROUNDBREAK',
        'Developer': 'DEVELOPER',
        'Developer Phone': 'DEVELOPER PHONE',
        'Sector Name': 'SECTOR NAME',
        'Submarket': 'REIS SUBMARKET',
    }

    CHI_PLUTO_CLEANING = {
        'pin': {
            'delete': 0,
            'new name': 'PIN',
        },
        'class': {
            'delete': 0,
            'new name': 'BLDG CODE',
        },
        'tax_year': {
            'delete': 0,
            'new name': 'TAX YEAR',
        },
        'nbhd': {
            'delete': 0,
            'new name': 'NEIGHBORHOOD',
        },
        'hd_sf': {
            'delete': 0,
            'new name': 'LAND SF',
        },
        'town_code': {
            'delete': 0,
            'new name': 'TOWN',
        },
        'type_resd': {
            'delete': 0,
            'new name': 'BLDG CAT',
        },
        'apts': {
            'delete': 0,
            'new name': '# UNITS',
        },
        'ext_wall': {
            'delete': 0,
            'new name': 'EXT MATERIAL',
        },
        'roof_cnst': {
            'delete': 0,
            'new name': 'ROOF MATERIAL',
        },
        'rooms': {
            'delete': 0,
            'new name': '# ROOMS',
        },
        'beds': {
            'delete': 0,
            'new name': '# BED',
        },
        'bsmt': {
            'delete': 0,
            'new name': 'BASEMENT',
        },
        'bsmt_fin': {
            'delete': 0,
            'new name': 'BASEMENT COND',
        },
        'heat': {
            'delete': 0,
            'new name': 'CENTRAL HEATING',
        },
        'oheat': {
            'delete': 0,
            'new name': 'OTHER HEATING',
        },
        'air': {
            'delete': 0,
            'new name': 'CENTRAL AIR',
        },
        'frpl': {
            'delete': 0,
            'new name': '# FIREPLACE',
        },
        'attic_type': {
            'delete': 0,
            'new name': 'ATTIC',
        },
        'attic_fnsh': {
            'delete': 0,
            'new name': 'ATTIC COND',
        },
        'hbath': {
            'delete': 0,
            'new name': '# POWDER',
        },
        'tp_plan': {
            'delete': 1,
        },
        'tp_dsgn': {  
            'delete': 0,
            'new name': 'CATHEDRAL CEILING',
        },
        'cnst_qlty': {
            'delete': 0,
            'new name': 'CONST QUALITY',
        },
        'renovation': {
            'delete': 1,
        },
        'site': {
            'delete': 1,
        },
        'gar1_size': {
            'delete': 0,
            'new name': 'GARAGE 1',
        },
        'gar1_cnst': {
            'delete': 0,
            'new name': 'GARAGE 1 MATERIAL',
        },
        'gar1_att': {
            'delete': 0,
            'new name': 'GARAGE ATTACHED',
        },
        'gar1_area': {
            'delete': 0,
            'new name': 'GARAGE 1 AREA'
        },
        'gar2_size': {
            'delete': 1,
        },
        'gar2_cnst': {
            'delete': 1,
        },
        'gar2_att': {
            'delete': 1,
        },
        'gar2_area': {
            'delete': 1,
        },
        'porch': {
            'delete': 0,
            'new name': 'ENCLOSED PORCH',
        },
        'ot_impr': {
            'delete': 1,
        },
        'bldg_sf': {
            'delete': 0,
            'new name': 'GSF',
        },
        'repair_cnd': {
            'delete': 0,
            'new name': 'INT COND',
        },
        'multi_code': {
            'delete': 0,
            'new name': '# BLDG',
        },
        'ncu': {
            'delete': 0,
            'new name': '# COMM',
        },
        'pri_est_land': {
            'delete': 0,
            'new name': 'LAND ASSD $ PY',
        },
        'pri_est_bldg': {
            'delete': 0,
            'new name': 'BLDG ASSD $ PY',
        },
        'most_recent_sale_date': {
            'delete': 0,
            'new name': 'SALE DATE',
        },
        'doc_no': {
            'delete': 0,
            'new name': 'Deed No.',
        },
        'most_recent_sale_price': {
            'delete': 0,
            'new name': 'SALE PRICE',
        },
        'centroid_x': {
            'delete': 0,
            'new name': 'LONGITUDE',
        },
        'centroid_y': {
            'delete': 0,
            'new name': 'LATITUDE',
        },
        'tractce': {
            'delete': 1,
        },
        'total_bldg_sf': {
            'delete': 0,
            'new name': 'Total Building Square Feet',
        },
        'multi_ind': {
            'delete': 1,
        },
        'addr': {
            'delete': 0,
            'new name': 'ADDRESS',
        },
        'modeling_group': {
            'delete': 0,
            'new name': 'Modeling Group',
        },
        'fbath': {
            'delete': 0,
            'new name': '# BATH',
        },
        'age': {
            'delete': 0,
            'new name': 'YEAR BUILT',
        },
        'use_1': {
            'delete': 0,
            'new name': 'PROPERTY TYPE',
        },
        'n_units': {
            'delete': 0,
            'new name': '# UNITS',
        },
        'per_ass': {
            'delete': 1,
        },
        'condo_class_factor': {
            'delete': 1,
        },
        'multi_family_ind': {
            'delete': 1,
        },
        'large_lot': {
            'delete': 1,
        },
        'deed_type': {
            'delete': 1,
        },
        'o_hare_noise': {
            'delete': 0,
            'new name': 'AIRPORT NOISE',
        },
        'floodplain': {
            'delete': 0,
            'new name': 'FEMA',
        },
        'near_major_road': {
            'delete': 0,
            'new name': 'Near Major Road',
        },
        'total_units': {
            'delete': 1,
        },
        'condo_strata': {
            'delete': 1,
        },
        'age_squared': {
            'delete': 1,
        },
        'age_decade': {
            'delete': 1,
        },
        'age_decade_squared': {
            'delete': 1,
        },
        'lot_size_squared': {
            'delete': 1,
        },
        'improvement_size_squared': {
            'delete': 1,
        },
        'location_factor': {
            'delete': 1,
        },
        'garage_indicator': {
            'delete': 1,
        },
        'residential_share_of_building': {
            'delete': 1,
        },
        'pure_market_sale': {
            'delete': 1,
        },
        'pure_market_filter': {
            'delete': 1,
        },
        'neigborhood_code_mapping_': {
            'delete': 1,
        },
        'square_root_of_lot_size': {
            'delete': 1
        },
        'square_root_of_age': {
            'delete': 1,
        },
        'square_root_of_improvement_size': {
            'delete': 1
        },
        'town_and_neighborhood': {
            'delete': 0,
            'new name': 'Town and Neighborhood'
        }
    }

    CHI_SALES_CLEANING_ADD = {
        'sale_date': {
            'delete': 0,
            'new name': 'SALE DATE',
        },
        'sale_year': {
            'delete': 1,
        },
        'sale_quarter': {
            'delete': 1,
        },
        'sale_half_year': {
            'delete': 1,
        },
        'sale_quarter_of_year': {
            'delete': 1,
        },
        'sale_month_of_year': {
            'delete': 1,
        },
        'sale_half_of_year': {
            'delete': 1,
        },
        'town_and_neighborhood_sf_group_only': {
            'delete': 0,
            'new name': 'Town and Neighborhood, SF Group Only'
        },
        'most_recent_sale': {
            'delete': 0,
            'new name': 'Most Rencent Sale'
        },
        'road_proximity': {
            'delete': 0,
            'new name': 'Road Proximity'
        },
        'est_bldg': {
            'delete': 0,
            'new name': 'Estimate (Building)',
        },
        'est_land': {
            'delete': 0,
            'new name': 'Estimate (Land)',
        },
        'sale_price': {
            'delete': 0,
            'new name': 'SALE PRICE',
        }
    }

    # combine two different dictionaries 
    CHI_SALES_CLEANING = {**CHI_PLUTO_CLEANING, **CHI_SALES_CLEANING_ADD}

    CHI_REIS_RENAME = {
        'Property Type': 'PROPERTY TYPE',
        'Street Address': 'ADDRESS',
        'City': 'CITY',
        'State': 'STATE',
        'Zip': 'ZIP',
        'County': 'COUNTY',
        'Year Renovated': 'YEAR RENOVATED',
        'Asking Rent (Units)': 'ASKING RENT (UNITS)',
        'Asking Rent (SF)': 'ASKING RENT (SF)',
        'Vacancy': 'VACANCY',
        'Building Class': 'BLDG CLASS',
        'Cap Rate': 'CAP RATE',
        'Sale Price': 'SALE PRICE',
        'Sale Date': 'SALE DATE',
        'Transaction Type': 'TRANSACTION TYPE',
        'Buyer': 'BUYER',
        'Year Built': 'YEAR BUILT',
        'Seller': 'SELLER',
        'Construction Status': 'CONSTRUCTION STATUS',
        'Expected Completion': 'EXPECTED COMPLETION',
        'Expected Groundbreak': 'EXPECTED GROUNDBREAK',
        'Developer': 'DEVELOPER',
        'Developer Phone': 'DEVELOPER PHONE',
        'Sector Name': 'SECTOR NAME',
        'Submarket': 'REIS SUBMARKET',
    }

    CHI_COL_MAPPING = {
        'GARAGE ATTACHED': {
            '2': '0',
        },
        'GARAGE 1 AREA': {
            '2': '0',
        },  
        'GARAGE 1': {
            '1': '1',
            '2': '1.5',
            '3': '2',
            '4': '2.5',
            '5': '3',
            '6': '3.5',
            '7': '0',
            '8': '4',
            '9': '4.5',
            '10': '5',
            '11': '5.5',
            '12': '6',
        },
        'BLDG CODE': {
            '202': 'SMALL 1 STORY',
            '203': 'MEDIUM 1 STORY',
            '204': 'LARGE 1 STORY',
            '210': 'TOWNHOUSE',
            '211': 'MULTI: 2 TO 6 UNITS',
            '212': 'MIXED USE',
            '234': 'SPLIT LEVEL',
            '295': 'TOWNHOUSE',
            '205': '2 OR MORE STORIES',
            '206': '2 OR MORE STORIES',
            '207': '2 OR MORE STORIES',
            '208': '2 OR MORE STORIES',
            '209': '2 OR MORE STORIES',
            '278': '2 OR MORE STORIES',
        },
        'BLDG CAT': {
            '1': '1',
            '2': '2',
            '3': '3',
            '5': '1.5',
            '6': '1.5',
            '7': '1.5',
            '8': '1.5',
            '9': '1.5',
        }
    }

    ### package all the instructions
    instructions = {
        'PHL_COLS_ADD': PHL_COLS_ADD,
        'PHL_PLUTO_RENAME': PHL_PLUTO_RENAME,
        'PHL_PLUTO_PROCESS': PHL_PLUTO_PROCESS,
        'PHL_LOGGING': PHL_LOGGING,
        'NYC_SALES_CLEANING': NYC_SALES_CLEANING,
        'NYC_PLUTO_CLEANING': NYC_PLUTO_CLEANING,
        'NYC_REIS_RENAME': NYC_REIS_RENAME,
        'CHI_PLUTO_CLEANING': CHI_PLUTO_CLEANING,
        'CHI_SALES_CLEANING': CHI_SALES_CLEANING,
        'CHI_REIS_RENAME': CHI_REIS_RENAME,
        'CHI_COL_MAPPING': CHI_COL_MAPPING,
    }
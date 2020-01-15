import pandas as pd
import numpy as np

class clean_instructions: 

    def __init__(self):
        pass

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
            'delele': 1,
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
        ''
    }




### package requirements
import pandas as pd
import numpy as np
import warnings
import urllib
import os
import time
import requests

from datetime import datetime
from datetime import date
from urllib.request import urlopen
from lycleaner import Address_cleaner

class cleaning_instructions:

	CHI_PLUTO_CLEANING = {
		'PIN': {
			'delete': 0,
			'new name': 'PIN',
		},
		'Property Class': {
			'delete': 0,
			'new name': 'BLDG CODE',
		},
		'Tax Year': {
			'delete': 0,
			'new name': 'TAX YEAR',
		},
		'Neighborhood Code': {
			'delete': 0,
			'new name': 'NEIGHBORHOOD',
		},
		'Land Square Feet': {
			'delete': 0,
			'new name': 'LAND SF',
		},
		'Town Code': {
			'delete': 0,
			'new name': 'TOWN',
		},
		'Type of Residence': {
			'delete': 0,
			'new name': 'BLDG CAT',
		},
		'Apartments': {
			'delete': 0,
			'new name': '# UNITS',
		},
		'Wall Material': {
			'delete': 0,
			'new name': 'EXT MATERIAL',
		},
		'Roof Material': {
			'delete': 0,
			'new name': 'ROOF MATERIAL',
		},
		'Rooms': {
			'delete': 0,
			'new name': '# ROOMS',
		},
		'Bedrooms': {
			'delete': 0,
			'new name': '# BED',
		},
		'Basement': {
			'delete': 0,
			'new name': 'BASEMENT',
		},
		'Basement Finish': {
			'delete': 0,
			'new name': 'BASEMENT COND',
		},
		'Central Heating': {
			'delete': 0,
			'new name': 'CENTRAL HEATING',
		},
		'Other Heating': {
			'delete': 0,
			'new name': 'OTHER HEATING',
		},
		'Central Air': {
			'delete': 0,
			'new name': 'CENTRAL AIR',
		},
		'Fireplaces': {
			'delete': 0,
			'new name': '# FIREPLACE',
		},
		'Attic Type': {
			'delete': 0,
			'new name': 'ATTIC',
		},
		'Attic Finish': {
			'delete': 0,
			'new name': 'ATTIC COND',
		},
		'Half Baths': {
			'delete': 0,
			'new name': '# POWDER',
		},
		'Design Plan': {
			'delete': 1,
		},
		'Cathedral Ceiling': {	
			'delete': 0,
			'new name': 'CATHEDRAL CEILING',
		},
		'Construction Quality': {
			'delete': 0,
			'new name': 'CONST QUALITY',
		},
		'Renovation': {
			'delete': 1,
		},
		'Site Desireability': {
			'delete': 1,
		},
		'Garage 1 Size': {
			'delete': 0,
			'new name': 'GARAGE 1',
		},
		'Garage 1 Material': {
			'delete': 0,
			'new name': 'GARAGE 1 MATERIAL',
		},
		'Garage 1 Attachment': {
			'delete': 0,
			'new name': 'GARAGE ATTACHED',
		},
		'Garage 1 Area': {
			'delete': 0,
			'new name': 'GARAGE 1 AREA'
		},
		'Garage 2 Size': {
			'delete': 1,
		},
		'Garage 2 Material': {
			'delete': 1,
		},
		'Garage 2 Attachment': {
			'delete': 1,
		},
		'Garage 2 Area': {
			'delete': 1,
		},
		'Porch': {
			'delete': 0,
			'new name': 'ENCLOSED PORCH',
		},
		'Other Improvements': {
			'delete': 1,
		},
		'Building Square Feet': {
			'delete': 0,
			'new name': 'GSF',
		},
		'Repair Condition': {
			'delete': 0,
			'new name': 'INT COND',
		},
		'Multi Code': {
			'delete': 0,
			'new name': '# BLDG',
		},
		'Number of Commercial Units': {
			'delete': 0,
			'new name': '# COMM',
		},
		'Prior Tax Year Market Value Estimate (Land)': {
			'delete': 0,
			'new name': 'LAND ASSD $ PY',
		},
		'Prior Tax Year Market Value Estimate (Building)': {
			'delete': 0,
			'new name': 'BLDG ASSD $ PY',
		},
		'Date of Most Recent Sale': {
			'delete': 0,
			'new name': 'SALE DATE',
		},
		'Deed No.': {
			'delete': 0,
			'new name': 'Deed No.',
		},
		'Sale Price': {
			'delete': 0,
			'new name': 'SALE PRICE',
		},
		'Longitude': {
			'delete': 0,
			'new name': 'LONGITUDE',
		},
		'Latitude': {
			'delete': 0,
			'new name': 'LATITUDE',
		},
		'Census Tract': {
			'delete': 1,
		},
		'Total Building Square Feet': {
			'delete': 0,
			'new name': 'Total Building Square Feet',
		},
		'Multi Property Indicator': {
			'delete': 1,
		},
		'Property Address': {
			'delete': 0,
			'new name': 'ADDRESS',
		},
		'Modeling Group': {
			'delete': 0,
			'new name': 'Modeling Group',
		},
		'Full Baths': {
			'delete': 0,
			'new name': '# BATH',
		},
		'Age': {
			'delete': 0,
			'new name': 'YEAR BUILT',
		},
		'Use': {
			'delete': 0,
			'new name': 'PROPERTY TYPE',
		},
		'Number of Units': {
			'delete': 0,
			'new name': '# UNITS',
		},
		'Percent Ownership': {
			'delete': 1,
		},
		'Condo Class Factor': {
			'delete': 1,
		},
		'Multi-Family Indicator': {
			'delete': 1,
		},
		'Large Lot': {
			'delete': 1,
		},
		'Condition, Desirability and Utility': {
			'delete': 1,
		},
		'Deed Type': {
			'delete': 1,
		},
		"O'Hare Noise": {
			'delete': 0,
			'new name': 'AIRPORT NOISE',
		},
		'Floodplain': {
			'delete': 0,
			'new name': 'FEMA',
		},
		'Near Major Road': {
			'delete': 0,
			'new name': 'Near Major Road',
		},
		'Total Units': {
			'delete': 1,
		},
		'Condo Strata': {
			'delete': 1,
		},
		'Age Squared': {
			'delete': 1,
		},
		'Age Decade': {
			'delete': 1,
		},
		'Age Decade Squared': {
			'delete': 1,
		},
		'Lot Size Squared': {
			'delete': 1,
		},
		'Improvement Size Squared': {
			'delete': 1,
		},
		'Location Factor': {
			'delete': 1,
		},
		'Garage indicator': {
			'delete': 1,
		},
		'Residential share of building': {
			'delete': 1,
		},
		'Pure Market Sale': {
			'delete': 1,
		},
		'Pure Market Filter': {
			'delete': 1,
		},
		'Neigborhood Code (mapping)': {
			'delete': 1,
		},
		'Square root of lot size': {
			'delete': 1
		},
		'Square root of age': {
			'delete': 1,
		},
		'Square root of age': {
			'delete': 1,
		},
		'Square root of improvement size': {
			'delete': 1
		},
		'Town and Neighborhood': {
			'delete': 1,
		}
	}

	CHI_SALES_CLEANING = CHI_PLUTO_CLEANING.update(
		{
			'Sale Date': {
				'delete': 0,
				'new name': 'SALE DATE',
			},
			'Sale Year': {
				'delete': 1,
			},
			'Sale Quarter': {
				'delete': 1,
			},
			'Sale Half-Year': {
				'delete': 1,
			},
			'Sale Quarter of Year': {
				'delete': 1,
			},
			'Sale Month of Year': {
				'delete': 1,
			},
			'Sale Half of Year': {
				'delete': 1,
			},
			'Town and Neighborhood, SF Group Only': {
				'delete': 1,
			}
		}
	)

	instructions = {
		'CHI_PLUTO_CLEANING': CHI_PLUTO_CLEANING,
		'CHI_SALES_CLEANING': CHI_SALES_CLEANING,
	}


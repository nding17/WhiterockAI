import pandas as pd
import numpy as np
import re
import warnings

__version__ = "0.0.6.1"
#                  "AVE":"AVENUE",
#"AVE":"AVENUE",

class Address_cleaner:

    def __init__(self):
        self.l = ["ST","STR","ST.","ARC","AVE","AV","AV.","AVE.","AVE,","AVE.,","AVENUE.","AVENUES","AVENUE`","AVE`",
                  "PL","RD","DR","BLVD","BLVD.","BLV","BLV.","BL","BLD","BLD.","CIR","CR","CRES","CT","CT.","CRT","CTR","CW","DR","DR.","DRIVE.",
                  "EXP","EXPWY","EXPWY.","EXPY","GDNS","GRN","GLN","HWY","IS","LN.","LN","LNDG","MNR","N.","PKWY","PKWY.","PKY","PL.","PLACE?","PLZ","PT","RD.","ROAD.","ROAD`",
                  "ROCKWAY","RT","S.","SQ","ST,","ST..","STREET,","STREET.","STREET:","STREET`","STR.","STRET","STREE","T.","TE","TER","TPK","TPK.","TPKE","TRL","W.","HTS",
                  "W","E","N","S","WA","WH","WY","FIRST","SECOND","THIRD","FOURTH","FIFTH","SIXTH","SEVENTH","EIGHTH","NINTH","TENTH","ELEVENTH","TWEFLTH","THIRTEENTH","FOURTEENTH",
                  "FIFTEENTH","SIXTEENTH","SEVENTEENTH","EIGHTEENTH","NINETEENTH","TWENTIETH","ONE","TWO","THREE","FOUR","FIVE","SIX","SEVEN","EIGHT","NINE","TEN","RSB","TERRAC",
                  "PK","NE","NW","SE","SW","BOULEVARD...","BOULEVAR...","PWKY","FT","FR.","RO","FRM","P"]
        self.d = {"ST":"STREET",
                  "STR":"STREET",
                  "ST.":"STREET",
                  "ARC":"ARCADE",
                  "AV":"AVENUE",
                  "AV.":"AVENUE",
                  "AVE.":"AVENUE",
                  "AVE.,":"AVENUE",
                  "AVE,":"AVENUE",
                  "AVE:":"AVENUE",
                  "AVE":"AVENUE",
                  "AVENUE.":"AVENUE",
                  "AVENUES":"AVENUE",
                  "AVENUE`":"AVENUE",
                  "AVE`":"AVENUE",
                  "PL":"PLACE",
                  "RD":"ROAD",
                  "BLVD":"BOULEVARD",
                  "BOULEVARD...":"BOULEVARD",
                  "BOULEVAR...":"BOULEVARD",
                  "BLVD.":"BOULEVARD",
                  "BLV":"BOULEVARD",
                  "BLV.":"BOULEVARD",
                  "BL":"BOULEVARD",
                  "BLD":"BOULEVARD",
                  "BLD.":"BOULEVARD",
                  "CIR":"CIRCLE",
                  "CMN":"COMMON",
                  "CT":"COURT",
                  "CRT":"COURT",
                  "CR": "CRESCENT",
                  "CRES":"CRESCENT",                  
                  "CT.":"COURT",
                  "CTR":"CENTER",
                  "CW":"CROSSWAY",
                  "DR":"DRIVE",
                  "DR.":"DRIVE",
                  "DRIVE.":"DRIVE",
                  "E":"EAST",
                  "EXP":"EXPRESSWAY",
                  "EXPWY":"EXPRESSWAY",
                  "EXPWY.":"EXPRESSWAY",
                  "EXPY":"EXPRESSWAY",
                  "FT":"FORT",
                  "FR.":"FATHER",
                  "FRM":"FARM",
                  "GDNS": "GARDENS",
                  "GRN": "GREEN",
                  "GLN": "GLEN",                  
                  "HWY":"HIGHWAY",
                  "IS":"ISLAND",
                  "LN.":"LN",
                  "LN":"LANE",
                  "LNDG":"LANDING",
                  "MNR":"MANOR",
                  "N.":"NORTH",
                  "N":"NORTH",
                  "PKWY":"PARKWAY",
                  "PKWY.":"PARKWAY",
                  "PWKY":"PARKWAY",
                  "PKY":"PARKWAY",
                  "PKWAY":"PARKWAY",
                  "P":"PATH",
                  "PK":"PARK",
                  "PL.":"PLACE",
                  "PLACE?":"PLACE",
                  "PLZ":"PLAZA",
                  "PT":"POINT",
                  "ROAD.":"ROAD",
                  "RD.":"ROAD",
                  "RD..":"ROAD",
                  "RD:":"ROAD",
                  "ROAD`":"ROAD",
                  "ROCKWAY":"ROCKWAYS",
                  "RO":"ROW",
                  "RSB":"RIVERSIDE BOULEVARD",
                  "RT":"ROUTE",
                  "S.":"SOUTH",
                  "S":"SOUTH",
                  "SQ":"SQUARE",
                  "ST,":"STREET",
                  "ST..":"STREET",
                  "STREET,":"STREET",
                  "STREET.":"STREET",
                  "STREET:":"STREET",
                  "STREET`":"STREET",
                  "STRET":"STREET",
                  "STR.":"STREET",
                  "STREE":"STREET",
                  "T.":"T",
                  "TPK":"TPKE",
                  "TPK.":"TPKE",
                  "TPKE":"TURNPIKE",
                  "TER":"TERRACE",
                  "TE":"TERRACE",
                  "TRL":"TRAIL",
                  "W.":"WEST",
                  "W":"WEST",
                  "WA": "WAY",
                  "WH": "WHARF",
                  "WY": "WAY",
                  "FIRST":"1",
                  "SECOND":"2",
                  "THIRD":"3",
                  "FOURTH":"4",
                  "FIFTH":"5",
                  "SIXTH":"6",
                  "SEVENTH":"7",
                  "EIGHTH":"8",
                  "NINTH":"9",
                  "TENTH":"10",
                  "ELEVENTH":"11",
                  "TWEFLTH":"12",
                  "THIRTEENTH":"13",
                  "FOURTEENTH":"14",
                  "FIFTEENTH":"15",
                  "SIXTEENTH":"16",
                  "SEVENTEENTH":"17",
                  "EIGHTEENTH":"18",
                  "NINETEENTH":"19",
                  "TWENTIETH":"20",
                  "ONE":"1",
                  "TWO":"2",
                  "THREE":"3",
                  "FOUR":"4",
                  "FIVE":"5",
                  "SIX":"6",
                  "SEVEN":"7",
                  "EIGHT":"8",
                  "NINE":"9",
                  "TEN":"10",
                  "TERRAC":"TERRACE",
                  "HTS":"HEIGHTS",
                  "NE":"NORTHEAST",
                  "NW":"NORTHWEST",
                  "SE":"SOUTHEAST",
                  "SW":"SOUTHWEST"
                  }
        self.prefix_l = ["W","W.","E","E.","EAS","N","N.","S","S.","ST.","MT","MT.","AV","AVE","AVE.","FT.","REV."]
        self.prefix_d = {
            "W":"WEST",
            "W.":"WEST",
            "E":"EAST",
            "E.":"EAST",
            "EAS":"EAST",
            "N":"NORTH",
            "N.":"NORTH",
            "S":"SOUTH",
            "S.":"SOUTH",
            "ST.":"ST",
            " ST ":" STREET ",
            "MT":"MOUNTAIN",
            "MT.":"MOUNTAIN",
            "AV":"AVENUE",
            "AVE.":"AVENUE",
            " AVE ":" AVENUE ",
            " DR ":" DRIVE ",
            " BLV ":" BOULEVARD ",        
            "FT.":"FT",
            "REV.":"REV"
        }

    def remove_city(self,dataframe,city_name,upcase=False):

        self.df = dataframe
        self.s = city_name

        def strip_with_comma(x,s):
            #if pd.isna(x): return np.NaN

            s_pat=re.compile("\s+")
            elements = re.split(s_pat,s)

            construct = elements[0]
            if len(elements) > 0:
                for element in elements[1:]:
                    construct = construct + "\s*" +element

            pat = re.compile("\s*,\s*"+construct+"\s*",re.I)

            return re.sub(pat,"",x)

        def s_upcase(x):
            #if pd.isna(x):return np.NaN
            return x.upper()

        self.df = self.df.apply(strip_with_comma,s=self.s)

        if upcase:
            self.df = self.df.apply(s_upcase)

        return self.df

    def describe(self,dataframe=pd.Series([])):
        if not dataframe.empty:
            return dataframe.apply(lambda x:x.strip(" ")).astype("category").value_counts().sort_index()
        else:
            return self.df.astype("category").value_counts().sort_index()

    def strip_space(self,dataframe):
        self.df = dataframe

        def calc0(x):
            #if pd.isna(x):return np.nan
            return x.strip(' ')

        def calc(x):
            #if pd.isna(x):return np.nan
            space = " "
            pat = re.compile("\s+")
            res = re.split(pat,x)
            return space.join(res)

        self.df=self.df.apply(calc0)

        return self.df.apply(calc)

    def fix_st_ave(self,dataframe):
        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan
            space = " "
            pat = re.compile("\s+")
            res = re.split(pat,x)
            for i in range(len(res)):
                if res[i] in self.l:
                    res[i] = self.d[res[i]]
                #return space.join(res)
            return space.join(res)

        return self.df.apply(calc)

    def fix_digit_th(self,dataframe):
        # will deprecate in the future
        print('\033[1;31;47mHi, I will remove this function in the future, try to use fix_digit_st() and set mode = True.\033[0m')
        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan
            space = " "
            pat = re.compile("\s+")
            res = re.split(pat,x)
            pat1 = re.compile("\d+TH$")
            res1 = []
            for part in res:
                if re.search(pat1,part):
                    part = part[:-2]
                res1.append(part)
            return space.join(res1)

        return self.df.apply(calc)

    def fix_digit_st(self,dataframe,mode = False):

        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan
            space = " "
            pat = re.compile("\s+")
            res = re.split(pat,x)

            pat1 = re.compile("(\d+)([A-Z]+)$")
            res1 = []
            for part in res:
                if pat1.findall(part):
                    part = space.join(pat1.findall(part)[0])
                res1.append(part)
            return space.join(res1)

        def calc2(x):
            #if pd.isna(x): return np.nan
            space = " "
            pat = re.compile("\s+")
            res = re.split(pat,x)

            pat1 = re.compile("(\d+)([NSRT][DHT])$")
            res1 = []
            for part in res:
                if pat1.findall(part):
                    part = pat1.findall(part)[0][0]
                res1.append(part)
            return space.join(res1)

        if mode: return self.df.apply(calc2)

        return self.df.apply(calc)

    def fix_add_st(self,dataframe):
        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan
            space = " "
            pat = re.compile("\s+")
            res = re.split(pat,x)

            pat1 = re.compile("\d+$")
            if re.match(pat1,res[-1]):
                res[-1] = res[-1]+" "+"STREET"

            return space.join(res)

        return self.df.apply(calc)

    def fix_describe(self,dataframe):
        self.df = dataframe
        def calc(x):
            #if pd.isna(x): return np.nan
            pat = re.compile("\s+")
            res = re.split(pat,x)
            return res[-1]
        return self.df.apply(calc).astype("category").value_counts().sort_index()

    def fix_digit_thdot(self,dataframe):
        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan
            space = " "
            pat = re.compile("\s+")
            res = re.split(pat,x)
            pat1 = re.compile("\d+TH\\.$")
            res1 = []
            for part in res:
                if re.search(pat1,part):
                    part = part[:-3]
                res1.append(part)
            return space.join(res1)

        return self.df.apply(calc)

    def fix_digit_stdot(self,dataframe):
        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan
            space = " "
            pat = re.compile("\s+")
            res = re.split(pat,x)
            pat1 = re.compile("\d+ST\\.$")
            res1 = []
            for part in res:
                if re.search(pat1,part):
                    part = part[:-3]
                res1.append(part)
            return space.join(res1)

        return self.df.apply(calc)

    def fix_digit_nddot(self,dataframe):
        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan
            space = " "
            pat = re.compile("\s+")
            res = re.split(pat,x)
            pat1 = re.compile("\d+ND\\.$")
            res1 = []
            for part in res:
                if re.search(pat1,part):
                    part = part[:-3]
                res1.append(part)
            return space.join(res1)

        return self.df.apply(calc)

    def fix_digit_rddot(self,dataframe):
        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan
            space = " "
            pat = re.compile("\s+")
            res = re.split(pat,x)
            pat1 = re.compile("\d+RD\\.$")
            res1 = []
            for part in res:
                if re.search(pat1,part):
                    part = part[:-3]
                res1.append(part)
            return space.join(res1)

        return self.df.apply(calc)

    def fix_digit_space_st(self,dataframe):
        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan

            pat = re.compile("1 ST ")
            if re.search(pat,x):
                return x.replace('1 ST',"1")
            return x

        return self.df.apply(calc)

    def fix_digit_space_nd(self,dataframe):
        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan

            pat = re.compile("2 ND ")
            if re.search(pat,x):
                return x.replace('2 ND',"2")
            return x

        return self.df.apply(calc)

    def fix_digit_space_rd(self,dataframe):
        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan

            pat = re.compile("3 RD ")
            if re.search(pat,x):
                return x.replace('3 RD',"3")
            return x

        return self.df.apply(calc)

    def fix_prefix(self,dataframe):
        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan
            space = " "
            pat = re.compile("\s+")
            res = re.split(pat,x)
            if res[0] in self.prefix_l:
                res[0] = self.prefix_d[res[0]]
                return (space.join(res)).strip(" ")
            return space.join(res)

        return self.df.apply(calc)

    def fix_second_prefix(self,dataframe):
        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan
            space = " "
            pat = re.compile("\s+")
            res = re.split(pat,x)

            if len(res)>1:
                if res[1] in self.prefix_l:
                    res[1] = self.prefix_d[res[1]]
                    return (space.join(res))

            return space.join(res)

        return self.df.apply(calc)

    def fix_e_dot_digit(self,dataframe):
        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan

            pat = re.compile("E\\.\d")
            if re.match(pat,x):
                return x.replace('E.',"EAST ")
            return x

        return self.df.apply(calc)

    def fix_e_digit(self,dataframe):
        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan

            pat = re.compile("E\d")
            if re.match(pat,x):
                s = x
                s = s[1:]
                s = "EAST "+ s
                return s
            return x

        return self.df.apply(calc)

    def fix_w_digit(self,dataframe):
        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan

            pat = re.compile("W\d")
            if re.match(pat,x):
                s = x
                s = s[1:]
                s = "WEST "+ s
                return s
            return x

        return self.df.apply(calc)

    def fix_east_digit(self,dataframe):
        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan

            pat = re.compile("EAST\d")
            if re.match(pat,x):
                s = x
                s = s[4:]
                s = "EAST "+ s
                return s
            return x

        return self.df.apply(calc)

    def fix_west_digit(self,dataframe):
        self.df = dataframe

        def calc(x):
            #if pd.isna(x): return np.nan

            pat = re.compile("WEST\d")
            if re.match(pat,x):
                s = x
                s = s[4:]
                s = "WEST "+ s
                return s
            return x

        return self.df.apply(calc)

    def easy_clean(self,dataframe):

        print("Hey, please be patient... it takes time")
        self.df = dataframe
        self.df = self.strip_space(self.df)
        print("space striped")
        self.df = self.fix_st_ave(self.df)
        print("suffix fixed")
        self.df = self.fix_digit_st(self.df,mode = True)
        print("1st, 2nd, 3rd, 0th, 4-9th removed")
        self.df = self.fix_prefix(self.df)
        self.df = self.fix_second_prefix(self.df)
        print("prefix fixed")
        self.df = self.fix_add_st(self.df)
        print("street added")
        self.df = self.fix_west_digit(self.df)
        self.df = self.fix_east_digit(self.df)
        self.df = self.fix_w_digit(self.df)
        self.df = self.fix_e_digit(self.df)
        self.df = self.fix_e_dot_digit(self.df)
        print('west \ east done!')
        self.df = self.fix_digit_space_rd(self.df)
        self.df = self.fix_digit_space_nd(self.df)
        self.df = self.fix_digit_space_st(self.df)
        print('fix digit space')
        self.df = self.fix_digit_rddot(self.df)
        self.df = self.fix_digit_nddot(self.df)
        self.df = self.fix_digit_thdot(self.df)
        self.df = self.fix_digit_th(self.df)

        return self.df

def retrieve_digit(dataframe):
    def calc(x):
        pat = re.compile("-?\d+\\.\d+")
        return pd.Series(pat.findall(x))
    return dataframe.apply(calc)

def fast_retrieve_digit(dataframe):
    attr = dataframe.name
    df = pd.DataFrame(dataframe)

    df["pos"] = df[attr].apply(lambda x: re.search(" ",x).span()[0]).array

    print("pos ready...")

    df = df.sort_values("pos")
    print('sort ready')

    grouped = df.groupby("pos")

    tot = pd.DataFrame([])
    for length,part in grouped:
        tot = pd.concat([tot,part[attr].apply(lambda x: x[:length])])

    print('first num retrieved')

    tot2 = pd.DataFrame([])
    for length,part in grouped:
        tot2 = pd.concat([tot2,part[attr].apply(lambda x: x[length+1:])])

    print('second num retrieved')
    res = pd.concat([tot,tot2],axis=1)
    return res.sort_index()

def merge(dataframe1,dataframe2):
    df1 = dataframe1.fillna("")
    df2 = dataframe2.fillna("")
    df3 = df1 + " " + df2
    return df3.apply(lambda x:x.strip(" "))

def fix_dollar(dataframe):
    df = dataframe
    return df.astype(str).apply(lambda x:x.replace("$","")).apply(lambda x:x.replace(",","")).astype(float)

def clean_apt_num(add):
    if add is not None:
        add_up = add.upper()
        return re.sub('APT.\s', '', add_up)
    else:
        return None
    
def split_apt_num(df_col, signal):
    return df_col.str.rsplit(signal,n=1,expand=True,)

def remove_num_bath(feature):
    try:
        res = re.sub('\s\|\s[0-9]\s[A-Z][a-z]{3}[s]?','',feature)
        for s in res.split():
            if s.isdigit():
                return int(s)
            elif s == 'Studio':
                return 0.0
    except:
        return np.nan

def remove_num_bed(feature):
    try:
        res = re.sub('[0-9]\s[A-Z][a-z]{2}[s]?\s\|\s','',feature)
        res = re.sub('[A-Z][a-z]{5}\s\|\s','',res)
        for s in res.split():
            if s.isdigit():
                return int(s)
    except:
        return np.nan

    
def num_bed(info):
    res = re.split(',\s',info)
    try:
        for s in res[0].split():
            if s.isdigit():
                return int(s) 
            elif s == 'Studio':
                return float('0')
    except:
        return np.nan

def num_bath(info):
    res = re.split(',\s',info)
    try:
        for s in res[1].split():
            if s.isdigit():
                return int(s) 
    except:
        return np.nan
    
    
def remove_city(add,city_name,upcase=False):
    
    def strip_with_comma(x,s):
        #if pd.isna(x): return np.NaN

        s_pat=re.compile("\s+")
        elements = re.split(s_pat,s)

        construct = elements[0]
        if len(elements) > 0:
            for element in elements[1:]:
                construct = construct + "\s*" +element

        pat = re.compile("\s*,\s*"+construct+"\s*",re.I)

        return re.sub(pat,"",x)

    def s_upcase(x):
        #if pd.isna(x):return np.NaN
        return x.upper()

    add_res = strip_with_comma(add,city_name)

    if upcase:
        add_res = s_upcase(add_res)

    return add_res

def remove_region(add):
    #if pd.isna(x): return np.NaN
    return re.sub('-\s[A-Z]+.*', '', add)

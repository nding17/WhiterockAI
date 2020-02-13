import pandas as pd
import numpy as np
import re
import warnings

__version__ = "0.0.6"

class Address_cleaner:

    def __init__(self):
        self.l = ["ST","STR","ST.","AVE","AV","AV.","AVE.","AVE,","AVE.,","AVENUE.","AVENUES","AVENUE`","AVE`",
                  "PL","RD","DR","BLVD","BLVD.","BLV","BLV.","BL","BLD","BLD.","CT","CT.","CRT","DR","DR.","DRIVE.",
                  "EXP","EXPWY","EXPWY.","EXPY","HWY","LN.","N.","PKWY","PKWY.","PKY","PL.","PLACE?","RD.","ROAD.","ROAD`",
                  "ROCKWAY","S.","ST,","ST..","STREET,","STREET.","STREET:","STREET`","STR.","STRET","STREE","T.","TPK","TPK.","W.",
                  "W","E","N","S"]
        self.d = {"ST":"STREET",
                  "STR":"STREET",
                  "ST.":"STREET",
                  "AVE":"AVENUE",
                  "AV":"AVENUE",
                  "AV.":"AVENUE",
                  "AVE.":"AVENUE",
                  "AVE.,":"AVENUE",
                  "AVE,":"AVENUE",
                  "AVENUE.":"AVENUE",
                  "AVENUES":"AVENUE",
                  "AVENUE`":"AVENUE",
                  "AVE`":"AVENUE",
                  "PL":"PLACE",
                  "RD":"ROAD",
                  "BLVD":"BOULEVARD",
                  "BLVD.":"BOULEVARD",
                  "BLV":"BOULEVARD",
                  "BLV.":"BOULEVARD",
                  "BL":"BOULEVARD",
                  "BLD":"BOULEVARD",
                  "BLD.":"BOULEVARD",
                  "CT":"COURT",
                  "CRT":"COURT",
                  "CT.":"COURT",
                  "DR":"DRIVE",
                  "DR.":"DRIVE",
                  "DRIVE.":"DRIVE",
                  "E":"EAST",
                  "EXP":"EXPRESSWAY",
                  "EXPWY":"EXPRESSWAY",
                  "EXPWY.":"EXPRESSWAY",
                  "EXPY":"EXPRESSWAY",
                  "HWY":"HIGHWAY",
                  "LN.":"LN",
                  "N.":"NORTH",
                  "N":"NORTH",
                  "PKWY":"PKWAY",
                  "PKWY.":"PKWAY",
                  "PKY":"PKWAY",
                  "PL.":"PLACE",
                  "PLACE?":"PLACE",
                  "ROAD.":"ROAD",
                  "RD.":"ROAD",
                  "ROAD`":"ROAD",
                  "ROCKWAY":"ROCKWAYS",
                  "S.":"SOUTH",
                  "S":"SOUTH",
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
                  "W.":"WEST",
                  "W":"WEST"
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
            "MT":"MOUNTAIN",
            "MT.":"MOUNTAIN",
            "AV":"AVENUE",
            "AVE":"AVENUE",
            "AVE.":"AVENUE",
            "FT.":"FT",
            "REV.":"REV"
        }

    def remove_city(self,dataframe,city_name,upcase=False):

        self.df = dataframe
        self.s = city_name

        def strip_with_comma(x,s):
            if pd.isna(x): return np.NaN

            s_pat=re.compile("\s+")
            elements = re.split(s_pat,s)

            construct = elements[0]
            if len(elements) > 0:
                for element in elements[1:]:
                    construct = construct + "\s*" +element

            pat = re.compile("\s*,\s*"+construct+"\s*",re.I)

            return re.sub(pat,"",x)

        def s_upcase(x):
            if pd.isna(x):return np.NaN
            return x.upper()

        self.df = self.df.apply(strip_with_comma,s=self.s)

        if upcase:
            self.df = self.df.apply(s_upcase)

        return self.df

    def describe(self,dataframe=pd.Series([])):
        if not dataframe.empty:
            return dataframe.astype("category").value_counts().sort_index()
        else:
            return self.df.astype("category").value_counts().sort_index()

    def strip_space(self,dataframe):
        self.df = dataframe
        def calc(x):
            if pd.isna(x):return np.nan
            return x.strip(' ')
        return self.df.apply(calc)

    def fix_st_ave(self,dataframe):
        self.df = dataframe

        def calc(x):
            if pd.isna(x): return np.nan
            space = " "
            pat = re.compile("\s+")
            res = re.split(pat,x)
            if res[-1] in self.l:
                res[-1] = self.d[res[-1]]
                return space.join(res)
            return space.join(res)

        return self.df.apply(calc)

    def fix_digit_th(self,dataframe):
        # will deprecate in the future
        print('\033[1;31;47mHi, I will remove this function in the future, try to use fix_digit_st() and set mode = True.\033[0m')
        self.df = dataframe

        def calc(x):
            if pd.isna(x): return np.nan
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
            if pd.isna(x): return np.nan
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
            if pd.isna(x): return np.nan
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
            if pd.isna(x): return np.nan
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
            if pd.isna(x): return np.nan
            pat = re.compile("\s+")
            res = re.split(pat,x)
            return res[-1]
        return self.df.apply(calc).astype("category").value_counts().sort_index()

    def fix_digit_thdot(self,dataframe):
        self.df = dataframe

        def calc(x):
            if pd.isna(x): return np.nan
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
            if pd.isna(x): return np.nan
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
            if pd.isna(x): return np.nan
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
            if pd.isna(x): return np.nan
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
            if pd.isna(x): return np.nan

            pat = re.compile("1 ST ")
            if re.search(pat,x):
                return x.replace('1 ST',"1")
            return x

        return self.df.apply(calc)

    def fix_digit_space_nd(self,dataframe):
        self.df = dataframe

        def calc(x):
            if pd.isna(x): return np.nan

            pat = re.compile("2 ND ")
            if re.search(pat,x):
                return x.replace('2 ND',"2")
            return x

        return self.df.apply(calc)

    def fix_digit_space_rd(self,dataframe):
        self.df = dataframe

        def calc(x):
            if pd.isna(x): return np.nan

            pat = re.compile("3 RD ")
            if re.search(pat,x):
                return x.replace('3 RD',"3")
            return x

        return self.df.apply(calc)

    def fix_prefix(self,dataframe):
        self.df = dataframe

        def calc(x):
            if pd.isna(x): return np.nan
            space = " "
            pat = re.compile("\s+")
            res = re.split(pat,x)
            if res[0] in self.prefix_l:
                res[0] = self.prefix_d[res[0]]
                return (space.join(res)).strip(" ")
            return space.join(res)

        return self.df.apply(calc)

    def fix_e_dot_digit(self,dataframe):
        self.df = dataframe

        def calc(x):
            if pd.isna(x): return np.nan

            pat = re.compile("E\\.\d")
            if re.match(pat,x):
                return x.replace('E.',"EAST ")
            return x

        return self.df.apply(calc)

    def fix_e_digit(self,dataframe):
        self.df = dataframe

        def calc(x):
            if pd.isna(x): return np.nan

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
            if pd.isna(x): return np.nan

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
            if pd.isna(x): return np.nan

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
            if pd.isna(x): return np.nan

            pat = re.compile("WEST\d")
            if re.match(pat,x):
                s = x
                s = s[4:]
                s = "WEST "+ s
                return s
            return x

        return self.df.apply(calc)

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

def fix_dollor(dataframe):
    df = dataframe
    return df.astype(str).apply(lambda x:x.replace("$","")).apply(lambda x:x.replace(",","")).astype(float)

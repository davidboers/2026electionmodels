import pandas as pd


current_year = 2026

race_data = pd.Series()

# US Senate

ossoff2026 = 'Jon Ossoff (I) (Dem)'
collins2026 = 'Mike Collins (Rep)'

ossoff2021 = 'Jon Ossoff (Dem)'
perdue2021 = 'David A. Perdue (I) (Rep)'

us_senate_meta = pd.DataFrame({
    'Previous Winner': {2026: ossoff2021},
    'Previous Runner-up': {2026: perdue2021},
    'Challenger': {2026: collins2026},
    'Previous Rep': {2026: perdue2021},
    'Previous Dem': {2026: ossoff2021},
    'Previous Lib': {},
    'Current Rep': {2026: collins2026},
    'Current Dem': {2026: ossoff2026},
    'Current Lib': {},
    'Previous Election': {2026: 2021},
    'Race file': 'us_senate_(perdue)',
})

if current_year == 2026:
    race_data['US Senate'] = us_senate_meta


# Governor

jackson2026 = 'Rick Jackson (Rep)'
bottoms2026 = 'Keisha Lance Bottoms (Dem)'

kemp2022 = 'Brian Kemp (I) (Rep)'
abrams2022 = 'Stacey Abrams (Dem)'
hazel2022 = 'Shane Hazel (Lib)'

kemp2018 = 'BRIAN KEMP  (REP)'
abrams2018 = 'STACEY ABRAMS  (DEM)'
metz2018 = 'TED METZ (LIB)'

race_data['Governor'] = pd.DataFrame({
    'Previous Winner': {2022: kemp2018, 2026: kemp2022},
    'Previous Runner-up': {2022: abrams2018, 2026: abrams2022},
    'Challenger': {2022: abrams2022, 2026: bottoms2026},
    'Previous Rep': {2022: kemp2018, 2026: kemp2022},
    'Previous Dem': {2022: abrams2018, 2026: abrams2022},
    'Previous Lib': {2022: metz2018, 2026: hazel2022},
    'Current Rep': {2022: kemp2022, 2026: jackson2026},
    'Current Dem': {2022: abrams2022, 2026: bottoms2026},
    'Current Lib': {2022: hazel2022},
    'Previous Election': {2026: 2022, 2022: 2018},
})


# Lieutenant governor

dolezal2026 = 'Greg Dolezal (Rep)'
mclaurin2026 = 'Josh McLaurin (Dem)'

bjones2022 = 'Burt Jones (Rep)'
bailey2022 = 'Charlie Bailey (Dem)'
graham2022 = 'Ryan Graham (Lib)'

duncan2018 = 'GEOFF DUNCAN  (REP)'
amico2018 = 'SARAH RIGGS AMICO (DEM)'

race_data['Lieutenant Governor'] = pd.DataFrame({
    'Previous Winner': {2022: duncan2018, 2026: bjones2022},
    'Previous Runner-up': {2022: amico2018, 2026: bailey2022},
    'Challenger': {2022: bailey2022, 2026: mclaurin2026},
    'Previous Rep': {2022: duncan2018, 2026: bjones2022},
    'Previous Dem': {2022: amico2018, 2026: bailey2022},
    'Previous Lib': {2026: graham2022},
    'Current Rep': {2022: bjones2022, 2026: dolezal2026},
    'Current Dem': {2022: bailey2022, 2026: mclaurin2026},
    'Current Lib': {2022: graham2022},
    'Previous Election': {2026: 2022, 2022: 2018},
})


# Secretary of State

fleming2026 = 'Tim Fleming (Rep)'
reynolds2026 = 'Penny Brown Reynolds (Dem)'

raffensperger2022 = 'Brad Raffensperger (I) (Rep)'
nguyen2022 = 'Bee Nguyen (Dem)'
metz2022 = 'Ted Metz (Lib)'

raffensperger2018 = 'BRAD RAFFENSPERGER  (REP)'
barrow2018 = 'JOHN BARROW  (DEM)'
duval2018 = 'SMYTHE DUVAL (LIB)'  # Should really be based off of runoff but I can't be bothered to load it in just for the test

race_data['Secretary of State'] = pd.DataFrame({
    'Previous Winner': {2022: raffensperger2018, 2026: raffensperger2022},
    'Previous Runner-up': {2022: barrow2018, 2026: nguyen2022},
    'Challenger': {2022: nguyen2022, 2026: reynolds2026},
    'Previous Rep': {2022: raffensperger2018, 2026: raffensperger2022},
    'Previous Dem': {2022: barrow2018, 2026: nguyen2022},
    'Previous Lib': {2022: duval2018, 2026: metz2022},
    'Current Rep': {2022: raffensperger2022, 2026: fleming2026},
    'Current Dem': {2022: nguyen2022, 2026: reynolds2026},
    'Current Lib': {2022: metz2022},
    'Previous Election': {2026: 2022, 2022: 2018},
})


# Attorney General

strickland2026 = 'Brian Strickland (Rep)'
miller2026 = 'Tanya Miller (Dem)'

carr2022 = 'Chris Carr (I) (Rep)'
jordan2022 = 'Jennifer ""Jen"" Jordan (Dem)'
cowen2022 = 'Martin Cowen (Lib)'

carr2018 = 'CHRIS CARR (I) (REP)'
bailey2018 = 'CHARLIE BAILEY  (DEM)'

race_data['Attorney General'] = pd.DataFrame({
    'Previous Winner': {2022: carr2018, 2026: carr2022},
    'Previous Runner-up': {2022: bailey2018, 2026: jordan2022},
    'Challenger': {2022: jordan2022, 2026: miller2026},
    'Previous Rep': {2022: carr2018, 2026: carr2022},
    'Previous Dem': {2022: bailey2018, 2026: jordan2022},
    'Previous Lib': {2026: cowen2022},
    'Current Rep': {2022: carr2022, 2026: strickland2026},
    'Current Dem': {2022: jordan2022, 2026: miller2026},
    'Current Lib': {2022: cowen2022},
    'Previous Election': {2026: 2022, 2022: 2018},
})


# Commissioner of Agriculture

harper2026 = 'Tyler Harper (I) (Rep)'
juhanarnold2026 = 'Katherine E. Juhan-Arnold (Dem)'

harper2022 = 'Tyler Harper (Rep)'
hemingway2022 = 'Nakita Hemingway (Dem)'
raudabaugh2022 = 'David Raudabaugh (Lib)'

black2018 = 'GARY BLACK (I) (REP)'
swann2018 = 'FRED SWANN  (DEM)'

race_data['Commissioner of Agriculture'] = pd.DataFrame({
    'Previous Winner': {2022: black2018, 2026: harper2022},
    'Previous Runner-up': {2022: swann2018, 2026: hemingway2022},
    'Challenger': {2022: hemingway2022, 2026: juhanarnold2026},
    'Previous Rep': {2022: black2018, 2026: harper2022},
    'Previous Dem': {2022: swann2018, 2026: hemingway2022},
    'Previous Lib': {2026: raudabaugh2022},
    'Current Rep': {2022: harper2022, 2026: harper2026},
    'Current Dem': {2022: hemingway2022, 2026: juhanarnold2026},
    'Current Lib': {2022: raudabaugh2022},
    'Previous Election': {2026: 2022, 2022: 2018},
})


# Commissioner of Insurance

king2026 = 'John King (I) (Rep)'
waites2026 = 'Keisha Sean Waites (Dem)'

king2022 = 'John King (I) (Rep)'
robinson2022 = 'Janice Laws Robinson (Dem)'

beck2018 = 'JIM BECK  (REP)'
laws2018 = 'JANICE LAWS  (DEM)'
foster2018 = 'DONNIE FOSTER (LIB)'

race_data['Commissioner of Insurance'] = pd.DataFrame({
    'Previous Winner': {2022: beck2018, 2026: king2022},
    'Previous Runner-up': {2022: laws2018, 2026: robinson2022},
    'Challenger': {2022: robinson2022, 2026: waites2026},
    'Previous Rep': {2022: beck2018, 2026: king2022},
    'Previous Dem': {2022: laws2018, 2026: robinson2022},
    'Previous Lib': {2022: foster2018},
    'Current Rep': {2022: king2022, 2026: king2026},
    'Current Dem': {2022: robinson2022, 2026: waites2026},
    'Current Lib': {},
    'Previous Election': {2026: 2022, 2022: 2018},
})


# Commissioner of Labor

holmes2026 = 'Bárbara Rivera Holmes (I) (Rep)'
porcher2026 = 'Nikki Porcher (Dem)'

thompson2022 = 'Bruce Thompson (Rep)'
boddie2022 = 'William ""Will"" Boddie, Jr (Dem)'
anderson2022 = 'Emily Anderson (Lib)'

butler2018 = 'MARK BUTLER (I) (REP)'
keatley2018 = 'RICHARD KEATLEY (DEM)'

race_data['Commissioner of Labor'] = pd.DataFrame({
    'Previous Winner': {2022: butler2018, 2026: thompson2022},
    'Previous Runner-up': {2022: keatley2018, 2026: boddie2022},
    'Challenger': {2022: boddie2022, 2026: porcher2026},
    'Previous Rep': {2022: butler2018, 2026: thompson2022},
    'Previous Dem': {2022: keatley2018, 2026: boddie2022},
    'Previous Lib': {2026: anderson2022},
    'Current Rep': {2022: thompson2022, 2026: holmes2026},
    'Current Dem': {2022: boddie2022, 2026: porcher2026},
    'Current Lib': {2022: anderson2022},
    'Previous Election': {2026: 2022, 2022: 2018},
})


# State School Superintendent

woods2026 = 'Richard Woods (I) (Rep)'
powell2026 = 'Lydia Powell (Dem)'

woods2022 = woods2026
searcy2022 = 'Alisha Thomas Searcy (Dem)'

woods2018 = 'RICHARD WOODS (I) (REP)'
thornton2018 = 'OTHA E. THORNTON, JR (DEM)'

race_data['State School Superintendent'] = pd.DataFrame({
    'Previous Winner': {2022: woods2018, 2026: woods2022},
    'Previous Runner-up': {2022: thornton2018, 2026: searcy2022},
    'Challenger': {2022: searcy2022, 2026: powell2026},
    'Previous Rep': {2022: woods2018, 2026: woods2022},
    'Previous Dem': {2022: thornton2018, 2026: searcy2022},
    'Previous Lib': {},
    'Current Rep': {2022: woods2022, 2026: woods2026},
    'Current Dem': {2022: searcy2022, 2026: powell2026},
    'Current Lib': {},
    'Previous Election': {2026: 2022, 2022: 2018},
    'Test swing': -1.17,
})


# Public Service Commission - District 3

johnson2026 = 'Fitz Johnson (Rep)'
hubbard2026 = 'Peter Hubbard (I) (Dem)'

johnson2025 = 'Fitz Johnson (I) (Rep)'
hubbard2025 = 'Peter Hubbard (Dem)'

psc_d3 = pd.DataFrame({
    'Previous Winner': {2026: hubbard2025},
    'Previous Runner-up': {2026: johnson2025},
    'Challenger': {2026: johnson2026},
    'Previous Rep': {2026: johnson2025},
    'Previous Dem': {2026: hubbard2025},
    'Previous Lib': {},
    'Current Rep': {2026: johnson2026},
    'Current Dem': {2026: hubbard2026},
    'Current Lib': {},
    'Previous Election': {2026: 2025},
    'Race file': 'psc_-_district_3'
})

if current_year == 2026:
    race_data['PSC - District 3'] = psc_d3


# Public Service Commission - District 5

tolbert2026 = 'Josh Tolbert (Rep)'
edwards2026 = 'Shelia Edwards (Dem)'

pridemore2018 = 'TRICIA PRIDEMORE (I) (REP)'
randolph2018 = 'DAWN A. RANDOLPH (DEM)'
turpish2018 = 'JOHN TURPISH  (LIB)'

psc_d5 = pd.DataFrame({
    'Previous Winner': {2026: pridemore2018},
    'Previous Runner-up': {2026: randolph2018},
    'Challenger': {2026: edwards2026},
    'Previous Rep': {2026: pridemore2018},
    'Previous Dem': {2026: randolph2018},
    'Previous Lib': {2026: turpish2018},
    'Current Rep': {2026: tolbert2026},
    'Current Dem': {2026: edwards2026},
    'Current Lib': {},
    'Previous Election': {2026: 2018},
    'Race file': 'public_service_commission,_district_5_-_western' # 2025_psc_-_district_3
})

if current_year == 2026:
    race_data['PSC - District 5'] = psc_d5


# Write-ins 

write_ins = pd.DataFrame({
    2022: {'Governor': 7 + 18, 'Secretary of State': 154},
    2018: {'Governor': 81}, # I can't find the full source for write ins
}).fillna(0).astype(int)
# Court data analysis
# James Bennett for Code for C-ville

import pandas as pd
import streamlit as st
import glob
from PIL import Image
import plotly.express as px
from matplotlib import pyplot as plt
import json

st.title('Court Data Analysis in Virginia')
image = Image.open('C:\\Users\\james Bennett\\Desktop\\Code_for_cville\\image\\freedom2.jpg')
json_url = 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json'
pop_url = "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/asrh/cc-est2019-alldata.csv"
st.image(image)


@st.cache(persist=True)
def load_data(folder):
    # Update path to location of the data
    path = 'C:\\Users\\james Bennett\\Desktop\\Code_for_cville\\' + folder
    # Use glob to identify all text files in path
    data_files = glob.glob(path + "/*.csv")
    # Read in each file as csv into Data Frames using pandas
    frame_list = []
    if folder == 'data_circuit':
        columns = ['HearingDate', 'HearingResult', 'HearingJury', 'HearingPlea', 'HearingType', 'HearingRoom',
                   'fips', 'CaseNumber', 'Filed', 'Commencedby', 'Locality', 'Defendant', 'AKA', 'Sex', 'Race', 'DOB',
                   'Address', 'Charge', 'CodeSection', 'ChargeType', 'Class', 'OffenseDate', 'ArrestDate',
                   'DispositionCode',
                   'DispositionDate', 'ConcludedBy', 'AmendedCharge', 'AmendedCodeSection', 'AmendedChargeType',
                   'JailPenitentiary', 'ConcurrentConsecutive', 'LifeDeath', 'SentenceTime', 'SentenceSuspended',
                   'OperatorLicenseSuspensionTime', 'FineAmount', 'Costs', 'FinesCostPaid', 'ProgramType',
                   'ProbationType',
                   'ProbationTime', 'ProbationStarts', 'CourtDMVSurrender', 'DriverImprovementClinic',
                   'DrivingRestrictions',
                   'RestrictionEffectiveDate', 'RestrictionEndDate', 'VAAlcoholSafetyAction', 'RestitutionPaid',
                   'RestitutionAmount', 'Military', 'TrafficFatality', 'AppealedDate', 'AKA2', 'person_id']
    elif folder == 'data_district':
        columms = ['HearingDate', 'HearingResult', 'HearingPlea', 'HearingContinuanceCode', 'HearingType',
                   'HearingCourtroom', 'fips', 'CaseNumber', 'FiledDate', 'Locality', 'Name', 'Status',
                   'DefenseAttorney', 'Address', 'AKA1', 'AKA2', 'Gender', 'Race', 'DOB', 'Charge', 'CodeSection',
                   'CaseType', 'Class', 'OffenseDate', 'ArrestDate', 'Complainant', 'AmendedCharge', 'AmendedCode',
                   'AmendedCaseType', 'FinalDisposition', 'SentenceTime', 'SentenceSuspendedTime', 'ProbationType',
                   'ProbationTime', 'ProbationStarts', 'OperatorLicenseSuspensionTime', 'RestrictionEffectiveDate',
                   'RestrictionEndDate', 'OperatorLicenseRestrictionCodes', 'Fine', 'Costs', 'FineCostsDue',
                   'FineCostsPaid', 'FineCostsPaidDate', 'VASAP', 'FineCostsPastDue', 'person_id']
    for data_file in data_files:
        df = pd.read_csv(data_file, usecols=columns)
        frame_list.append(df)

    df = pd.concat(frame_list, ignore_index=True)
    df.fips = "51" + df.fips.astype(str).str.zfill(3)

    return df


def map_data(df, va_census):
    charge = st.sidebar.selectbox("select the Charge type", df.ChargeType.unique())
    county_pop = va_census[va_census.AGEGRP == 0].set_index('fips')['TOT_POP'].to_dict()
    df = df.loc[df.ChargeType == charge]

    fips_counts = df['fips'].value_counts().reset_index()
    fips_counts.columns = ['fips', 'counts']
    # fips_counts["counts_per_100k"] = fips_counts.apply(lambda row: row.counts / (county_pop[row.fips] / 100000), axis=1)
    import urllib
    response = urllib.request.urlopen(json_url)
    counties = json.loads(response.read())
    st.write("per Virginia County")
    ranker = px.choropleth(fips_counts, geojson=counties, locations='fips', color='counts',
                                          color_continuous_scale='fall',
                                          scope='usa',
                                          labels={'counts_per_100k': 'Cases per 100K'})

    ranker.update_geos(fitbounds = "locations", visible = False)
    ranker.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(ranker)
    tabla = df.groupby('Race')['person_id'].nunique()
    st.write(tabla)


def main():
    cir_df = load_data('data_circuit')
    #####Cencus Data
    va_census = pd.read_csv(pop_url, encoding="latin-1", dtype={"COUNTY": str, "STATE": str})
    va_census = va_census[va_census["STATE"] == 51]
    va_census.COUNTY = va_census.COUNTY.astype(str).str.zfill(3)
    va_census = va_census[va_census.YEAR >= 15]
    va_census['fips'] = va_census.STATE + va_census.COUNTY

    # dist_df = read_files('data_district')
    menu = ["Home", "Search", "Analysis", "About"]
    st.sidebar.subheader(" Pick something")
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == 'Home':
        st.subheader('Home')
    elif choice == 'Search':
        st.subheader('Search')
    elif choice == 'Analysis':
        map_data(cir_df, va_census)
        st.write("""***""")

    elif choice == 'About':
        st.subheader(choice)
    else:
        st.error('Something is wrong')


if __name__ == '__main__':
    main()

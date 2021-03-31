# Court data analysis
# James Bennett for Code for C-ville

import pandas as pd
import streamlit as st
import numpy as np
import glob
from PIL import Image
import plotly.express as px
from matplotlib import pyplot as plt
import json
from datetime import datetime
import streamlit_theme as stt


st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.title('A view of court data in Virginia ')
stt.set_theme({'primary': '#1b3388'})
#st.title('Court Data Analysis in Virginia')
#image = Image.open('C:\\Users\\james Bennett\\Desktop\\Code_for_cville\\image\\freedom2.jpg')
#image2 = Image.open('C:\\Users\\james Bennett\\Desktop\\Code_for_cville\\image\\behind_bars_xsmall.jpg')
#image3 = Image.open('C:\\Users\\james Bennett\\Desktop\\Code_for_cville\\image\\3652284.jpg')
json_url = 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json'
pop_url = "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/asrh/cc-est2019-alldata.csv"


# x1, x2, x3 = st.beta_columns((1, 1, 1))

# with x1:
#   st.image(image3)
# with x2:
#  st.image(image2)
# with x3:
#   st.image(image)


@st.cache(persist=True)
def load_data(folder):
    # Update path to location of the data
    path = 'C:\\Users\\james Bennett\\Desktop\\Code_for_cville\\' + folder
    # Use glob to identify all text files in path
    data_files = glob.glob(path + "/*.csv")
    # Read in each file as csv into Data Frames using pandas
    frame_list = []
    if folder == 'data_circuit':
        columns = ['HearingDate', 'HearingResult', 'HearingJury', 'HearingPlea', 'HearingType',
                   'fips', 'Filed', 'Locality', 'Sex', 'Race',
                   'Charge', 'ChargeType', 'Class', 'OffenseDate', 'ArrestDate',
                   'DispositionCode', 'ConcludedBy', 'AmendedCharge', 'AmendedChargeType',
                   'ConcurrentConsecutive', 'LifeDeath', 'SentenceTime', 'SentenceSuspended',
                   'OperatorLicenseSuspensionTime', 'FineAmount', 'Costs', 'FinesCostPaid',
                   'ProbationType', 'ProbationTime', 'ProbationStarts', 'CourtDMVSurrender', 'DriverImprovementClinic',
                   'RestitutionAmount', 'TrafficFatality', 'AppealedDate', 'person_id']
    elif folder == 'data_district':
        columns = ['HearingDate', 'HearingResult', 'HearingPlea', 'HearingType',
                   'fips', 'FiledDate', 'Locality', 'Name', 'Status',
                   'DefenseAttorney', 'Address', 'AKA1', 'AKA2', 'Gender', 'Race', 'DOB', 'Charge', 'CodeSection',
                   'CaseType', 'Class', 'OffenseDate', 'ArrestDate', 'Complainant', 'AmendedCharge', 'AmendedCode',
                   'AmendedCaseType', 'FinalDisposition', 'SentenceTime', 'SentenceSuspendedTime', 'ProbationType',
                   'ProbationTime', 'ProbationStarts',
                   'OperatorLicenseRestrictionCodes', 'Fine', 'Costs', 'FineCostsDue',
                   'FineCostsPaid', 'FineCostsPaidDate', 'VASAP', 'FineCostsPastDue', 'person_id']
    for data_file in data_files:
        df = pd.read_csv(data_file, usecols=columns)
        frame_list.append(df)

    df = pd.concat(frame_list, ignore_index=True)
    df.fips = "51" + df.fips.astype(str).str.zfill(3)
    ###clean some data

    if folder == 'data_circuit':
        df.Race.replace(['White Caucasian (Non-Hispanic)', 'Black (Non-Hispanic)', 'American Indian'],
                        ['White', 'Black', 'American Indian Or Alaskan Native'], inplace=True)
    elif folder == 'data_district':
        df.Race.replace(['White Caucasian(Non-Hispanic)', 'Black(Non-Hispanic)', 'Unknown (Includes Not Applicable, Unknown)',
                         'Unknown', 'American Indian or Alaskan Native', 'Asian or Pacific Islander', 'American Indian'],
                        ['White', 'Black', 'Other(Includes Not Applicable, Unknown)', 'Other(Includes Not Applicable, Unknown)',
                         'American Indian Or Alaskan Native', 'Asian Or Pacific Islander', 'American Indian Or Alaskan Native'], inplace=True)
    df.SentenceTime = df['SentenceTime'].fillna(0)

    return df


def map_data(df, va_census, option):

    if option == 'Circuit':
        charge = st.sidebar.selectbox("Select the charge type", df.ChargeType.unique())
        df = df.loc[df.ChargeType == charge]
    elif option == "District":
        charge = st.sidebar.selectbox("Select the Case type", df.CaseType.unique())
        df = df.loc[df.CaseType == charge]

    county_pop = va_census[va_census.AGEGRP == 0].set_index('fips')['TOT_POP'].to_dict()

    fips_counts = df['fips'].value_counts().reset_index()
    fips_counts.columns = ['fips', 'counts']

    dfw = df.loc[df.Race == "White"]
    w_fips_counts = dfw['fips'].value_counts().reset_index()
    w_fips_counts.columns = ['fips', 'counts']

    dfb = df.loc[df.Race == "Black"]
    b_fips_counts = dfb['fips'].value_counts().reset_index()
    b_fips_counts.columns = ['fips', 'counts']

    # fips_counts["counts_per_100k"] = fips_counts.apply(lambda row: row.counts / (county_pop[row.fips] / 100000), axis=1)
    import urllib
    response = urllib.request.urlopen(json_url)
    counties = json.loads(response.read())

    ranker = px.choropleth(fips_counts, geojson=counties, locations='fips', color='counts',
                           color_continuous_scale='Viridis',
                           scope='usa',
                           range_color=[0, df.shape[0] / 100],
                           width=500,
                           height=500,
                           basemap_visible=False,
                           labels={'counts_per_100k': 'Cases per 100K'})

    ranker.update_geos(fitbounds="locations", visible=False)
    ranker.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    ranker.update_layout(coloraxis_colorbar=dict(
                         thicknessmode="pixels", thickness=10,
                         lenmode="pixels", len=150,
                         yanchor="top", y=0.8,
                         ticks="outside", ticksuffix=" %",
                         dtick=5, bgcolor='rgba(0,0,0,0)'
                                                )
                        )

    w_ranker = px.choropleth(w_fips_counts, geojson=counties, locations='fips', color='counts',
                             color_continuous_scale='Viridis',
                             scope='usa',
                             range_color=[0, df.shape[0] / 100],
                             width=500,
                             height=500,
                             labels={'counts_per_100k': 'Cases per 100K'})

    w_ranker.update_geos(fitbounds="locations", visible=False)
    w_ranker.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    w_ranker.update_layout(coloraxis_colorbar=dict(
        thicknessmode="pixels", thickness=10,
        lenmode="pixels", len=150,
        yanchor="top", y=0.8,
        ticks="outside", ticksuffix=" %",
        dtick=5
    ))
    b_ranker = px.choropleth(b_fips_counts, geojson=counties, locations='fips', color='counts',
                             color_continuous_scale='Viridis',
                             scope='usa',
                             range_color=[0, df.shape[0] / 100],
                             width=500,
                             height=500,
                             labels={'counts_per_100k': 'Cases per 100K'})

    b_ranker.update_geos(fitbounds="locations", visible=False)
    b_ranker.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    b_ranker.update_layout(coloraxis_colorbar=dict(
        thicknessmode="pixels", thickness=10,
        lenmode="pixels", len=150,
        yanchor="top", y=0.8,
        ticks="outside", ticksuffix=" %",
        dtick=5
    ))

    c1, c2, c3 = st.beta_columns((1, 1, 1))
    with c3:
        st.title("Total # of cases")
        st.plotly_chart(ranker)
    with c2:
        st.title("Black - Not Latino")
        st.plotly_chart(b_ranker)
    with c1:
        st.title("White Caucasian")
        st.plotly_chart(w_ranker)
    tabla = df.groupby('Race')['person_id'].nunique()
    df_tabla = pd.DataFrame([tabla]).T

    total = df_tabla.sum()
    df_tabla['Percentage'] = df_tabla/total
    df_tabla['pop'] = [42678,597486,1698568,836481,273137, 5223737]
    pop_total = df_tabla['pop'].sum()
    df_tabla['Percent_pop'] = df_tabla['pop']/pop_total
    df_tabla.rename(columns={'person_id': 'Count_per'}, inplace= True)
    st.table(df_tabla)


def main():
    cir_df = load_data('data_circuit')
    dist_df = load_data('data_district')
    # st.write(cir_df[['OffenseDate', 'ArrestDate', 'HearingDate','HearingResult']].head(10))
    #####Cencus Data#####
    va_census = pd.read_csv(pop_url, encoding="latin-1", dtype={"COUNTY": str, "STATE": str})
    va_census = va_census[va_census["STATE"] == 51]
    va_census.COUNTY = va_census.COUNTY.astype(str).str.zfill(3)
    va_census = va_census[va_census.YEAR >= 15]
    va_census['fips'] = va_census.STATE + va_census.COUNTY
    ################################################

    menu = ["Home", "District", "Circuit", "About"]
    st.sidebar.subheader("Select Option")
    choice = st.sidebar.selectbox("Court", menu)

    if choice == 'Home':
        st.subheader('Home')
    elif choice == 'District':
        map_data(dist_df, va_census,choice)
        st.write("""***""")
    elif choice == 'Circuit':
        map_data(cir_df, va_census, choice)
        st.write("""***""")

    elif choice == 'About':
        st.subheader(choice)
    else:
        st.error('Something is wrong')


if __name__ == '__main__':
    main()

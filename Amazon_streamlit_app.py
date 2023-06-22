#########################################################################
# Authors: Natalie Eversole and Team members
# Date: 12/08/2022
# Description: This code creates our Amazon book recommender application
#########################################################################

from pandas.core.dtypes.common import is_datetime64_any_dtype, is_numeric_dtype, is_categorical_dtype, is_object_dtype

import streamlit as st
from streamlit_option_menu import option_menu  # pip install streamlit-option-menu
import pandas as pd
from pymongo import MongoClient
import pymongo
import certifi
import numpy as np
import networkx
import matplotlib.pyplot as plt
import seaborn as sns

page_title = "Data Divas\nCPTS415"
page_icon = ":house:"  # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
layout = "wide"

st.set_page_config(page_title=page_title,
                   page_icon=page_icon,
                   layout=layout)
st.title(page_title + " " + page_icon)

# --- HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- NAVIGATION MENU ---
selected = option_menu(
    menu_title=None,
    options=["Data Visualization", "Book Recommender"],
    icons=["pencil-fill", "bar-chart-fill"],
    orientation="horizontal",
)


# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    CONNECTION_STRING = "mongodb+srv://wsu_cpts_415:2022CPTS415@cluster0.owwy0gt.mongodb.net/?retryWrites=true&w=majority"
    return pymongo.MongoClient(CONNECTION_STRING,
                               tlsCAFile=certifi.where())


# Pull data from the collection.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_singleton
def get_mongo_data():
    db = client.CPTS415_PROJECT
    # select the collection within the database
    test = db.BookRecommend
    data = pd.DataFrame(list(test.find()))
    # Delete the "_id" column
    del data['_id']
    return data


def upload_csv_file(file):
    df = pd.read_csv(file)
    return df


def get_collections():
    db = client.CPTS415_PROJECT
    collections = db.products.distinct("group")
    return collections


def get_unique_asin():
    db = client.CPTS415_PROJECT
    ids = db.products.distinct("ASIN")
    ids = ids[0:10]
    return ids


def get_unique_ratings(df_data):
    # returns minimum and maximum
    return np.unique(df_data.AvgRating).tolist()


def get_unique_salesrank(df_data):
    # returns minimum and maximum
    return np.unique(df_data.SalesRank).tolist()


def get_unique_totalreviews(df_data):
    # returns minimum and maximum
    return np.unique(df_data.TotalReviews).tolist()


def filter_ratings(df_data, start_range, end_range):
    df_filtered_ratings = pd.DataFrame()
    ratings_list = np.arange(start_range, end_range + 0.5, 0.5)
    df_filtered_ratings = df_data[df_data['AvgRating'].isin(ratings_list)]
    return df_filtered_ratings


def filter_salesrank(df_data, start_range, end_range):
    df_filtered_ratings = pd.DataFrame()
    ratings_list = np.arange(start_range, end_range + 1.0, 0.5)
    df_filtered_ratings = df_data[df_data['SalesRank'].isin(ratings_list)]
    return df_filtered_ratings


def filter_reviews(df_data, start_range, end_range):
    df_filtered_ratings = pd.DataFrame()
    ratings_list = np.arange(start_range, end_range + 1.0, 0.5)
    df_filtered_ratings = df_data[df_data['TotalReviews'].isin(ratings_list)]
    return df_filtered_ratings


def return_asin_from_book_title(book_title, amazon_dict):
    df = pd.DataFrame.from_dict(amazon_dict, orient='index')
    asin_selection = df.loc[df['Title'] == book_title, 'ASIN'].item()
    return (asin_selection)


def filter_book_titles(amazon_dict):
    df = pd.DataFrame.from_dict(amazon_dict, orient='index')
    df2 = df.loc[(df['AvgRating'] >= 4.0) & (df['TotalReviews'] >= 1) & (df['DegreeCentrality'] >= 100) & (
            df['ClusteringCoeff'] >= 0.1)]
    book_list = df2['Title'].unique()
    return list(book_list)


@st.experimental_singleton
def read_book_recommender_data():
    # Read the data
    fhr = open('amazon-books.txt', 'r', encoding='utf-8', errors='ignore')
    amazonBooks = {}
    fhr.readline()
    for line in fhr:
        cell = line.split('\t')
        MetaData = {}
        MetaData['Id'] = cell[0].strip()
        ASIN = cell[1].strip()
        MetaData['ASIN'] = ASIN
        MetaData['Title'] = cell[2].strip()
        MetaData['Categories'] = cell[3].strip()
        MetaData['Group'] = cell[4].strip()
        MetaData['Copurchased'] = cell[5].strip()
        MetaData['SalesRank'] = int(cell[6].strip())
        MetaData['TotalReviews'] = int(cell[7].strip())
        MetaData['AvgRating'] = float(cell[8].strip())
        MetaData['DegreeCentrality'] = int(cell[9].strip())
        MetaData['ClusteringCoeff'] = float(cell[10].strip())
        amazonBooks[ASIN] = MetaData
    fhr.close()

    # Read the data from node edge list
    fhr = open("amazon-books-copurchase.edgelist", "rb")
    copurchaseGraph = networkx.read_weighted_edgelist(fhr)
    fhr.close()
    return (amazonBooks, copurchaseGraph)


def find_top_book_recommend(userASIN, amazonBooks, copurchaseGraph):
    st.write("Looking for Recommendations for ASIN user purchasing a Book:")
    st.write("ASIN = ", userASIN)
    st.write("Title = ", amazonBooks[userASIN]['Title'])
    st.write("SalesRank = ", amazonBooks[userASIN]['SalesRank'])
    st.write("TotalReviews = ", amazonBooks[userASIN]['TotalReviews'])
    st.write("AvgRating = ", amazonBooks[userASIN]['AvgRating'])

    # Get the depth-1 ego network of userASIN from copurchaseGraph
    n = userASIN
    ego = networkx.ego_graph(copurchaseGraph, n, radius=1)
    userASINEgoGraph = networkx.Graph(ego)
    pos = networkx.layout.spring_layout(userASINEgoGraph)
    M = userASINEgoGraph.number_of_edges()
    nodes = networkx.draw_networkx_nodes(userASINEgoGraph, pos, node_size=50, node_color='blue')
    edges = networkx.draw_networkx_edges(userASINEgoGraph, pos, node_size=50, edge_cmap=plt.cm.Blues, width=2,
                                         alpha=0.1)

    threshold = 0.5
    userASINEgoTrimGraph = networkx.Graph()
    for f, t, e in userASINEgoGraph.edges(data=True):
        if e['weight'] >= threshold:
            userASINEgoTrimGraph.add_edge(f, t, weight=e['weight'])
    pos = networkx.layout.spring_layout(userASINEgoTrimGraph)
    M = userASINEgoTrimGraph.number_of_edges()
    nodes = networkx.draw_networkx_nodes(userASINEgoTrimGraph, pos, node_size=50, node_color='blue', label=True)
    edges = networkx.draw_networkx_edges(userASINEgoTrimGraph, pos, node_size=50, edge_cmap=plt.cm.Blues, width=2,
                                         alpha=0.1)

    # Get the list of nodes connected to the userASIN
    userASINNeighbours = userASINEgoTrimGraph.neighbors(userASIN)

    # Get Top Five book recommendations
    AsMeta = []
    for asin in userASINNeighbours:
        ASIN = asin
        Title = amazonBooks[asin]['Title']
        SalesRank = amazonBooks[asin]['SalesRank']
        TotalReviews = amazonBooks[asin]['TotalReviews']
        AvgRating = amazonBooks[asin]['AvgRating']
        DegreeCentrality = amazonBooks[asin]['DegreeCentrality']
        ClusteringCoeff = amazonBooks[asin]['ClusteringCoeff']
        AsMeta.append((ASIN, Title, SalesRank, TotalReviews, AvgRating, DegreeCentrality, ClusteringCoeff))

    # Sorting the top five nodes by Average Rating then by TotalReviews
    T5_byAvgRating_then_byTotalReviews = sorted(AsMeta, key=lambda x: (x[4], x[3]), reverse=True)[:5]

    # Print Top 5 Recommendations
    st.write('Top 5 Recommended Books for selected user:')
    for asin in T5_byAvgRating_then_byTotalReviews:
        st.write(asin)


client = init_connection()
productsdata = get_mongo_data()

AmazonBooks, GraphData = read_book_recommender_data()
book_list = filter_book_titles(AmazonBooks)

####################
### INTRODUCTION ###
####################
row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns((.1, 2.3, .1, 1.3, .1))
with row0_1:
    st.title('Amazon - Copurchasing Data Analyzer')
with row0_2:
    st.text("")
    st.subheader('Running with Streamlit App')

row3_spacer1, row3_1, row3_spacer2 = st.columns((.1, 3.2, .1))
with row3_1:
    st.markdown(
        "Hello fellow CPTSD415 mates! Have you ever purchased items on Amazon and wanted to know how it ranks and what books to recommend? This site will aid you in this adventure ")
    st.markdown("You can find the source code in the [Data Diva's GitHub Repository](https://github.com/spetersen)")
    st.markdown("If you are interested in how this app was developed, reach out to any of the Data Diva masters")

#################
### SELECTION ###
#################
if selected == "Data Visualization":
    st.sidebar.empty()
    st.header("Data Visulization")
    st.sidebar.text('')
    st.sidebar.text('')
    st.sidebar.text('')
    unique_avgrating = get_unique_ratings(productsdata)
    unique_salesrank = get_unique_salesrank(productsdata)
    unique_reviews = get_unique_totalreviews(productsdata)

    st.sidebar.markdown("**First select the data range you want to analyze:** 👇")
    selected_rating = st.sidebar.select_slider('Select the average rating', unique_avgrating,
                                               value=[min(unique_avgrating), max(unique_avgrating)])
    df_data_filtered_rating = filter_ratings(productsdata, selected_rating[0], selected_rating[1])

    selected_salesrank = st.sidebar.select_slider('Select the average sales ranking', unique_salesrank,
                                                  value=[min(unique_salesrank), max(unique_salesrank)])
    df_data_filtered_sales = filter_salesrank(df_data_filtered_rating, selected_salesrank[0], selected_salesrank[1])

    selected_reviews = st.sidebar.select_slider('Select the average reviews', unique_reviews,
                                                value=[min(unique_reviews), max(unique_reviews)])
    df_data_filtered_reviews = filter_salesrank(df_data_filtered_rating, selected_reviews[0], selected_reviews[1])

    # Metric Visualizations #
    fig = plt.figure(figsize=(10, 5))
    sns.countplot(x='AvgRating', data=df_data_filtered_rating)
    st.pyplot(fig)

    fig4 = sns.relplot(data=df_data_filtered_rating, x="SalesRank", y="TotalReviews")
    st.pyplot(fig4)

    fig5 = sns.relplot(data=df_data_filtered_rating, x="AvgRating", y="TotalReviews")
    st.pyplot(fig5)

    ### SEE DATA ###
    row6_spacer1, row6_1, row6_spacer2 = st.columns((.2, 7.1, .2))
    with row6_1:
        st.subheader("Currently selected data:")

    row2_spacer1, row2_1 = st.columns((.2, 1.6))
    with row2_1:
        unique_items_in_df = df_data_filtered_rating['Id'].count()
        str_items = "🏟️ " + str(unique_items_in_df) + " Items"
        st.markdown(str_items)

    row3_spacer1, row3_1, row3_spacer2 = st.columns((.2, 7.1, .2))
    with row3_1:
        st.markdown("")
        see_data = st.expander('You can click here to see the raw data first 👉')
        with see_data:
            st.dataframe(data=df_data_filtered_reviews.reset_index(drop=True))
    st.text('')

if selected == "Book Recommender":
    st.sidebar.empty()
    # Read book recommender files
    AmazonBooks, GraphData = read_book_recommender_data()
    # book_list = filter_book_titles(AmazonBooks)

    st.header("Book Recommender")
    st.sidebar.text('Book Recommender')
    # number = st.text_input('Insert the users ASIN', help='Enter Amazon ASIN #')
    # number = st.sidebar.text_input('Enter the users ASIN #')
    book_title = st.sidebar.selectbox('Enter the name of a book to find recommendations', book_list)

    if book_title:
        asin_return = return_asin_from_book_title(book_title, AmazonBooks)
        # st.write(asin_return)
        find_top_book_recommend(asin_return, AmazonBooks, GraphData)

import streamlit as st
import pandas as pd
import time
from google.cloud import firestore
from google.oauth2 import service_account

# Keys
import json
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)

# Set Collection and shortcuts
dbNames = db.collection("movies")
sidebar = st.sidebar
placeholder = st.empty()

# Title
st.header("Netflix app")

# Prepare main dataframe
@st.cache_data
def get_df():
  movies_ref = list(db.collection(u'movies').stream())
  movies_dict = list(map(lambda x: x.to_dict(), movies_ref))
  st.success("Done! (using st.cache)")
  return pd.DataFrame(movies_dict)

movies_dataframe = get_df()

# Full df visibility
fullView = sidebar.checkbox("Mostrar todos los filmes")
if fullView:
  printDF = st.dataframe(movies_dataframe)

# Search by title
nameSearch = sidebar.text_input("Título del filme:")
btnSearch = sidebar.button("Buscar filmes")

if btnSearch:
 doc = movies_dataframe[movies_dataframe["name"].str.contains(nameSearch.title())]
 if len(doc) == 0:
  sidebar.write("Sin resultados")
 else:
  printDF = st.dataframe(doc)
  sidebar.write(f"Filmes encontrados: {len(doc)}")

# Filter by director
selectFilter = sidebar.selectbox(
    "Seleccionar director",
    movies_dataframe['director'].unique(),
    index = None,
    placeholder = ""
)
btnFilter = sidebar.button("Filtrar director")

if btnFilter:
 doc = movies_dataframe[movies_dataframe["director"].str.contains(selectFilter)]
 printDF = st.dataframe(doc)
 sidebar.write(f"Filmes encontrados: {len(doc)}")

# New entry
st.sidebar.markdown("""---""")
sidebar.subheader("Nuevo filme")

nameSet = sidebar.text_input("Name")
compSelect = sidebar.selectbox(
    "Company",
    movies_dataframe['company'].unique()
)
dirSelect = sidebar.selectbox(
    "Director",
    movies_dataframe['director'].unique()
)
gnrSelect = sidebar.selectbox(
    "Genre",
    movies_dataframe['genre'].unique()
)

submit = sidebar.button("Crear un nuevo filme")

# Upload to database
if nameSet and compSelect and dirSelect and gnrSelect and submit:
 new_movie = {"company": compSelect,
              "director": dirSelect,
              "genre": gnrSelect,
              "name": nameSet}
 update_time, movie_ref = db.collection("movies").add(new_movie)
 sidebar.write("Filme añadido correctamente")
 get_df.clear()
 st.rerun()

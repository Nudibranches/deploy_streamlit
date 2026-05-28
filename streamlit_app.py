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
  with placeholder:
    sidebar.write("Sin resultados")
    time.sleep(2)
    st.empty()
 else:
  printDF = st.dataframe(doc)
  with placeholder:
    sidebar.write(f"Filmes encontrados: {len(doc)}")
    time.sleep(2)
    st.empty()

# Filter by director
def loadByDirector(name):
 names_ref = dbNames.where(u'director', u'==', name)
 currentName = None
 for myname in names_ref.stream():
  currentName = myname
 return currentName

selectFilter = sidebar.selectbox(
    "Seleccionar director",
    movies_dataframe['director'].unique(),
    index = None,
    placeholder = ""
)
btnFilter = sidebar.button("Filtrar director")

if btnFilter:
 doc = loadByDirector(selectFilter)
 st.write(doc.to_dict())

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
 doc_ref = db.collection("movies").document(nameSet)
 doc_ref.set({
     "company": compSelect,
     "director": dirSelect,
     "genre": gnrSelect,
     "name": nameSet
 })
 st.sidebar.write("Filme añadido correctamente")

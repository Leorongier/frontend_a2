import streamlit as st
import requests
import pandas as pd

# Configure the Streamlit page layout to utilize a wider area of the browser
st.set_page_config(layout="wide")

# Function to fetch movies from the Flask backend server
def fetch_movies():
    backend_url = 'https://backend-service-a2-62asncaisq-oa.a.run.app//load_movies'
    response = requests.get(backend_url)
    return pd.DataFrame(response.json()) if response.status_code == 200 else st.error('Failed to fetch movies from the backend.')

# Function to fetch movie details from the Flask backend using TMDB ID
def fetch_movie_details(tmdb_id):
    backend_url = backend_url = f'https://backend-service-a2-62asncaisq-oa.a.run.app/movie_details?tmdb_id={tmdb_id}'

    response = requests.get(backend_url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error('Failed to fetch movie details from the backend.')
        return None

# Function to fetch recommendations for a user from the Flask backend
def fetch_recommendations(user_id):
    backend_url = f'https://backend-service-a2-62asncaisq-oa.a.run.app/recommendations?user_id={user_id}'
    response = requests.get(backend_url)
    if response.status_code == 200:
        return pd.read_json(response.text)
    else:
        st.error("Error during recommendation retrieval: " + response.text)
        return pd.DataFrame()

# Function to fetch search results from the Flask backend based on a user query
@st.cache(ttl=600, show_spinner=False)
def fetch_search_results(query):
    response = requests.get(f"https://backend-service-a2-62asncaisq-oa.a.run.app/search?q={query}")
    if response.status_code == 200:
        return response.json()  # Return the search results
    else:
        st.error("Failed to fetch search results")
        return []

# Initialize or fetch the list of movies in the watch list from session state
if 'watch_list' not in st.session_state:
    st.session_state['watch_list'] = []

# Sidebar for maintaining a personal watch list
with st.sidebar:
    st.title("🎬 My Watch List")
    for movie in st.session_state['watch_list']:
        with st.expander(f"{movie['title']}"):
            st.write(f"Genres: {movie['genres']}")

# Main area for movie search
st.title("🔍 Search a Movie")
query = st.text_input("Type a movie title to search:", key="search_query")
if query:
    search_results = fetch_search_results(query)
    if search_results:
        selected_title = st.selectbox("Search Results:", [movie['title'] for movie in search_results])
        selected_movie = next((movie for movie in search_results if movie['title'] == selected_title), None)
        if selected_movie:
            st.image(selected_movie.get('poster_path', ''), caption='Movie Poster')
            st.write(f"Title: {selected_movie['title']}")
            st.write(f"Genres: {selected_movie.get('genres', 'Unknown')}")
            st.write(f"Overview: {selected_movie.get('overview', 'No description available.')}")
            if st.button("➕ Add to Watch List", key=f"add-{selected_movie['movieId']}"):
                if selected_movie not in st.session_state['watch_list']:
                    st.session_state['watch_list'].append(selected_movie)

# Recommendations section, displaying suggested movies for a user
st.title("🌟 Movies Recommendations")
user_id = 123  # Fixed user ID for demonstration, adjust as necessary
recommendations = fetch_recommendations(user_id)
if not recommendations.empty:
    st.write("Recommendations found:")
    st.write(recommendations)
else:
    st.write("No recommendations found or there was an error fetching them.")
import streamlit as st
import requests
import pandas as pd

# Configure the Streamlit page layout to utilize a wider area of the browser
st.set_page_config(layout="wide")

# Function to fetch movies from the Flask backend server
@st.cache_data(ttl=600, show_spinner=False)
def fetch_movies():
    backend_url = 'https://backend-a2-2-62asncaisq-oa.a.run.app/load_movies'
    response = requests.get(backend_url)
    return pd.DataFrame(response.json()) if response.status_code == 200 else None

# Function to fetch movie details from the Flask backend using TMDB ID
@st.cache_data(ttl=600, show_spinner=False)
def fetch_movie_details(tmdb_id):
    backend_url = f'https://backend-a2-2-62asncaisq-oa.a.run.app/movie_details?tmdb_id={tmdb_id}'
    response = requests.get(backend_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to fetch search results from the Flask backend based on a user query
@st.cache_data(ttl=600, show_spinner=False)
def fetch_search_results(query):
    backend_url = f"https://backend-a2-2-62asncaisq-oa.a.run.app/search?q={query}"
    response = requests.get(backend_url)
    return response.json() if response.status_code == 200 else []

# Initialize or fetch the list of movies in the watch list from session state
if 'watch_list' not in st.session_state:
    st.session_state['watch_list'] = []

with st.sidebar:
    st.title("🎬 My Watch List")
    # On crée une copie pour itérer car nous allons modifier la liste originale en cas de suppression
    for movie in st.session_state['watch_list'][:]:
        with st.expander(f"{movie['title']}"):
            st.write(f"Genres: {movie['genres']}")
            if st.button(f"Retirer de la Watch List", key=f"remove-{movie['movieId']}"):
                # Supprimer le film de la liste de surveillance
                st.session_state['watch_list'].remove(movie)
                st.experimental_rerun()  # Relancer le script pour mettre à jour la sidebar

# Main area for movie search
st.title("🔍 Search a Movie")
query = st.text_input("Type a movie title to search:", key="search_query")
if query:
    search_results = fetch_search_results(query)
    if search_results:
        selected_title = st.selectbox("Search Results:", [movie['title'] for movie in search_results])
        selected_movie = next((movie for movie in search_results if movie['title'] == selected_title), None)
        if selected_movie:
            # Check if there is a valid poster path. If not, display a placeholder or message.
            poster_path = selected_movie.get('poster_path')
            if poster_path:
                st.image(poster_path, caption='Movie Poster')
            else:
                st.write("No poster available for this movie.")

            st.write(f"Title: {selected_movie['title']}")
            st.write(f"Genres: {selected_movie.get('genres', 'Unknown')}")
            st.write(f"Overview: {selected_movie.get('overview', 'No description available.')}")
            # Add to watch list button
            if st.button("➕ Add to Watch List", key=f"add-{selected_movie['movieId']}"):
                if selected_movie not in st.session_state['watch_list']:
                    st.session_state['watch_list'].append(selected_movie)

# Recommendations section, displaying suggested movies for a user
st.title("🌟 Movie Recommendations")

@st.cache_data(ttl=600, show_spinner=False)
def get_recommendations_from_backend(preferred_movies):
    backend_url = 'https://backend-a2-2-62asncaisq-oa.a.run.app/recommendations'
    response = requests.post(backend_url, json={'preferred_movies': preferred_movies})
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch recommendations: {}".format(response.text))
        return []

# Fetch recommendations when user clicks the button
if st.button("Get Recommendations"):
    preferred_movies = [movie['movieId'] for movie in st.session_state['watch_list']]
    recommendations = get_recommendations_from_backend(preferred_movies)

    if recommendations:
        st.write("Recommendations based on your watchlist:")
        # Display each recommended movie with details and poster
        for movie_rec in recommendations:
            movie_details = fetch_movie_details(movie_rec['movieId'])
            if movie_details and 'poster_path' in movie_details and 'title' in movie_details:
                poster_url = f"https://image.tmdb.org/t/p/w500{movie_details['poster_path']}"
                st.image(poster_url, caption=movie_details['title'])
                st.caption(movie_details['title'])  # This line adds the movie title below the poster
            else:
                st.write(f"No poster available for movie ID {movie_rec['movieId']}.")
    else:
        st.write("No recommendations found or there was an error fetching them.")

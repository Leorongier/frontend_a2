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
    backend_url = 'https://backend-a2-2-62asncaisq-oa.a.run.app/search'
    response = requests.get(backend_url, params={'q': query})
    if response.status_code == 200:
        return response.json()
    else:
        st.error('Failed to fetch search results.')
        return []

# Initialize or fetch the list of movies in the watch list from session state
if 'watch_list' not in st.session_state:
    st.session_state['watch_list'] = []

with st.sidebar:
    st.title("🎬 My Watch List")
    for movie in st.session_state['watch_list'][:]:
        with st.expander(f"{movie['title']}"):
            st.write(f"Genres: {movie['genres']}")
            if st.button(f"Retirer de la Watch List", key=f"remove-{movie['movieId']}"):
                st.session_state['watch_list'].remove(movie)
                st.experimental_rerun() 

# Main area for movie search
st.title("🔍 Search a Movie")
query = st.text_input("Type a movie title to search:", key="search_query")

# Display the search results as a selectbox with movie titles
if query:
    search_results = fetch_search_results(query)
    if search_results:
        movie_titles = [movie['title'] for movie in search_results]
        selected_title = st.selectbox("Select a movie:", movie_titles)
        if movie_titles:
            selected_title = st.selectbox("Select a movie:", movie_titles)
            selected_movie = next((movie for movie in search_results if movie['title'] == selected_title), None)
            if selected_movie and selected_movie.get('poster_path'):
                st.image(selected_movie['poster_path'], caption=selected_movie['title'])
                st.write(f"Genres: {selected_movie.get('genres', 'Unknown')}")
                st.write(f"Overview: {selected_movie.get('overview', 'No description available.')}")
                if st.button("➕ Add to Watch List", key=f"add-{selected_movie['movieId']}"):
                    if selected_movie not in st.session_state.watch_list:
                        st.session_state.watch_list.append(selected_movie)
        else:
            st.write("No movies found.")
    else:
        st.write("Start typing to search for movies...")

# Recommendations section, displaying suggested movies for a user
st.title("🌟 Movie Recommendations")

@st.cache_data(ttl=600, show_spinner=False)
def get_recommendations_from_backend(preferred_movies):
    backend_url = 'http://127.0.0.1:5000/recommendations'
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

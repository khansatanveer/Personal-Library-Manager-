# Import necessary libraries
import streamlit as st  # Web app framework
import pandas as pd     # Data manipulation
import json             # For saving/loading data
import os               # File path handling
from datetime import datetime  # For timestamps
import time             # To delay actions if needed
import random           # (Unused but imported)
import plotly.express as px     # For visualizations
import plotly.graph_objects as go
from streamlit_lottie import st_lottie  # To load Lottie animations
import requests         # For making HTTP requests

# -------------------- PAGE SETUP --------------------
# Set basic configuration for the Streamlit page
st.set_page_config(
    page_title="Personal Library Manager",
    page_icon="📚✨", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# -------------------- CUSTOM CSS --------------------
# Injecting custom styles into the app using markdown
st.markdown("""
<style>
...  # Styles omitted for brevity, but includes styling for headers, cards, badges, buttons, etc.

/* Set the background image for the entire page */
   [data-testid="stAppViewContainer"] > .main {
        background-image: url('https://your-image-url.com/path-to-image.jpg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- LOAD LOTTIE FUNCTION --------------------
# Function to fetch Lottie animation from a URL
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# -------------------- SESSION STATE INITIALIZATION --------------------
# Initialize session state variables if not already set
if 'library' not in st.session_state:
    st.session_state.library = []

if 'search_results' not in st.session_state:
    st.session_state.search_results = []

if 'book_added' not in st.session_state:
    st.session_state.book_added = False

if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False

if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

# -------------------- LIBRARY LOAD & SAVE FUNCTIONS --------------------
# Load existing library data from JSON file
def load_library():
    try:
        if os.path.exists("library.json"):
            with open("library.json", "r") as file:
                st.session_state.library = json.load(file)
                return True
        return False
    except Exception as e:
        st.error(f"An error occurred while loading the library. {e}")
        return False

# Save current library data to JSON file
def save_library():
    try:
        with open("library.json", "w") as file:
            json.dump(st.session_state.library, file)
        return True
    except Exception as e:
        st.error(f"An error occurred while saving the library. {e}")
        return False

# -------------------- BOOK MANAGEMENT FUNCTIONS --------------------
# Add a book to the library
def add_book(title, author, publication_year, genre, read_status, pages):
    book = {
        "title": title,
        "author": author,
        "publication_year": publication_year,
        "genre": genre,
        "read_status": read_status,
        "pages": pages,
        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(1)  # Short delay for UX smoothness

# Remove a book from the library by index
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

# Search books based on title, author, or genre
def search_books(search_term, search_by):
    search_term = search_term.lower()
    results = []

    for book in st.session_state.library:
        if search_by == "Title" and search_term in book["title"].lower():
            results.append(book)
        elif search_by == "Author" and search_term in book["author"].lower():
            results.append(book)
        elif search_by == "Genre" and search_term in book["genre"].lower():
            results.append(book)
    
    st.session_state.search_results = results

# -------------------- LIBRARY STATISTICS --------------------
# Generate statistics for visualization
def get_library_status():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book["read_status"])
    percentage = (read_books / total_books) * 100 if total_books > 0 else 0

    genres, authors, decades = {}, {}, {}

    for book in st.session_state.library:
        # Genre count
        genres[book["genre"]] = genres.get(book["genre"], 0) + 1
        # Author count
        authors[book["author"]] = authors.get(book["author"], 0) + 1
        # Decade count
        decade = (book["publication_year"] // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1

    return {
        "total_books": total_books,
        "read_books": read_books,
        "percentage": percentage,
        "genres": dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)),
        "authors": dict(sorted(authors.items(), key=lambda x: x[1], reverse=True)),
        "decades": dict(sorted(decades.items(), key=lambda x: x[0], reverse=True))
    }

# -------------------- VISUALIZATIONS --------------------
# Create and display charts using Plotly
def create_visulations(status):
    if status["total_books"] > 0:
        # Pie chart for read status
        fig_read_status = go.Figure(data=[go.Pie(
            labels=["Read", "Not Read"], 
            values=[status["read_books"], status["total_books"] - status["read_books"]],
            hole=0.3,
            marker_colors=["#10B981", "#F87171"]
        )])
        fig_read_status.update_layout(title="Read vs Not Read Books", height=400)
        st.plotly_chart(fig_read_status, use_container_width=True)

        # Bar chart for genres
        if status['genres']:
            genres_df = pd.DataFrame({'Genre': list(status['genres'].keys()), 'Count': list(status['genres'].values())})
            fig_genres = px.bar(genres_df, x='Genre', y='Count', color='Count', color_continuous_scale=px.colors.sequential.Blues)
            fig_genres.update_layout(title="Books by Genre", height=400)
            st.plotly_chart(fig_genres, use_container_width=True)

        # Line chart for decades
        if status['decades']:
            decades_df = pd.DataFrame({'Decade': [f"{dec}s" for dec in status['decades'].keys()], 'Count': list(status['decades'].values())})
            fig_decades = px.line(decades_df, x='Decade', y='Count', markers=True, line_shape="spline")
            fig_decades.update_layout(title="Books by Publication Decade", height=400)
            st.plotly_chart(fig_decades, use_container_width=True)

# -------------------- MAIN UI --------------------
# Load the library on app start
load_library()

# Sidebar navigation menu
st.sidebar.markdown("<h1 style='text-align: center;'>Navigation</h1>", unsafe_allow_html=True)

# Load Lottie animation
lottie_book = load_lottie_url("https://assets9.lottiefiles.com/temp/lf20_aKAfIn.json")
if lottie_book:
    with st.sidebar:
        st_lottie(lottie_book, width=200, height=200, key="book_animation")

# Navigation radio buttons
nav_options = st.sidebar.radio("Choose option", ["View Library", "Add Book", "Search Books", "Library Statistics"])
st.session_state.current_view = {
    "View Library": "library",
    "Add Book": "add",
    "Search Books": "search",
    "Library Statistics": "status"
}[nav_options]

# Main header
st.markdown("<h1 class='main-header'> PERSONAL LIBRARY MANAGER </h1>", unsafe_allow_html=True)

# -------------------- ADD BOOK VIEW --------------------
if st.session_state.current_view == "add":
    st.markdown("<h2 class='sub-header'> Add a new book </h2>", unsafe_allow_html=True)

    with st.form("add_book_form"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Book Title", max_chars=100)
            author = st.text_input("Author", max_chars=100)
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1, value=datetime.now().year)

        with col2:
            genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science Fiction", "Fantasy", "Mystery", "Thriller", "Romance", "Biography", "Autobiography", "Self-Help", "Historical Fiction", "Young Adult", "Children's", "Poetry", "Graphic Novel", "Others"])
            read_status = st.radio("Read Status", ["Read", "Not Read"], horizontal=True)
            read_bool = read_status == "Read"
            pages = st.number_input("Pages", min_value=1, max_value=10000, step=1, value=100)

        submit_button = st.form_submit_button(label="Add Book")

    if submit_button and title and author:
        add_book(title, author, publication_year, genre, read_bool, pages)

    if st.session_state.get("book_added"):
        st.markdown("<div class='success'> Book added successfully! </div>", unsafe_allow_html=True)
        st.balloons()
        st.session_state.book_added = False
        st.session_state.current_view = "library"

# Display the header for the library view
st.markdown("<h2 class = 'sub-header'> YOUR LIBRARY </h2>", unsafe_allow_html=True)

# Check if the library is empty
if not st.session_state.library:
    st.markdown("<div class='warning'> Your library is empty. Add a book to get started! </div>", unsafe_allow_html=True)
else:
    cols = st.columns(2)  # Display books in two columns
    for i, book in enumerate(st.session_state.library):
        with cols[i % 2]:  # Alternate books between two columns
            
            st.markdown(f"""
            <div style="background: linear-gradient(to right, #f9fafb, #f3f4f6); 
            border-radius: 1rem; 
            padding: 1.5rem; 
            margin-bottom: 1rem; 
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); 
            border-left: 5px solid {'#10b981' if book.get('read_status', False) else '#ef4444'};">
    <h3 style="margin: 0; font-size: 1.5rem; font-weight: bold; color: #111827;">📖 {book.get('title', 'Unknown Title')}</h3>
    <p style="margin: 0.5rem 0;"><strong>👤 Author:</strong> {book.get('author', 'Unknown')}</p>
    <p style="margin: 0.5rem 0;"><strong>🏷️ Genre:</strong> {book.get('genre', 'Unknown')}</p>
    <p style="margin: 0.5rem 0;"><strong>📅 Year:</strong> {book.get('publication_year', 'N/A')}</p>
    <p style="margin: 0.5rem 0;"><strong>📄 Pages:</strong> {book.get('pages', 'N/A')}</p>
    <p style="margin: 0.5rem 0;">
        <span style="padding: 0.2rem 0.6rem; 
                     border-radius: 9999px; 
                     background-color: {'#dcfce7' if book.get('read_status', False) else '#fee2e2'}; 
                     color: {'#15803d' if book.get('read_status', False) else '#b91c1c'}; 
                     font-weight: 600; 
                     font-size: 0.875rem;">
            {"✔️ Read" if book.get("read_status", False) else "❌ Not Read"}
        </span>
    </p>
    <p style="font-size: 0.85rem; color: #6b7280;">🕒 Added on: {book.get('date_added', 'N/A')}</p>
</div>
""", unsafe_allow_html=True)
            
            # Add Remove and Toggle Read Status buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Remove Book", key=f"remove_{i}", use_container_width=True):
                    if remove_book(i):  # Remove the book and rerun app
                        st.rerun()
            with col2:
                new_status = not book["read_status"]  # Toggle read status
                status_lable = "Mark as Read" if not book["read_status"] else "Mark as Not Read"
                if st.button(status_lable, key=f"status_{i}", use_container_width=True):
                    st.session_state.library[i]["read_status"] = new_status
                    save_library()  # Save the updated status
                    st.rerun()

# Show a success message if a book was removed
if st.session_state.get("book_removed"):
    st.markdown("<div class='success-message'> Book removed successfully! </div>", unsafe_allow_html=True)
    st.session_state.book_removed = False  # Reset flag

# ================= SEARCH BOOKS VIEW =================
if st.session_state.current_view == "search":
    st.markdown("<h2 class='sub-header'> Search Books </h2>", unsafe_allow_html=True)

    # Dropdown to choose search field
    search_by = st.selectbox("Search by:", ["Title", "Author", "Genre"])
    search_term = st.text_input("Search term")

    if st.button("Search", use_container_width=True):
        if search_term:
            with st.spinner("Searching..."):
                search_books(search_term, search_by)  # Perform search

            # Display search results
            if hasattr(st.session_state, "search_results"):
                if st.session_state.search_results:
                    st.markdown(f"<h3>Found {len(st.session_state.search_results)} result(s):</h3>", unsafe_allow_html=True)

                    for book in st.session_state.search_results:
                        st.markdown(f"""
                            <div class='book-card'>
                                <h3>{book['title']}</h3>
                                <p><strong>Author:</strong> {book['author']}</p>
                                <p><strong>Genre:</strong> {book['genre']}</p>
                                <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                                <p><strong>Pages:</strong> {book['pages']}</p>
                                <p><span class='read-badge'>
                                    {"Read" if book["read_status"] else "Not Read"}
                                </span></p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("<div class='warning-message'> No book found matching your search. </div>", unsafe_allow_html=True)

# ================= LIBRARY STATISTICS VIEW =================
elif st.session_state.current_view == "status":
    st.markdown("<h2 class='sub-header'> Library Statistics </h2>", unsafe_allow_html=True)

    if not st.session_state.library:
        st.markdown("<div class='warning-message'> Your library is empty. Add some books to see statistics! </div>", unsafe_allow_html=True)
    else:
        stats = get_library_status()  # Retrieve statistics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Books", stats["total_books"])
        with col2:
            st.metric("Read Books", stats["read_books"])
        with col3:
            st.metric("Percentage Read", f"{stats['percentage']:.1f}%")

        # Create plots and charts using Plotly
        create_visualizations(stats)  

        # Display top authors
        if stats['authors']:
            st.markdown("<h3> Top Authors </h3>", unsafe_allow_html=True)
            top_authors = dict(list(stats['authors'].items())[:5])  # Show top 5
            for author, count in top_authors.items():
                st.markdown(f"**{author}**: {count} book{'s' if count > 1 else ''}")

# ================= FOOTER =================
st.markdown("---")
st.markdown("Copyright © 2025 Khansa TanveerAhmed — Personal Library Manager", unsafe_allow_html=True)


import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu  

st.set_page_config(page_title="Personal Library Manager", page_icon="📚", layout="wide")

LIBRARY_FILE = "library.json"

st.markdown("""
    <style>
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border radius: 5 pixels;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .stTextInput input {
        border-radius: 5px;
        padding: 10px;
    }
    .stRadio label {
        font-size: 16px;
    }
    .stHeader {
        font-size: 24px;
        font-weight: bold;
        color: #4CAF50;
    }
    .book-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .book-card h3 {
        margin: 0;
        font-size: 20px;
        color: #4CAF50;
    }
    .book-card p {
        margin: 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def load_library():
    if os.path.exists(LIBRARY_FILE):
        with open(LIBRARY_FILE, "r") as file:
            library = json.load(file)
            for book in library:
                if "read_status" not in book:
                    book["read_status"] = False  
            return library
    return []

def save_library(library):
    with open(LIBRARY_FILE, "w") as file:
        json.dump(library, file)

def add_book(library):
    st.subheader("📖 Add a Book")
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Title", placeholder="Enter the book title")
        author = st.text_input("Author", placeholder="Enter the author's name")
    with col2:
        year = st.number_input("Publication Year", min_value=1800, max_value=2100, step=1)
        genre = st.text_input("Genre", placeholder="Enter the genre")
    read_status = st.radio("Have you read this book?", ("Yes", "No"), index=1)
    
    if st.button("➕ Add Book"):
        if title and author and genre:
            book = {
                "title": title,
                "author": author,
                "year": int(year),
                "genre": genre,
                "read_status": read_status == "Yes"
            }
            library.append(book)
            save_library(library)
            st.success("✅ Book added successfully!")
        else:
            st.error("❌ Please fill in all fields.")

def remove_book(library):
    st.subheader("🗑️ Remove a Book")
    title_to_remove = st.text_input("Enter the title of the book to remove", placeholder="Enter the book title")
    
    if st.button("➖ Remove Book"):
        initial_count = len(library)
        library[:] = [book for book in library if book["title"].lower() != title_to_remove.lower()]
        if len(library) < initial_count:
            save_library(library)
            st.success("✅ Book removed successfully!")
        else:
            st.error("❌ Book not found.")

def search_book(library):
    st.subheader("🔍 Search for a Book")
    search_option = st.radio("Search by:", ("Title", "Author"))
    search_query = st.text_input(f"enter the {search_option.lower()} to search", placeholder= f"Enter {search_option.lower()}")
    
    if st.button("🔎 Search"):
        results = []
        if search_option == "Title":
            results = [book for book in library if search_query.lower() in book["title"].lower()]
        elif search_option == "Author":
            results = [book for book in library if search_query.lower() in book["author"].lower()]
        
        if results:
            st.write("📚 Matching Books:")
            for book in results:
                with st.expander(f"{book['title']} by {book['author']}"):
                    st.write(f"**Year:** {book['year']}")
                    st.write(f"**Genre:** {book['genre']}")
                    st.write(f"**Status:** {'📖 Read' if book.get('read_status', False) else '📚 Unread'}")
        else:
            st.write("❌ No matching books found.")

import streamlit as st

def display_all_books(library):
    st.subheader("📚 Your Library")

    if library:
        # Sorting options
        sort_option = st.selectbox("Sort by:", ["Title", "Author", "Year"])
        if sort_option == "Title":
            library.sort(key=lambda x: x["title"].lower())
        elif sort_option == "Author":
            library.sort(key=lambda x: x["author"].lower())
        elif sort_option == "Year":
            library.sort(key=lambda x: x["year"])  # Ensure 'year' key is lowercase

        # Create two columns
        cols = st.columns(2)

        for i, book in enumerate(library):
            with cols[i % 2]:  # Alternate between two columns
                st.markdown(f"""
                    <div style="
                        padding: 10px; 
                        border: 1px solid #ddd; 
                        border-radius: 10px; 
                        margin-bottom: 10px;
                        background-color: #f9f9f9;">
                        <h3>{book['title']}</h3>
                        <p><b>Author:</b> {book["author"]}</p>
                        <p><b>Year:</b> {book["year"]}</p>  
                        <p><b>Genre:</b> {book["genre"]}</p>  
                        <p><b>Status:</b> {'📖 Read' if book['read_status'] else '📚 Unread'}</p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.write("📭 Your library is empty.")


def display_statistics(library):
    st.subheader("📊 Library Statistics")
    total_books = len(library)
    read_books = sum(book.get("read_status", False) for book in library)
    unread_books = total_books - read_books
    percentage_read = (read_books / total_books * 100) if total_books > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Books", total_books)
    with col2:
        st.metric("Books Read", read_books)
    with col3:
        st.metric("Books Unread", unread_books)
    
    st.progress(percentage_read / 100)
    st.write(f"**Percentage Read:** {percentage_read:.1f}%")
    
    if total_books > 0:
        df = pd.DataFrame({
            "Status": ["Read", "Unread"],
            "Count": [read_books, unread_books]
        })
  
        colors = ["#4CAF50", "#FF5252"] 
        fig = px.pie(df, values="Count", names="Status", title="Read vs Unread Books", hole=0.4, color_discrete_sequence=colors)
        st.plotly_chart(fig, use_container_width=True)

def main():
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📚 Personal Library Manager</h1>", unsafe_allow_html=True)
    
    library = load_library()
    
    with st.sidebar:
        choice = option_menu(
            menu_title="Menu",
            options=["Add a book", "Remove a book", "Search for a book", "Display all books", "Display statistics", "Exit"],
            icons=["plus-circle", "dash-circle", "search", "list-task", "bar-chart", "box-arrow-right"],
            default_index=0,
        )
    
    if choice == "Add a book":
        add_book(library)
    elif choice == "Remove a book":
        remove_book(library)
    elif choice == "Search for a book":
        search_book(library)
    elif choice == "Display all books":
        display_all_books(library)
    elif choice == "Display statistics":
        display_statistics(library)
    elif choice == "Exit":
        st.write("📁 Library saved to file. Goodbye! 👋")
        save_library(library)
        st.stop()

if __name__ == "__main__":
    main() 
    st.markdown("---")
st.markdown("<p style='text-align: center;'>🌍 Made with ❤ by Uzma kanwal 🌟 </p>", unsafe_allow_html=True)
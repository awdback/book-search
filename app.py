import streamlit as st
import pandas as pd
import json

# Konfigurasi halaman
st.set_page_config(
    page_title="Books Search App",
    page_icon="📚",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    try:
        with open('data/books.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    except FileNotFoundError:
        st.error("File books.json tidak ditemukan. Pastikan Anda sudah menjalankan scraping.")
        return pd.DataFrame()

# Main app
def main():
    st.title("📚 Books Search App")
    st.markdown("*Web Crawler untuk Books to Scrape menggunakan Scrapy*")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.warning("Tidak ada data untuk ditampilkan.")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filter Pencarian")
    
    # Search by title
    search_title = st.sidebar.text_input("Cari berdasarkan judul:")
    
    # Filter by category
    categories = ['All'] + sorted(df['category'].dropna().unique().tolist())
    selected_category = st.sidebar.selectbox("Pilih kategori:", categories)
    
    # Filter by rating
    rating_filter = st.sidebar.slider("Rating minimal:", 1, 5, 1)
    
    # Filter by price range
    if not df['price'].isna().all():
        prices = df['price'].str.replace('£', '').astype(float)
        min_price = st.sidebar.number_input("Harga minimal (£):", value=0.0, min_value=0.0)
        max_price = st.sidebar.number_input("Harga maksimal (£):", value=float(prices.max()), min_value=0.0)
    
    # Apply filters
    filtered_df = df.copy()
    
    if search_title:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search_title, case=False, na=False)]
    
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    filtered_df = filtered_df[filtered_df['rating'] >= rating_filter]
    
    if not df['price'].isna().all():
        price_values = filtered_df['price'].str.replace('£', '').astype(float)
        filtered_df = filtered_df[(price_values >= min_price) & (price_values <= max_price)]
    
    # Display results
    st.header(f"📖 Hasil Pencarian ({len(filtered_df)} buku)")
    
    if not filtered_df.empty:
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Buku", len(filtered_df))
        
        with col2:
            avg_rating = filtered_df['rating'].mean()
            st.metric("Rating Rata-rata", f"{avg_rating:.1f}")
        
        with col3:
            if not filtered_df['price'].isna().all():
                avg_price = filtered_df['price'].str.replace('£', '').astype(float).mean()
                st.metric("Harga Rata-rata", f"£{avg_price:.2f}")
        
        with col4:
            total_categories = filtered_df['category'].nunique()
            st.metric("Kategori", total_categories)
        
        # Display books
        for index, book in filtered_df.iterrows():
            with st.expander(f"📚 {book['title']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Kategori:** {book['category']}")
                    st.write(f"**Rating:** {'⭐' * book['rating']} ({book['rating']}/5)")
                    st.write(f"**Harga:** {book['price']}")
                    st.write(f"**Ketersediaan:** {book['availability']} tersedia")
                    
                    if book['description']:
                        st.write(f"**Deskripsi:** {book['description']}")
                
                with col2:
                    st.write(f"**URL:** [Lihat Buku]({book['url']})")
    else:
        st.info("Tidak ada buku yang sesuai dengan filter yang dipilih.")

if __name__ == "__main__":
    main()
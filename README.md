shl_recommender/
├── data/                    # Store your scraped JSON and CSV files here
├── scraper/
│   └── shl_scraper.py       # Script to crawl the SHL catalog
├── recommender/
│   ├── indexer.py           # Code to generate embeddings and store in ChromaDB
│   └── engine.py            # The RAG logic and recommendation balancing
├── api/
│   └── main.py              # FastAPI application (endpoints)
├── frontend/
│   └── app.py               # Streamlit web interface
└── requirements.txt         # Dependencies
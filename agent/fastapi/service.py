import os
import logging
from google.cloud import storage
import requests
from serpapi import GoogleSearch
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from langchain_core.tools import tool  # Corrected import

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# GCS setup
bucket_name = os.getenv("GCS_BUCKET_NAME")
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
file_paths = [
    "cfai_publications/The Economics of Private Equity: A Critical Review/The Economics of Private Equity: A Critical Review.pdf",
    "cfai_publications/Investment Horizon, Serial Correlation, and Better (Retirement) Portfolios/Investment Horizon, Serial Correlation, and Better (Retirement) Portfolios.pdf",
    "cfai_publications/An Introduction to Alternative Credit/An Introduction to Alternative Credit.pdf"
]

# Initialize GCS client
if credentials_path:
    gcs_client = storage.Client.from_service_account_json(credentials_path)
    logging.info("GCS client initialized successfully.")
else:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")

# Document Selection Tool
@tool("select_document")
def get_available_documents_from_gcs():
    """Fetches the specified documents from Google Cloud Storage if they exist."""
    logging.info("Fetching specified documents from GCS.")
    bucket = gcs_client.bucket(bucket_name)
    available_docs = []

    for file_path in file_paths:
        blob = bucket.blob(file_path)
        if blob.exists():
            logging.info(f"Document found: {file_path}")
            available_docs.append(file_path)
        else:
            logging.warning(f"Document not found in GCS: {file_path}")

    return available_docs or None

# Arxiv Fetch Function
@tool("fetch_arxiv")
def fetch_arxiv(query: str):
    """Fetches research papers from ArXiv based on a query."""
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=5"
    response = requests.get(url)
    if response.status_code != 200:
        return "Error fetching data from Arxiv."

    root = ET.fromstring(response.content)
    results = []
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        title = entry.find("{http://www.w3.org/2005/Atom}title").text
        summary = entry.find("{http://www.w3.org/2005/Atom}summary").text
        published = entry.find("{http://www.w3.org/2005/Atom}published").text
        authors = [
            author.find("{http://www.w3.org/2005/Atom}name").text
            for author in entry.findall("{http://www.w3.org/2005/Atom}author")
        ]
        link = entry.find("{http://www.w3.org/2005/Atom}id").text

        results.append({
            "title": title,
            "summary": summary,
            "published": published,
            "authors": authors,
            "link": link
        })
    return results

# Web Search Function using SerpAPI
serpapi_api_key = os.getenv("SERPAPI_KEY")

@tool("web_search")
def web_search(query: str):
    """Performs a Google search for general knowledge queries using SerpAPI."""
    search = GoogleSearch({
        "q": query,
        "num": 5,
        "engine": "google",
        "api_key": serpapi_api_key
    })
    results = search.get_dict().get("organic_results", [])
    return [{
        "title": x["title"],
        "snippet": x["snippet"],
        "link": x["link"]
    } for x in results]

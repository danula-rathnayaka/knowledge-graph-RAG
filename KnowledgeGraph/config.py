import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph


def load_neo4j_graph():
    load_dotenv()

    NEO4J_URI = os.getenv('NEO4J_URI')
    NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
    NEO4J_DATABASE = os.getenv('NEO4J_DATABASE') or 'neo4j'

    GROQ_API_KEY = os.getenv('GROQ_API_KEY')

    graph = Neo4jGraph(
        url=NEO4J_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
        database=NEO4J_DATABASE
    )

    return graph, GROQ_API_KEY
from KnowledgeGraph.knoledgeGraph import ingest_Chunks, embed_text, create_nodes, create_relationship, create_vector_index
from KnowledgeGraph.chunking import split_data_from_file
from KnowledgeGraph.config import load_neo4j_graph
import json

print("Loading Neo4j graph and GROQ API key...")
graph, GROQ_API_KEY = load_neo4j_graph()
print("Graph loaded successfully.")

# file_names = ["Talleyrand", "Napoleon", "Battle_of_Waterloo"]
#
# for name in file_names:
#     print(f"\nProcessing file: {name}")
#     file = f"data/{name}.json"
#
#     print(f"Splitting data from file: {file}")
#     chunks = split_data_from_file(file)
#     print(f"Number of chunks created: {len(chunks)}")
#
#     with open(file, 'r', encoding='utf-8') as f:
#         data = json.load(f)
#
#     print(f"Creating nodes for: {name}")
#     if name == "Battle_of_Waterloo":
#         create_nodes(graph=graph, data=data, node_label="Event", node_name=name)
#     else:
#         create_nodes(graph=graph, data=data, node_label="Person", node_name=name)
#
#     print(f"Ingesting chunks for: {name}")
#     ingest_Chunks(graph=graph, chunks=chunks, node_name=name, node_label='Chunk')

# Create relationships
print("\nCreating relationships...")

rel_section_chunk = """
MATCH (s:Section), (c:Chunk)
WHERE s.type = c.source AND s.parent_name = c.node_name
MERGE (s)-[:HAS_CHUNK]->(c);
"""

rel_person_person = """
MATCH (p1:Person), (p2:Person)
WHERE id(p1) < id(p2)
MERGE (p1)-[:RELATED_TO]->(p2)
MERGE (p2)-[:RELATED_TO]->(p1);
"""

rel_person_event = """
MATCH (p:Person), (e:Event)
MERGE (p)-[:RELATED_TO]->(e)
MERGE (e)-[:RELATED_TO]->(p);
"""

rel_person_section = """
MATCH (p:Person), (s:Section)
WHERE p.name = s.parent_name
MERGE (p)-[:HAS_SECTION]->(s);
"""

rel_event_section = """
MATCH (e:Event), (s:Section)
WHERE e.name = s.parent_name
MERGE (e)-[:HAS_SECTION]->(s);
"""

queries = [
    ("rel_section_chunk", rel_section_chunk),
    ("rel_person_person", rel_person_person),
    ("rel_person_event", rel_person_event),
    ("rel_person_section", rel_person_section),
    ("rel_event_section", rel_event_section)
]

for name, query in queries:
    print(f"Running relationship query: {name}")
    create_relationship(graph=graph, query=query)

print("\nCreating vector index on 'Chunk' nodes...")
create_vector_index(graph=graph, index_name='Chunk')
print("Vector index created.")

print("Embedding text for 'Chunk' nodes...")
embed_text(graph=graph, node_name='Chunk')
print("Text embedding completed.")

print("\n✅ All tasks completed successfully.")

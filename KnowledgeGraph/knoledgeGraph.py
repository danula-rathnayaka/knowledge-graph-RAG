from langchain_community.embeddings import HuggingFaceEmbeddings
from tqdm import tqdm


# 1. Add main nodes without creating relationships
def create_nodes(graph, data: dict, node_label: str, node_name: str):
    # Create the main node
    main_node_query = f"""
    MERGE (main:{node_label} {{name: $name}})
    """
    graph.query(main_node_query, params={"name": node_name})

    # Create section nodes only (without relationships)
    for section, content in data.items():
        query = f"""
        MERGE (s:Section {{type: $type, parent_name: $name}})

        """
        params = {
            "type": section,
            "name": node_name
        }
        graph.query(query, params=params)


# 2. Add Chunks
def ingest_Chunks(graph, chunks, node_name, node_label):
    """
    Ingests file chunk data into the knowledge graph by merging chunk nodes.

    Args:
        graph: A knowledge graph client or connection object that has a `query` method.
        chunks: A list of dictionaries, each representing a file chunk with keys:
                     'chunkId', 'text', 'source', 'formItem', and 'chunkSeqId'.
        node_name: A string used to tag the chunk nodes.
        node_label: The dynamic label for the chunk nodes.
    """
    merge_chunk_node_query = f"""
    MERGE (mergedChunk:{node_label} {{chunkId: $chunkParam.chunkId}})
        ON CREATE SET
            mergedChunk.text = $chunkParam.text, 
            mergedChunk.source = $chunkParam.Source, 
            mergedChunk.formItem = $chunkParam.formItem, 
            mergedChunk.chunkSeqId = $chunkParam.chunkSeqId,
            mergedChunk.node_name = $node_name
    RETURN mergedChunk
    """

    node_count = 0
    for chunk in chunks:
        print(f"Creating `:{node_label}` node for chunk ID {chunk['chunkId']}")
        graph.query(merge_chunk_node_query, params={'chunkParam': chunk, 'node_name': node_name})
        node_count += 1
    print(f"Created {node_count} nodes")


# 3. Create Relationships

def create_relationship(graph, query: str):
    """
    Executes the provided Cypher query on the given graph.

    Parameters:
        graph: An instance of your Neo4j connection.
        query: A string containing a valid Cypher query.
    """
    graph.query(query)


def create_vector_index(graph, index_name):
    # Create the vector index if it does not exist, using the dynamic node label
    vector_index_query = f"""
    CREATE VECTOR INDEX `{index_name}` IF NOT EXISTS
    FOR (n:{index_name}) ON (n.textEmbeddingOpenAI) 
    OPTIONS {{ indexConfig: {{
        `vector.dimensions`: 1536,
        `vector.similarity_function`: 'cosine'
    }}}}
    """
    graph.query(vector_index_query)


def embed_text(graph, node_name, model_name="BAAI/bge-base-en-v1.5"):
    """
    Creates embeddings for nodes with a dynamic label using Hugging Face's embedding model,
    and displays a single-line progress bar using tqdm.

    Args:
        graph: A knowledge graph client/connection object that has a `query` method.
        model_name: The Hugging Face model to use for embeddings (default: BAAI/bge-base-en-v1.5).
        node_name: The label of nodes to process (default: Chunk).
    """
    print("Starting embedding update...")

    # Initialize HuggingFaceEmbeddings model
    try:
        embedding_model = HuggingFaceEmbeddings(
            model_name=model_name,
            encode_kwargs={'normalize_embeddings': True}
        )
        print(f"Initialized HuggingFaceEmbeddings with model: {model_name}")
    except Exception as e:
        print(f"Failed to initialize HuggingFaceEmbeddings with model: {model_name}. Error: {e}")
        raise

    # Fetch nodes without embeddings using elementId to avoid deprecated id() warnings
    fetch_nodes_query = f"""
    MATCH (n:{node_name})
    WHERE n.textEmbeddingHuggingFace IS NULL
    RETURN elementId(n) AS node_id, n.text AS text
    """
    nodes = list(graph.query(fetch_nodes_query))
    total_nodes = len(nodes)
    print(f"Found {total_nodes} nodes without embeddings.")

    # Use a single-line progress bar for node updates
    with tqdm(total=total_nodes, desc="Embedding nodes", ncols=100, leave=True) as pbar:
        for record in nodes:
            node_id = record["node_id"]
            text = record["text"]

            try:
                # Generate embedding using HuggingFaceEmbeddings
                embedding = embedding_model.embed_query(text)
                print(f"Generated embedding for node {node_id} with text: '{text[:15]}...'")

                # Update query to set the embedding in Neo4j
                update_query = f"""
                MATCH (n:{node_name})
                WHERE elementId(n) = $node_id
                SET n.textEmbeddingHuggingFace = $embedding
                """
                graph.query(update_query, params={
                    "node_id": node_id,
                    "embedding": embedding
                })
            except Exception as e:
                print(f"Error processing node {node_id} with text: '{text[:15]}...'. Error: {e}")
                continue

            pbar.update(1)

    print("Finished embedding update.")

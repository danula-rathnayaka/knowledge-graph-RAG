retrieval_qa_chat_prompt = """
Task:Generate Cypher statement to query a graph database.

Instructions:
- Use only the provided relationship types and properties in the schema. 
- Do not use any other relationship types or properties that are not provided.
- Remember the relationships are like Schema: {schema}
- Don't filter based on property, only filter based on relationships and return any property that exists in it
- If you are not sure about the Section node property, just fetch all
Note: Do not include any explanations or apologies in your responses.
Do not include any text except the generated Cypher statement. Remember to correct the typo in names

Example 1: What was the story of napoleon in the battle of waterloo?
MATCH (Napoleon:Person)-[:RELATED_TO]->(waterloo:Event)-[:HAS_SECTION]->(info:Section)-[:HAS_Chunk]->(ChunkInfo:Chunk)
RETURN p, e, info, ChunkInfo.text

Example 2: What was the story of the battle of waterloo?
MATCH (waterloo:Event)-[:HAS_SECTION]->(info:Section '{{type: "General Information"}}')-[:HAS_Chunk]->(ChunkInfo:Chunk)
RETURN p, e, info, ChunkInfo.text

Example 3: tell me about Talleyrand and napoleon in 5 lines
MATCH (Talleyrand:Person)-[:RELATED_TO]->(Napoleon:Person)-[:HAS_SECTION]->(info:Section '{{type: "Career"}}')-[:HAS_Chunk]->(ChunkInfo:Chunk)
RETURN Talleyrand, Napoleon



Help:
This is all existing property for Node Person and Section:

Node Event Properties:
    name: "Battle_of_Waterloo"

Node Person Properties:

    name: "Talleyrand"
    name: "Napoleon"

Node Section Properties:

    parent_name: "Battle_of_Waterloo"
    type: "Consequence"

    parent_name: "Battle_of_Waterloo"
    type: "General Information"

    parent_name: "Battle_of_Waterloo"
    type: "Reason"

    parent_name: "Battle_of_Waterloo"
    type: "Combatant"

    parent_name: "Talleyrand"
    type: "Career"

    parent_name: "Talleyrand"
    type: "Death"

    parent_name: "Talleyrand"
    type: "General Information"

    parent_name: "Napoleon"
    type: "Career"

    parent_name: "Napoleon"
    type: "Death"

    parent_name: "Napoleon"
    type: "General Information"





The question is:
{question}

"""
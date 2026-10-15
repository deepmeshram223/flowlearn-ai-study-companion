import json
import re
from collections import Counter

from backend.services.concept_discovery import discover_topics
from backend.services.llm import generate_roadmap_answer


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ============================================================
# QUESTION / PRACTICE CONTENT DETECTION
# ============================================================

def is_question_content(text):
    """
    Detect chunks that mainly contain question banks,
    answer keys, or practice questions.
    """

    upper = text.upper()

    patterns = [
        "SAMPLE QUESTION PAPER",
        "SAMPLE QUESTION PAPERS",
        "ADDITIONAL PRACTICE QUESTIONS",
        "ANSWER KEY",
        "MULTIPLE CHOICE QUESTIONS",
    ]

    for pattern in patterns:
        if pattern in upper:
            return True

    question_count = len(
        re.findall(r"\b\d{1,3}[\.\\)]\s", text)
    )

    return question_count >= 8


# ============================================================
# KEYWORD EXTRACTION
# ============================================================

def extract_keywords(text):
    """
    Extract repeated useful terms from a cluster.

    This is only a local signal.
    The LLM decides the final topic names.
    """

    words = re.findall(
        r"\b[A-Za-z][A-Za-z-]{3,}\b",
        text.lower()
    )

    stopwords = {
        "this",
        "that",
        "with",
        "from",
        "which",
        "shall",
        "where",
        "when",
        "their",
        "there",
        "these",
        "those",
        "such",
        "into",
        "have",
        "will",
        "would",
        "should",
        "could",
        "also",
        "than",
        "then",
        "only",
        "each",
        "used",
        "using",
        "following",
        "section",
        "chapter",
        "page",
        "aircraft",
        "flight",
    }

    words = [
        word
        for word in words
        if word not in stopwords
    ]

    return Counter(words)


# ============================================================
# BUILD ONE CLUSTER SUMMARY
# ============================================================

def build_cluster_summary(cluster):
    """
    Convert a large cluster into a compact representation.

    We deliberately do NOT send every chunk to the LLM.
    """

    content_chunks = []

    for chunk in cluster.get("chunks", []):

        text = clean_text(chunk["text"])

        if not text:
            continue

        if is_question_content(text):
            continue

        content_chunks.append({
            "id": chunk["id"],
            "page": chunk["page"],
            "text": text,
        })

    if not content_chunks:
        return None

    # --------------------------------------------------------
    # Extract repeated keywords
    # --------------------------------------------------------

    keyword_counter = Counter()

    for chunk in content_chunks:

        keyword_counter.update(
            extract_keywords(chunk["text"])
        )

    keywords = [
        word
        for word, _ in keyword_counter.most_common(8)
    ]

    # --------------------------------------------------------
    # Select representative chunks
    # --------------------------------------------------------

    sample_count = min(
        2,
        len(content_chunks)
    )

    if len(content_chunks) <= sample_count:

        representatives = content_chunks

    else:

        if sample_count == 1:

            positions = [0]

        else:

            positions = [
                int(
                    i * (len(content_chunks) - 1)
                    / (sample_count - 1)
                )
                for i in range(sample_count)
            ]

        representatives = [
            content_chunks[position]
            for position in positions
        ]

    # --------------------------------------------------------
    # Compact representative material
    # --------------------------------------------------------

    representative_material = []

    for chunk in representatives:

        representative_material.append({
            "page": chunk["page"],
            "text": chunk["text"][:250],
        })

    # --------------------------------------------------------
    # Page range
    # --------------------------------------------------------

    pages = sorted(
        set(
            chunk["page"]
            for chunk in content_chunks
        )
    )

    return {
        "cluster_id": cluster["cluster_id"],
        "chunk_count": len(content_chunks),
        "page_range": {
            "start": pages[0],
            "end": pages[-1],
        },
        "keywords": keywords,
        "representative_material": representative_material,
    }


# ============================================================
# BUILD CONCEPT INVENTORY
# ============================================================

def build_concept_inventory(
    document_id,
    number_of_topics=30,
):
    """
    Run local clustering and convert the result into a compact
    concept inventory.

    No LLM call happens here.
    """

    clusters = discover_topics(
        document_id=document_id,
        number_of_topics=number_of_topics,
    )

    inventory = []

    for cluster in clusters:

        summary = build_cluster_summary(
            cluster
        )

        if summary is None:
            continue

        inventory.append(summary)

    return inventory


# ============================================================
# BUILD SAFE INVENTORY FOR LLM
# ============================================================

def build_compact_inventory(inventory):
    """
    Convert the local concept inventory into a compact JSON
    representation.

    The hard character limit prevents the roadmap request
    from becoming too large for Groq.
    """

    # Keep the inventory small enough that the prompt + response
    # remain safely inside the model's limits.
    MAX_INVENTORY_CHARS = 9000

    compact_parts = []

    current_size = 0

    for concept in inventory:

        concept_text = json.dumps(
            concept,
            ensure_ascii=False,
            separators=(",", ":"),
        )

        remaining = (
            MAX_INVENTORY_CHARS
            - current_size
        )

        if remaining <= 0:
            break

        # If the entire concept fits, keep it.
        if len(concept_text) <= remaining:

            compact_parts.append(
                concept_text
            )

            current_size += len(
                concept_text
            )

        else:

            # Do not cut JSON in the middle.
            # Simply stop before this concept.
            break

    compact_inventory = (
        "["
        + ",".join(compact_parts)
        + "]"
    )

    print(
        f"Roadmap inventory size: "
        f"{len(compact_inventory)} characters"
    )

    print(
        f"Concept groups sent to LLM: "
        f"{len(compact_parts)} / {len(inventory)}"
    )

    return compact_inventory


# ============================================================
# JSON CLEANING
# ============================================================

def clean_json_response(response):

    response = response.strip()

    # Remove ```json
    response = re.sub(
        r"^```json\s*",
        "",
        response,
        flags=re.IGNORECASE,
    )

    # Remove ```
    response = re.sub(
        r"^```\s*",
        "",
        response,
    )

    response = re.sub(
        r"\s*```$",
        "",
        response,
    )

    # Find JSON object.
    start = response.find("{")
    end = response.rfind("}")

    if start == -1 or end == -1:

        raise ValueError(
            "LLM did not return a JSON object."
        )

    return response[
        start:end + 1
    ]


# ============================================================
# VALIDATE ROADMAP STRUCTURE
# ============================================================

def validate_roadmap(roadmap):

    if not isinstance(roadmap, dict):
        raise ValueError(
            "Roadmap must be a JSON object."
        )

    if "title" not in roadmap:
        raise ValueError(
            "Roadmap JSON does not contain 'title'."
        )

    if "description" not in roadmap:
        raise ValueError(
            "Roadmap JSON does not contain 'description'."
        )

    if "parents" not in roadmap:
        raise ValueError(
            "Roadmap JSON does not contain 'parents'."
        )

    if not isinstance(
        roadmap["parents"],
        list
    ):
        raise ValueError(
            "'parents' must be a list."
        )

    if len(roadmap["parents"]) == 0:
        raise ValueError(
            "Roadmap contains no parent topics."
        )

    all_ids = set()

    for parent in roadmap["parents"]:

        if not isinstance(parent, dict):
            raise ValueError(
                "Every parent must be an object."
            )

        required_parent_fields = [
            "id",
            "title",
            "description",
            "children",
        ]

        for field in required_parent_fields:

            if field not in parent:
                raise ValueError(
                    f"Parent is missing '{field}'."
                )

        parent_id = parent["id"]

        if parent_id in all_ids:
            raise ValueError(
                f"Duplicate ID detected: {parent_id}"
            )

        all_ids.add(parent_id)

        if not isinstance(
            parent["children"],
            list
        ):
            raise ValueError(
                f"Children of parent '{parent_id}' "
                f"must be a list."
            )

        for subtopic in parent["children"]:

            if not isinstance(subtopic, dict):
                raise ValueError(
                    "Every subtopic must be an object."
                )

            required_subtopic_fields = [
                "id",
                "title",
                "children",
            ]

            for field in required_subtopic_fields:

                if field not in subtopic:
                    raise ValueError(
                        f"Subtopic is missing '{field}'."
                    )

            subtopic_id = subtopic["id"]

            if subtopic_id in all_ids:
                raise ValueError(
                    f"Duplicate ID detected: {subtopic_id}"
                )

            all_ids.add(subtopic_id)

            if not isinstance(
                subtopic["children"],
                list
            ):
                raise ValueError(
                    f"Children of subtopic '{subtopic_id}' "
                    f"must be a list."
                )

            for node in subtopic["children"]:

                if not isinstance(node, dict):
                    raise ValueError(
                        "Every learning node must be an object."
                    )

                required_node_fields = [
                    "id",
                    "title",
                    "description",
                    "source_pages",
                    "prerequisites",
                ]

                for field in required_node_fields:

                    if field not in node:
                        raise ValueError(
                            f"Learning node is missing '{field}'."
                        )

                node_id = node["id"]

                if node_id in all_ids:
                    raise ValueError(
                        f"Duplicate ID detected: {node_id}"
                    )

                all_ids.add(node_id)

                if not isinstance(
                    node["source_pages"],
                    list
                ):
                    raise ValueError(
                        f"source_pages for '{node_id}' "
                        f"must be a list."
                    )

                if not isinstance(
                    node["prerequisites"],
                    list
                ):
                    raise ValueError(
                        f"prerequisites for '{node_id}' "
                        f"must be a list."
                    )

    # --------------------------------------------------------
    # Validate prerequisite references
    # --------------------------------------------------------

    learning_node_ids = set()

    for parent in roadmap["parents"]:

        for subtopic in parent["children"]:

            for node in subtopic["children"]:

                learning_node_ids.add(
                    node["id"]
                )

    for parent in roadmap["parents"]:

        for subtopic in parent["children"]:

            for node in subtopic["children"]:

                for prerequisite in node["prerequisites"]:

                    if prerequisite not in learning_node_ids:
                        raise ValueError(
                            f"Learning node '{node['id']}' "
                            f"references unknown prerequisite "
                            f"'{prerequisite}'."
                        )

    return True


# ============================================================
# GENERATE HIERARCHICAL ROADMAP
# ============================================================

def generate_hierarchical_roadmap(
    document_id,
    number_of_topics=30,
):
    """
    Generate a hierarchical FlowLearn roadmap.

    Pipeline:

        document
            ↓
        embeddings
            ↓
        local clustering
            ↓
        compact concept inventory
            ↓
        ONE LLM call
            ↓
        hierarchical roadmap
    """

    print(
        f"Starting hierarchical roadmap generation "
        f"for document {document_id}"
    )

    # --------------------------------------------------------
    # STEP 1 — Local concept discovery
    # --------------------------------------------------------

    inventory = build_concept_inventory(
        document_id=document_id,
        number_of_topics=number_of_topics,
    )

    if not inventory:

        raise ValueError(
            "No meaningful concepts were discovered."
        )

    print(
        f"Discovered {len(inventory)} concept groups."
    )

    # --------------------------------------------------------
    # STEP 2 — Compact inventory
    # --------------------------------------------------------

    compact_inventory = build_compact_inventory(
        inventory
    )

    if compact_inventory == "[]":

        raise ValueError(
            "Concept inventory became empty."
        )

    # --------------------------------------------------------
    # STEP 3 — LLM prompt
    # --------------------------------------------------------

    prompt = f"""
You are the curriculum architect for FlowLearn.

Your task is to transform a document's discovered concepts
into a hierarchical learning roadmap.

The document may be very large.

The information below is already a compact representation
of the document.

Do NOT invent concepts that are not supported by the
supplied material.

Do NOT create a simple list.

Create a hierarchy:

Parent Topic
    ↓
Subtopic
    ↓
Learning Nodes

The roadmap should represent how a student should learn
the material, not simply reproduce the order of the document.

RULES:

1. Create approximately 8 to 12 parent topics.

2. A parent topic represents a major area of knowledge.

3. Each parent should contain approximately 2 to 6 subtopics.

4. Each subtopic should contain 1 to 4 actual learning nodes.

5. Learning nodes must represent something a student can
   actually study.

6. Do not create a learning node for every chunk.

7. Merge closely related concepts.

8. Do not use question papers, answer keys, sample questions,
   or practice questions as learning topics.

9. Preserve important technical terminology from the document.

10. Do not use the document's page order as the roadmap order
    unless it also makes pedagogical sense.

11. Establish prerequisites between learning nodes where the
    supplied material supports a dependency.

12. Do not create unnecessary prerequisite relationships.

13. Every learning node must contain source_pages.

14. source_pages must only contain pages appearing in the
    supplied material.

15. Do not use outside knowledge.

16. Do not create phases.

17. Do not create a fixed number of learning nodes.

18. The result must be a hierarchical roadmap.

19. Parent topics must be broad enough to contain multiple
    related subtopics.

20. Subtopics must be narrower concepts belonging to their
    parent topic.

21. Learning nodes must be concrete studyable concepts.

22. Avoid duplicate parent topics.

23. Avoid duplicate subtopics.

24. Avoid duplicate learning nodes.

25. Prefer meaningful prerequisite relationships over
    arbitrary connections.

26. Return ONLY valid JSON.

27. Do not wrap the JSON in Markdown code fences.

28. Make sure the JSON is COMPLETE.

29. Make sure every opening {{ has a matching closing }}.

30. Do not stop generating until the entire JSON object
    has been completed.

Required structure:

{{
  "title": "FlowLearn Roadmap",
  "description": "Short description of the roadmap",
  "parents": [
    {{
      "id": "parent_1",
      "title": "Parent Topic",
      "description": "Short description",
      "children": [
        {{
          "id": "subtopic_1",
          "title": "Subtopic",
          "children": [
            {{
              "id": "node_1",
              "title": "Learning Node",
              "description": "What the student learns",
              "source_pages": [1, 2],
              "prerequisites": []
            }}
          ]
        }}
      ]
    }}
  ]
}}

IMPORTANT:

IDs must be unique.

Use this pattern:

parent_1
parent_2

subtopic_1
subtopic_2

node_1
node_2

prerequisites must contain only existing
learning node IDs.

DOCUMENT CONCEPT INVENTORY:

{compact_inventory}
"""

    print(
        "Sending compact roadmap request to LLM..."
    )

    # --------------------------------------------------------
    # STEP 4 — ONE LLM CALL
    # --------------------------------------------------------

    response = generate_roadmap_answer(
        prompt
    )

    if not response:

        raise ValueError(
            "Roadmap model returned an empty response."
        )

    response = response.strip()

    # --------------------------------------------------------
    # STEP 5 — Parse JSON
    # --------------------------------------------------------

    try:

        cleaned = clean_json_response(
            response
        )

        roadmap = json.loads(
            cleaned
        )

    except Exception as error:

        print(
            "\n===== INVALID ROADMAP RESPONSE ====="
        )

        print(
            response[:10000]
        )

        print(
            "\n===== ERROR ====="
        )

        print(
            error
        )

        raise ValueError(
            f"Roadmap model returned invalid JSON: "
            f"{error}"
        )

    # --------------------------------------------------------
    # DEBUG — PRINT COMPLETE GENERATED ROADMAP
    # --------------------------------------------------------

    print(
        "\n===== GENERATED ROADMAP ====="
    )

    print(
        json.dumps(
            roadmap,
            indent=2,
            ensure_ascii=False
        )
    )

    print(
        "=============================\n"
    )

    # --------------------------------------------------------
    # STEP 6 — Validate roadmap structure
    # --------------------------------------------------------

    validate_roadmap(
        roadmap
    )

    # --------------------------------------------------------
    # FINAL SUCCESS
    # --------------------------------------------------------

    print(
        "Roadmap generated successfully."
    )

    print(
        f"Parent topics: "
        f"{len(roadmap['parents'])}"
    )

    total_subtopics = 0
    total_learning_nodes = 0

    for parent in roadmap["parents"]:

        total_subtopics += len(
            parent["children"]
        )

        for subtopic in parent["children"]:

            total_learning_nodes += len(
                subtopic["children"]
            )

    print(
        f"Subtopics: {total_subtopics}"
    )

    print(
        f"Learning nodes: {total_learning_nodes}"
    )

    return roadmap
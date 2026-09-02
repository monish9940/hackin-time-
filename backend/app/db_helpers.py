from bson import ObjectId
from typing import Dict, Any, List

def get_next_sequence_value(db, sequence_name: str) -> int:
    """
    Generates auto-incrementing integer sequence for MongoDB collections.
    """
    sequence_doc = db.counters.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return sequence_doc["sequence_value"]

def clean_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cleans MongoDB document by formatting BSON _id into string/int id.
    """
    if doc is None:
        return None
    d = dict(doc)
    if "_id" in d:
        if "id" not in d:
            d["id"] = str(d["_id"])
        del d["_id"]
    return d

def clean_docs(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [clean_doc(d) for d in docs if d is not None]

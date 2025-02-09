import json
import csv
import datetime
from app.models import Document

def export_dataset(db, format="jsonl", task="qa"):
    documents = db.query(Document).all()
    export_filename = f"export_{task}_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{format}"
    if format == "jsonl":
        with open(export_filename, "w", encoding="utf-8") as f:
            for doc in documents:
                if task == "qa":
                    record = {
                        "prompt": f"Q: {doc.title}\nA:",
                        "completion": f" {doc.content}"
                    }
                elif task == "summarization":
                    record = {
                        "prompt": f"Summarize the following document:\n{doc.content}\nSummary:",
                        "completion": ""
                    }
                else:
                    record = {"prompt": doc.title, "completion": doc.content}
                f.write(json.dumps(record) + "\n")
    elif format == "csv":
        with open(export_filename, "w", newline='', encoding="utf-8") as csvfile:
            fieldnames = ["prompt", "completion"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for doc in documents:
                if task == "qa":
                    record = {
                        "prompt": f"Q: {doc.title}\nA:",
                        "completion": f" {doc.content}"
                    }
                elif task == "summarization":
                    record = {
                        "prompt": f"Summarize the following document:\n{doc.content}\nSummary:",
                        "completion": ""
                    }
                else:
                    record = {"prompt": doc.title, "completion": doc.content}
                writer.writerow(record)
    else:
        raise ValueError("Unsupported export format")
    return export_filename
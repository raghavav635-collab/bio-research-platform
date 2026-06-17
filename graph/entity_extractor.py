import pandas as pd


BIOMEDICAL_ENTITIES = {
    "Alzheimer's disease": "Disease",
    "Mild cognitive impairment": "Disease",
    "Amyloid beta": "Biomarker",
    "Amyloid": "Biomarker",
    "Tau": "Biomarker",
    "Total tau": "Biomarker",
    "Phosphorylated tau": "Biomarker",
    "APOE4": "Gene/Risk Factor",
    "Memory loss": "Symptom",
    "Cognitive decline": "Symptom",
    "Neurodegeneration": "Biological Process",
    "Donepezil": "Treatment",
    "Memantine": "Treatment"
}


def extract_entities_from_text(text):
    results = []

    text_lower = text.lower()

    for entity, entity_type in BIOMEDICAL_ENTITIES.items():
        if entity.lower() in text_lower:
            results.append({
                "entity": entity,
                "type": entity_type
            })

    return results


if __name__ == "__main__":
    sample_text = """
    Alzheimer's disease is associated with amyloid beta, tau, phosphorylated tau,
    APOE4, memory loss, cognitive decline, and neurodegeneration.
    Donepezil and memantine are treatments used in clinical care.
    """

    entities = extract_entities_from_text(sample_text)

    df = pd.DataFrame(entities)
    df.to_csv("graph/biomedical_entities.csv", index=False)

    print(df)
    print("Entities saved to graph/biomedical_entities.csv")
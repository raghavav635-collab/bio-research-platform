import pandas as pd

relationships = [
    ["Amyloid beta", "associated_with", "Alzheimer's disease"],
    ["Tau", "biomarker_for", "Alzheimer's disease"],
    ["Phosphorylated tau", "biomarker_for", "Alzheimer's disease"],
    ["APOE4", "risk_factor_for", "Alzheimer's disease"],
    ["Memory loss", "symptom_of", "Alzheimer's disease"],
    ["Cognitive decline", "symptom_of", "Alzheimer's disease"],
    ["Donepezil", "treatment_for", "Alzheimer's disease"],
    ["Memantine", "treatment_for", "Alzheimer's disease"]
]

df = pd.DataFrame(
    relationships,
    columns=["source", "relationship", "target"]
)

df.to_csv("graph/knowledge_graph.csv", index=False)

print(df)
print("\nKnowledge graph saved.")
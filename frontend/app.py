import os
import tempfile
import pdfplumber
import chromadb
import streamlit as st
import pandas as pd
import joblib
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path="./database/chroma_db")
collection = chroma_client.get_or_create_collection(name="biomedical_papers")

st.set_page_config(page_title="Biomedical Research Assistant", layout="wide")

st.title("Biomedical Research Assistant")
st.write("AI-powered biomedical literature analysis and patient digital twin exploration.")

tab1, tab2 = st.tabs(["Research Assistant", "Patient Digital Twin"])


def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def chunk_text(text, chunk_size=500):
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]


def calculate_risk_score(patient):
    score = 0
    reasons = []

    mmse = patient["MMSE"]
    amyloid = patient["CSF Amyloid (pg/mL)"]
    tau = patient["CSF Total tau (pg/mL)"]
    ptau = patient["CSF Phosphorylated tau (pg/mL)"]
    apoe4 = patient["APOE4"]

    if mmse < 24:
        score += 25
        reasons.append("Lower MMSE score")

    if amyloid < 600:
        score += 20
        reasons.append("Lower CSF amyloid level")

    if tau > 500:
        score += 25
        reasons.append("Elevated total tau")

    if ptau > 60:
        score += 20
        reasons.append("Elevated phosphorylated tau")

    if str(apoe4).lower() == "yes":
        score += 10
        reasons.append("APOE4 positive")

    return min(score, 100), reasons


with tab1:
    st.subheader("Biomedical Literature Research Assistant")
    st.write("Upload biomedical PDFs and ask research questions.")

    uploaded_files = st.file_uploader(
        "Upload biomedical research PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} PDF(s) uploaded.")

        if st.button("Process PDFs"):
            total_chunks = 0

            with st.spinner("Processing PDFs..."):
                for uploaded_file in uploaded_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                        temp_file.write(uploaded_file.read())
                        temp_path = temp_file.name

                    text = extract_text_from_pdf(temp_path)
                    chunks = chunk_text(text)
                    embeddings = embedding_model.encode(chunks)

                    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                        collection.add(
                            documents=[chunk],
                            embeddings=[embedding.tolist()],
                            ids=[f"{uploaded_file.name}_chunk_{i}"],
                            metadatas=[{
                                "source": uploaded_file.name,
                                "chunk": i
                            }]
                        )

                    total_chunks += len(chunks)

            st.success(f"Processed {len(uploaded_files)} PDF(s) and stored {total_chunks} chunks.")

    st.divider()

    question = st.text_input("Ask a research question:")

    if st.button("Get Answer"):
        if not question:
            st.warning("Please enter a question.")
        else:
            with st.spinner("Searching across uploaded PDFs and generating answer..."):
                results = collection.query(
                    query_texts=[question],
                    n_results=5
                )

                context = "\n\n".join(results["documents"][0])

                prompt = f"""
You are a biomedical research assistant.

Answer the question using ONLY the context below.
If the context partially answers the question, answer only from the available context and clearly say what is not provided.
If the context does not contain enough information, say that the provided paper context does not contain enough information.

Question:
{question}

Context:
{context}
"""

                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )

                answer = response.choices[0].message.content

            st.subheader("Answer")
            st.write(answer)

            st.subheader("Retrieved Evidence")
            for i, doc in enumerate(results["documents"][0], start=1):
                metadata = results["metadatas"][0][i - 1]

                st.markdown(f"**Source Chunk {i}**")
                st.write(f"Source: {metadata.get('source', 'Unknown')}")
                st.write(f"Chunk: {metadata.get('chunk', 'Unknown')}")
                st.write(doc[:900])
                st.divider()


with tab2:
    st.header("Alzheimer's Disease Digital Twin")
    st.write("Explore de-identified Alzheimer's patient profiles using clinical and biomarker features.")

    patient_data_path = "data/patient_data.csv"

    if not os.path.exists(patient_data_path):
        st.warning("Patient dataset not found. Please add patient_data.csv inside the data folder.")
    else:
        df = pd.read_csv(patient_data_path)
        df.columns = df.columns.str.strip()

        model_path = "models/progression_model.pkl"


        knowledge_graph_path = "graph/knowledge_graph.csv"

        if os.path.exists(knowledge_graph_path):
            knowledge_graph_df = pd.read_csv(knowledge_graph_path)
        else:
            knowledge_graph_df = pd.DataFrame()

        if os.path.exists(model_path):
            progression_model = joblib.load(model_path)
        else:
            progression_model = None

        st.subheader("Dataset Overview")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Patients", len(df))

        with col2:
            st.metric("Average Age", round(df["Age"].mean(), 1))

        with col3:
            st.metric("Average MMSE", round(df["MMSE"].mean(), 1))

        st.divider()

        selected_patient = st.selectbox(
            "Select Patient Sample",
            df["Sample"].astype(str).tolist()
        )

        patient = df[df["Sample"].astype(str) == selected_patient].iloc[0]

        st.subheader(f"Patient Twin: Sample {selected_patient}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Diagnosis", patient["Diagnostic"])
            st.metric("Sex", patient["Sex"])

        with col2:
            st.metric("Age", patient["Age"])
            st.metric("MMSE Score", patient["MMSE"])

        with col3:
            st.metric("APOE4", patient["APOE4"])

            progression = patient["Progression to Alzheimer's Disease"]

            if patient["Diagnostic"] == "Alzheimer's Disease":
                st.metric("Progression Status", "Already Diagnosed")

            elif pd.isna(progression):
                st.metric("Progression Status", "Not Available")

            else:
                st.metric("Progression Status", progression)
        st.divider()

        st.subheader("Biomarker Profile")

        bio1, bio2, bio3 = st.columns(3)

        with bio1:
            st.metric("CSF Amyloid (pg/mL)", patient["CSF Amyloid (pg/mL)"])

        with bio2:
            st.metric("CSF Total Tau (pg/mL)", patient["CSF Total tau (pg/mL)"])

        with bio3:
            st.metric("CSF Phosphorylated Tau (pg/mL)", patient["CSF Phosphorylated tau (pg/mL)"])

        st.divider()

#        # Risk Score Section
        st.subheader("Risk Score")

        risk_score, risk_reasons = calculate_risk_score(patient)

        risk_col1, risk_col2 = st.columns(2)

        with risk_col1:
            st.metric("Estimated Alzheimer's Risk Score", f"{risk_score}%")

        with risk_col2:
            if risk_score >= 70:
                st.error("High risk profile")
            elif risk_score >= 40:
                st.warning("Moderate risk profile")
            else:
                st.success("Lower risk profile")

        st.write("Contributing Factors:")

        if risk_reasons:
            for reason in risk_reasons:
                st.write(f"- {reason}")
        else:
            st.write("- No major risk indicators detected using current rule-based criteria.")

        st.divider()

        st.subheader("ML Progression Prediction")

        if progression_model is not None:

            model_input = pd.DataFrame([{
                "Age": patient["Age"],
                "MMSE": patient["MMSE"],
                "CSF Amyloid (pg/mL)": patient["CSF Amyloid (pg/mL)"],
                "CSF Total tau (pg/mL)": patient["CSF Total tau (pg/mL)"],
                "CSF Phosphorylated tau (pg/mL)": patient["CSF Phosphorylated tau (pg/mL)"],
                "APOE4": 1 if str(patient["APOE4"]).lower() == "yes" else 0
            }])

            probability = progression_model.predict_proba(model_input)[0][1]
            prediction = progression_model.predict(model_input)[0]

            st.metric(
                "Predicted Progression Risk",
                f"{probability * 100:.1f}%"
            )

            if prediction == 1:
                st.warning("Likely Progressor")
            else:
                st.success("Lower Progression Likelihood")

        else:
            st.info("Progression model not available")

        st.divider()

        # -----------------------------
        # Similar Patient Search
        # -----------------------------

        st.subheader("Similar Patient Search")

        features = [
            "Age",
            "MMSE",
            "CSF Amyloid (pg/mL)",
            "CSF Total tau (pg/mL)",
            "CSF Phosphorylated tau (pg/mL)"
        ]

        similarity_df = df.copy()

        for feature in features:
            similarity_df[feature] = pd.to_numeric(similarity_df[feature], errors="coerce")

        current_vector = similarity_df[
            similarity_df["Sample"].astype(str) == selected_patient
        ][features].iloc[0]

        comparison_df = similarity_df.dropna(subset=features).copy()

        for feature in features:
            feature_std = comparison_df[feature].std()
            if feature_std == 0:
                feature_std = 1

            comparison_df[f"{feature}_diff"] = (
                (comparison_df[feature] - current_vector[feature]) / feature_std
            ) ** 2

        diff_columns = [f"{feature}_diff" for feature in features]

        comparison_df["Similarity Score"] = comparison_df[diff_columns].sum(axis=1) ** 0.5

        similar_patients = comparison_df[
            comparison_df["Sample"].astype(str) != selected_patient
        ].sort_values("Similarity Score").head(5)

        st.write("Most similar patients based on age, MMSE, amyloid, total tau, and phosphorylated tau:")

        st.write(f"Found {len(similar_patients)} similar patients")

        st.dataframe(
            similar_patients[
                [
                    "Sample",
                    "Diagnostic",
                    "Age",
                    "Sex",
                    "MMSE",
                    "CSF Amyloid (pg/mL)",
                    "CSF Total tau (pg/mL)",
                    "CSF Phosphorylated tau (pg/mL)",
                    "APOE4",
                    "Similarity Score"
                ]
            ],
            use_container_width=True
        )

        st.divider()

        st.subheader("Biomedical Knowledge Graph")

        if not knowledge_graph_df.empty:

            st.write(
                "Relationships extracted from biomedical domain knowledge."
            )

            st.dataframe(
                knowledge_graph_df,
                use_container_width=True
            )

        else:
            st.info("Knowledge graph not available.")

        st.divider()


        st.subheader("Patient Twin Summary")

        patient_summary = f"""
        This de-identified patient profile represents Sample {selected_patient}.

        Diagnostic group: {patient["Diagnostic"]}
        Age: {patient["Age"]}
        Sex: {patient["Sex"]}
        MMSE score: {patient["MMSE"]}
        CSF Amyloid: {patient["CSF Amyloid (pg/mL)"]} pg/mL
        CSF Total Tau: {patient["CSF Total tau (pg/mL)"]} pg/mL
        CSF Phosphorylated Tau: {patient["CSF Phosphorylated tau (pg/mL)"]} pg/mL
        APOE4 status: {patient["APOE4"]}
        Progression to Alzheimer's Disease: {patient["Progression to Alzheimer's Disease"]}
        Progression time: {patient["Progression time (months)"]} months
        """

        st.text(patient_summary)

        if st.button("Generate AI Patient Insight"):
            with st.spinner("Generating patient digital twin insight..."):
                knowledge_graph_text = knowledge_graph_df.to_string(index=False)

                prompt = f"""
                You are a biomedical AI assistant.

                Analyze the following de-identified Alzheimer's patient profile using:
                1. Patient clinical and biomarker data
                2. Biomedical knowledge graph relationships

                Do not provide a medical diagnosis.
                Provide a research-style interpretation only.
                Mention cognitive status, biomarker pattern, genetic risk factor, progression information, and relevant knowledge graph relationships.

                Patient Profile:
                {patient_summary}

                Biomedical Knowledge Graph:
                {knowledge_graph_text}
                """

                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )

                insight = response.choices[0].message.content

            st.subheader("AI Patient Insight")
            st.write(insight)
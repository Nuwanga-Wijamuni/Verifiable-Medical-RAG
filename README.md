# Verifiable Medical RAG

A specialized Retrieval-Augmented Generation (RAG) system designed to deliver accurate, source-grounded, and verifiable answers to medical questions by leveraging authoritative knowledge bases. This system is engineered to mitigate LLM hallucination by always providing explicit citations from the source material.

## 🌐 Live Deployment

**Try the application here:** [Verifiable Medical RAG Web Interface](https://your-deployment-url.com)

*Note: Replace the above URL with your actual deployed application URL*

## 🚀 Key Features

* **Verifiable Output:** Every generated answer is paired with the specific citation (document name, page number, or chunk ID) from the source knowledge base.
* **High-Performance API:** The system is powered by a high-throughput **FASTAPI** backend for serving RAG queries efficiently.
* **Specialized Ingestion:** Leverages the **LLAMA cloud document parser** (or a LlamaIndex component) for robust handling and structuring of complex medical documents (PDFs, DOCX).
* **Advanced Embeddings:** Utilizes pre-trained **Google Word Embeddings** (e.g., Word2Vec trained on a large corpus) for superior vector representation of medical terminology, enhancing retrieval accuracy.
* **Open-Source LLM Core:** The final generation step uses an optimized **GPTOSS** (Open-Source GPT) model, providing a cost-effective and transparent solution.

## 📐 System Architecture

The architecture is a three-stage RAG pipeline: Ingestion, API Service, and Retrieval/Generation.

1.  **Document Ingestion:**
    * **Source Data:** Authoritative medical documents (clinical guidelines, textbooks).
    * **Parsing:** The **LLAMA cloud document parser** processes and cleans the raw text.
    * **Vectorization:** Text chunks are converted into vectors using **Google Word Embeddings**.
    * **Storage:** Vectors and source metadata are stored in a specialized Vector Database.

2.  **API Service Layer:**
    * A **FASTAPI** server exposes a primary `/query` endpoint, managing authentication, request validation, and orchestrating the RAG chain.

3.  **RAG Query Chain:**
    * An incoming user query is embedded.
    * The system retrieves the top-K relevant text chunks from the Vector DB.
    * The query and retrieved chunks (context) are packaged into a prompt.
    * The **GPTOSS**-based LLM generates a concise, grounded answer.
    * The final response includes the answer and the metadata (verifiable source citations) of the retrieved chunks.

## 🛠️ Setup and Installation

### Prerequisites

* Python 3.10+
* A Vector Database (e.g., Chroma, Milvus, or Pinecone) configured.
* Environment variables for API keys (`LLAMA_CLOUD_API_KEY`, etc.).

### Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Nuwa98/Verifiable-Medical-Rag.git
    cd Verifiable-Medical-Rag
    ```

2.  **Setup Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Configure:**
    Create a `.env` file in the root directory and add your required secrets:
    ```
    LLAMA_CLOUD_API_KEY=your_api_key_here
    EMBEDDING_MODEL_PATH=google/word2vec-model-path
    VECTOR_DB_PATH=./vector_db
    LLM_MODEL_PATH=./models/gptoss-model
    ```

### Ingestion (One-Time)

Run the ingestion script to process your medical corpus using the **LLAMA cloud document parser** and **Google Word Embeddings**:

```bash
python ingest.py --path ./corpus --embedding_model $EMBEDDING_MODEL_PATH
```

### Running the FASTAPI Service

Start the FASTAPI server with Uvicorn:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000. You can access the auto-generated Swagger UI documentation at http://localhost:8000/docs.


## 🔗 Technologies

* **API Framework:** FASTAPI
* **LLM Engine:** GPTOSS (Open-Source LLM)
* **Document Processing:** LLAMA cloud document parser (LlamaIndex)
* **Embeddings:** Google Word Embeddings
* **Web Interface:** Gradio (for Hugging Face Space deployment)
* **Vector DB:** Chroma (or your chosen vector database)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

For questions or feedback, please open an issue on GitHub or contact the project maintainer.

---

*This system is intended for research and educational purposes. Always consult with healthcare professionals for medical advice.*

# Medical Chatbot

A powerful medical assistant chatbot that leverages LangChain, Google's Generative AI, and vector databases to provide accurate medical information. The chatbot processes user queries, retrieves relevant information from medical documents, and augments responses with web search results.


## Features

- **Document-Based Knowledge**: Leverages medical PDFs stored in the `data` directory
- **Web Search Integration**: Uses Tavily Search to access up-to-date medical information
- **Vector Database**: Utilizes Pinecone for efficient similarity search
- **Conversational UI**: Clean, responsive interface with markdown support
- **Multi-Tool Integration**: Combines document retrieval and web search for comprehensive answers

## Project Structure

```
medical-chatbot/
├── app.py                 # Flask application
├── chatbot.py             # Chatbot implementation and LangGraph workflow
├── requirements.txt       # Project dependencies
├── data/                  # Directory containing medical PDFs
│   └── m_data.pdf         # Sample medical data
├── static/                # Static assets
│   ├── script.js          # Frontend JavaScript
│   └── style.css          # CSS styles
└── templates/             # HTML templates
    └── index.html         # Main application page
```

## Technologies Used

- **Backend**:
  - Flask: Web framework
  - LangChain: Framework for building applications with LLMs
  - LangGraph: For creating cognitive workflows
  - Pinecone: Vector database for semantic search
  - Google Generative AI: For text generation and embeddings
  - Tavily: For web search integration

- **Frontend**:
  - Bootstrap: For responsive layout
  - Marked.js: For markdown rendering
  - Highlight.js: For code syntax highlighting

## Setup Instructions

### Prerequisites

- Python 3.8+
- API keys for:
  - Google AI (Gemini)
  - Tavily Search
  - Pinecone

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Karthic-Elangovan/Medical-Chatbot.git
   cd Medical-chatbot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your API keys:
   ```
   GOOGLE_API_KEY=your_google_api_key
   TAVILY_API_KEY=your_tavily_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_ENV=your_pinecone_environment
   ```

4. Initialize Pinecone:
   - Create a serverless Pinecone index named "medical-chatbot"
   - Ensure your index is properly dimensioned for Google's embedding model

### Data Setup

Place your medical PDF documents in the `data` directory. The system will automatically process them and create vector embeddings for retrieval.

### Running the Application

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Access the application at `http://localhost:5000`

## Usage

1. Enter a medical question in the input field
2. The system will:
   - Search through your medical documents for relevant information
   - Augment with web search results if needed
   - Generate a comprehensive response
3. The response will be displayed with proper markdown formatting

## Development

### Extending the Knowledge Base

To add more medical documents to the knowledge base:
1. Add PDF files to the `data` directory
2. The system will automatically process and index them

### Customizing the Model

To modify the model behavior or parameters, edit the `chatbot.py` file:
- Adjust the `chunk_size` and `chunk_overlap` parameters in the `process_documents` function
- Modify the prompt template in the `generate_response` function

## Deployment

For production deployment:

1. Update the Flask configuration in `app.py`:
   ```python
   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
   ```

2. Deploy to a platform of your choice (Heroku, AWS, GCP, etc.)


## Acknowledgements

- LangChain for the framework
- Google for the Generative AI models
- Pinecone for vector database
- Tavily for search API

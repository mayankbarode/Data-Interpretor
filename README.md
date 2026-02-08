# 📊 Data Interpretor

An AI-powered data analysis application that allows users to upload datasets and interact with them through natural language queries. Built with FastAPI, LangChain/LangGraph, and React.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![LangChain](https://img.shields.io/badge/LangChain-Enabled-green)

## ✨ Features

- **📁 File Upload** - Support for CSV and Excel files
- **💬 Natural Language Queries** - Ask questions about your data in plain English
- **🤖 AI-Powered Analysis** - Leverages LangChain and LangGraph for intelligent data processing
- **📈 Interactive Visualizations** - Dynamic charts using Plotly
- **⚡ Real-time Updates** - WebSocket-based communication for streaming responses
- **🔧 Code Execution** - Generates and executes Python code for data analysis

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **LangChain & LangGraph** - AI agent orchestration
- **OpenAI** - LLM integration
- **Pandas** - Data manipulation
- **Plotly, Matplotlib, Seaborn** - Visualization libraries
- **Scikit-learn, Statsmodels** - Statistical analysis

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Plotly.js** - Interactive charts
- **Axios** - HTTP client

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- OpenAI API Key

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:5173`

## 📖 Usage

1. **Upload a Dataset** - Click the upload button and select a CSV or Excel file
2. **View Summary** - The AI will automatically generate a summary of your data
3. **Ask Questions** - Type natural language questions about your data
4. **Explore Visualizations** - View generated charts and insights

### Example Queries

- *"Show me the distribution of sales by region"*
- *"What's the correlation between price and quantity?"*
- *"Create a bar chart of top 10 products by revenue"*
- *"Summarize the key statistics of this dataset"*

## 📁 Project Structure

```
Data_Interpretor/
├── backend/
│   ├── app/
│   │   ├── agents/       # LangGraph agent definitions
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Configuration
│   │   ├── main.py       # FastAPI application
│   │   ├── models.py     # Pydantic models
│   │   ├── state.py      # State management
│   │   └── tools.py      # Agent tools
│   ├── uploads/          # Uploaded files storage
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── App.jsx       # Main app component
│   │   └── main.jsx      # Entry point
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) for the AI orchestration framework
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Plotly](https://plotly.com/) for interactive visualizations

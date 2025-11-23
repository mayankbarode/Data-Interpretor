import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.state import AgentState
from app.tools import execute_python_code, get_data_summary
from app.core.config import settings

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY)

def summarizer_node(state: AgentState):
    """Generates an intelligent LLM-based summary of the uploaded data."""
    print("DEBUG: --- Node: Summarizer ---")
    logger.info("--- Node: Summarizer ---")
    file_path = state['file_path']
    
    # Get technical data overview
    technical_summary = get_data_summary(file_path)
    print(f"DEBUG: Technical summary generated (len: {len(technical_summary)})")
    
    # Use LLM to generate theoretical insights
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert data analyst. Analyze the provided dataset information and generate a concise, insightful summary.

        Focus on:
        1. **Dataset Purpose**: What kind of data is this? What domain does it belong to?
        2. **Key Characteristics**: Main features, data types, and structure
        3. **Potential Insights**: What interesting patterns or relationships might exist?
        4. **Recommended Analyses**: What types of analysis would be most valuable?

        Output: 1. Summary
                2. Sample data

        Be concise, professional, and focus on theoretical understanding rather than just listing technical details.
        Avoid repeating raw technical information - instead provide meaningful interpretation."""),
        
        ("human", "Dataset Information:\n{data_info}")
    ])
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    chain = prompt | llm
    
    response = chain.invoke({"data_info": technical_summary})
    theoretical_summary = response.content
    
    print(f"DEBUG: Theoretical summary generated (len: {len(theoretical_summary)})")
    
    return {
        "df_head": technical_summary,  # Store technical info for later use
        "messages": [AIMessage(content=f"{theoretical_summary}")]
    }

def supervisor_node(state: AgentState):
    """Decides which agent to call next."""
    print("DEBUG: --- Node: Supervisor ---")
    logger.info("--- Node: Supervisor ---")
    messages = state['messages']
    last_message = messages[-1]
    
    # Simple router for now: if last message is from user, go to planner.
    # If from executor, go to summarizer (to show result) or end?
    # Actually, let's make it simpler: User -> Planner -> Coder -> Executor -> Response
    
    return {}

def planner_node(state: AgentState):
    """Breaks down the user query into steps."""
    print("DEBUG: --- Node: Planner ---")
    logger.info("--- Node: Planner ---")
    messages = state['messages']
    df_head = state.get('df_head', '')
    
    # Build conversation history for context
    # Filter to get only user and AI message pairs (skip system messages)
    conversation_history = []
    for msg in messages[:-1]:  # Exclude the current user message
        if hasattr(msg, 'content'):
            role = "User" if msg.type == "human" else "Assistant"
            conversation_history.append(f"{role}: {msg.content}")
    
    history_text = "\n".join(conversation_history[-6:]) if conversation_history else "No previous conversation"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a data analysis planner. Given a user query, dataframe summary, and conversation history, plan the steps to answer the query.
        
The available tool is python code execution on a dataframe 'df'.
IMPORTANT: Use the conversation history to understand context and references (like "that", "those", "previous", etc.)
Output a concise plan."""),
        ("user", """Data Summary:
{df_head}

Previous Conversation:
{history}

Current Query: {query}""")
    ])
    
    chain = prompt | llm
    current_query = messages[-1].content
    print(f"DEBUG: Invoking Planner LLM with query: {current_query}")
    logger.info(f"Invoking Planner LLM with query: {current_query}")
    response = chain.invoke({"df_head": df_head, "history": history_text, "query": current_query})
    print(f"DEBUG: Planner Output: {response.content}")
    logger.info(f"Planner Output: {response.content}")
    return {"messages": [response]}

def coder_node(state: AgentState):
    """Generates Python code based on the plan."""
    print("DEBUG: --- Node: Coder ---")
    logger.info("--- Node: Coder ---")
    messages = state['messages']
    df_head = state.get('df_head', '')
    plan = messages[-1].content
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Python data analyst. Write python code to analyze the dataframe 'df' based on the plan.

CRITICAL: Your code MUST always produce output. Never write code that doesn't show results.

FORMATTING RULES:
1. For DataFrame results (like top N rows, filtered data, aggregations):
   - Store in variable: result = df.head(10)
   - DO NOT print it - it will be auto-formatted as a table

2. For simple information (counts, column names, data types, shape):
   - Use print() to display the information
   - Examples:
     * print(f"Number of columns: {{len(df.columns)}}")
     * print(f"Column names: {{', '.join(df.columns.tolist())}}")
     * print(f"Dataset shape: {{df.shape}}")
     * print(f"Column types:\\n{{df.dtypes}}")

3. For statistics or single values:
   - Use print() with descriptive labels
   - Example: print(f"Average price: {{df['Price'].mean():.2f}}")

4. For plots/visualizations - USE PLOTLY WITH INSIGHTS:
   - Import: import plotly.express as px or import plotly.graph_objects as go
   - Use VIBRANT color schemes (NOT plain blue):
     * color_discrete_sequence=['#FF6B9D', '#C44569', '#8E44AD', '#3742FA']
     * color_continuous_scale='Viridis' or 'Sunset' or 'Turbo'
   - For EACH plot, print insights in this EXACT format:
     
     print("PLOT_INSIGHT_START")
     print("Title: [Short descriptive title]")
     print("Key Finding: [Main insight from this visualization]")
     print("Details: [2-3 sentences explaining what the plot shows]")
     print("PLOT_INSIGHT_END")
     
     fig = px.histogram(df, x='Price', color_discrete_sequence=['#FF6B9D'])
     fig.show()
   
   - Example with insights:
     print("PLOT_INSIGHT_START")
     print("Title: Price Distribution Analysis")
     print("Key Finding: Prices are right-skewed with most products under $100")
     print("Details: The histogram reveals that 70% of products fall in the $20-$80 range. There's a long tail extending to $500, indicating premium product segments. The distribution suggests a diverse pricing strategy.")
     print("PLOT_INSIGHT_END")
     fig = px.histogram(df, x='Price', nbins=30, color_discrete_sequence=['#FF6B9D'])
     fig.update_layout(template='plotly_white', title_font_size=18)
     fig.show()

REMEMBER:
- ALWAYS add PLOT_INSIGHT_START/END markers before each fig.show()
- Use colorful, vibrant palettes
- Insights must be data-driven and specific
- Do NOT use markdown blocks like ```python - just return raw code
The 'df' variable is already loaded."""),
        ("user", "Data Summary:\n{df_head}\n\nPlan: {plan}")
    ])
    
    chain = prompt | llm
    print("DEBUG: Invoking Coder LLM...")
    logger.info("Invoking Coder LLM...")
    response = chain.invoke({"df_head": df_head, "plan": plan})
    code = response.content.replace("```python", "").replace("```", "").strip()
    print(f"DEBUG: Coder Output: {code}")
    logger.info(f"Coder Output: {code}")
    return {"analysis_code": code, "messages": [AIMessage(content=f"Generated Code:\n```python\n{code}\n```")]}

def debugger_node(state: AgentState):
    """Refines code based on errors."""
    print("DEBUG: --- Node: Debugger ---")
    logger.info("--- Node: Debugger ---")
    messages = state['messages']
    code = state['analysis_code']
    error = state['error']
    df_head = state.get('df_head', '')
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Python debugging expert. The following code failed with an error.
        
        Your task is to FIX the code.
        1. Analyze the error message and the code.
        2. Rewrite the code to resolve the issue.
        3. Ensure the fixed code still fulfills the original goal.
        4. CRITICAL: Return ONLY the fixed python code. No markdown, no explanations.
        
        Common Fixes:
        - "Value of 'names' is not the name of a column...": Use df.index if trying to plot the index, or check column names.
        - "No module named...": Use standard libraries or pandas/matplotlib/seaborn/plotly only.
        - Syntax errors: Fix indentation or missing brackets.
        """),
        ("user", """Data Summary:
        {df_head}

        Failed Code:
        {code}

        Error Message:
        {error}

        Fix the code:""")
            ])
    
    chain = prompt | llm
    print("DEBUG: Invoking Debugger LLM...")
    logger.info("Invoking Debugger LLM...")
    response = chain.invoke({"df_head": df_head, "code": code, "error": error})
    fixed_code = response.content.replace("```python", "").replace("```", "").strip()
    
    print(f"DEBUG: Debugger Output: {fixed_code}")
    logger.info(f"Debugger Output: {fixed_code}")
    
    return {
        "analysis_code": fixed_code, 
        "messages": [AIMessage(content=f"Debugger Fixed Code:\n```python\n{fixed_code}\n```")]
    }

def executor_node(state: AgentState):
    """Executes the generated code."""
    print("DEBUG: --- Node: Executor ---")
    logger.info("--- Node: Executor ---")
    code = state['analysis_code']
    file_path = state['file_path']
    session_id = state.get('session_id', 'default')
    retry_count = state.get('retry_count', 0)
    
    result = execute_python_code(code, file_path, session_id)
    output = result['output']
    image = result['image']
    plotly_figures = result.get('plotly_figures', [])
    
    print(f"DEBUG: Executor Output: {output}")
    logger.info(f"Executor Output: {output}")
    
    # Check for execution errors
    if "Error executing code" in output or "System Error" in output:
        print(f"DEBUG: Execution failed. Retry count: {retry_count}")
        return {
            "error": output,
            "retry_count": retry_count + 1,
            "messages": [AIMessage(content=f"Execution Error (Attempt {retry_count+1}): {output}")]
        }
    
    # Success! Clear error state
    response_content = f"Execution Output:\n{output}"
    if image:
        response_content += "\n(Image generated)"
    if plotly_figures:
        response_content += f"\n({len(plotly_figures)} interactive plot(s) generated)"
        
    return {
        "analysis_output": output, 
        "image_path": image, 
        "plotly_html": plotly_figures, 
        "error": None, # Clear error
        "retry_count": 0, # Reset retries
        "messages": [AIMessage(content=response_content)]
    }

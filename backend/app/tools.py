import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io
import base64
from app.core.config import settings
import os

def get_data_summary(file_path: str) -> str:
    """Reads the file and returns an intelligent LLM-generated summary of the dataset."""
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            return "Unsupported file format."
        
        # Get basic technical info
        buffer = io.StringIO()
        df.info(buf=buffer)
        info_str = buffer.getvalue()
        
        # Get sample data
        head_str = df.head(5).to_string()
        
        # Get statistical summary for numeric columns
        numeric_summary = ""
        if len(df.select_dtypes(include=[np.number]).columns) > 0:
            numeric_summary = df.describe().to_string()
        
        # Return combined technical info for LLM analysis
        return f"""TECHNICAL DATA OVERVIEW:
                {info_str}

                SAMPLE DATA (First 5 rows):
                {head_str}

                {f'STATISTICAL SUMMARY:{chr(10)}{numeric_summary}' if numeric_summary else ''}"""
        
    except Exception as e:
        return f"Error reading file: {e}"

def execute_python_code(code: str, file_path: str, session_id: str = None) -> dict:
    """Executes the given python code on the dataframe and saves plots to session-specific directories."""
    try:
        # Import plotly for interactive charts
        import plotly.express as px
        import plotly.graph_objects as go
        
        # Load dataframe
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            return {"output": "Unsupported file format.", "image": None, "plotly_figures": []}

        # Prepare execution environment with Plotly support
        # CRITICAL: Set Plotly renderer to prevent opening browser tabs
        import plotly.io as pio
        pio.renderers.default = None  # Disable rendering to prevent tabs and avoid IPython requirement
        
        local_vars = {"df": df, "plt": plt, "sns": sns, "pd": pd, "np": np, "px": px, "go": go}
        
        # Capture stdout
        old_stdout = io.StringIO()
        # We need to redirect stdout to capture print statements
        import sys
        sys.stdout = old_stdout
        
        
        try:
            exec(code, {}, local_vars)
        except Exception as e:
            sys.stdout = sys.__stdout__
            return {"output": f"Error executing code: {e}", "image": None, "plotly_figures": []}
        
        sys.stdout = sys.__stdout__
        output = old_stdout.getvalue()
        
        # Parse insights from output (PLOT_INSIGHT_START/END markers)
        # Parse insights from output (PLOT_INSIGHT_START/END markers)
        plot_insights = []
        clean_output_lines = []
        lines = output.split('\n')
        i = 0
        while i < len(lines):
            if 'PLOT_INSIGHT_START' in lines[i]:
                insight = {"title": "", "key_finding": "", "details": ""}
                i += 1
                while i < len(lines) and 'PLOT_INSIGHT_END' not in lines[i]:
                    line = lines[i].strip()
                    # Handle bolding and case sensitivity
                    lower_line = line.lower()
                    if lower_line.startswith('title:') or lower_line.startswith('**title:**'):
                        insight['title'] = line.split(':', 1)[1].strip().replace('**', '')
                    elif lower_line.startswith('key finding:') or lower_line.startswith('**key finding:**'):
                        insight['key_finding'] = line.split(':', 1)[1].strip().replace('**', '')
                    elif lower_line.startswith('details:') or lower_line.startswith('**details:**'):
                        insight['details'] = line.split(':', 1)[1].strip().replace('**', '')
                    i += 1
                plot_insights.append(insight)
                # Skip the END marker
                i += 1
            else:
                clean_output_lines.append(lines[i])
                i += 1
        
        # Update output to exclude the insight blocks
        output = '\n'.join(clean_output_lines).strip()
        
        
        # Check for Plotly figures FIRST (interactive plots take priority)
        plotly_figures = []
        try:
            import plotly.graph_objects as go
            print(f"DEBUG: local_vars keys: {list(local_vars.keys())}")
            print(f"DEBUG: Checking for Plotly figures...")
            fig_index = 0
            for var_name, var_value in local_vars.items():
                print(f"DEBUG: Checking {var_name}: {type(var_value)}")
                if isinstance(var_value, (go.Figure,)):
                    print(f"DEBUG: Found Plotly figure: {var_name}")
                    # Convert Plotly figure to HTML
                    html_str = var_value.to_html(
                        include_plotlyjs='cdn',
                        config={'responsive': True, 'displayModeBar': True}
                    )
                    # Pair with insight if available
                    insight = plot_insights[fig_index] if fig_index < len(plot_insights) else {
                        "title": f"Visualization {fig_index + 1}",
                        "key_finding": "Data visualization",
                        "details": "Interactive plot for data analysis."
                    }
                    plotly_figures.append({
                        "html": html_str,
                        "insight": insight
                    })
                    fig_index += 1
            print(f"DEBUG: Total Plotly figures found: {len(plotly_figures)}")
        except Exception as e:
            print(f"Warning: Could not process Plotly figures: {e}")
            import traceback
            traceback.print_exc()
        
        # Check if there's a result DataFrame in local_vars
        # Common variable names for results: result, output, df_result, top, etc.
        result_df = None
        for var_name in ['result', 'output_df', 'df_result', 'top', 'summary']:
            if var_name in local_vars and isinstance(local_vars[var_name], pd.DataFrame):
                result_df = local_vars[var_name]
                break
        
        # If we found a DataFrame result, format it as markdown table
        if result_df is not None and not result_df.empty:
            # Convert DataFrame to markdown table (no index to avoid alignment issues)
            markdown_table = result_df.to_markdown(index=False)
            # Use ONLY the markdown table, ignore any print output to avoid duplication
            output = markdown_table
        elif output.strip():
            # Try to detect if the output looks like a DataFrame print
            # and hasn't been formatted yet
            lines = output.strip().split('\n')
            if len(lines) > 2:
                # Check if it looks like DataFrame output (has consistent spacing/columns)
                first_line = lines[0].strip()
                # If it has multiple words separated by spaces, might be a table
                if len(first_line.split()) > 2:
                    # Attempt to parse and reformat
                    try:
                        # Try to recreate the output in a better format
                        # This is a heuristic - if the code printed a DataFrame,
                        # we should have caught it above
                        pass
                    except:
                        pass
        
        # Check for plots and save them
        image_data = None
        fig_nums = plt.get_fignums()
        if fig_nums:
            # If multiple plots were created, we need to save them all
            if len(fig_nums) > 1:
                # Create a combined figure with all plots in a vertical layout
                import math
                from matplotlib.figure import Figure
                from matplotlib.backends.backend_agg import FigureCanvasAgg
                
                # Calculate grid dimensions (prefer vertical stacking)
                n_plots = len(fig_nums)
                cols = min(2, n_plots)  # Max 2 columns
                rows = math.ceil(n_plots / cols)
                
                # Create new combined figure
                combined_fig = Figure(figsize=(12 * cols, 6 * rows))
                canvas = FigureCanvasAgg(combined_fig)
                
                # Copy each plot into the combined figure
                for idx, fig_num in enumerate(fig_nums):
                    fig = plt.figure(fig_num)
                    ax_orig = fig.gca()
                    
                    # Add subplot to combined figure
                    ax_new = combined_fig.add_subplot(rows, cols, idx + 1)
                    
                    # Copy plot elements (this is a simplified approach)
                    # For histogram/line plots, we get the data and replot
                    for line in ax_orig.get_lines():
                        ax_new.plot(line.get_xdata(), line.get_ydata(), 
                                   color=line.get_color(), linewidth=line.get_linewidth())
                    
                    for patch in ax_orig.patches:
                        from matplotlib.patches import Rectangle
                        if isinstance(patch, Rectangle):
                            ax_new.add_patch(Rectangle(
                                (patch.get_x(), patch.get_y()),
                                patch.get_width(), patch.get_height(),
                                facecolor=patch.get_facecolor(),
                                edgecolor=patch.get_edgecolor()
                            ))
                    
                    # Copy labels and title
                    ax_new.set_title(ax_orig.get_title())
                    ax_new.set_xlabel(ax_orig.get_xlabel())
                    ax_new.set_ylabel(ax_orig.get_ylabel())
                    ax_new.set_xlim(ax_orig.get_xlim())
                    ax_new.set_ylim(ax_orig.get_ylim())
                
                combined_fig.tight_layout()
                
                # Save combined figure
                if session_id:
                    plots_dir = os.path.join(settings.UPLOAD_DIR, 'plots', session_id)
                    os.makedirs(plots_dir, exist_ok=True)
                    
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    plot_filename = f"plot_combined_{timestamp}.png"
                    plot_path = os.path.join(plots_dir, plot_filename)
                    
                    combined_fig.savefig(plot_path, format='png', dpi=100, bbox_inches='tight')
                    print(f"Combined plot ({n_plots} visualizations) saved to: {plot_path}")
                
                # Encode combined figure as base64
                img_buffer = io.BytesIO()
                combined_fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
                img_buffer.seek(0)
                image_data = base64.b64encode(img_buffer.read()).decode('utf-8')
                
            else:
                # Single plot - use original logic
                if session_id:
                    plots_dir = os.path.join(settings.UPLOAD_DIR, 'plots', session_id)
                    os.makedirs(plots_dir, exist_ok=True)
                    
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    plot_filename = f"plot_{timestamp}.png"
                    plot_path = os.path.join(plots_dir, plot_filename)
                    
                    plt.savefig(plot_path, format='png', dpi=100, bbox_inches='tight')
                    print(f"Plot saved to: {plot_path}")
                
                # Encode as base64 for immediate display
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
                img_buffer.seek(0)
                image_data = base64.b64encode(img_buffer.read()).decode('utf-8')
            
            plt.close('all')  # Close all figures to free memory
            
        # Determine appropriate output message
        if not output.strip():
            if plotly_figures:
                descriptions = []
                for fig in plotly_figures:
                    insight = fig.get('insight', {})
                    title = insight.get('title', 'Visualization')
                    # Use key finding as the primary description, fallback to details
                    desc = insight.get('key_finding') or insight.get('details') or 'Interactive plot.'
                    descriptions.append(f"**{title}**: {desc}")
                
                output = "📊 **Generated Visualizations:**\n" + "\n".join(f"- {d}" for d in descriptions)
            elif image_data:
                output = "📊 Visualization generated successfully!"
            else:
                output = "Code executed successfully (no output)"
        
        return {"output": output, "image": image_data, "plotly_figures": plotly_figures}

    except Exception as e:
        return {"output": f"System Error: {e}", "image": None, "plotly_figures": []}


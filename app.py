from flask import Flask, render_template, request
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for rendering to files
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Load Kepler data
def load_data():
    return pd.read_csv('data.csv')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    df = load_data()
    
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        search_column = request.form.get('search_column')
        
        # Check for empty search inputs
        if search_term and search_column in df.columns:
            # Perform exact match search
            results = df[df[search_column].astype(str) == search_term]
        else:
            results = pd.DataFrame()  # Empty DataFrame if no valid search

        return render_template('search.html', 
                                results=results.to_dict('records'), 
                                columns=df.columns.tolist())
    
    return render_template('search.html', 
                            columns=df.columns.tolist())

@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    df = load_data()
    
    if request.method == 'POST':
        # Get selected parameters from the form
        x_axis = request.form.get('x_axis')
        y_axis = request.form.get('y_axis')
        graph_type = request.form.get('graph_type')
        
        # Create the plot based on user selection
        plt.figure(figsize=(10, 6))
        
        if graph_type == 'scatter':
            plt.scatter(df[x_axis], df[y_axis], alpha=0.6)
        elif graph_type == 'line':
            plt.plot(df[x_axis], df[y_axis], marker='o')
        elif graph_type == 'bar':
            df.groupby(x_axis)[y_axis].mean().plot(kind='bar', figsize=(10, 6))
        
        plt.title(f'{y_axis} vs {x_axis}')
        plt.xlabel(x_axis)
        plt.ylabel(y_axis)
        
        # Save plot to base64
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        
        # Basic statistics
        stats = {
            'Total Planets': len(df),
            'Confirmed Planets': len(df[df['koi_disposition'] == 'CONFIRMED']),
            'Candidate Planets': len(df[df['koi_disposition'] == 'CANDIDATE']),
            'Average Stellar Radius': df['koi_srad'].mean()
        }
        
        return render_template('analysis.html', plot_url=plot_url, 
                               stats=stats)
    
    # If GET request, show basic analysis
    return render_template('analysis.html')

if __name__ == '__main__':
    app.run(debug=True)
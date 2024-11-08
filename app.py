from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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
        
        # Perform search
        results = df[df[search_column].astype(str).str.contains(search_term, case=False)]
        
        return render_template('search.html', 
                                results=results.to_dict('records'), 
                                columns=df.columns.tolist())
    
    return render_template('search.html', 
                            columns=df.columns.tolist())

@app.route('/analysis')
def analysis():
    df = load_data()
    
    # Create scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(df['koi_disposition'], df['koi_srad'], alpha=0.6)
    plt.title('Kepler Exoplanet Disposition vs srad')
    plt.xlabel('Disposition')
    plt.ylabel('Insolation')
    
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
    
    return render_template('analysis.html', 
                           plot_url=plot_url, 
                           stats=stats)

if __name__ == '__main__':
    app.run(debug=True)
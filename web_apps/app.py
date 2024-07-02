from flask import Flask, render_template, request
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.io as pio
import plotly.figure_factory as ff

app = Flask(__name__)

def plot_sentiment_and_stock(file_path, stock_symbol):
    # Load the data
    data = pd.read_csv(file_path)

    # Convert 'Date' to datetime
    data['Date'] = pd.to_datetime(data['Date'])

    # Filter data from 2021 to the most recent date
    data = data[data['Date'] >= '2021-01-01']

    # Sort the data by date from oldest to newest
    data.sort_values(by='Date', inplace=True)

    # Create subplots: one for sentiment trends and another for stock price
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, subplot_titles=("Sentiment Trends", "Stock Price Movements"))

    # Add traces for sentiment scores to the first subplot
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Negative'], mode='lines', name='Negative Sentiment'), row=1, col=1)
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Nuetral'], mode='lines', name='Neutral Sentiment'), row=1, col=1)
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Positive'], mode='lines', name='Positive Sentiment'), row=1, col=1)

    # Add a trace for stock price to the second subplot
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Stock Price'], mode='lines', name='Stock Price'), row=2, col=1)

    # Update layout
    fig.update_layout(
        title= f"{stock_symbol} Sentiment Trends and Stock Price Movements",
        height=600
    )

    # Convert plot to HTML
    plot_html = pio.to_html(fig, full_html=False)

    return plot_html, data  # Also return the data frame

def plot_correlation_heatmap(file_path):
    # Load the data
    data = pd.read_csv(file_path)

    # Calculate correlation matrix
    columns = ['Negative', 'Nuetral', 'Positive', 'Stock Price']
    correlation_matrix = data[columns].corr()

    # Round correlation matrix to 2 decimal places
    correlation_matrix = correlation_matrix.round(2)

    # Create heatmap
    heatmap = ff.create_annotated_heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns.tolist(),
        y=correlation_matrix.columns.tolist(),
        colorscale='RdYlGn'
    )

    heatmap.update_layout(
        title='Correlation Matrix',
        height=600
    )

    # Convert heatmap to HTML
    heatmap_html = pio.to_html(heatmap, full_html=False)

    return heatmap_html

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    stock_symbol = request.form['stock_symbol']
    if stock_symbol == 'MSFT':
        file_path = 'https://raw.githubusercontent.com/HAZCHEM234/My_data/main/UpdateMSFT__2024-06-30_data.csv'
    elif stock_symbol == 'AAPL':
        file_path = 'https://raw.githubusercontent.com/HAZCHEM234/My_data/main/UpdateAAPL__2024-06-29_data.csv'
    elif stock_symbol == 'ADBE':
        file_path = 'https://raw.githubusercontent.com/HAZCHEM234/My_data/main/UpdateADBE__2024-07-02_data.csv'
    elif stock_symbol == 'V':
        file_path = 'https://raw.githubusercontent.com/HAZCHEM234/My_data/main/UpdateV__2024-07-02_data.csv'
    else:
        return "Invalid stock symbol!"

    plot_html, data = plot_sentiment_and_stock(file_path, stock_symbol)
    heatmap_html = plot_correlation_heatmap(file_path)

    # Explanation of correlation coefficients
    correlation_explanation = """
    <h3>Explanation of Correlation Coefficients</h3>
    <p>Correlation coefficients (r) range from -1 to 1, indicating the strength and direction of the relationship between two variables:</p>
    <ul>
        <li><b>+1:</b> Perfect positive correlation. When one variable increases, the other variable increases proportionally.</li>
        <li><b>+0.7 to +0.9:</b> Strong positive correlation. An increase in one variable tends to correspond with a strong increase in the other.</li>
        <li><b>+0.4 to +0.6:</b> Moderate positive correlation. One variable increases with the other, but less consistently than stronger correlations.</li>
        <li><b>+0.1 to +0.3:</b> Weak positive correlation. There's a slight tendency for one variable to increase when the other increases.</li>
        <li><b>0:</b> No correlation. There's no discernible relationship between the variables.</li>
        <li><b>-0.1 to -0.3:</b> Weak negative correlation. One variable tends to decrease slightly when the other increases.</li>
        <li><b>-0.4 to -0.6:</b> Moderate negative correlation. An increase in one variable generally corresponds with a decrease in the other.</li>
        <li><b>-0.7 to -0.9:</b> Strong negative correlation. When one variable increases, the other tends to decrease significantly.</li>
        <li><b>-1:</b> Perfect negative correlation. An increase in one variable leads to a proportional decrease in the other.</li>
    </ul>
    """

    return render_template('plot.html', plot_html=plot_html, heatmap_html=heatmap_html, correlation_explanation=correlation_explanation, stock_symbol=stock_symbol, data_table=data.to_html())

if __name__ == '__main__':
    app.run(debug=True)

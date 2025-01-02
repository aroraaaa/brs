from flask import Flask, render_template, request
import pickle
import numpy as np

# Load the required pickled objects
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

# Ensure all image URLs use HTTPS
popular_df['Image-URL-M'] = popular_df['Image-URL-M'].str.replace('http://', 'https://', regex=False)
books['Image-URL-M'] = books['Image-URL-M'].str.replace('http://', 'https://', regex=False)

app = Flask(__name__)

# Home route
@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

# Recommendation UI route
@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

# Route to get book recommendations based on user input
@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    try:
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(
            list(enumerate(similarity_scores[index])),
            key=lambda x: x[1],
            reverse=True
        )[1:5]

        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
            data.append(item)

        if not data:
            return render_template('recommend.html', data=None, message="No recommendations found for this book.")
        
        return render_template('recommend.html', data=data)
    except IndexError:
        return render_template('recommend.html', data=None, message="No data available for this book.")


if __name__ == '__main__':
    app.run(debug=True)

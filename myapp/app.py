from flask import Flask, jsonify, request, redirect, url_for, render_template
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Influencer_Dataset"
mongo = PyMongo(app)

@app.route('/')
def home():
    # declare profiles and turn it into a list
    profiles = mongo.db.profiles.find()  
    profiles_list = list(profiles)
    # print("Fetched profiles:", profiles_list)  
    return render_template('index.html', profiles=profiles_list)

@app.route('/new', methods=['GET', 'POST'])
def new_profile():
    if request.method == 'POST':
        # Insert new profile data into the database
        profile_data = {
        }
        mongo.db.profiles.insert_one(profile_data)
        return redirect(url_for('home'))
    return render_template('create_profile.html') 

@app.route('/create', methods=['POST'])
def create_profile():
    # Extract form data
    profile_data = {
        'account': request.form.get('account'),
        'followers': request.form.get('followers', type=int),
        'posts_count': request.form.get('posts_count', type=int),
        'is_business_account': request.form.get('is_business_account') == 'true',
        'is_professional_account': request.form.get('is_professional_account') == 'true',
        'is_verified': request.form.get('is_verified') == 'true',
        'avg_engagement': request.form.get('avg_engagement', type=float),
        'external_url': request.form.get('external_url'),
        'biography': request.form.get('biography'),
        'business_category_name': request.form.get('business_category_name'),
        'category_name': request.form.get('category_name'),
        'following': request.form.get('following', type=int)
    }
    
    # Insert new profile into the 'profiles' collection
    mongo.db.profiles.insert_one(profile_data)
    return redirect(url_for('home'))

@app.route('/update/<profile_id>', methods=['GET', 'POST'])
def update_profile(profile_id):
    # If the method is POST, it means that the form has been submitted and we should process the update.
    if request.method == 'POST':
        # Extract the updated data from the form submission.
        updated_data = {
            'account': request.form.get('account'),
            'followers': request.form.get('followers', type=int),
            'posts_count': request.form.get('posts_count', type=int),
            'is_business_account': request.form.get('is_business_account') in ['true', 'on', True],
            'is_professional_account': request.form.get('is_professional_account') in ['true', 'on', True],
            'is_verified': request.form.get('is_verified') in ['true', 'on', True],
            'avg_engagement': request.form.get('avg_engagement', type=float),
            'external_url': request.form.get('external_url'),
            'biography': request.form.get('biography'),
            'business_category_name': request.form.get('business_category_name'),
            'category_name': request.form.get('category_name'),
            'following': request.form.get('following', type=int),
        }
        # Perform the update in the database.
        mongo.db.profiles.update_one({'_id': ObjectId(profile_id)}, {'$set': updated_data})
        return redirect(url_for('home'))

    # If the method is GET, it means that the user wants to see the form to edit a profile.
    elif request.method == 'GET':
        # Find the existing profile data from the database and pass to template
        profile = mongo.db.profiles.find_one({'_id': ObjectId(profile_id)})
        if profile:
            return render_template('update_profile.html', profile=profile)
        else:
            return "Profile not found", 404

    return "Method not allowed", 405 


@app.route('/delete/<profile_id>', methods=['POST'])
def delete_profile(profile_id):
    profile_id = ObjectId(profile_id)
    
    mongo.db.profiles.delete_one({'_id': profile_id})
    return redirect(url_for('home'))

@app.route('/posts/<profile_id>', methods=['GET'])
def get_posts(profile_id):
    profile = mongo.db.profiles.find_one({'_id': ObjectId(profile_id)})
    return jsonify(profile['posts'])

@app.route('/posts/add/<profile_id>', methods=['POST'])
def add_post_to_profile(profile_id):
    # Add a post to a profile's 'posts' list
    new_post = request.get_json()
    mongo.db.profiles.update_one({'_id': ObjectId(profile_id)}, {'$push': {'posts': new_post}})
    return redirect(url_for('get_posts', profile_id=profile_id))
profiles = mongo.db.get_collection('profiles').find()

@app.route('/search')
def search():
    query = request.args.get('query')
    # Perform a case-insensitive search for profiles where 'account' matches 'query'
    results = mongo.db.profiles.find({"account": {"$regex": query, "$options": "i"}})
    return render_template('search_results.html', profiles=list(results))

@app.route('/debug')
def debug_db():
    try:
        # Attempt to fetch one document from the 'profiles' collection
        profile = mongo.db.profiles.find_one()
        return str(profile)
    except Exception as e:
        return "Error accessing the collection: " + str(e)


if __name__ == '__main__':
    app.run(debug=True)

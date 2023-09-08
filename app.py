from flask import request, jsonify, render_template, redirect
from models import app,db,Posts
import json

# Endpoint ke halaman index
@app.route('/')
def index():
    # Kirim data posts ke halaman HTML
    articles = Posts.query.all()
    return render_template('index.html',articles = articles)

#Endpoint ke halaman edit artikel
@app.route('/editarticle/<int:id>')
def edit(id):
    # Kirim data post dengan id ke halaman edit
    response = show_byid(id)
    article = json.loads(response.data)
    return render_template('editarticle.html', article=article, id=id)

# Endpoint ke halaman hapus artikel
@app.route('/hapusarticle/<int:id>')
def delete(id):
    # Kirim data post dengan id ke fungsi delete
    delete_article(id)
    return redirect(request.referrer)

# Endpoint ke halaman add artikel
@app.route('/addarticle/')
def add():
    # Redirect ke halaman add artikel
    return render_template('addnew.html')

# Endpoint ke halaman preview artikel
@app.route('/showarticle/<int:id>')
def show(id):
    # Ambil data dari fungsi show_byid menggunakan parameter id
    response = show_byid(id)
    article = json.loads(response.data)
    return render_template('preview.html', article=article)

# Endpoint untuk menerima request dengan method POST di URL /article
@app.route('/article/', methods=['POST'])
def create_article():
    # Mengambil nilai dari request json
    dtitle = request.json['Title']
    dcontent = request.json['Content']
    dcategory = request.json['Category']
    dstatus = request.json['Status']

    # Validate data
    message, status = validate_post_data(dtitle, dcontent, dcategory, dstatus)
    if message is not None:
        return jsonify(message), status

    # Mengembalikan response dengan data yang telah berhasil disimpan
    post = Posts(title=dtitle, content=dcontent,
                      category=dcategory, status=dstatus)

    db.session.add(post)
    db.session.commit()

    return jsonify({'success': True}), 201

# Memastikan tipe konten data adalah json sebelum dikirim sebagai request 
@app.before_request
def before_request():
    if request.headers.get('Content-Type') == 'application/json':
        request.data = request.get_json()

# Fungsi untuk mevalidasi data dengan atribut title, content, category, dan status
def validate_post_data(title, content, category, status):
    if not title or len(title) < 20:
        return {'message': 'Title must be at least 20 characters'}, 400

    if not content or len(content) < 200:
        return {'message': 'Content must be at least 200 characters'}, 400

    if not category or len(category) < 3:
        return {'message': 'Category must be at least 3 characters'}, 400

    if status not in ['Publish', 'Draft', 'Thrash']:
        return {'message': 'Invalid status'}, 400

    return None, None

# Fungsi untuk mevalidasi data sekaligus mengupdate dengan atribut title, content, category, dan status
def validate_post_data_and_update(title, content, category, status, article):
    if title is None or len(title) < 20:
        errorCheck+=1
        if (title is not None):
            return {'message': 'Title must be at least 20 characters'}, 401
    else :
        article.title = title

    if content is None or len(content) < 200:
        if (content is not None):
            return {'message': 'Content must be at least 200 characters'}, 401
    else :
        article.content = content

    if category is None or len(category) < 3:
        if(category is not None):
            return {'message': 'Content must be at least 200 characters'}, 401
    else :
        article.category = category

    if status is None or status not in ['Publish', 'Draft', 'Thrash']:
        if (status is not None):
            return {'message': 'Invalid status'}, 401
    else :
        article.status = status
    return None, None

# Endpoint untuk menerima data dengan parameter limit dan offset
@app.route('/article/<int:limit>/<int:offset>', methods=['GET'])
def get_articles(limit, offset):
    # Memasukkan data ke variable articles
    articles = Posts.query.with_entities(Posts.title, Posts.content, Posts.category, Posts.status).limit(limit).offset(offset).all()
    result = []
    for article in articles:
        result.append({
            'Title': article.title,
            'Content': article.content,
            'Category': article.category,
            'Status': article.status
        })
    return jsonify(result)

# Endpoint untuk menerima data dengan parameter id
@app.route('/article/<int:id>', methods=['GET'])
def show_byid(id):
    #Memasukkan data ke variable articles
    article = Posts.query.with_entities(
        Posts.title, Posts.content, Posts.category, Posts.status).filter_by(id=id).first()
    if article:
        return jsonify({
            'Title': article.title,
            'Content': article.content,
            'Category': article.category,
            'Status': article.status
        })
    else:
        return jsonify({'message': 'Article not found'})

# Endpoint untuk mengupdate data dengan parameter id
@app.route('/article/<int:id>', methods=['POST', 'PUT', 'PATCH'])
def update_article(id):
    # Mengambil nilai dari data
    try:
        if request.json is not None :
            article = Posts.query.get(id)
            dtitle = request.json.get('Title', None)
            dcontent = request.json.get('Content', None)
            dcategory = request.json.get('Category', None)
            dstatus = request.json.get('Status', None)
            # Validate data
            message, status = validate_post_data_and_update(
                dtitle, dcontent, dcategory, dstatus, article)
            if message is not None:
                return jsonify(message), status

            db.session.commit()

        return jsonify({'message': 'Article updated successfully'})
    except Exception as e:
        # Jika menerima error code 400 ataupun json encode fail yang dimana tidak ditemukan request json
        # dan metode yang digunakan adalah POST maka akan dialihkan ke fungsi delete article
        if hasattr(e, 'code') and e.code == 400:
            if(request.method == 'POST'):
                delete_article(id)
                return jsonify({'message': 'Article deleted successfully.'})
        return jsonify({"Error decoding JSON:", e})

# Endpoint untuk menghapus data dengan parameter id
@app.route('/article/<int:id>', methods=['DELETE'])
def delete_article(id):
    article = Posts.query.filter_by(id=id).first()
    if article:
        db.session.delete(article)
        db.session.commit()
        return jsonify({'message': 'Article deleted successfully.'})
    else:
        return jsonify({'message': 'Article not found.'}), 404

if __name__ == '__main__':
    app.run(debug=True)

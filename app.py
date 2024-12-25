from flask import Flask, render_template
import os

from upload import upload_bp
app = Flask(__name__,
            static_folder='static')

app.config['SECRET_KEY'] = os.urandom(24)  
app.config['VIDEO_FOLDER'] = 'video'
app.config['SPARSE_RECONSTRUCTION'] = 'sparse_reconstruction'
app.config['DENSE_RECONSTRUCTION'] = 'dense_reconstruction'

if not os.path.exists(app.config['VIDEO_FOLDER']):
    os.makedirs(app.config['VIDEO_FOLDER'])

if not os.path.exists(app.config['SPARSE_RECONSTRUCTION']):
    os.makedirs(app.config['SPARSE_RECONSTRUCTION'])

# Register Blueprints
app.register_blueprint(upload_bp, url_prefix='/')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

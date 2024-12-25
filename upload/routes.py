from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
import os

from . import upload_bp
from utils import execute_command

@upload_bp.route('/execute', methods=['POST'])
def execute():
    cmd = request.form['command']
    output = execute_command(cmd)
    return jsonify({'output': output})

@upload_bp.route('/upload')
def uploadPage():
    # Get the list of video files in the upload folder
    video_files = []
    if os.path.exists(current_app.config['VIDEO_FOLDER']):
        video_files = [f for f in os.listdir(current_app.config['VIDEO_FOLDER']) if f.endswith(('mp4', 'avi', 'mov', 'mkv'))]
    
    # Print to check the video files
    print('video_files:', video_files)
    
    return render_template('upload/index.html', video_files=video_files)

@upload_bp.route('/upload_video', methods=['GET', 'POST'])
def upload_video():
    # List the video files before upload
    video_files = []
    if os.path.exists(current_app.config['VIDEO_FOLDER']):
        video_files = [f for f in os.listdir(current_app.config['VIDEO_FOLDER']) if f.endswith(('mp4', 'avi', 'mov', 'mkv'))]
    
    if os.path.exists(current_app.config['SPARSE_RECONSTRUCTION']):
        subdirectories = [d for d in os.listdir(current_app.config['SPARSE_RECONSTRUCTION']) if os.path.isdir(os.path.join(current_app.config['SPARSE_RECONSTRUCTION'], d))]
    else:
        subdirectories = []

    if request.method == 'POST':
        if 'video' not in request.files:
            flash('No file part')
            return redirect(request.url)
        video = request.files['video']
        if video.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if video:
            filename = video.filename
            video.save(os.path.join(current_app.config['VIDEO_FOLDER'], filename))
            flash('Video uploaded successfully!')

            # After uploading, redirect to the upload page to view the list
            return redirect(url_for('upload_bp.uploadPage'))  # Redirect after upload

    return render_template('upload/index.html', video_files=video_files, subdirectories=subdirectories)

@upload_bp.route('/generate_sparse_reconstruction', methods=['POST'])
def generate_sparse_reconstruction():
    # Get the selected video file from the form
    selected_video = request.form.get('selected_video')
    
    if not selected_video:
        flash('No video selected for reconstruction.')
        return redirect(url_for('upload_bp.uploadPage'))
    
    # Construct the command to execute
    video_path = os.path.join(current_app.config['VIDEO_FOLDER'], selected_video)
    output_dir = os.path.join(current_app.config['SPARSE_RECONSTRUCTION'], selected_video)  # Customize as needed
    cmd = f"ns-process-data video --data {video_path} --output-dir {output_dir}"
    
    # Execute the command
    try:
        output = execute_command(cmd)  # Assuming `execute_command` handles subprocess calls
        flash(f'Sparse reconstruction executed: {output}')
    except Exception as e:
        flash(f'Error during reconstruction: {e}')
    
    # Redirect back to the upload page
    return redirect(url_for('upload_bp.uploadPage'))

@upload_bp.route('/generate_dense_reconstruction', methods=['POST'])
def generate_dense_reconstruction():
    # Get the selected video file from the form
    selected_subdirectory = request.form.get('selected_subdirectory')
    
    if not selected_subdirectory:
        flash('No video selected for reconstruction.')
        return redirect(url_for('upload_bp.uploadPage'))
    
    # Construct the command to execute
    sparse_path = os.path.join(current_app.config['SPARSE_RECONSTRUCTION'], selected_subdirectory)
    dense_dir = os.path.join(current_app.config['DENSE_RECONSTRUCTION'], selected_subdirectory)  # Customize as needed
    cmd = f"ns-train splatfacto-w --data {sparse_path} --viewer.make-share-url True"
    
    # Execute the command
    try:
        output = execute_command(cmd)  # Assuming `execute_command` handles subprocess calls
        flash(f'Dense reconstruction executed: {output}')
    except Exception as e:
        flash(f'Error during reconstruction: {e}')
    
    # Redirect back to the upload page
    return redirect(url_for('upload_bp.uploadPage'))
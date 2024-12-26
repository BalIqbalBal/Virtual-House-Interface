from flask import render_template, request, redirect, url_for, flash, jsonify, current_app, Response, stream_with_context
import os
import json
import time
import threading

from . import upload_bp
from utils import execute_command_in_background, execute_command, get_cmd_status, cmd_status


@upload_bp.route('/execute', methods=['GET'])
def execute():
    cmd = request.args.get('command')  # Get the command from the query parameters
    
    def generate():
        for line in execute_command(cmd):
            yield f"data: {json.dumps({'output': line})}\n\n"
        yield f"data: {json.dumps({'status': 'complete'})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream'
    )

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

# Handle POST and GET requests for task execution and status
@upload_bp.route('/generate_sparse_reconstruction', methods=['POST', 'GET'])
def generate_sparse_reconstruction():
    if request.method == 'POST':
        # Handle POST: Start the command execution
        video_files = request.form.get('selected_video')
        
        if not video_files:
            return jsonify({'status': 'error', 'message': 'No file selected for processing.'})
        
        file_path = os.path.join(current_app.config['VIDEO_FOLDER'], video_files)
        output_dir = os.path.join(current_app.config['VIDEO_FOLDER'], video_files)
        cmd = f"process-data --input {file_path} --output {output_dir}"
        
        # Generate a unique task_id for this request (could use a UUID or timestamp)
        task_id = video_files

        # Start the background task
        background_thread = threading.Thread(target=execute_command_in_background, args=(cmd, task_id))
        background_thread.start()

        # Return the task ID so the client can check progress
        return jsonify({'status': 'success', 'task_id': task_id})

    elif request.method == 'GET':
        # Handle GET: Stream the status using SSE
        task_id = request.args.get('task_id')
        
        if task_id not in cmd_status:
            return jsonify({'status': 'error', 'message': 'Invalid task ID or task not found.'})
        
        def generate():
            while task_id in cmd_status:
                status = get_cmd_status(task_id)
                yield f"data: {json.dumps(status)}\n\n"
                time.sleep(1)  # Sleep for a moment to avoid overwhelming the client with too many messages
                
                # Check if the status is "complete", then break out of the loop to stop SSE
                if status.get('status') == 'complete':
                    break
        
        return Response(generate(), mimetype='text/event-stream')

@upload_bp.route('/generate_dense_reconstruction', methods=['POST', 'GET'])
def generate_dense_reconstruction():
    if request.method == 'POST':
        # Handle POST: Start the command execution for dense reconstruction
        selected_subdirectory = request.form.get('selected_subdirectory')
        
        if not selected_subdirectory:
            return jsonify({'status': 'error', 'message': 'No video selected for reconstruction.'})
        
        sparse_path = os.path.join(current_app.config['SPARSE_RECONSTRUCTION'], selected_subdirectory)
        dense_dir = os.path.join(current_app.config['DENSE_RECONSTRUCTION'], selected_subdirectory)  # Customize as needed
        cmd = f"ns-train splatfacto-w --data {sparse_path} --viewer.make-share-url True"
        
        # Generate a unique task_id for this request
        task_id = selected_subdirectory

        # Start the background task for dense reconstruction
        background_thread = threading.Thread(target=execute_command_in_background, args=(cmd, task_id))
        background_thread.start()

        # Return the task ID so the client can check progress
        return jsonify({'status': 'success', 'task_id': task_id})

    elif request.method == 'GET':
        # Handle GET: Stream the status using SSE for dense reconstruction
        task_id = request.args.get('task_id')
        
        if task_id not in cmd_status:
            return jsonify({'status': 'error', 'message': 'Invalid task ID or task not found.'})
        
        def generate():
            while task_id in cmd_status:
                status = get_cmd_status(task_id)
                yield f"data: {json.dumps(status)}\n\n"
                time.sleep(1)  # Sleep for a moment to avoid overwhelming the client with too many messages
                
                # Check if the status is "complete", then break out of the loop to stop SSE
                if status.get('status') == 'complete':
                    break
        
        return Response(generate(), mimetype='text/event-stream')


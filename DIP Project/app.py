from flask import Flask, render_template, request, send_from_directory, url_for
import cv2
import numpy as np
import os

app = Flask(__name__)

# Path for uploaded images
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Homepage route
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle image upload and background removal
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'bg-image' not in request.files or 'target-image' not in request.files:
        return "Please upload both background and target images."

    bg_file = request.files['bg-image']
    target_file = request.files['target-image']

    if bg_file.filename == '' or target_file.filename == '':
        return "Please upload both background and target images."

    # Save the uploaded files
    background_path = os.path.join(app.config['UPLOAD_FOLDER'], 'background.png')
    target_path = os.path.join(app.config['UPLOAD_FOLDER'], 'target.png')
    bg_file.save(background_path)
    target_file.save(target_path)

    # Call the background removal function
    foreground = remove_background(background_path, target_path)

    # Save and send the result
    result_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.png')
    cv2.imwrite(result_path, foreground)

    # Get the result image URL
    result_url = url_for('uploaded_file', filename='result.png')

    return render_template('result.html', result_url=result_url)

# Background removal function
def remove_background(background_path, target_path):
    # Load and resize images
    background = cv2.imread(background_path)
    target = cv2.imread(target_path)
    background = cv2.resize(background, (640, 480))
    target = cv2.resize(target, (640, 480))

    # Get color difference
    diff = cv2.absdiff(background, target)
    diff_sum = np.sum(diff, axis=2)  # Sum across color channels

    # Apply threshold
    _, mask = cv2.threshold(diff_sum.astype(np.uint8), 50, 255, cv2.THRESH_BINARY)

    # Convert to uint8
    mask = np.uint8(mask)

    # Morphological operations
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)  # Fill small holes
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)   # Remove noise

    # Optional: Smooth edges (blur mask)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)

    # Extract foreground
    foreground = cv2.bitwise_and(target, target, mask=mask)

    return foreground


# Route to serve the uploaded file (result)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)

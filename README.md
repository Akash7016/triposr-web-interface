# TripoSR Web Interface

A Flask web application that provides a user-friendly interface for converting 2D images to 3D models using TripoSR. Upload an image and watch the real-time processing progress as it generates downloadable 3D mesh files.

## Features

- 🖼️ **Image Upload**: Drag & drop or browse for JPG/PNG images
- 📊 **Real-time Progress**: Live progress bar and detailed processing logs
- 🎯 **3D Generation**: Powered by TripoSR for high-quality 3D mesh creation
- ⬬ **Download Results**: Direct download of OBJ files and textures
- 🎨 **Modern UI**: Clean, responsive interface with futuristic styling

## Project Structure

```
streamlit-app/
├── src/
│   └── app.py               # Main Flask application with UI and backend
├── static/
│   ├── uploads/             # Uploaded images storage
│   └── bg.jpg              # Background image for UI
├── requirements.txt         # Python dependencies
├── config.toml             # Configuration settings
└── README.md               # This documentation
```

## Prerequisites

- Python 3.8+
- TripoSR installed at `C:\ai3d\TripoSR\`
- PowerShell scripts: `run_fast.ps1` and `launch_picker.ps1`
- Virtual environment set up for TripoSR

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd streamlit-app
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up TripoSR:**
   - Ensure TripoSR is installed at `C:\ai3d\TripoSR\`
   - Verify PowerShell scripts exist: `run_fast.ps1`, `launch_picker.ps1`
   - Make sure the TripoSR virtual environment is properly configured

4. **Add background image:**
   - Place `bg.jpg` in the `static/` directory for the UI background

## Usage

1. **Start the Flask server:**
   ```bash
   python src/app.py
   ```

2. **Open your browser:**
   - Navigate to `http://127.0.0.1:5000`

3. **Upload and process:**
   - Upload a JPG/PNG image using drag & drop or browse
   - Click "Upload" to start 3D generation
   - Watch real-time progress and logs
   - Download the generated 3D files when complete

## How It Works

1. **Upload**: Images are saved to `static/uploads/`
2. **Processing**: Calls `run_fast.ps1` with the uploaded image
3. **TripoSR**: Generates 3D mesh using CPU processing
4. **Output**: Creates OBJ files and textures in task-specific folders
5. **Download**: Provides direct download links for all generated files

## API Endpoints

- `GET /` - Main interface
- `POST /ajax_upload` - Handle file uploads
- `GET /ajax_progress` - Get processing status and logs
- `GET /ajax_outputs` - List output files
- `GET /download_output/<task_id>/<filename>` - Download generated files

## Configuration

The app connects to TripoSR using these paths:
- **PowerShell Script**: `C:\ai3d\TripoSR\run_fast.ps1`
- **Output Directory**: `C:\ai3d\TripoSR\output\{task_id}\`
- **Upload Directory**: `static/uploads/`

## Dependencies

- Flask
- Werkzeug (file handling)
- UUID (task management)
- Threading (background processing)
- Subprocess (PowerShell integration)

## Screenshots

*Add screenshots of the interface here*

## Troubleshooting

- **"Method Not Allowed"**: Ensure you're accessing the correct endpoints
- **"Unknown" status**: Check that PowerShell scripts are executable
- **File not found**: Verify TripoSR installation paths
- **Processing fails**: Check TripoSR virtual environment setup

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

*Add your license information here*

## Dependencies
streamlit run src/app.py
```

## Usage

Once the application is running, you will see an input button where you can enter your data. After entering the data, click the submit button to process the input.

## Configuration

You can customize the application settings by modifying the `config.toml` file. This file allows you to set theme settings and server configurations.

## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request with your changes.
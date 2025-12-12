# 🎓 QuizMaster - AI-Powered Assessment System

A comprehensive web application that extracts content from documents (PDF/TXT/DOCX), generates intelligent questions using AI, and evaluates user answers with advanced metrics including plagiarism detection and AI-content detection.

## 🌟 Features

### Core Features
- **Multi-Format Document Upload**: Support for PDF, TXT, and DOCX files
- **AI-Powered Question Generation**: Uses Claude AI to generate contextual questions
- **Difficulty Levels**: Easy, Medium, and Hard question types
- **Real-Time Timer**: Tracks time spent on each question
- **Comprehensive Evaluation**: 
  - Correctness scoring (0-100%)
  - Answer similarity analysis
  - Plagiarism detection
  - AI-generated content detection
- **Beautiful Modern UI**: Dark-themed, responsive interface with smooth animations

### Technical Features
- **Single-File Architecture**: Maximum 5 files for easy maintenance
- **RESTful API**: Clean backend architecture
- **Error Handling**: Comprehensive error management
- **File Validation**: Security checks and file type validation
- **Progress Tracking**: Visual progress indicators

## 📁 Project Structure

```
quiz-master/
├── app.py              # Flask backend (all APIs)
├── index.html          # Complete frontend
├── requirements.txt    # Python dependencies
├── .env               # Configuration file
└── README.md          # This file
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Anthropic API key (free tier available)

### Step 1: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### Step 2: Configure API Key

1. Get your free Anthropic API key:
   - Visit: https://console.anthropic.com/
   - Sign up for a free account
   - Navigate to API Keys section
   - Create a new API key

2. Edit the `.env` file:
```bash
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### Step 3: Run the Application

```bash
# Start the Flask server
python app.py
```

The server will start at `http://localhost:5000`

### Step 4: Open in Browser

Navigate to `http://localhost:5000` in your web browser.

## 📖 How to Use

### 1. Upload Document
- Click the upload zone or drag & drop your file
- Supported formats: PDF, TXT, DOCX (max 10MB)
- Wait for content extraction

### 2. Configure Quiz
- Select number of questions (1-20)
- Choose difficulty level:
  - **Easy**: Basic recall questions
  - **Medium**: Application and analysis
  - **Hard**: Synthesis and evaluation
- Click "Generate Questions"

### 3. Answer Questions
- Timer starts when you focus on a question
- Type your answers in the text areas
- Progress bar shows completion status
- All questions must be answered

### 4. View Results
- Overall performance metrics
- Detailed question-by-question analysis
- Correctness scores and feedback
- Plagiarism and AI-detection alerts
- Time spent per question

## 🛠️ Customization Guide

### Changing File Upload Limits

In `app.py`, modify:
```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # Change 10 to desired MB
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}  # Add/remove formats
```

### Adjusting Question Count Limits

In `app.py`:
```python
if num_questions < 1 or num_questions > 20:  # Change max limit
```

In `index.html`:
```html
<input type="number" id="numQuestions" min="1" max="20" value="5">
```

### Customizing UI Colors

In `index.html`, modify CSS variables:
```css
:root {
    --primary: #6366f1;        /* Main theme color */
    --success: #10b981;        /* Success messages */
    --danger: #ef4444;         /* Error messages */
    --bg: #0f172a;            /* Background color */
    /* ... more variables ... */
}
```

### Modifying Evaluation Criteria

In `app.py`, adjust the `evaluate_answer_with_claude()` function:
```python
# Change scoring thresholds
correctness = min(similarity + 10, 100)  # Adjust formula

# Modify plagiarism threshold
is_plagiarized = similarity > 90  # Change 90 to desired threshold

# Adjust AI detection logic
is_ai_generated = len(user_answer) > 200 and user_answer.count(',') > 5
```

### Adding New Difficulty Levels

1. In `app.py`, update `difficulty_guidance`:
```python
difficulty_guidance = {
    'easy': '...',
    'medium': '...',
    'hard': '...',
    'expert': 'Advanced critical thinking questions'  # New level
}
```

2. In `index.html`, add option:
```html
<option value="expert">Expert - Advanced analysis</option>
```

### Changing API Model

In `app.py`, modify the model name:
```python
message = client.messages.create(
    model="claude-sonnet-4-20250514",  # Change model here
    max_tokens=4000,
    messages=[{"role": "user", "content": prompt}]
)
```

## 🔧 API Endpoints

### POST /upload
Upload and extract document content
- **Input**: Multipart form data with file
- **Output**: JSON with extracted content

### POST /generate-questions
Generate questions from content
- **Input**: `{content, num_questions, difficulty}`
- **Output**: JSON array of questions

### POST /evaluate-answers
Evaluate user answers
- **Input**: Array of submissions
- **Output**: Detailed results and scores

### GET /health
Health check endpoint
- **Output**: Server status

## 🎨 UI Components

### Step Indicator
Shows current progress through the workflow

### Upload Zone
Drag-and-drop file upload with visual feedback

### Question Cards
Individual question containers with timers

### Progress Bar
Visual representation of quiz completion

### Result Cards
Color-coded feedback for each answer

### Score Summary
Grid display of key metrics

## ⚙️ Configuration Options

### Environment Variables (.env)
```bash
ANTHROPIC_API_KEY=your_key
MAX_FILE_SIZE_MB=10
UPLOAD_FOLDER=uploads
```

### Flask Configuration (app.py)
```python
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
```

## 🔒 Security Features

- File type validation
- File size limits
- Secure filename handling
- CORS protection
- Input sanitization
- Error message sanitization

## 🐛 Troubleshooting

### Issue: API Key Error
**Solution**: Ensure `.env` file has correct API key

### Issue: File Upload Fails
**Solution**: Check file size (<10MB) and format (PDF/TXT/DOCX)

### Issue: Questions Not Generated
**Solution**: 
1. Verify API key is valid
2. Check document has sufficient content (>50 characters)
3. Review console for errors

### Issue: Port Already in Use
**Solution**: Change port in `app.py`:
```python
app.run(debug=True, port=5001)  # Use different port
```

### Issue: CORS Errors
**Solution**: Ensure Flask-CORS is installed:
```bash
pip install flask-cors
```

## 📊 Performance Tips

1. **Optimize Document Size**: Smaller documents process faster
2. **Limit Question Count**: Start with 5-10 questions for testing
3. **Use Easy Difficulty**: Faster generation for simple questions
4. **Clear Browser Cache**: If UI issues persist

## 🔄 Future Enhancements

### Easy to Add
- Export results to PDF/CSV
- User authentication
- Question templates
- Multi-language support
- Batch document processing

### How to Extend
1. **Add New File Types**: Update `extract_document_content()` function
2. **Custom Evaluation Metrics**: Modify `evaluate_answer_with_claude()`
3. **Database Integration**: Replace in-memory storage
4. **User Profiles**: Add Flask-Login for user management

## 📝 Code Organization

### app.py Structure
```
├── Configuration & Setup
├── Document Processing Functions
│   ├── extract_text_from_pdf()
│   ├── extract_text_from_docx()
│   └── extract_text_from_txt()
├── AI Functions
│   ├── generate_questions_with_claude()
│   └── evaluate_answer_with_claude()
├── Fallback Functions
│   ├── generate_fallback_questions()
│   └── fallback_evaluation()
└── API Routes
    ├── /upload
    ├── /generate-questions
    ├── /evaluate-answers
    └── /health
```

### index.html Structure
```
├── Styles (CSS)
├── HTML Structure
│   ├── Header
│   ├── Step Indicator
│   └── Four Main Sections
│       ├── Upload
│       ├── Configure
│       ├── Quiz
│       └── Results
└── JavaScript Logic
    ├── State Management
    ├── Upload Handling
    ├── Question Rendering
    ├── Timer Management
    └── Results Display
```

## 📞 Support

For issues or questions:
1. Check this README
2. Review error messages in browser console
3. Verify all dependencies are installed
4. Ensure API key is configured correctly

## 🎯 Best Practices

1. **Always backup** your `.env` file
2. **Test with small documents** first
3. **Monitor API usage** on Anthropic dashboard
4. **Use virtual environment** for Python packages
5. **Keep dependencies updated** for security

## 📄 License

This project is provided as-is for educational and personal use.

## 🚀 Quick Start Summary

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add API key to .env file
ANTHROPIC_API_KEY=your_key_here

# 3. Run the application
python app.py

# 4. Open browser to http://localhost:5000
```

---

**Built with ❤️ using Flask**

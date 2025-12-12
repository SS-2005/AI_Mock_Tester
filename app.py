"""
QuizMaster - AI-Powered Question Generation & Assessment System
Flask Backend with Document Processing, Question Generation, and Answer Evaluation
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import re
import time
from datetime import datetime
from werkzeug.utils import secure_filename
import PyPDF2
import docx
import anthropic
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize Anthropic client (using free tier)
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"PDF extraction error: {str(e)}")

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise Exception(f"DOCX extraction error: {str(e)}")

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read().strip()
    except Exception as e:
        raise Exception(f"TXT extraction error: {str(e)}")

def extract_document_content(file_path, filename):
    """Extract content based on file type"""
    ext = filename.rsplit('.', 1)[1].lower()
    
    if ext == 'pdf':
        return extract_text_from_pdf(file_path)
    elif ext == 'docx':
        return extract_text_from_docx(file_path)
    elif ext == 'txt':
        return extract_text_from_txt(file_path)
    else:
        raise Exception("Unsupported file format")

def generate_questions_with_claude(content, num_questions, difficulty):
    """Generate questions using Claude API"""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    difficulty_guidance = {
        'easy': 'Simple recall and basic understanding questions',
        'medium': 'Application and analysis questions requiring deeper understanding',
        'hard': 'Complex synthesis, evaluation, and critical thinking questions'
    }
    
    prompt = f"""Based on the following content, generate exactly {num_questions} {difficulty} difficulty questions.

Content:
{content[:4000]}

Requirements:
- Generate {difficulty} level questions: {difficulty_guidance[difficulty]}
- Provide the correct answer for each question
- Make questions specific to the content provided
- Ensure questions test understanding, not just memorization

Return ONLY a valid JSON array in this exact format:
[
  {{
    "question": "Question text here?",
    "correct_answer": "Detailed correct answer here",
    "difficulty": "{difficulty}"
  }}
]

Do not include any other text, explanations, or markdown formatting. Just the JSON array."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        
        # Clean response - remove markdown code blocks if present
        response_text = re.sub(r'^```json\s*', '', response_text)
        response_text = re.sub(r'^```\s*', '', response_text)
        response_text = re.sub(r'\s*```$', '', response_text)
        
        questions = json.loads(response_text)
        
        # Validate structure
        if not isinstance(questions, list):
            raise ValueError("Response is not a list")
        
        for q in questions:
            if not all(key in q for key in ['question', 'correct_answer', 'difficulty']):
                raise ValueError("Invalid question structure")
        
        return questions[:num_questions]  # Ensure we return exact number
        
    except Exception as e:
        print(f"Claude API Error: {str(e)}")
        # Fallback to template questions
        return generate_fallback_questions(content, num_questions, difficulty)

def generate_fallback_questions(content, num_questions, difficulty):
    """Generate fallback questions if API fails"""
    sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20][:10]
    questions = []
    
    templates = {
        'easy': [
            f"What is mentioned about {{topic}}?",
            f"According to the text, what is {{topic}}?",
            f"Describe {{topic}} as mentioned in the document."
        ],
        'medium': [
            f"Explain the significance of {{topic}} in the context of the document.",
            f"How does {{topic}} relate to the main themes discussed?",
            f"Analyze the role of {{topic}} in the given content."
        ],
        'hard': [
            f"Critically evaluate the implications of {{topic}} based on the content.",
            f"Synthesize the information about {{topic}} and propose potential applications.",
            f"Compare and contrast different perspectives on {{topic}} presented in the text."
        ]
    }
    
    for i in range(min(num_questions, len(sentences))):
        topic = sentences[i][:50]
        template = templates[difficulty][i % len(templates[difficulty])]
        questions.append({
            "question": template.replace("{topic}", topic),
            "correct_answer": f"Based on the content: {sentences[i]}",
            "difficulty": difficulty
        })
    
    return questions

def evaluate_answer_with_claude(question, correct_answer, user_answer):
    """Evaluate answer using Claude API"""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    prompt = f"""Evaluate the following answer:

Question: {question}
Expected Answer: {correct_answer}
User's Answer: {user_answer}

Provide a comprehensive evaluation in JSON format with these metrics:
1. correctness_score: 0-100 (how correct is the answer)
2. similarity_score: 0-100 (how similar to expected answer)
3. is_plagiarized: true/false (if copied from source)
4. is_ai_generated: true/false (likelihood of AI generation)
5. feedback: detailed feedback string

Return ONLY valid JSON:
{{
  "correctness_score": 85,
  "similarity_score": 75,
  "is_plagiarized": false,
  "is_ai_generated": false,
  "feedback": "Your answer is..."
}}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        response_text = re.sub(r'^```json\s*', '', response_text)
        response_text = re.sub(r'^```\s*', '', response_text)
        response_text = re.sub(r'\s*```$', '', response_text)
        
        evaluation = json.loads(response_text)
        return evaluation
        
    except Exception as e:
        print(f"Evaluation Error: {str(e)}")
        # Fallback evaluation
        return fallback_evaluation(user_answer, correct_answer)

def fallback_evaluation(user_answer, correct_answer):
    """Simple fallback evaluation"""
    user_lower = user_answer.lower()
    correct_lower = correct_answer.lower()
    
    # Simple word matching
    user_words = set(user_lower.split())
    correct_words = set(correct_lower.split())
    
    if len(correct_words) == 0:
        similarity = 0
    else:
        common_words = user_words.intersection(correct_words)
        similarity = int((len(common_words) / len(correct_words)) * 100)
    
    correctness = min(similarity + 10, 100)
    
    return {
        "correctness_score": correctness,
        "similarity_score": similarity,
        "is_plagiarized": similarity > 90,
        "is_ai_generated": len(user_answer) > 200 and user_answer.count(',') > 5,
        "feedback": f"Your answer shows {similarity}% similarity to the expected answer. " + 
                   ("Good job!" if correctness > 70 else "Please review the topic and try to provide more relevant information.")
    }

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_document():
    """Handle document upload and text extraction"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: PDF, TXT, DOCX'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(file_path)
        
        # Extract content
        content = extract_document_content(file_path, filename)
        
        if len(content) < 50:
            os.remove(file_path)
            return jsonify({'error': 'Document content too short. Please upload a document with more text.'}), 400
        
        # Clean up file after extraction
        try:
            os.remove(file_path)
        except:
            pass
        
        return jsonify({
            'success': True,
            'content': content,
            'filename': filename,
            'content_length': len(content),
            'word_count': len(content.split())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-questions', methods=['POST'])
def generate_questions():
    """Generate questions from document content"""
    try:
        data = request.json
        content = data.get('content', '')
        num_questions = int(data.get('num_questions', 5))
        difficulty = data.get('difficulty', 'medium')
        
        if not content:
            return jsonify({'error': 'No content provided'}), 400
        
        if num_questions < 1 or num_questions > 20:
            return jsonify({'error': 'Number of questions must be between 1 and 20'}), 400
        
        if difficulty not in ['easy', 'medium', 'hard']:
            return jsonify({'error': 'Invalid difficulty level'}), 400
        
        # Generate questions
        questions = generate_questions_with_claude(content, num_questions, difficulty)
        
        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(questions)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/evaluate-answers', methods=['POST'])
def evaluate_answers():
    """Evaluate all user answers"""
    try:
        data = request.json
        submissions = data.get('submissions', [])
        
        if not submissions:
            return jsonify({'error': 'No submissions provided'}), 400
        
        results = []
        total_score = 0
        total_time = 0
        
        for submission in submissions:
            question = submission.get('question', '')
            correct_answer = submission.get('correct_answer', '')
            user_answer = submission.get('user_answer', '')
            time_taken = submission.get('time_taken', 0)
            
            # Evaluate answer
            evaluation = evaluate_answer_with_claude(question, correct_answer, user_answer)
            
            result = {
                'question': question,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'time_taken': time_taken,
                **evaluation
            }
            
            results.append(result)
            total_score += evaluation.get('correctness_score', 0)
            total_time += time_taken
        
        avg_score = total_score / len(submissions) if submissions else 0
        
        # Generate overall feedback
        performance_level = "Excellent" if avg_score >= 80 else "Good" if avg_score >= 60 else "Needs Improvement"
        
        return jsonify({
            'success': True,
            'results': results,
            'summary': {
                'total_questions': len(submissions),
                'average_score': round(avg_score, 2),
                'total_time': total_time,
                'performance_level': performance_level,
                'plagiarism_detected': any(r.get('is_plagiarized', False) for r in results),
                'ai_generated_detected': any(r.get('is_ai_generated', False) for r in results)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'api_configured': bool(ANTHROPIC_API_KEY)
    })

if __name__ == '__main__':
    print("=" * 60)
    print("QuizMaster - AI-Powered Assessment System")
    print("=" * 60)
    print(f"Server starting on http://localhost:5000")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"API configured: {bool(ANTHROPIC_API_KEY)}")
    print("=" * 60)
    app.run(debug=True, port=5000)
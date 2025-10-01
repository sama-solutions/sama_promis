/**
 * SAMA PROMIS Training Website - Quiz System
 * Comprehensive quiz and assessment functionality
 */

// ============================================
// Quiz Data Structure
// ============================================
const QuizData = {
  /**
   * Sample quiz structure
   */
  sampleQuiz: {
    quizId: 'admin-user-module1',
    title: 'Module 1: Installation et Configuration',
    description: 'Testez vos connaissances sur l\'installation de SAMA PROMIS',
    timeLimit: 20, // minutes
    passingScore: 80, // percentage
    questions: [
      {
        id: 1,
        type: 'multiple-choice',
        question: 'Quelle est la version minimale de Python requise pour SAMA PROMIS?',
        options: [
          { id: 'a', text: 'Python 3.8', correct: false },
          { id: 'b', text: 'Python 3.10', correct: false },
          { id: 'c', text: 'Python 3.11', correct: true },
          { id: 'd', text: 'Python 3.12', correct: false }
        ],
        explanation: 'SAMA PROMIS nécessite Python 3.11 ou supérieur pour la compatibilité avec Odoo 18 CE.',
        points: 2
      },
      {
        id: 2,
        type: 'multiple-choice',
        question: 'Quelle base de données est utilisée par SAMA PROMIS?',
        options: [
          { id: 'a', text: 'MySQL', correct: false },
          { id: 'b', text: 'PostgreSQL', correct: true },
          { id: 'c', text: 'MongoDB', correct: false },
          { id: 'd', text: 'SQLite', correct: false }
        ],
        explanation: 'SAMA PROMIS utilise PostgreSQL 13+ comme système de gestion de base de données.',
        points: 2
      },
      {
        id: 3,
        type: 'true-false',
        question: 'SAMA PROMIS peut fonctionner sur Odoo 17 Community Edition.',
        options: [
          { id: 'true', text: 'Vrai', correct: false },
          { id: 'false', text: 'Faux', correct: true }
        ],
        explanation: 'SAMA PROMIS est spécifiquement conçu pour Odoo 18 Community Edition.',
        points: 1
      },
      {
        id: 4,
        type: 'multiple-select',
        question: 'Quelles sont les phases complétées de SAMA PROMIS? (Sélectionnez toutes les réponses correctes)',
        options: [
          { id: 'a', text: 'Gestion multi-sources de financement', correct: true },
          { id: 'b', text: 'Plans de passation de marchés', correct: true },
          { id: 'c', text: 'Gestion de la conformité', correct: true },
          { id: 'd', text: 'Portail public de transparence', correct: true },
          { id: 'e', text: 'Intelligence artificielle', correct: false }
        ],
        explanation: 'SAMA PROMIS a complété 4 phases: financement multi-sources, passation de marchés, conformité et portail public.',
        points: 3
      }
    ]
  }
};

// ============================================
// Quiz Renderer Class
// ============================================
class QuizRenderer {
  constructor(quizData, containerId) {
    this.quizData = quizData;
    this.container = document.getElementById(containerId);
    this.currentQuestion = 0;
    this.answers = {};
    this.startTime = null;
    this.timerInterval = null;
    this.timeRemaining = quizData.timeLimit * 60; // Convert to seconds
  }
  
  /**
   * Initialize and render the quiz
   */
  render() {
    if (!this.container) {
      console.error('Quiz container not found');
      return;
    }
    
    this.startTime = new Date();
    this.renderQuizHeader();
    this.renderQuestions();
    this.renderNavigation();
    this.startTimer();
  }
  
  /**
   * Render quiz header with title and timer
   */
  renderQuizHeader() {
    const header = document.createElement('div');
    header.className = 'quiz-header mb-4 p-3 bg-light rounded';
    header.innerHTML = `
      <div class="row align-items-center">
        <div class="col-md-8">
          <h3 class="mb-1">${this.quizData.title}</h3>
          <p class="text-muted mb-0">${this.quizData.description}</p>
        </div>
        <div class="col-md-4 text-md-end">
          <div class="quiz-timer">
            <i class="fas fa-clock me-2"></i>
            <span id="quiz-timer-display" class="fw-bold fs-4">
              ${this.formatTime(this.timeRemaining)}
            </span>
          </div>
          <small class="text-muted">Temps restant</small>
        </div>
      </div>
      <div class="progress mt-3" style="height: 5px;">
        <div id="quiz-progress-bar" class="progress-bar bg-success" role="progressbar" style="width: 0%"></div>
      </div>
    `;
    this.container.appendChild(header);
  }
  
  /**
   * Render all questions
   */
  renderQuestions() {
    const questionsContainer = document.createElement('div');
    questionsContainer.id = 'quiz-questions-container';
    
    this.quizData.questions.forEach((question, index) => {
      const questionDiv = this.renderQuestion(question, index);
      questionsContainer.appendChild(questionDiv);
    });
    
    this.container.appendChild(questionsContainer);
  }
  
  /**
   * Render a single question
   */
  renderQuestion(question, index) {
    const questionDiv = document.createElement('div');
    questionDiv.className = 'quiz-question mb-4 p-4 bg-white rounded shadow-sm';
    questionDiv.dataset.questionId = question.id;
    
    let optionsHtml = '';
    
    switch (question.type) {
      case 'multiple-choice':
      case 'true-false':
        optionsHtml = this.renderMultipleChoice(question);
        break;
      case 'multiple-select':
        optionsHtml = this.renderMultipleSelect(question);
        break;
      case 'fill-blank':
        optionsHtml = this.renderFillBlank(question);
        break;
    }
    
    questionDiv.innerHTML = `
      <div class="d-flex justify-content-between align-items-start mb-3">
        <h5 class="mb-0">
          <span class="badge bg-primary me-2">${index + 1}</span>
          ${question.question}
        </h5>
        <span class="badge bg-secondary">${question.points} pt${question.points > 1 ? 's' : ''}</span>
      </div>
      <div class="quiz-options">
        ${optionsHtml}
      </div>
    `;
    
    return questionDiv;
  }
  
  /**
   * Render multiple choice options
   */
  renderMultipleChoice(question) {
    return question.options.map(option => `
      <div class="quiz-option mb-2 p-3 border rounded" 
           data-question-id="${question.id}" 
           data-option-id="${option.id}"
           onclick="quizInstance.selectAnswer(${question.id}, '${option.id}', 'single')">
        <div class="form-check">
          <input class="form-check-input" 
                 type="radio" 
                 name="question-${question.id}" 
                 value="${option.id}" 
                 id="q${question.id}-opt${option.id}">
          <label class="form-check-label w-100" for="q${question.id}-opt${option.id}">
            ${option.text}
          </label>
        </div>
      </div>
    `).join('');
  }
  
  /**
   * Render multiple select options
   */
  renderMultipleSelect(question) {
    return `
      <p class="text-muted small mb-3"><i class="fas fa-info-circle me-1"></i>Sélectionnez toutes les réponses correctes</p>
      ${question.options.map(option => `
        <div class="quiz-option mb-2 p-3 border rounded" 
             data-question-id="${question.id}" 
             data-option-id="${option.id}"
             onclick="quizInstance.selectAnswer(${question.id}, '${option.id}', 'multiple')">
          <div class="form-check">
            <input class="form-check-input" 
                   type="checkbox" 
                   name="question-${question.id}" 
                   value="${option.id}" 
                   id="q${question.id}-opt${option.id}">
            <label class="form-check-label w-100" for="q${question.id}-opt${option.id}">
              ${option.text}
            </label>
          </div>
        </div>
      `).join('')}
    `;
  }
  
  /**
   * Render fill in the blank
   */
  renderFillBlank(question) {
    return `
      <input type="text" 
             class="form-control form-control-lg" 
             id="answer-${question.id}"
             placeholder="Entrez votre réponse..."
             onchange="quizInstance.selectAnswer(${question.id}, this.value, 'text')">
    `;
  }
  
  /**
   * Render navigation buttons
   */
  renderNavigation() {
    const nav = document.createElement('div');
    nav.className = 'quiz-navigation text-center mt-4 p-3 bg-light rounded';
    nav.innerHTML = `
      <button class="btn btn-promis-primary btn-lg" onclick="quizInstance.submitQuiz()">
        <i class="fas fa-check-circle me-2"></i>Soumettre le Quiz
      </button>
      <p class="text-muted small mt-2 mb-0">
        <i class="fas fa-exclamation-triangle me-1"></i>
        Assurez-vous d'avoir répondu à toutes les questions avant de soumettre
      </p>
    `;
    this.container.appendChild(nav);
  }
  
  /**
   * Handle answer selection
   */
  selectAnswer(questionId, value, type) {
    if (type === 'single' || type === 'text') {
      this.answers[questionId] = value;
      
      // Update UI for single choice
      if (type === 'single') {
        const questionDiv = document.querySelector(`[data-question-id="${questionId}"]`);
        questionDiv.querySelectorAll('.quiz-option').forEach(opt => {
          opt.classList.remove('selected');
        });
        const selectedOption = questionDiv.querySelector(`[data-option-id="${value}"]`);
        if (selectedOption) {
          selectedOption.classList.add('selected');
        }
      }
    } else if (type === 'multiple') {
      // Handle multiple select
      if (!this.answers[questionId]) {
        this.answers[questionId] = [];
      }
      
      const index = this.answers[questionId].indexOf(value);
      if (index > -1) {
        this.answers[questionId].splice(index, 1);
      } else {
        this.answers[questionId].push(value);
      }
      
      // Update UI
      const optionDiv = document.querySelector(`[data-question-id="${questionId}"][data-option-id="${value}"]`);
      if (optionDiv) {
        optionDiv.classList.toggle('selected');
      }
    }
    
    this.updateProgress();
  }
  
  /**
   * Update progress bar
   */
  updateProgress() {
    const totalQuestions = this.quizData.questions.length;
    const answeredQuestions = Object.keys(this.answers).length;
    const percentage = (answeredQuestions / totalQuestions) * 100;
    
    const progressBar = document.getElementById('quiz-progress-bar');
    if (progressBar) {
      progressBar.style.width = `${percentage}%`;
      progressBar.setAttribute('aria-valuenow', percentage);
    }
  }
  
  /**
   * Start quiz timer
   */
  startTimer() {
    this.timerInterval = setInterval(() => {
      this.timeRemaining--;
      
      const timerDisplay = document.getElementById('quiz-timer-display');
      if (timerDisplay) {
        timerDisplay.textContent = this.formatTime(this.timeRemaining);
        
        // Change color when time is running out
        if (this.timeRemaining <= 60) {
          timerDisplay.classList.add('text-danger');
        } else if (this.timeRemaining <= 300) {
          timerDisplay.classList.add('text-warning');
        }
      }
      
      if (this.timeRemaining <= 0) {
        this.stopTimer();
        this.submitQuiz(true); // Auto-submit when time expires
      }
    }, 1000);
  }
  
  /**
   * Stop timer
   */
  stopTimer() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
    }
  }
  
  /**
   * Format time in MM:SS
   */
  formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  }
  
  /**
   * Submit quiz
   */
  submitQuiz(autoSubmit = false) {
    // Check if all questions are answered
    const totalQuestions = this.quizData.questions.length;
    const answeredQuestions = Object.keys(this.answers).length;
    
    if (!autoSubmit && answeredQuestions < totalQuestions) {
      const unanswered = totalQuestions - answeredQuestions;
      if (!confirm(`Vous avez ${unanswered} question(s) non répondue(s). Voulez-vous vraiment soumettre?`)) {
        return;
      }
    }
    
    this.stopTimer();
    
    // Calculate score
    const results = this.calculateScore();
    
    // Save results
    this.saveResults(results);
    
    // Show results
    this.showResults(results, autoSubmit);
  }
  
  /**
   * Calculate quiz score
   */
  calculateScore() {
    let totalPoints = 0;
    let earnedPoints = 0;
    let correctAnswers = 0;
    const questionResults = [];
    
    this.quizData.questions.forEach(question => {
      totalPoints += question.points;
      const userAnswer = this.answers[question.id];
      const isCorrect = this.checkAnswer(question, userAnswer);
      
      if (isCorrect) {
        earnedPoints += question.points;
        correctAnswers++;
      }
      
      questionResults.push({
        questionId: question.id,
        question: question.question,
        userAnswer,
        correct: isCorrect,
        explanation: question.explanation
      });
    });
    
    const percentage = totalPoints > 0 ? Math.round((earnedPoints / totalPoints) * 100) : 0;
    const passed = percentage >= this.quizData.passingScore;
    
    return {
      quizId: this.quizData.quizId,
      quizTitle: this.quizData.title,
      totalQuestions: this.quizData.questions.length,
      answeredQuestions: Object.keys(this.answers).length,
      correctAnswers,
      totalPoints,
      earnedPoints,
      percentage,
      passed,
      passingScore: this.quizData.passingScore,
      timeSpent: this.quizData.timeLimit * 60 - this.timeRemaining,
      timestamp: new Date().toISOString(),
      questionResults
    };
  }
  
  /**
   * Check if answer is correct
   */
  checkAnswer(question, userAnswer) {
    if (!userAnswer) return false;
    
    switch (question.type) {
      case 'multiple-choice':
      case 'true-false':
        const correctOption = question.options.find(opt => opt.correct);
        return userAnswer === correctOption.id;
        
      case 'multiple-select':
        const correctIds = question.options.filter(opt => opt.correct).map(opt => opt.id).sort();
        const userIds = Array.isArray(userAnswer) ? userAnswer.sort() : [];
        return JSON.stringify(correctIds) === JSON.stringify(userIds);
        
      case 'fill-blank':
        return userAnswer.toLowerCase().trim() === question.correctAnswer.toLowerCase().trim();
        
      default:
        return false;
    }
  }
  
  /**
   * Save results to localStorage
   */
  saveResults(results) {
    const key = `promis_quiz_${results.quizId}`;
    const attempts = JSON.parse(localStorage.getItem(key) || '[]');
    attempts.push(results);
    localStorage.setItem(key, JSON.stringify(attempts));
  }
  
  /**
   * Show results modal
   */
  showResults(results, autoSubmit) {
    const modalHtml = `
      <div class="modal fade" id="quizResultsModal" tabindex="-1" data-bs-backdrop="static">
        <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
          <div class="modal-content">
            <div class="modal-header ${results.passed ? 'bg-success' : 'bg-warning'} text-white">
              <h5 class="modal-title">
                <i class="fas fa-${results.passed ? 'trophy' : 'redo'} me-2"></i>
                Résultats du Quiz
              </h5>
            </div>
            <div class="modal-body">
              ${autoSubmit ? '<div class="alert alert-warning"><i class="fas fa-clock me-2"></i>Le temps est écoulé. Le quiz a été soumis automatiquement.</div>' : ''}
              
              <div class="text-center mb-4">
                <div class="display-1 ${results.passed ? 'text-success' : 'text-warning'} mb-2">
                  ${results.percentage}%
                </div>
                <h4>${results.correctAnswers} / ${results.totalQuestions} réponses correctes</h4>
                <p class="text-muted">Score requis: ${results.passingScore}%</p>
              </div>
              
              <div class="alert alert-${results.passed ? 'success' : 'warning'}">
                <h6 class="alert-heading">
                  ${results.passed 
                    ? '<i class="fas fa-check-circle me-2"></i>Félicitations! Vous avez réussi le quiz.' 
                    : '<i class="fas fa-times-circle me-2"></i>Score insuffisant. Veuillez réviser et réessayer.'}
                </h6>
                <hr>
                <p class="mb-0">
                  <strong>Points obtenus:</strong> ${results.earnedPoints} / ${results.totalPoints}<br>
                  <strong>Temps passé:</strong> ${this.formatTime(results.timeSpent)}
                </p>
              </div>
              
              <h6 class="mt-4 mb-3">Détails des Réponses</h6>
              <div class="accordion" id="resultsAccordion">
                ${results.questionResults.map((qr, index) => `
                  <div class="accordion-item">
                    <h2 class="accordion-header">
                      <button class="accordion-button ${index === 0 ? '' : 'collapsed'}" type="button" data-bs-toggle="collapse" data-bs-target="#result${index}">
                        <i class="fas fa-${qr.correct ? 'check-circle text-success' : 'times-circle text-danger'} me-2"></i>
                        Question ${index + 1}
                      </button>
                    </h2>
                    <div id="result${index}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" data-bs-parent="#resultsAccordion">
                      <div class="accordion-body">
                        <p><strong>${qr.question}</strong></p>
                        <p class="mb-1"><strong>Votre réponse:</strong> ${qr.correct ? '<span class="text-success">Correcte</span>' : '<span class="text-danger">Incorrecte</span>'}</p>
                        ${qr.explanation ? `<p class="text-muted small mb-0"><i class="fas fa-info-circle me-1"></i>${qr.explanation}</p>` : ''}
                      </div>
                    </div>
                  </div>
                `).join('')}
              </div>
            </div>
            <div class="modal-footer">
              ${results.passed 
                ? '<button type="button" class="btn btn-success" onclick="location.reload()">Continuer</button>'
                : '<button type="button" class="btn btn-warning" onclick="location.reload()">Réessayer</button>'}
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fermer</button>
            </div>
          </div>
        </div>
      </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('quizResultsModal'));
    modal.show();
    
    // Remove modal from DOM after hiding
    document.getElementById('quizResultsModal').addEventListener('hidden.bs.modal', function() {
      this.remove();
    });
  }
}

// ============================================
// Global Quiz Instance
// ============================================
let quizInstance = null;

/**
 * Initialize a quiz
 */
function initQuiz(quizId, containerId = 'quiz-container') {
  // Load quiz data (in production, this would fetch from a JSON file)
  const quizData = QuizData.sampleQuiz; // Replace with actual data loading
  
  quizInstance = new QuizRenderer(quizData, containerId);
  quizInstance.render();
}

// Export for use in other scripts
window.QuizRenderer = QuizRenderer;
window.QuizData = QuizData;
window.initQuiz = initQuiz;

/**
 * SAMA PROMIS Training Website - Core JavaScript
 * Handles progress tracking, navigation, user data, and interactive elements
 */

/**
 * Helper function to resolve paths dynamically
 * Uses the global path resolver if in file:// mode, otherwise builds from origin
 */
function getResolvedPath(relativePath) {
    if (window.resolveTrainingPath) {
        return window.resolveTrainingPath(relativePath);
    }
    // When running over HTTP without resolveTrainingPath, build URL from origin
    const baseUrl = window.location.origin + '/docs/training/';
    return new URL(relativePath, baseUrl).href;
}

// ============================================
// Progress Tracking System
// ============================================
const ProgressTracker = {
  /**
   * Save progress to localStorage
   */
  saveProgress(role, level, moduleId, lessonId, completed) {
    const key = `promis_training_${role}_${level}`;
    let progress = JSON.parse(localStorage.getItem(key) || '{}');
    
    if (!progress[moduleId]) {
      progress[moduleId] = {};
    }
    
    progress[moduleId][lessonId] = {
      completed: completed,
      timestamp: new Date().toISOString(),
      attempts: (progress[moduleId][lessonId]?.attempts || 0) + 1
    };
    
    localStorage.setItem(key, JSON.stringify(progress));
    
    // Update UI if progress indicators exist
    this.updateProgressIndicators(role, level);
  },
  
  /**
   * Get progress for a role/level
   */
  getProgress(role, level) {
    const key = `promis_training_${role}_${level}`;
    return JSON.parse(localStorage.getItem(key) || '{}');
  },
  
  /**
   * Calculate completion percentage
   */
  getCompletionRate(role, level, totalLessons) {
    const progress = this.getProgress(role, level);
    let completed = 0;
    
    Object.values(progress).forEach(module => {
      Object.values(module).forEach(lesson => {
        if (lesson.completed) completed++;
      });
    });
    
    return totalLessons > 0 ? Math.round((completed / totalLessons) * 100) : 0;
  },
  
  /**
   * Check if a specific lesson is completed
   */
  isLessonCompleted(role, level, moduleId, lessonId) {
    const progress = this.getProgress(role, level);
    return progress[moduleId]?.[lessonId]?.completed || false;
  },
  
  /**
   * Get all completed lessons count
   */
  getCompletedCount(role, level) {
    const progress = this.getProgress(role, level);
    let count = 0;
    
    Object.values(progress).forEach(module => {
      Object.values(module).forEach(lesson => {
        if (lesson.completed) count++;
      });
    });
    
    return count;
  },
  
  /**
   * Reset progress for a role/level
   */
  resetProgress(role, level) {
    const key = `promis_training_${role}_${level}`;
    localStorage.removeItem(key);
    this.updateProgressIndicators(role, level);
  },
  
  /**
   * Update progress indicators in the UI
   */
  updateProgressIndicators(role, level) {
    const progressBars = document.querySelectorAll('.progress-bar-promis');
    const progressCircles = document.querySelectorAll('.progress-circle');
    
    // Update progress bars
    progressBars.forEach(bar => {
      const totalLessons = parseInt(bar.dataset.totalLessons || 0);
      const percentage = this.getCompletionRate(role, level, totalLessons);
      bar.style.width = `${percentage}%`;
      bar.setAttribute('aria-valuenow', percentage);
      
      const percentageText = bar.querySelector('.percentage-text');
      if (percentageText) {
        percentageText.textContent = `${percentage}%`;
      }
    });
    
    // Update progress circles
    progressCircles.forEach(circle => {
      const totalLessons = parseInt(circle.dataset.totalLessons || 0);
      const percentage = this.getCompletionRate(role, level, totalLessons);
      circle.style.setProperty('--progress', `${percentage}%`);
      
      const percentageSpan = circle.querySelector('span');
      if (percentageSpan) {
        percentageSpan.textContent = `${percentage}%`;
      }
    });
  }
};

// ============================================
// Quiz Manager
// ============================================
const QuizManager = {
  currentQuiz: null,
  currentAnswers: {},
  
  /**
   * Initialize a quiz
   */
  initQuiz(quizId, questions) {
    this.currentQuiz = { quizId, questions };
    this.currentAnswers = {};
    this.renderQuiz();
  },
  
  /**
   * Render quiz questions
   */
  renderQuiz() {
    const container = document.getElementById('quiz-container');
    if (!container || !this.currentQuiz) return;
    
    let html = '<div class="quiz-wrapper">';
    
    this.currentQuiz.questions.forEach((question, index) => {
      html += `
        <div class="quiz-question mb-4" data-question-id="${question.id}">
          <h5 class="mb-3">Question ${index + 1}: ${question.question}</h5>
          <div class="quiz-options">
      `;
      
      question.options.forEach(option => {
        html += `
          <div class="quiz-option" data-option-id="${option.id}" onclick="QuizManager.selectAnswer(${question.id}, '${option.id}')">
            <input type="radio" name="question-${question.id}" value="${option.id}" id="option-${question.id}-${option.id}">
            <label for="option-${question.id}-${option.id}">${option.text}</label>
          </div>
        `;
      });
      
      html += `
          </div>
        </div>
      `;
    });
    
    html += `
      <div class="text-center mt-4">
        <button class="btn btn-promis-primary btn-lg" onclick="QuizManager.submitQuiz()">
          <i class="fas fa-check-circle me-2"></i>Soumettre le Quiz
        </button>
      </div>
    </div>
    `;
    
    container.innerHTML = html;
  },
  
  /**
   * Handle answer selection
   */
  selectAnswer(questionId, optionId) {
    this.currentAnswers[questionId] = optionId;
    
    // Update UI
    const questionDiv = document.querySelector(`[data-question-id="${questionId}"]`);
    questionDiv.querySelectorAll('.quiz-option').forEach(opt => {
      opt.classList.remove('selected');
    });
    
    const selectedOption = questionDiv.querySelector(`[data-option-id="${optionId}"]`);
    if (selectedOption) {
      selectedOption.classList.add('selected');
    }
  },
  
  /**
   * Submit quiz and calculate score
   */
  submitQuiz() {
    if (!this.currentQuiz) return;
    
    // Check if all questions are answered
    const totalQuestions = this.currentQuiz.questions.length;
    const answeredQuestions = Object.keys(this.currentAnswers).length;
    
    if (answeredQuestions < totalQuestions) {
      Utils.showNotification('Veuillez répondre à toutes les questions avant de soumettre.', 'warning');
      return;
    }
    
    // Calculate score
    let correctAnswers = 0;
    let totalPoints = 0;
    let earnedPoints = 0;
    
    this.currentQuiz.questions.forEach(question => {
      totalPoints += question.points || 1;
      const userAnswer = this.currentAnswers[question.id];
      const correctOption = question.options.find(opt => opt.correct);
      
      if (userAnswer === correctOption.id) {
        correctAnswers++;
        earnedPoints += question.points || 1;
      }
    });
    
    const percentage = Math.round((earnedPoints / totalPoints) * 100);
    const passed = percentage >= (this.currentQuiz.passingScore || 80);
    
    const results = {
      quizId: this.currentQuiz.quizId,
      totalQuestions,
      correctAnswers,
      percentage,
      passed,
      timestamp: new Date().toISOString()
    };
    
    // Save results
    this.saveResults(results);
    
    // Show results
    this.showResults(results);
  },
  
  /**
   * Save quiz results to localStorage
   */
  saveResults(results) {
    const key = `promis_quiz_${results.quizId}`;
    const attempts = JSON.parse(localStorage.getItem(key) || '[]');
    attempts.push(results);
    localStorage.setItem(key, JSON.stringify(attempts));
  },
  
  /**
   * Get quiz results
   */
  getResults(quizId) {
    const key = `promis_quiz_${quizId}`;
    return JSON.parse(localStorage.getItem(key) || '[]');
  },
  
  /**
   * Show quiz results in a modal
   */
  showResults(results) {
    const modalHtml = `
      <div class="modal fade" id="quizResultsModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content modal-promis">
            <div class="modal-header">
              <h5 class="modal-title">
                <i class="fas fa-${results.passed ? 'check-circle' : 'times-circle'} me-2"></i>
                Résultats du Quiz
              </h5>
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body text-center">
              <div class="mb-4">
                <div class="display-1 ${results.passed ? 'text-success' : 'text-danger'}">
                  ${results.percentage}%
                </div>
                <p class="lead">${results.correctAnswers} / ${results.totalQuestions} réponses correctes</p>
              </div>
              <div class="alert alert-${results.passed ? 'success' : 'warning'}">
                ${results.passed 
                  ? '<i class="fas fa-trophy me-2"></i>Félicitations! Vous avez réussi le quiz.' 
                  : '<i class="fas fa-redo me-2"></i>Score insuffisant. Veuillez réviser et réessayer.'}
              </div>
            </div>
            <div class="modal-footer">
              ${results.passed 
                ? '<button type="button" class="btn btn-promis-primary" data-bs-dismiss="modal">Continuer</button>'
                : '<button type="button" class="btn btn-promis-secondary" onclick="location.reload()">Réessayer</button>'}
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
};

// ============================================
// Navigation System
// ============================================
const Navigation = {
  /**
   * Initialize navigation
   */
  init() {
    this.setupSmoothScroll();
    this.setupMobileMenu();
    this.highlightActiveSection();
  },
  
  /**
   * Setup smooth scrolling for anchor links
   */
  setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href === '#') return;
        
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
  },
  
  /**
   * Setup mobile menu toggle
   */
  setupMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
      navbarCollapse.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
          if (window.innerWidth < 992) {
            navbarToggler.click();
          }
        });
      });
    }
  },
  
  /**
   * Highlight active section in navigation
   */
  highlightActiveSection() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    
    window.addEventListener('scroll', () => {
      let current = '';
      
      sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (window.pageYOffset >= sectionTop - 200) {
          current = section.getAttribute('id');
        }
      });
      
      navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
          link.classList.add('active');
        }
      });
    });
  },
  
  /**
   * Navigate to a specific lesson
   */
  goToLesson(role, level, moduleId, lessonId) {
    const relativePath = `roles/${role}/${level}/module-${moduleId}/lesson-${lessonId}.html`;
    window.location.href = getResolvedPath(relativePath);
  },
  
  /**
   * Navigate to role training page
   */
  goToRoleTraining(role, level) {
    const relativePath = `roles/${role}/${level}-level.html`;
    window.location.href = getResolvedPath(relativePath);
  },
  
  /**
   * Navigate to home
   */
  goToHome() {
    window.location.href = getResolvedPath('index.html');
  },
  
  /**
   * Navigate to certification
   */
  goToCertification() {
    const relativePath = 'certification/index.html';
    window.location.href = getResolvedPath(relativePath);
  },
  
  /**
   * Navigate to downloads
   */
  goToDownloads() {
    const relativePath = 'downloads/index.html';
    window.location.href = getResolvedPath(relativePath);
  },
  
  /**
   * Navigate to next lesson
   */
  nextLesson(currentModule, currentLesson, totalLessons) {
    // Implementation depends on lesson structure
    const nextLesson = currentLesson + 1;
    if (nextLesson <= totalLessons) {
      window.location.href = `lesson-${nextLesson}.html`;
    } else {
      Utils.showNotification('Vous avez terminé ce module!', 'success');
    }
  },
  
  /**
   * Navigate to previous lesson
   */
  previousLesson(currentModule, currentLesson) {
    const prevLesson = currentLesson - 1;
    if (prevLesson >= 1) {
      window.location.href = `lesson-${prevLesson}.html`;
    }
  }
};

// ============================================
// User Data Management
// ============================================
const UserData = {
  /**
   * Save user information
   */
  saveUser(userData) {
    const user = {
      ...userData,
      registeredAt: userData.registeredAt || new Date().toISOString(),
      userId: userData.userId || Utils.generateId()
    };
    localStorage.setItem('promis_user', JSON.stringify(user));
  },
  
  /**
   * Get user information
   */
  getUser() {
    return JSON.parse(localStorage.getItem('promis_user') || 'null');
  },
  
  /**
   * Check if user is registered
   */
  isRegistered() {
    return this.getUser() !== null;
  },
  
  /**
   * Update user information
   */
  updateUser(updates) {
    const user = this.getUser();
    if (user) {
      const updatedUser = { ...user, ...updates };
      this.saveUser(updatedUser);
    }
  },
  
  /**
   * Clear user data
   */
  clearUser() {
    localStorage.removeItem('promis_user');
  }
};

// ============================================
// Interactive Elements
// ============================================
const Interactive = {
  /**
   * Initialize tooltips
   */
  initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  },
  
  /**
   * Initialize modals
   */
  initModals() {
    // Modal event handlers can be added here
    document.querySelectorAll('.modal').forEach(modal => {
      modal.addEventListener('show.bs.modal', function(event) {
        // Custom logic when modal opens
      });
    });
  },
  
  /**
   * Initialize accordions
   */
  initAccordions() {
    document.querySelectorAll('.accordion-button').forEach(button => {
      button.addEventListener('click', function() {
        // Custom accordion logic if needed
      });
    });
  },
  
  /**
   * Initialize tabs
   */
  initTabs() {
    const triggerTabList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tab"]'));
    triggerTabList.forEach(function(triggerEl) {
      const tabTrigger = new bootstrap.Tab(triggerEl);
      
      triggerEl.addEventListener('click', function(event) {
        event.preventDefault();
        tabTrigger.show();
      });
    });
  }
};

// ============================================
// Utility Functions
// ============================================
const Utils = {
  /**
   * Format date to French locale
   */
  formatDate(date) {
    return new Date(date).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  },
  
  /**
   * Format date and time
   */
  formatDateTime(date) {
    return new Date(date).toLocaleString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  },
  
  /**
   * Generate unique ID
   */
  generateId() {
    return 'PROMIS-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9).toUpperCase();
  },
  
  /**
   * Show notification toast
   */
  showNotification(message, type = 'info') {
    const toastHtml = `
      <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'warning' ? 'warning' : type === 'error' ? 'danger' : 'info'} border-0" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : type === 'error' ? 'times-circle' : 'info-circle'} me-2"></i>
            ${message}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>
    `;
    
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
      document.body.appendChild(toastContainer);
    }
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 5000 });
    toast.show();
    
    toastElement.addEventListener('hidden.bs.toast', function() {
      this.remove();
    });
  },
  
  /**
   * Validate email format
   */
  validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  },
  
  /**
   * Debounce function
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },
  
  /**
   * Copy text to clipboard
   */
  copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
      this.showNotification('Copié dans le presse-papiers!', 'success');
    }).catch(() => {
      this.showNotification('Erreur lors de la copie', 'error');
    });
  }
};

// ============================================
// Initialization
// ============================================
document.addEventListener('DOMContentLoaded', () => {
  // Initialize navigation
  Navigation.init();
  
  // Initialize interactive elements
  Interactive.initTooltips();
  Interactive.initModals();
  Interactive.initAccordions();
  Interactive.initTabs();
  
  // Check if user is registered (for protected pages)
  const currentPath = window.location.pathname;
  if (currentPath.includes('/roles/') && !currentPath.includes('index.html')) {
    if (!UserData.isRegistered()) {
      // Redirect to registration page
      Utils.showNotification('Veuillez vous inscrire pour accéder aux formations.', 'warning');
      setTimeout(() => {
        window.location.href = getResolvedPath('register.html');
      }, 2000);
    }
  }
  
  // Update progress indicators if on a training page
  const progressElements = document.querySelectorAll('[data-role][data-level]');
  if (progressElements.length > 0) {
    const role = progressElements[0].dataset.role;
    const level = progressElements[0].dataset.level;
    ProgressTracker.updateProgressIndicators(role, level);
  }
  
  // Add animation to elements as they come into view
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('fade-in-up');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);
  
  document.querySelectorAll('.role-card, .stat-card, .level-card, .testimonial-card').forEach(el => {
    observer.observe(el);
  });
});

// Export for use in other scripts
window.ProgressTracker = ProgressTracker;
window.QuizManager = QuizManager;
window.Navigation = Navigation;
window.UserData = UserData;
window.Interactive = Interactive;
window.Utils = Utils;

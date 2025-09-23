/* SAMA PROMIS - JavaScript pour le portail public */

// Variables globales
let samaPromis = {
    apiBase: '/promispublic/api',
    currentUser: null,
    stats: {},
    projects: []
};

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    initSamaPromis();
});

// Fonction d'initialisation principale
function initSamaPromis() {
    console.log('🚀 Initialisation SAMA PROMIS Public Portal');
    
    // Ajouter les animations
    addAnimations();
    
    // Initialiser les composants
    initComponents();
    
    // Charger les statistiques
    loadStatistics();
    
    // Initialiser les événements
    initEventListeners();
}

// Ajouter des animations aux éléments
function addAnimations() {
    // Animation fade-in pour les cartes
    const cards = document.querySelectorAll('.card, .stat-card, .project-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in-up');
    });
}

// Initialiser les composants Bootstrap et autres
function initComponents() {
    // Initialiser les tooltips
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Initialiser les modals
    if (typeof bootstrap !== 'undefined') {
        var modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'));
        modalTriggerList.forEach(function (modalTriggerEl) {
            modalTriggerEl.addEventListener('click', function() {
                var target = modalTriggerEl.getAttribute('data-bs-target');
                var modal = new bootstrap.Modal(document.querySelector(target));
                modal.show();
            });
        });
    }
}

// Charger les statistiques via API
function loadStatistics() {
    fetch(samaPromis.apiBase + '/stats')
        .then(response => response.json())
        .then(data => {
            samaPromis.stats = data;
            updateStatisticsDisplay(data);
        })
        .catch(error => {
            console.error('Erreur lors du chargement des statistiques:', error);
        });
}

// Mettre à jour l'affichage des statistiques
function updateStatisticsDisplay(stats) {
    // Mettre à jour les compteurs avec animation
    animateCounter('total-projects', stats.total_projects);
    animateCounter('active-projects', stats.active_projects);
    animateCounter('completed-projects', stats.completed_projects);
    
    // Mettre à jour les graphiques si présents
    updateCharts(stats);
}

// Animation des compteurs
function animateCounter(elementId, targetValue) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const startValue = 0;
    const duration = 2000; // 2 secondes
    const startTime = performance.now();
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Fonction d'easing
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const currentValue = Math.floor(startValue + (targetValue - startValue) * easeOutQuart);
        
        element.textContent = currentValue.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }
    
    requestAnimationFrame(updateCounter);
}

// Mettre à jour les graphiques
function updateCharts(stats) {
    // Graphique par type de projet
    updateProjectTypeChart(stats.by_type);
    
    // Graphique par état
    updateProjectStateChart(stats.by_state);
}

// Graphique des types de projets (si Chart.js est disponible)
function updateProjectTypeChart(typeData) {
    const canvas = document.getElementById('projectTypeChart');
    if (!canvas || typeof Chart === 'undefined') return;
    
    const ctx = canvas.getContext('2d');
    const labels = Object.keys(typeData).map(key => typeData[key].label);
    const data = Object.keys(typeData).map(key => typeData[key].count);
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#1e3a8a',
                    '#059669',
                    '#f59e0b',
                    '#ef4444'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Initialiser les événements
function initEventListeners() {
    // Recherche en temps réel
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value);
            }, 500);
        });
    }
    
    // Filtres
    const filterSelects = document.querySelectorAll('select[name^="filter"]');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            applyFilters();
        });
    });
    
    // Boutons de suivi de projets
    document.addEventListener('click', function(e) {
        if (e.target.matches('.btn-follow-project')) {
            const projectId = e.target.getAttribute('data-project-id');
            followProject(projectId);
        }
        
        if (e.target.matches('.btn-unfollow-project')) {
            const projectId = e.target.getAttribute('data-project-id');
            unfollowProject(projectId);
        }
    });
    
    // Smooth scroll pour les ancres
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Fonction de recherche
function performSearch(query) {
    if (query.length < 3) return;
    
    showLoadingSpinner();
    
    fetch(`${samaPromis.apiBase}/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            updateProjectsList(data.projects);
            hideLoadingSpinner();
        })
        .catch(error => {
            console.error('Erreur lors de la recherche:', error);
            hideLoadingSpinner();
        });
}

// Appliquer les filtres
function applyFilters() {
    const form = document.querySelector('form');
    if (form) {
        form.submit();
    }
}

// Suivre un projet
function followProject(projectId) {
    fetch(`/promispublic/citizen/follow/${projectId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Projet ajouté à vos suivis!', 'success');
            updateFollowButton(projectId, true);
        } else {
            showNotification(data.message || 'Erreur lors du suivi', 'error');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showNotification('Erreur lors du suivi du projet', 'error');
    });
}

// Ne plus suivre un projet
function unfollowProject(projectId) {
    fetch(`/promispublic/citizen/unfollow/${projectId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Projet retiré de vos suivis', 'info');
            updateFollowButton(projectId, false);
        } else {
            showNotification(data.message || 'Erreur lors du retrait', 'error');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showNotification('Erreur lors du retrait du suivi', 'error');
    });
}

// Mettre à jour le bouton de suivi
function updateFollowButton(projectId, isFollowing) {
    const button = document.querySelector(`[data-project-id="${projectId}"]`);
    if (button) {
        if (isFollowing) {
            button.classList.remove('btn-follow-project', 'btn-outline-primary');
            button.classList.add('btn-unfollow-project', 'btn-outline-danger');
            button.innerHTML = '<i class="fa fa-heart-broken mr-1"></i>Ne plus suivre';
        } else {
            button.classList.remove('btn-unfollow-project', 'btn-outline-danger');
            button.classList.add('btn-follow-project', 'btn-outline-primary');
            button.innerHTML = '<i class="fa fa-heart mr-1"></i>Suivre';
        }
    }
}

// Afficher une notification
function showNotification(message, type = 'info') {
    // Créer l'élément de notification
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Ajouter au DOM
    document.body.appendChild(notification);
    
    // Supprimer automatiquement après 5 secondes
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Afficher le spinner de chargement
function showLoadingSpinner() {
    const spinner = document.createElement('div');
    spinner.id = 'loading-spinner';
    spinner.className = 'sama-spinner';
    
    const container = document.querySelector('.container');
    if (container) {
        container.appendChild(spinner);
    }
}

// Masquer le spinner de chargement
function hideLoadingSpinner() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.remove();
    }
}

// Obtenir le token CSRF
function getCsrfToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

// Mettre à jour la liste des projets
function updateProjectsList(projects) {
    const container = document.querySelector('.projects-container');
    if (!container) return;
    
    // Vider le conteneur
    container.innerHTML = '';
    
    // Ajouter les nouveaux projets
    projects.forEach(project => {
        const projectCard = createProjectCard(project);
        container.appendChild(projectCard);
    });
}

// Créer une carte de projet
function createProjectCard(project) {
    const card = document.createElement('div');
    card.className = 'col-lg-6 col-xl-4 mb-4';
    card.innerHTML = `
        <div class="card project-card sama-card">
            <div class="card-header">
                <span class="badge badge-sama-primary">${project.reference}</span>
                <span class="badge badge-sama-${getStateColor(project.state)} float-right">
                    ${project.state}
                </span>
            </div>
            <div class="card-body">
                <h5 class="project-title">
                    <a href="/promispublic/project/${project.id}">${project.name}</a>
                </h5>
                <p class="project-description">${project.description || 'Aucune description'}</p>
                <div class="project-meta">
                    <i class="fa fa-building"></i> ${project.donor || 'Aucun bailleur'}
                </div>
                <div class="project-meta">
                    <i class="fa fa-money-bill"></i> ${formatCurrency(project.budget)}
                </div>
                <div class="progress progress-sama mb-2">
                    <div class="progress-bar" style="width: ${project.progress}%"></div>
                </div>
                <small class="text-muted">Progression: ${project.progress}%</small>
            </div>
            <div class="card-footer">
                <a href="/promispublic/project/${project.id}" class="btn btn-sama-primary btn-sm">
                    <i class="fa fa-eye mr-1"></i>Voir détails
                </a>
            </div>
        </div>
    `;
    return card;
}

// Obtenir la couleur selon l'état
function getStateColor(state) {
    const colors = {
        'draft': 'secondary',
        'submitted': 'info',
        'under_review': 'warning',
        'approved': 'primary',
        'in_progress': 'info',
        'completed': 'success',
        'cancelled': 'danger'
    };
    return colors[state] || 'secondary';
}

// Formater la devise
function formatCurrency(amount) {
    if (!amount) return '0 XOF';
    return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'XOF',
        minimumFractionDigits: 0
    }).format(amount);
}

// Fonctions utilitaires pour l'export
window.samaPromis = samaPromis;
window.followProject = followProject;
window.unfollowProject = unfollowProject;
window.showNotification = showNotification;
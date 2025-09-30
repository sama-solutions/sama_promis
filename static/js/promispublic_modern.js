/**
 * SAMA PROMIS - Modern Public Portal JavaScript
 * Interactive features for the public transparency dashboard
 */

(function() {
    'use strict';

    // =========================================================================
    // UTILITY FUNCTIONS
    // =========================================================================

    /**
     * Debounce function to limit rate of function calls
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Show toast notification
     */
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast-notification ${type}`;
        toast.innerHTML = `
            <div class="d-flex align-center gap-2">
                <i class="fa fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Show loading overlay
     */
    function showLoading() {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.id = 'loading-overlay';
        overlay.innerHTML = '<div class="loading-spinner"></div>';
        document.body.appendChild(overlay);
    }

    /**
     * Hide loading overlay
     */
    function hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    /**
     * Update URL parameters without page reload
     */
    function updateURLParameter(param, value) {
        const url = new URL(window.location);
        if (value) {
            url.searchParams.set(param, value);
        } else {
            url.searchParams.delete(param);
        }
        window.history.pushState({}, '', url);
    }

    /**
     * Get URL parameter value
     */
    function getURLParameter(param) {
        const url = new URL(window.location);
        return url.searchParams.get(param);
    }

    // =========================================================================
    // FILTER MANAGEMENT
    // =========================================================================

    const FilterManager = {
        activeFilters: {},

        init() {
            this.bindFilterEvents();
            this.loadFiltersFromURL();
            this.loadFiltersFromStorage();
        },

        bindFilterEvents() {
            // Filter dropdowns
            document.querySelectorAll('.filter-dropdown').forEach(dropdown => {
                const toggle = dropdown.querySelector('.dropdown-toggle');
                const menu = dropdown.querySelector('.dropdown-menu');
                
                if (toggle && menu) {
                    toggle.addEventListener('click', (e) => {
                        e.stopPropagation();
                        dropdown.classList.toggle('open');
                    });

                    // Close dropdown when clicking outside
                    document.addEventListener('click', () => {
                        dropdown.classList.remove('open');
                    });

                    // Handle filter selection
                    menu.querySelectorAll('.dropdown-item').forEach(item => {
                        item.addEventListener('click', (e) => {
                            e.preventDefault();
                            const filterType = dropdown.dataset.filter;
                            const filterValue = item.dataset.value;
                            this.applyFilter(filterType, filterValue);
                        });
                    });
                }
            });

            // Filter chips
            document.querySelectorAll('.filter-chip').forEach(chip => {
                chip.addEventListener('click', () => {
                    chip.classList.toggle('active');
                    const filterType = chip.dataset.filter;
                    const filterValue = chip.dataset.value;
                    
                    if (chip.classList.contains('active')) {
                        this.applyFilter(filterType, filterValue);
                    } else {
                        this.removeFilter(filterType, filterValue);
                    }
                });
            });

            // Clear filters button
            const clearBtn = document.getElementById('clear-filters');
            if (clearBtn) {
                clearBtn.addEventListener('click', () => this.clearAllFilters());
            }

            // Apply filters button
            const applyBtn = document.getElementById('apply-filters');
            if (applyBtn) {
                applyBtn.addEventListener('click', () => this.refreshData());
            }
        },

        applyFilter(type, value) {
            if (!this.activeFilters[type]) {
                this.activeFilters[type] = [];
            }
            
            if (!this.activeFilters[type].includes(value)) {
                this.activeFilters[type].push(value);
            }
            
            this.updateFilterDisplay();
            this.saveFiltersToStorage();
            this.refreshData();
        },

        removeFilter(type, value) {
            if (this.activeFilters[type]) {
                this.activeFilters[type] = this.activeFilters[type].filter(v => v !== value);
                if (this.activeFilters[type].length === 0) {
                    delete this.activeFilters[type];
                }
            }
            
            this.updateFilterDisplay();
            this.saveFiltersToStorage();
            this.refreshData();
        },

        clearAllFilters() {
            this.activeFilters = {};
            
            // Remove active class from all filter chips
            document.querySelectorAll('.filter-chip.active').forEach(chip => {
                chip.classList.remove('active');
            });
            
            this.updateFilterDisplay();
            this.saveFiltersToStorage();
            this.refreshData();
        },

        updateFilterDisplay() {
            const container = document.getElementById('active-filters');
            if (!container) return;

            container.innerHTML = '';
            
            Object.entries(this.activeFilters).forEach(([type, values]) => {
                values.forEach(value => {
                    const chip = document.createElement('div');
                    chip.className = 'filter-chip active';
                    chip.innerHTML = `
                        ${value}
                        <i class="fa fa-times ml-2" style="cursor: pointer;"></i>
                    `;
                    chip.querySelector('i').addEventListener('click', () => {
                        this.removeFilter(type, value);
                    });
                    container.appendChild(chip);
                });
            });
        },

        loadFiltersFromURL() {
            const params = new URLSearchParams(window.location.search);
            params.forEach((value, key) => {
                if (key.startsWith('filter_')) {
                    const filterType = key.replace('filter_', '');
                    this.activeFilters[filterType] = value.split(',');
                }
            });
            this.updateFilterDisplay();
        },

        saveFiltersToStorage() {
            localStorage.setItem('promis_filters', JSON.stringify(this.activeFilters));
        },

        loadFiltersFromStorage() {
            const saved = localStorage.getItem('promis_filters');
            if (saved && Object.keys(this.activeFilters).length === 0) {
                this.activeFilters = JSON.parse(saved);
                this.updateFilterDisplay();
            }
        },

        refreshData() {
            // Update URL with filter parameters
            Object.entries(this.activeFilters).forEach(([type, values]) => {
                updateURLParameter(`filter_${type}`, values.join(','));
            });

            // Refresh project list
            if (typeof ProjectList !== 'undefined') {
                ProjectList.loadProjects();
            }
        }
    };

    // =========================================================================
    // SEARCH FUNCTIONALITY
    // =========================================================================

    const SearchManager = {
        searchHistory: [],

        init() {
            this.bindSearchEvents();
            this.loadSearchHistory();
        },

        bindSearchEvents() {
            const searchInput = document.getElementById('search-input');
            if (!searchInput) return;

            // Debounced search
            searchInput.addEventListener('input', debounce((e) => {
                this.performSearch(e.target.value);
            }, 300));

            // Search on enter
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch(e.target.value);
                }
            });

            // Show search suggestions
            searchInput.addEventListener('focus', () => {
                this.showSearchSuggestions();
            });
        },

        performSearch(query) {
            if (!query || query.length < 2) return;

            // Add to search history
            this.addToHistory(query);

            // Update URL
            updateURLParameter('q', query);

            // Perform search via AJAX
            fetch(`/promispublic/search?q=${encodeURIComponent(query)}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                this.displaySearchResults(data);
            })
            .catch(error => {
                console.error('Search error:', error);
                showToast('Erreur lors de la recherche', 'error');
            });
        },

        displaySearchResults(data) {
            const container = document.getElementById('search-results');
            if (!container) return;

            container.innerHTML = '';
            
            if (data.projects && data.projects.length > 0) {
                data.projects.forEach(project => {
                    // Render project card
                    const card = this.createProjectCard(project);
                    container.appendChild(card);
                });
            } else {
                container.innerHTML = '<p class="text-center text-promis-gray">Aucun résultat trouvé</p>';
            }
        },

        createProjectCard(project) {
            const card = document.createElement('div');
            card.className = 'project-card';
            card.innerHTML = `
                <div class="project-header">
                    <div class="project-code">${project.code}</div>
                    <h3 class="project-title">${project.name}</h3>
                    <div class="project-meta">
                        <span class="badge-promis-${project.state_class}">${project.state_label}</span>
                    </div>
                </div>
                <div class="project-footer">
                    <a href="/promispublic/project/${project.id}" class="btn-promis-primary">Voir détails</a>
                </div>
            `;
            return card;
        },

        showSearchSuggestions() {
            if (this.searchHistory.length === 0) return;

            const input = document.getElementById('search-input');
            const suggestions = document.createElement('div');
            suggestions.className = 'search-suggestions';
            suggestions.innerHTML = this.searchHistory.slice(0, 5).map(term => `
                <div class="suggestion-item">${term}</div>
            `).join('');

            // Position suggestions below input
            input.parentNode.appendChild(suggestions);

            // Handle suggestion clicks
            suggestions.querySelectorAll('.suggestion-item').forEach(item => {
                item.addEventListener('click', () => {
                    input.value = item.textContent;
                    this.performSearch(item.textContent);
                    suggestions.remove();
                });
            });
        },

        addToHistory(query) {
            if (!this.searchHistory.includes(query)) {
                this.searchHistory.unshift(query);
                this.searchHistory = this.searchHistory.slice(0, 10); // Keep last 10
                localStorage.setItem('promis_search_history', JSON.stringify(this.searchHistory));
            }
        },

        loadSearchHistory() {
            const saved = localStorage.getItem('promis_search_history');
            if (saved) {
                this.searchHistory = JSON.parse(saved);
            }
        }
    };

    // =========================================================================
    // STATISTICS UPDATES
    // =========================================================================

    const StatsManager = {
        refreshInterval: 300000, // 5 minutes

        init() {
            this.startAutoRefresh();
            this.bindRefreshButton();
        },

        startAutoRefresh() {
            setInterval(() => {
                this.fetchStats();
            }, this.refreshInterval);
        },

        bindRefreshButton() {
            const refreshBtn = document.getElementById('refresh-stats');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', () => {
                    this.fetchStats();
                });
            }
        },

        fetchStats() {
            fetch('/promispublic/api/stats')
                .then(response => response.json())
                .then(data => {
                    this.updateStats(data);
                })
                .catch(error => {
                    console.error('Stats fetch error:', error);
                });
        },

        updateStats(data) {
            // Animate number changes
            Object.entries(data).forEach(([key, value]) => {
                const element = document.querySelector(`[data-stat="${key}"]`);
                if (element) {
                    this.animateNumber(element, parseInt(value));
                }
            });
        },

        animateNumber(element, targetValue) {
            const currentValue = parseInt(element.textContent.replace(/\D/g, '')) || 0;
            const duration = 1000;
            const steps = 60;
            const increment = (targetValue - currentValue) / steps;
            let current = currentValue;
            let step = 0;

            const timer = setInterval(() => {
                step++;
                current += increment;
                element.textContent = Math.round(current).toLocaleString();

                if (step >= steps) {
                    element.textContent = targetValue.toLocaleString();
                    clearInterval(timer);
                }
            }, duration / steps);
        }
    };

    // =========================================================================
    // INTERACTIVE CHARTS
    // =========================================================================

    const ChartManager = {
        charts: {},

        init() {
            if (typeof Chart === 'undefined') {
                console.warn('Chart.js not loaded');
                return;
            }

            this.initProjectTypeChart();
            this.initBudgetChart();
            this.initTimelineChart();
        },

        initProjectTypeChart() {
            const canvas = document.getElementById('project-type-chart');
            if (!canvas) return;

            fetch('/promispublic/api/charts?type=project_types')
                .then(response => response.json())
                .then(data => {
                    this.charts.projectType = new Chart(canvas, {
                        type: 'pie',
                        data: {
                            labels: data.labels,
                            datasets: [{
                                data: data.values,
                                backgroundColor: [
                                    '#1e3a8a',
                                    '#059669',
                                    '#f59e0b',
                                    '#3b82f6',
                                    '#ef4444'
                                ]
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    position: 'bottom'
                                }
                            }
                        }
                    });
                });
        },

        initBudgetChart() {
            const canvas = document.getElementById('budget-chart');
            if (!canvas) return;

            fetch('/promispublic/api/charts?type=budget_by_donor')
                .then(response => response.json())
                .then(data => {
                    this.charts.budget = new Chart(canvas, {
                        type: 'bar',
                        data: {
                            labels: data.labels,
                            datasets: [{
                                label: 'Budget (FCFA)',
                                data: data.values,
                                backgroundColor: '#1e3a8a'
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                });
        },

        initTimelineChart() {
            const canvas = document.getElementById('timeline-chart');
            if (!canvas) return;

            fetch('/promispublic/api/charts?type=timeline')
                .then(response => response.json())
                .then(data => {
                    this.charts.timeline = new Chart(canvas, {
                        type: 'line',
                        data: {
                            labels: data.labels,
                            datasets: [{
                                label: 'Projets',
                                data: data.values,
                                borderColor: '#1e3a8a',
                                backgroundColor: 'rgba(30, 58, 138, 0.1)',
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false
                        }
                    });
                });
        }
    };

    // =========================================================================
    // PAGINATION & INFINITE SCROLL
    // =========================================================================

    const ProjectList = {
        currentPage: 1,
        loading: false,
        hasMore: true,

        init() {
            this.bindInfiniteScroll();
            this.bindPaginationButtons();
        },

        bindInfiniteScroll() {
            if (!document.getElementById('projects-container')) return;

            window.addEventListener('scroll', debounce(() => {
                if (this.loading || !this.hasMore) return;

                const scrollPosition = window.innerHeight + window.scrollY;
                const threshold = document.documentElement.scrollHeight - 500;

                if (scrollPosition >= threshold) {
                    this.loadNextPage();
                }
            }, 200));
        },

        bindPaginationButtons() {
            const nextBtn = document.getElementById('next-page');
            const prevBtn = document.getElementById('prev-page');

            if (nextBtn) {
                nextBtn.addEventListener('click', () => this.loadNextPage());
            }

            if (prevBtn) {
                prevBtn.addEventListener('click', () => this.loadPrevPage());
            }
        },

        loadNextPage() {
            this.currentPage++;
            this.loadProjects(true);
        },

        loadPrevPage() {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.loadProjects(false);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        },

        loadProjects(append = false) {
            if (this.loading) return;

            this.loading = true;
            this.showLoadingSpinner();

            const filters = FilterManager.activeFilters;
            const params = new URLSearchParams({
                page: this.currentPage,
                ...filters
            });

            fetch(`/promispublic/api/projects?${params}`)
                .then(response => response.json())
                .then(data => {
                    this.renderProjects(data.projects, append);
                    this.hasMore = data.has_more;
                    this.loading = false;
                    this.hideLoadingSpinner();
                })
                .catch(error => {
                    console.error('Error loading projects:', error);
                    this.loading = false;
                    this.hideLoadingSpinner();
                    showToast('Erreur lors du chargement des projets', 'error');
                });
        },

        renderProjects(projects, append) {
            const container = document.getElementById('projects-container');
            if (!container) return;

            if (!append) {
                container.innerHTML = '';
            }

            projects.forEach(project => {
                const card = SearchManager.createProjectCard(project);
                container.appendChild(card);
            });
        },

        showLoadingSpinner() {
            const spinner = document.getElementById('loading-spinner');
            if (spinner) {
                spinner.style.display = 'block';
            }
        },

        hideLoadingSpinner() {
            const spinner = document.getElementById('loading-spinner');
            if (spinner) {
                spinner.style.display = 'none';
            }
        }
    };

    // =========================================================================
    // QR CODE GENERATION
    // =========================================================================

    const QRCodeManager = {
        init() {
            this.bindQRCodeButtons();
            this.generatePageQRCode();
        },

        bindQRCodeButtons() {
            // Copy link button
            const copyBtn = document.getElementById('copy-link');
            if (copyBtn) {
                copyBtn.addEventListener('click', () => {
                    navigator.clipboard.writeText(window.location.href);
                    showToast('Lien copié!', 'success');
                });
            }

            // Download QR code button
            const downloadBtn = document.getElementById('download-qr');
            if (downloadBtn) {
                downloadBtn.addEventListener('click', () => {
                    this.downloadQRCode();
                });
            }

            // Share buttons
            this.bindShareButtons();
        },

        generatePageQRCode() {
            const container = document.getElementById('qr-code');
            if (!container || typeof QRCode === 'undefined') return;

            new QRCode(container, {
                text: window.location.href,
                width: 200,
                height: 200,
                colorDark: '#1e3a8a',
                colorLight: '#ffffff',
                correctLevel: QRCode.CorrectLevel.H
            });
        },

        downloadQRCode() {
            const canvas = document.querySelector('#qr-code canvas');
            if (!canvas) return;

            const link = document.createElement('a');
            link.download = 'promis-qrcode.png';
            link.href = canvas.toDataURL();
            link.click();
        },

        bindShareButtons() {
            const url = encodeURIComponent(window.location.href);
            const title = encodeURIComponent(document.title);

            // WhatsApp
            const whatsappBtn = document.querySelector('.share-btn.whatsapp');
            if (whatsappBtn) {
                whatsappBtn.href = `https://wa.me/?text=${title}%20${url}`;
            }

            // Twitter
            const twitterBtn = document.querySelector('.share-btn.twitter');
            if (twitterBtn) {
                twitterBtn.href = `https://twitter.com/intent/tweet?text=${title}&url=${url}`;
            }

            // Facebook
            const facebookBtn = document.querySelector('.share-btn.facebook');
            if (facebookBtn) {
                facebookBtn.href = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
            }

            // Email
            const emailBtn = document.querySelector('.share-btn.email');
            if (emailBtn) {
                emailBtn.href = `mailto:?subject=${title}&body=${url}`;
            }
        }
    };

    // =========================================================================
    // MODAL MANAGEMENT
    // =========================================================================

    const ModalManager = {
        init() {
            this.bindModalTriggers();
            this.bindModalClose();
        },

        bindModalTriggers() {
            document.querySelectorAll('[data-modal]').forEach(trigger => {
                trigger.addEventListener('click', (e) => {
                    e.preventDefault();
                    const modalId = trigger.dataset.modal;
                    this.openModal(modalId);
                });
            });
        },

        bindModalClose() {
            document.querySelectorAll('.modal-promis').forEach(modal => {
                // Close on backdrop click
                modal.addEventListener('click', (e) => {
                    if (e.target === modal) {
                        this.closeModal(modal);
                    }
                });

                // Close on close button click
                const closeBtn = modal.querySelector('.modal-close');
                if (closeBtn) {
                    closeBtn.addEventListener('click', () => {
                        this.closeModal(modal);
                    });
                }
            });

            // Close on ESC key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.closeAllModals();
                }
            });
        },

        openModal(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.style.display = 'flex';
                document.body.style.overflow = 'hidden';
            }
        },

        closeModal(modal) {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        },

        closeAllModals() {
            document.querySelectorAll('.modal-promis').forEach(modal => {
                this.closeModal(modal);
            });
        }
    };

    // =========================================================================
    // ANIMATIONS & TRANSITIONS
    // =========================================================================

    const AnimationManager = {
        init() {
            this.initIntersectionObserver();
            this.bindSmoothScroll();
        },

        initIntersectionObserver() {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-fade-in-up');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1
            });

            document.querySelectorAll('.modern-card, .stat-card, .project-card').forEach(el => {
                observer.observe(el);
            });
        },

        bindSmoothScroll() {
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function(e) {
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
    };

    // =========================================================================
    // RESPONSIVE BEHAVIOR
    // =========================================================================

    const ResponsiveManager = {
        init() {
            this.bindMobileMenu();
            this.handleResize();
        },

        bindMobileMenu() {
            const menuToggle = document.getElementById('mobile-menu-toggle');
            const mobileMenu = document.getElementById('mobile-menu');

            if (menuToggle && mobileMenu) {
                menuToggle.addEventListener('click', () => {
                    mobileMenu.classList.toggle('open');
                });
            }
        },

        handleResize() {
            let resizeTimer;
            window.addEventListener('resize', () => {
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(() => {
                    // Redraw charts on resize
                    if (ChartManager.charts) {
                        Object.values(ChartManager.charts).forEach(chart => {
                            if (chart) chart.resize();
                        });
                    }
                }, 250);
            });
        }
    };

    // =========================================================================
    // INITIALIZATION
    // =========================================================================

    document.addEventListener('DOMContentLoaded', () => {
        FilterManager.init();
        SearchManager.init();
        StatsManager.init();
        ChartManager.init();
        ProjectList.init();
        QRCodeManager.init();
        ModalManager.init();
        AnimationManager.init();
        ResponsiveManager.init();

        console.log('SAMA PROMIS Public Portal initialized');
    });

})();

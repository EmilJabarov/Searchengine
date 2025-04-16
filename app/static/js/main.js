// Flash message auto-dismiss
document.addEventListener('DOMContentLoaded', function() {
    // Flash message handling
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.style.opacity = '1';
        alert.style.transition = 'opacity 0.3s ease';
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 3000);
    });

    // Search form animation
    const searchInput = document.querySelector('.search-box input');
    if (searchInput) {
        searchInput.addEventListener('focus', () => {
            searchInput.parentElement.classList.add('focused');
        });
        searchInput.addEventListener('blur', () => {
            searchInput.parentElement.classList.remove('focused');
        });
    }

    // Profile preferences auto-save
    const preferencesForm = document.querySelector('.preferences-form');
    if (preferencesForm) {
        let saveTimeout;
        const preferencesInput = preferencesForm.querySelector('textarea');
        const saveStatus = document.createElement('div');
        saveStatus.className = 'save-status';
        preferencesForm.appendChild(saveStatus);

        preferencesInput.addEventListener('input', () => {
            saveStatus.textContent = 'Saving...';
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                const formData = new FormData(preferencesForm);
                fetch('/profile', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (response.ok) {
                        saveStatus.textContent = 'Saved!';
                        setTimeout(() => {
                            saveStatus.textContent = '';
                        }, 2000);
                    } else {
                        saveStatus.textContent = 'Error saving';
                    }
                })
                .catch(() => {
                    saveStatus.textContent = 'Error saving';
                });
            }, 1000);
        });
    }

    // Mobile navigation toggle
    const navToggle = document.createElement('button');
    navToggle.className = 'nav-toggle';
    navToggle.innerHTML = '<span></span><span></span><span></span>';
    document.querySelector('.navbar').appendChild(navToggle);

    navToggle.addEventListener('click', () => {
        document.querySelector('.nav-links').classList.toggle('active');
        navToggle.classList.toggle('active');
    });

    // Search history interaction
    const historyItems = document.querySelectorAll('.history-item');
    historyItems.forEach(item => {
        item.addEventListener('click', () => {
            const query = item.querySelector('.original-query').textContent.replace('Original: ', '');
            if (searchInput) {
                searchInput.value = query;
                searchInput.focus();
            }
        });
    });

    // Results animation
    const resultCards = document.querySelectorAll('.result-card');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '50px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    resultCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        observer.observe(card);
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                    
                    const errorMsg = document.createElement('div');
                    errorMsg.className = 'error-message';
                    errorMsg.textContent = 'This field is required';
                    
                    if (!field.nextElementSibling?.classList.contains('error-message')) {
                        field.parentElement.appendChild(errorMsg);
                    }
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });

        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                input.classList.remove('error');
                const errorMsg = input.parentElement.querySelector('.error-message');
                if (errorMsg) {
                    errorMsg.remove();
                }
            });
        });
    });

    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('.copy-button');
    copyButtons.forEach(button => {
        button.addEventListener('click', () => {
            const textToCopy = button.getAttribute('data-copy');
            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalText = button.textContent;
                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = originalText;
                }, 2000);
            });
        });
    });
});
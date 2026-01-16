// Daily Deal Darling - Main JavaScript

(function() {
    'use strict';

    // =====================
    // Exit Intent Email Popup
    // =====================

    const POPUP_STORAGE_KEY = 'ddd_popup_shown';

    function initExitIntentPopup() {
        // Check if popup was already shown this session
        if (sessionStorage.getItem(POPUP_STORAGE_KEY)) {
            return;
        }

        const popup = document.getElementById('email-popup');
        if (!popup) return;

        let popupShown = false;
        let mouseLeftDocument = false;

        // Exit intent detection - mouse moves toward top of viewport
        document.addEventListener('mouseout', function(e) {
            if (popupShown) return;

            // Check if mouse is leaving toward the top
            if (e.clientY < 10 && e.relatedTarget === null) {
                mouseLeftDocument = true;
                showPopup();
            }
        });

        // Also trigger on rapid mouse movement upward
        let lastY = 0;
        document.addEventListener('mousemove', function(e) {
            if (popupShown) return;

            // Detect rapid upward movement toward browser top
            if (e.clientY < 50 && lastY > e.clientY && (lastY - e.clientY) > 30) {
                showPopup();
            }
            lastY = e.clientY;
        });

        function showPopup() {
            if (popupShown) return;
            popupShown = true;

            popup.classList.add('show');
            sessionStorage.setItem(POPUP_STORAGE_KEY, 'true');

            // Prevent body scroll
            document.body.style.overflow = 'hidden';
        }

        function hidePopup() {
            popup.classList.remove('show');
            document.body.style.overflow = '';
        }

        // Close button
        const closeBtn = popup.querySelector('.popup-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', hidePopup);
        }

        // Click outside to close
        popup.addEventListener('click', function(e) {
            if (e.target === popup) {
                hidePopup();
            }
        });

        // ESC key to close
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && popup.classList.contains('show')) {
                hidePopup();
            }
        });

        // Popup form submission
        const popupForm = popup.querySelector('.popup-form');
        if (popupForm) {
            popupForm.addEventListener('submit', function(e) {
                e.preventDefault();

                const emailInput = popupForm.querySelector('input[type="email"]');
                const email = emailInput.value.trim();

                if (email && isValidEmail(email)) {
                    // For now, just console.log (will connect to ConvertKit later)
                    console.log('Popup Email Signup:', email);

                    // Show success state
                    const formContent = popup.querySelector('.popup-form-content');
                    const successContent = popup.querySelector('.popup-success');

                    if (formContent) formContent.style.display = 'none';
                    if (successContent) successContent.classList.add('show');

                    // Auto close after 3 seconds
                    setTimeout(hidePopup, 3000);
                }
            });
        }
    }

    // =====================
    // Footer Email Signup
    // =====================

    function initFooterSignup() {
        const footerForm = document.getElementById('footer-signup-form');
        if (!footerForm) return;

        footerForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const emailInput = footerForm.querySelector('input[type="email"]');
            const email = emailInput.value.trim();
            const submitBtn = footerForm.querySelector('button');

            if (email && isValidEmail(email)) {
                // For now, just console.log (will connect to ConvertKit later)
                console.log('Footer Email Signup:', email);

                // Show success feedback
                const originalText = submitBtn.textContent;
                submitBtn.textContent = 'Subscribed!';
                submitBtn.disabled = true;
                emailInput.value = '';

                setTimeout(function() {
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                }, 3000);
            }
        });
    }

    // =====================
    // Quiz Functionality
    // =====================

    function initQuiz() {
        const quizContainer = document.querySelector('.quiz-container');
        if (!quizContainer) return;

        const questions = quizContainer.querySelectorAll('.quiz-question');
        const progressBar = quizContainer.querySelector('.quiz-progress-bar');
        const prevBtn = quizContainer.querySelector('.quiz-btn-prev');
        const nextBtn = quizContainer.querySelector('.quiz-btn-next');
        const resultsSection = quizContainer.querySelector('.quiz-results');

        let currentQuestion = 0;
        const answers = {};

        function updateQuiz() {
            // Hide all questions
            questions.forEach((q, index) => {
                q.style.display = index === currentQuestion ? 'block' : 'none';
            });

            // Update progress bar
            if (progressBar) {
                const progress = ((currentQuestion + 1) / questions.length) * 100;
                progressBar.style.width = progress + '%';
            }

            // Update buttons
            if (prevBtn) {
                prevBtn.disabled = currentQuestion === 0;
            }
            if (nextBtn) {
                nextBtn.textContent = currentQuestion === questions.length - 1 ? 'See Results' : 'Next';
            }
        }

        // Option selection
        questions.forEach((question, qIndex) => {
            const options = question.querySelectorAll('.quiz-option');
            options.forEach((option, oIndex) => {
                option.addEventListener('click', function() {
                    // Remove selected from siblings
                    options.forEach(o => o.classList.remove('selected'));
                    // Add selected to clicked
                    option.classList.add('selected');
                    // Store answer
                    answers[qIndex] = oIndex;
                });
            });
        });

        // Navigation
        if (prevBtn) {
            prevBtn.addEventListener('click', function() {
                if (currentQuestion > 0) {
                    currentQuestion--;
                    updateQuiz();
                }
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', function() {
                if (currentQuestion < questions.length - 1) {
                    currentQuestion++;
                    updateQuiz();
                } else {
                    // Show results
                    showResults();
                }
            });
        }

        function showResults() {
            const questionsWrapper = quizContainer.querySelector('.quiz-questions');
            const navWrapper = quizContainer.querySelector('.quiz-nav');
            const progressWrapper = quizContainer.querySelector('.quiz-progress');

            if (questionsWrapper) questionsWrapper.style.display = 'none';
            if (navWrapper) navWrapper.style.display = 'none';
            if (progressWrapper) progressWrapper.style.display = 'none';
            if (resultsSection) resultsSection.classList.add('show');

            console.log('Quiz completed. Answers:', answers);
        }

        // Initialize
        updateQuiz();
    }

    // =====================
    // Utility Functions
    // =====================

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // =====================
    // Initialize Everything
    // =====================

    document.addEventListener('DOMContentLoaded', function() {
        initExitIntentPopup();
        initFooterSignup();
        initQuiz();
    });

})();

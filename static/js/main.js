document.addEventListener('DOMContentLoaded', function() {
    // Get the button and quiz section
    const findMatchBtn = document.getElementById('findMatchBtn');
    const quizSection = document.getElementById('quiz');
    const quizForm = document.getElementById('quiz-form');

    // Add click event listener to the Find Your Match button
    if (findMatchBtn) {
        findMatchBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // Show the quiz section
            quizSection.style.display = 'block';
            // Smooth scroll to the quiz section
            quizSection.scrollIntoView({ behavior: 'smooth' });
        });
    }

    // Handle form submission
    if (quizForm) {
        quizForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show loading state
            const submitButton = quizForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Finding your perfect matches...
            `;
            submitButton.disabled = true;

            // Collect form data
            const formData = new FormData(quizForm);
            const data = {};
            for (let [key, value] of formData.entries()) {
                if (data[key]) {
                    // If the key already exists, make it an array
                    if (!Array.isArray(data[key])) {
                        data[key] = [data[key]];
                    }
                    data[key].push(value);
                } else {
                    data[key] = value;
                }
            }

            // Send data to backend
            fetch('/get_recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayRecommendations(data.recommendations);
                } else {
                    displayError();
                }
            })
            .catch(() => {
                displayError();
            })
            .finally(() => {
                // Reset button state
                submitButton.innerHTML = originalButtonText;
                submitButton.disabled = false;
            });
        });
    }

    function displayRecommendations(recommendations) {
        const resultsContainer = document.createElement('div');
        resultsContainer.className = 'recommendations-container mt-4';
        
        let html = `
            <h3 class="text-center mb-4">Your Personalized Recommendations</h3>
            <div class="row">
        `;
        
        recommendations.forEach(item => {
            html += `
                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">${item.name}</h5>
                            <p class="card-text">${item.description}</p>
                            <p class="card-text"><small class="text-muted">$${item.price}</small></p>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';
        resultsContainer.innerHTML = html;
        
        // Replace the form with the results
        quizForm.style.display = 'none';
        quizForm.parentNode.insertBefore(resultsContainer, quizForm.nextSibling);
    }

    function displayError() {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger mt-3';
        errorDiv.role = 'alert';
        errorDiv.innerHTML = 'Sorry, there was an error processing your request. Please try again.';
        quizForm.insertAdjacentElement('beforebegin', errorDiv);
        
        // Remove the error message after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    // Add smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Feedback Form Handling
    document.getElementById('feedbackForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form values
        const name = document.getElementById('feedbackName').value;
        const email = document.getElementById('feedbackEmail').value;
        const type = document.getElementById('feedbackType').value;
        const message = document.getElementById('feedbackMessage').value;
        const consent = document.getElementById('feedbackConsent').checked;
        
        // Create feedback data object
        const feedbackData = {
            name,
            email,
            type,
            message,
            consent,
            timestamp: new Date().toISOString()
        };
        
        // Show loading state
        const submitBtn = document.querySelector('#feedbackForm button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        submitBtn.disabled = true;
        
        // Simulate sending feedback (replace with actual API call)
        setTimeout(() => {
            // Reset form
            document.getElementById('feedbackForm').reset();
            
            // Show success message
            const modalBody = document.querySelector('#feedbackModal .modal-body');
            const successMessage = document.createElement('div');
            successMessage.className = 'alert alert-success';
            successMessage.innerHTML = `
                <i class="fas fa-check-circle me-2"></i>
                Thank you for your feedback! We'll review it shortly.
            `;
            modalBody.insertBefore(successMessage, document.getElementById('feedbackForm'));
            
            // Reset button
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            
            // Close modal after delay
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('feedbackModal'));
                modal.hide();
                
                // Remove success message after modal is hidden
                successMessage.remove();
            }, 3000);
        }, 1500);
    });

    // Add event listener for Get Started link
    const getStartedLink = document.querySelector('a[href="#quiz"]');
    if (getStartedLink) {
        getStartedLink.addEventListener('click', function(e) {
            e.preventDefault();
            const quizSection = document.getElementById('quiz');
            if (quizSection) {
                quizSection.style.display = 'block';
                quizSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
}); 
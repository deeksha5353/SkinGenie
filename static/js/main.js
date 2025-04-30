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
    const surveyForm = document.getElementById('survey-form');
    if (surveyForm) {
        // Check if the form has a data-ajax attribute set to "true"
        const useAjax = surveyForm.getAttribute('data-ajax') === 'true';
        
        surveyForm.addEventListener('submit', function(e) {
            // If not using AJAX, just let the form submit normally
            if (!useAjax) {
                return true;
            }
            
            e.preventDefault();
            
            // Show loading state
            const submitButton = surveyForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Finding your perfect matches...
            `;
            submitButton.disabled = true;

            // Collect form data
            const formData = new FormData(surveyForm);
            
            // Send data to backend
            fetch('/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new URLSearchParams(formData)
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.error || 'An error occurred while processing your request');
                    });
                }
                return response.text().then(text => {
                    try {
                        return JSON.parse(text);
                    } catch (e) {
                        console.error('Error parsing JSON:', e);
                        console.error('Response text:', text);
                        throw new Error('Invalid response from server');
                    }
                });
            })
            .then(data => {
                if (!Array.isArray(data)) {
                    throw new Error('Invalid response format: expected an array');
                }

                // Create recommendations container
                const container = document.createElement('div');
                container.className = 'container mt-4';
                container.id = 'recommendations-container';
                
                // Create recommendations header
                const header = document.createElement('h2');
                header.className = 'text-center mb-4';
                header.textContent = 'Your Personalized Recommendations';
                container.appendChild(header);
                
                if (data.length === 0) {
                    // Show message if no recommendations
                    const noResults = document.createElement('div');
                    noResults.className = 'alert alert-info';
                    noResults.textContent = 'No recommendations found. Please try adjusting your preferences.';
                    container.appendChild(noResults);
                } else {
                    // Create table for recommendations
                    const table = document.createElement('table');
                    table.className = 'table table-hover';
                    
                    // Create table header
                    const thead = document.createElement('thead');
                    thead.innerHTML = `
                        <tr>
                            <th>Category</th>
                            <th>Product Name</th>
                            <th>Price</th>
                            <th>Action</th>
                        </tr>
                    `;
                    table.appendChild(thead);
                    
                    // Create table body
                    const tbody = document.createElement('tbody');
                    data.forEach(product => {
                        // Validate product data
                        if (!product || typeof product !== 'object') {
                            console.error('Invalid product data:', product);
                            return;
                        }

                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${product.Category || 'N/A'}</td>
                            <td>${product['Product Name'] || 'N/A'}</td>
                            <td>${product.Price || 'N/A'}</td>
                            <td>
                                ${product.URL && product.URL !== '#' ? 
                                    `<a href="${product.URL}" target="_blank" class="btn btn-sm btn-primary" onclick="return checkLink(event, this)">View Product</a>` :
                                    `<span class="text-muted">Link not available</span>`
                                }
                            </td>
                        `;
                        tbody.appendChild(row);
                    });
                    table.appendChild(tbody);
                    container.appendChild(table);
                }
                
                // Add back button
                const backButton = document.createElement('div');
                backButton.className = 'text-center mt-4';
                backButton.innerHTML = '<a href="/" class="btn btn-primary">Start Over</a>';
                container.appendChild(backButton);
                
                // Replace form with recommendations
                surveyForm.parentNode.replaceChild(container, surveyForm);
                
                // Scroll to the top of the recommendations
                window.scrollTo({
                    top: container.offsetTop - 20,
                    behavior: 'smooth'
                });
            })
            .catch(error => {
                console.error('Error:', error);
                submitButton.innerHTML = originalButtonText;
                submitButton.disabled = false;
                
                // Show error message to user
                const errorDiv = document.createElement('div');
                errorDiv.className = 'alert alert-danger mt-3';
                errorDiv.role = 'alert';
                errorDiv.innerHTML = `
                    <i class="fas fa-exclamation-circle me-2"></i>
                    ${error.message || 'An error occurred. Please try again.'}
                `;
                
                // Remove any existing error messages
                const existingError = surveyForm.querySelector('.alert-danger');
                if (existingError) {
                    existingError.remove();
                }
                
                // Insert error message before the form
                surveyForm.parentNode.insertBefore(errorDiv, surveyForm);
                
                // Remove the error message after 5 seconds
                setTimeout(() => {
                    errorDiv.remove();
                }, 5000);
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

function checkLink(event, linkElement) {
    const url = linkElement.href;
    if (!url || url === '#' || !url.startsWith('http')) {
        event.preventDefault();
        alert('This product link is not available at the moment.');
        return false;
    }
    return true; 
} 
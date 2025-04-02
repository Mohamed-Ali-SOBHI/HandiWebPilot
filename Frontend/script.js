// Ajoutez ces fonctions au début du fichier
function saveSearchResults(question, results) {
    localStorage.setItem('lastQuestion', question);
    localStorage.setItem('lastResults', results);
}

function loadSearchResults() {
    const lastQuestion = localStorage.getItem('lastQuestion');
    const lastResults = localStorage.getItem('lastResults');
    
    if (lastQuestion && lastResults) {
        const questionInput = document.getElementById('questionInput');
        const searchSection = document.querySelector('.search-section');
        const results = document.getElementById('results');
        const resultsContent = document.getElementById('resultsContent');
        
        questionInput.value = lastQuestion;
        searchSection.classList.add('hidden');
        results.classList.remove('hidden');
        resultsContent.innerHTML = formatResponse(lastResults);
    }
}

async function performSearch() {
    const questionInput = document.getElementById('questionInput');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const resultsContent = document.getElementById('resultsContent');
    const searchSection = document.querySelector('.search-section');
    
    const question = questionInput.value.trim();
    if (!question) {
        showNotification('Veuillez entrer une question');
        return;
    }
    
    searchSection.classList.add('hidden');
    loading.classList.remove('hidden');
    results.classList.add('hidden');
    
    try {
        const response = await fetch('https://handiwebpilot.onrender.com/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            mode: 'cors',
            body: JSON.stringify({ question })
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Erreur ${response.status}: ${errorText}`);
        }
        
        const data = await response.json();
        loading.classList.add('hidden');
        results.classList.remove('hidden');
        
        const formattedResult = data.error ? createErrorMessage(data.error) : formatResponse(data.result);
        resultsContent.innerHTML = formattedResult;
        results.scrollIntoView({ behavior: 'smooth' });
        
        // Sauvegarder les résultats
        saveSearchResults(question, data.result);
        
    } catch (error) {
        console.error('Erreur de recherche:', error);
        loading.classList.add('hidden');
        results.classList.remove('hidden');
        resultsContent.innerHTML = createErrorMessage(`Une erreur est survenue: ${error.message}`);
    }
}

function createErrorMessage(message) {
    return `<div class="error-message"><i class="fas fa-exclamation-circle"></i> <p>${message}</p></div>`;
}

function formatResponse(text) {
    marked.setOptions({ 
        breaks: true, 
        sanitize: false, 
        gfm: true,
        renderer: new marked.Renderer()
    });

    // Personnaliser le rendu des liens
    const renderer = new marked.Renderer();
    renderer.link = function(href, title, text) {
        return `<a href="${href}" target="_blank" rel="noopener noreferrer">${text}</a>`;
    };

    try {
        const htmlContent = marked.parse(text, { renderer });
        return `<div class="markdown-content">${htmlContent}</div>`;
    } catch (error) {
        console.error('Erreur du markdown:', error);
        return text;
    }
}

function resetSearch() {
    const questionInput = document.getElementById('questionInput');
    const results = document.getElementById('results');
    const searchSection = document.querySelector('.search-section');
    
    results.classList.add('hidden');
    searchSection.classList.remove('hidden');
    questionInput.value = '';
    questionInput.focus();
    document.querySelector('.search-section').scrollIntoView({ behavior: 'smooth' });
    
    // Effacer les résultats sauvegardés
    localStorage.removeItem('lastQuestion');
    localStorage.removeItem('lastResults');
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.innerHTML = `<div class="notification-content"><i class="fas fa-info-circle"></i> <span>${message}</span></div>`;
    document.body.appendChild(notification);
    setTimeout(() => { notification.classList.add('show'); }, 10);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => { notification.remove(); }, 300);
    }, 3000);
}

document.getElementById('questionInput').addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'Enter') {
        performSearch();
    }
});

// Add this new function for handling contact form submission
function handleContactFormSubmission(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);

    fetch('sendmail.php', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        showNotification(data);
        if (data.includes("Thank You")) {
            form.reset();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Une erreur est survenue lors de l\'envoi du message.');
    });
}

function setQuestion(question) {
    const questionInput = document.getElementById('questionInput');
    questionInput.value = question;
    performSearch();
}

// Ajoutez cet écouteur d'événements à la fin du fichier
document.addEventListener('DOMContentLoaded', loadSearchResults);

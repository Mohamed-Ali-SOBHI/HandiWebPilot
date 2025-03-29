async function performSearch() {
    const questionInput = document.getElementById('questionInput');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const resultsContent = document.getElementById('resultsContent');
    
    const question = questionInput.value.trim();
    
    if (!question) {
        alert('Veuillez entrer une question');
        return;
    }

    // Afficher le chargement
    loading.classList.remove('hidden');
    results.classList.add('hidden');

    try {
        const response = await fetch('http://localhost:5000/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            mode: 'cors', // Explicitement définir le mode CORS
            body: JSON.stringify({ question: question })
        });

        // Vérifier si la réponse est OK
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }

        const data = await response.json();
        
        loading.classList.add('hidden');
        results.classList.remove('hidden');
        
        if (data.error) {
            resultsContent.innerHTML = `<p style="color: red">${data.error}</p>`;
        } else {
            resultsContent.innerHTML = formatResponse(data.result);
        }
    } catch (error) {
        console.error('Erreur de recherche détaillée:', error);
        resultsContent.innerHTML = `Une erreur est survenue lors de la recherche: ${error.message}`;
        loading.classList.add('hidden');
        results.classList.remove('hidden');
    }
}

function formatResponse(text) {
    // Configure marked options for security
    marked.setOptions({
        breaks: true,  // Convert \n to <br>
        sanitize: false, // Allow HTML
        gfm: true,     // Enable GitHub Flavored Markdown
    });
    
    try {
        // Convert markdown to HTML
        const htmlContent = marked.parse(text);
        return `<div class="markdown-content">${htmlContent}</div>`;
    } catch (error) {
        console.error('Error parsing markdown:', error);
        return text; // Fallback to plain text if parsing fails
    }
}
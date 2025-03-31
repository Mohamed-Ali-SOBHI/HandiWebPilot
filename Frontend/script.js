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
    
    // Masquer la section de recherche
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
      
      resultsContent.innerHTML = data.error ? createErrorMessage(data.error) : formatResponse(data.result);
      results.scrollIntoView({ behavior: 'smooth' });
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
    marked.setOptions({ breaks: true, sanitize: false, gfm: true });
    try {
      const htmlContent = marked.parse(text);
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
    searchSection.classList.remove('hidden'); // Réaffiche la section de recherche
    questionInput.value = '';
    questionInput.focus();
    document.querySelector('.search-section').scrollIntoView({ behavior: 'smooth' });
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

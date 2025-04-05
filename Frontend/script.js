// Fonctions pour la sauvegarde et le chargement des résultats
function saveSearchResults(question, clarifications, results) {
  localStorage.setItem('lastQuestion', question);
  localStorage.setItem('lastClarifications', JSON.stringify(clarifications || {}));
  localStorage.setItem('lastResults', results);
}

function loadSearchResults() {
  const lastQuestion = localStorage.getItem('lastQuestion');
  const lastClarifications = localStorage.getItem('lastClarifications');
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
      
      // Si nous avons des clarifications, les afficher
      if (lastClarifications) {
          const clarificationsObj = JSON.parse(lastClarifications);
          const clarificationsHtml = formatClarifications(clarificationsObj);
          
          if (clarificationsHtml) {
              const clarificationsDiv = document.createElement('div');
              clarificationsDiv.className = 'clarifications-summary';
              clarificationsDiv.innerHTML = `
                  <h3>Précisions fournies :</h3>
                  ${clarificationsHtml}
              `;
              resultsContent.insertAdjacentElement('afterbegin', clarificationsDiv);
          }
      }
  }
}

// Fonction pour le processus de recherche en deux étapes
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
      // Étape 1: Vérifier si des clarifications sont nécessaires
      const clarificationResponse = await fetch('https://handiwebpilot.onrender.com/api/check-clarification', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          mode: 'cors',
          body: JSON.stringify({ question })
      });
      
      if (!clarificationResponse.ok) {
          const errorText = await clarificationResponse.text();
          throw new Error(`Erreur ${clarificationResponse.status}: ${errorText}`);
      }
      
      const clarificationData = await clarificationResponse.json();
      
      // Si la question n'est pas légitime
      if (clarificationData.status === 'error') {
          loading.classList.add('hidden');
          results.classList.remove('hidden');
          resultsContent.innerHTML = createErrorMessage(clarificationData.error);
          return;
      }
      
      // Si des clarifications sont nécessaires
      if (clarificationData.needs_clarification && clarificationData.questions.length > 0) {
          loading.classList.add('hidden');
          
          // Afficher les questions de clarification
          const clarifications = await showClarificationDialog(clarificationData.questions);
          
          if (!clarifications) {
              // L'utilisateur a annulé
              searchSection.classList.remove('hidden');
              return;
          }
          
          // Réafficher le loader pour la recherche avec clarifications
          searchSection.classList.add('hidden');
          loading.classList.remove('hidden');
          
          // Étape 2: Effectuer la recherche avec les clarifications
          return executeSearch(question, clarifications);
      }
      
      // Si aucune clarification n'est nécessaire, procéder directement à la recherche
      return executeSearch(question);
      
  } catch (error) {
      console.error('Erreur lors de la vérification des clarifications:', error);
      loading.classList.add('hidden');
      results.classList.remove('hidden');
      resultsContent.innerHTML = createErrorMessage(`Une erreur est survenue: ${error.message}`);
  }
}

// Fonction pour afficher un dialogue de clarification
function showClarificationDialog(questions) {
  return new Promise((resolve) => {
      // Créer le modal de clarification
      const modalOverlay = document.createElement('div');
      modalOverlay.className = 'modal-overlay';
      
      const modalContainer = document.createElement('div');
      modalContainer.className = 'modal-container';
      
      let questionHtml = '';
      questions.forEach((question, index) => {
          questionHtml += `
              <div class="clarification-question">
                  <label for="clarification-${index}">${question}</label>
                  <textarea id="clarification-${index}" class="clarification-input" rows="2"></textarea>
              </div>
          `;
      });
      
      modalContainer.innerHTML = `
          <div class="modal-header">
              <h3>Des précisions sont nécessaires</h3>
          </div>
          <div class="modal-body">
              ${questionHtml}
          </div>
          <div class="modal-footer">
            <button id="submit-clarification" class="btn btn-primary">Rechercher</button>
            <button id="cancel-clarification" class="btn btn-outline">Annuler</button>
          </div>
      `;
      
      modalOverlay.appendChild(modalContainer);
      document.body.appendChild(modalOverlay);
      
      // Animation d'ouverture
      setTimeout(() => modalOverlay.classList.add('active'), 10);
      
      // Gérer les actions
      document.getElementById('cancel-clarification').addEventListener('click', () => {
          closeModal();
          resolve(null);
      });
      
      document.getElementById('submit-clarification').addEventListener('click', () => {
          const clarifications = {};
          questions.forEach((question, index) => {
              const input = document.getElementById(`clarification-${index}`);
              clarifications[question] = input.value.trim() || "Information non fournie";
          });
          
          closeModal();
          resolve(clarifications);
      });
      
      // Fonction pour fermer le modal
      function closeModal() {
          modalOverlay.classList.remove('active');
          setTimeout(() => modalOverlay.remove(), 300);
      }
  });
}

// Formater les clarifications pour l'affichage
function formatClarifications(clarifications) {
  if (!clarifications || Object.keys(clarifications).length === 0) {
      return '';
  }
  
  let html = '<ul class="clarifications-list">';
  for (const [question, answer] of Object.entries(clarifications)) {
      html += `<li><strong>${question}</strong> ${answer}</li>`;
  }
  html += '</ul>';
  
  return html;
}

// Fonction pour exécuter la recherche (avec ou sans clarifications)
async function executeSearch(question, clarifications = null) {
  const loading = document.getElementById('loading');
  const results = document.getElementById('results');
  const resultsContent = document.getElementById('resultsContent');
  
  try {
      const response = await fetch('https://handiwebpilot.onrender.com/api/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          mode: 'cors',
          body: JSON.stringify({ 
              question: question,
              clarifications: clarifications || {}
          })
      });
      
      if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Erreur ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      loading.classList.add('hidden');
      results.classList.remove('hidden');
      
      let formattedResult = '';
      
      if (data.error) {
          formattedResult = createErrorMessage(data.error);
      } else {
          // Ajouter le résultat formaté
          formattedResult += formatResponse(data.result);
      }
      
      resultsContent.innerHTML = formattedResult;
      results.scrollIntoView({ behavior: 'smooth' });
      
      // Sauvegarder les résultats
      saveSearchResults(question, clarifications, data.result);
      
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
    // Prétraiter le texte pour convertir les liens markdown en HTML
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    const htmlWithLinks = text.replace(linkRegex, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    
    marked.setOptions({ 
      breaks: true, 
      sanitize: false, 
      gfm: true
    });
  
    try {
      const htmlContent = marked.parse(htmlWithLinks);
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
  localStorage.removeItem('lastClarifications');
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

// Ajouter un événement pour charger le jeton CSRF et configurer le formulaire
document.addEventListener('DOMContentLoaded', function() {
    loadSearchResults();
    
    // Charger le jeton CSRF si on est sur la page de contact
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        // Chargement du jeton CSRF
        fetch('init_session.php')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur lors du chargement du jeton CSRF');
                }
                return response.text();
            })
            .then(token => {
                if (token && token.trim() !== '') {
                    document.getElementById('csrf_token').value = token.trim();
                    console.log('Jeton CSRF chargé avec succès');
                } else {
                    console.error('Le jeton CSRF reçu est vide');
                    showNotification('Erreur de sécurité: impossible de charger le jeton CSRF');
                }
            })
            .catch(error => {
                console.error('Erreur CSRF:', error);
                showNotification('Erreur de sécurité: impossible de charger le jeton CSRF');
            });
        
        // Ajout de l'écouteur d'événement pour la soumission du formulaire
        contactForm.addEventListener('submit', handleContactFormSubmission);
    }
});

function setQuestion(question) {
  const questionInput = document.getElementById('questionInput');
  questionInput.value = question;
  performSearch();
}

// Fonction pour gérer la soumission du formulaire de contact
function handleContactFormSubmission(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.textContent;
    
    // Changer le texte du bouton pour indiquer le chargement
    submitButton.textContent = 'Envoi en cours...';
    submitButton.disabled = true;
    
    // Préparer les données du formulaire
    const formData = new FormData(form);
    
    // Envoyer la requête
    fetch(form.action, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erreur réseau');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Afficher un message de succès
            showNotification(data.message);
            
            // Réinitialiser le formulaire
            form.reset();
        } else {
            // Afficher les erreurs
            let errorMessage = data.message || 'Une erreur est survenue';
            
            if (data.errors && data.errors.length > 0) {
                errorMessage += ': ' + data.errors.join(', ');
            }
            
            showNotification(errorMessage);
        }
    })
    .catch(error => {
        console.error('Erreur lors de l\'envoi du formulaire:', error);
        showNotification('Une erreur est survenue lors de l\'envoi du message. Veuillez réessayer plus tard.');
    })
    .finally(() => {
        // Restaurer le texte original du bouton
        submitButton.textContent = originalButtonText;
        submitButton.disabled = false;
    });
}

// Modifiez également la partie du DOMContentLoaded pour supprimer la partie CSRF
document.addEventListener('DOMContentLoaded', function() {
    loadSearchResults();
    
    // Ajouter l'écouteur d'événement pour la soumission du formulaire de contact
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactFormSubmission);
    }
});
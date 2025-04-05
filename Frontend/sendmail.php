<?php
// Configuration des paramètres d'email
$admin_email = "mohammedalisobhi@gmail.com";
$site_name = "Handicap Info";

// Fonction pour nettoyer les entrées
function clean_input($data) {
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}

// Vérifier si la méthode est POST
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    
    // Récupération et nettoyage des données du formulaire
    $subject = isset($_POST['subject']) ? clean_input($_POST['subject']) : '';
    $name = isset($_POST['name']) ? clean_input($_POST['name']) : '';
    $email = isset($_POST['email']) ? clean_input($_POST['email']) : '';
    $message = isset($_POST['message']) ? clean_input($_POST['message']) : '';
    
    // Validation des données
    $errors = [];
    
    if (empty($subject)) {
        $errors[] = "Le sujet est requis";
    }
    
    if (empty($name)) {
        $errors[] = "Le nom est requis";
    }
    
    if (empty($email)) {
        $errors[] = "L'email est requis";
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $errors[] = "Format d'email invalide";
    }
    
    if (empty($message)) {
        $errors[] = "Le message est requis";
    }
    
    // Si des erreurs existent, renvoyer les erreurs
    if (!empty($errors)) {
        echo json_encode([
            'success' => false,
            'message' => 'Erreurs de validation',
            'errors' => $errors
        ]);
        exit;
    }
    
    // Préparer l'email
    $to = $admin_email;
    $email_subject = "[Contact $site_name] $subject";
    
    $email_body = "Vous avez reçu un nouveau message du formulaire de contact de $site_name.\n\n";
    $email_body .= "Détails:\n";
    $email_body .= "Nom: $name\n";
    $email_body .= "Email: $email\n";
    $email_body .= "Sujet: $subject\n\n";
    $email_body .= "Message:\n$message\n";
    
    $headers = "From: $email\r\n";
    $headers .= "Reply-To: $email\r\n";
    
    // Protection contre les injections d'en-têtes
    $name = str_replace(array("\r", "\n"), '', $name);
    $email = str_replace(array("\r", "\n"), '', $email);
    
    // Tentative d'envoi de l'email
    try {
        if (mail($to, $email_subject, $email_body, $headers)) {
            // Email envoyé avec succès
            
            // Enregistrer le contact dans un fichier log (optionnel)
            $log_file = 'contact_log.txt';
            $log_message = date('Y-m-d H:i:s') . " - Nom: $name, Email: $email, Sujet: $subject\n";
            
            if (file_exists($log_file)) {
                file_put_contents($log_file, $log_message, FILE_APPEND);
            }
            
            // Réponse de succès
            echo json_encode([
                'success' => true,
                'message' => 'Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.'
            ]);
        } else {
            // Échec de l'envoi de l'email
            echo json_encode([
                'success' => false,
                'message' => 'Une erreur est survenue lors de l\'envoi du message. Veuillez réessayer plus tard.'
            ]);
        }
    } catch (Exception $e) {
        // Capturer toute exception
        echo json_encode([
            'success' => false,
            'message' => 'Une erreur système est survenue: ' . $e->getMessage()
        ]);
    }
} else {
    // Si la méthode n'est pas POST, rediriger vers la page de contact
    header('Location: contact.html');
    exit;
}
?>
<?php
session_start();

if($_SERVER["REQUEST_METHOD"] == "POST") {
    if (!isset($_POST['csrf_token']) || !isset($_SESSION['csrf_token']) || 
        $_POST['csrf_token'] !== $_SESSION['csrf_token']) {
        http_response_code(403);
        echo "Token CSRF invalide";
        exit;
    }
    $name = strip_tags(trim($_POST["name"]));
    $email = filter_var(trim($_POST["email"]), FILTER_SANITIZE_EMAIL);
    $message = trim($_POST["message"]);
    $subject = strip_tags(trim($_POST["subject"]));

    if ( empty($name) OR empty($message) OR !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        // Handle the error here
        echo "Veuillez remplir tous les champs correctement";
        exit;
    }

    // Sécuriser les headers en vérifiant les caractères spéciaux
    if (preg_match("/[\r\n]/", $name) || preg_match("/[\r\n]/", $email)) {
        http_response_code(400);
        echo "En-têtes invalides détectés";
        exit;
    }

    $recipient = "mohammedalisobhi@gmail.com";
    $email_subject = "[$subject] Message de $name";
    $email_content = "Sujet: $subject\n";
    $email_content .= "Nom: $name\n";
    $email_content .= "Email: $email\n\n";
    $email_content .= "Message:\n$message\n";

    $email_headers = "From: =?UTF-8?B?".base64_encode($name)."?= <{$email}>\r\n";
    $email_headers .= "MIME-Version: 1.0\r\n";
    $email_headers .= "Content-Type: text/plain; charset=UTF-8\r\n";

    if (mail($recipient, $email_subject, $email_content, $email_headers)) {
        // Set a 200 (okay) response code.
        http_response_code(200);
        echo "Merci! Votre message a été envoyé avec succès.";
    } else {
        // Set a 500 (internal server error) response code.
        http_response_code(500);
        echo "Désolé! Une erreur s'est produite lors de l'envoi du message.";
    }
} else {
    // Not a POST request, set a 403 (forbidden) response code.
    http_response_code(403);
    echo "Il y a eu un problème avec votre soumission, veuillez réessayer.";
}
?>
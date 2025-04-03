<?php
session_start();
header('Content-Type: text/plain');
header('Cache-Control: no-store, no-cache, must-revalidate');
if (empty($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}
echo $_SESSION['csrf_token'];
?>

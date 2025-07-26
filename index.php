<?php
// Dashboard generator for rotating screensaver displays
// Ideal for Kindle jailbreaks with the Online-ScreenSavers extension

$dashboards = ['weather'];//, 'alerts', 'image'];
$stateFile = __DIR__ . '/dashboard_state.txt';

$current = 0;
if (file_exists($stateFile)) {
    $current = (int)file_get_contents($stateFile);
}

$dashboard = $dashboards[$current];
file_put_contents($stateFile, ($current + 1) % count($dashboards));

// Render and serve
require_once __DIR__ . "/dashboards/$dashboard.php";
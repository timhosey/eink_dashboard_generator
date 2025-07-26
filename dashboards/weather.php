<?php
header("Content-Type: image/png");

$width = 600;
$height = 800;

$img = imagecreatetruecolor($width, $height);
$white = imagecolorallocate($img, 255, 255, 255);
$black = imagecolorallocate($img, 0, 0, 0);
imagefilledrectangle($img, 0, 0, $width, $height, $white);

// Dummy weather info (replace with real API call!)
$weather = "Partly Cloudy";
$temp = "72°F";
$date = date("Y-m-d H:i");

imagettftext($img, 20, 0, 20, 60, $black, "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "Weather");
imagettftext($img, 16, 0, 20, 120, $black, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "Condition: $weather");
imagettftext($img, 16, 0, 20, 160, $black, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "Temp: $temp");
imagettftext($img, 12, 0, 20, 780, $black, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "Updated: $date");

imagepng($img);
imagedestroy($img);
<?php
header("Content-Type: image/png");

$width = 600;
$height = 800;

// Step 1: Create truecolor canvas (RGB)
$true = imagecreatetruecolor($width, $height);

// Step 2: Fill with white background
$white = imagecolorallocate($true, 255, 255, 255);
imagefilledrectangle($true, 0, 0, $width, $height, $white);

// Step 3: Draw content (you can use shades of gray, black, etc.)
$black = imagecolorallocate($true, 0, 0, 0);
$gray = imagecolorallocate($true, 128, 128, 128);
imagettftext($true, 20, 0, 20, 60, $black, "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "E-Ink Grayscale FTW!");
imagettftext($true, 16, 0, 20, 100, $gray, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "Smooth like a kitten~");

// Step 4: Convert to 8-bit grayscale palette
$grayscale = imagecreate($width, $height);
imagecopy($grayscale, $true, 0, 0, 0, 0, $width, $height);
imagetruecolortopalette($grayscale, false, 256); // false = no dithering

// Step 5: Output as PNG
imagepng($grayscale);

// Cleanup
imagedestroy($true);
imagedestroy($grayscale);
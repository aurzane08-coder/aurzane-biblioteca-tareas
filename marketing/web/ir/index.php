<?php
// Enlace corto de AURZANE: aurzane.com/ir/CODIGO -> página con utm. Cuenta el clic sin guardar datos personales.
header('Cache-Control: no-store, max-age=0');
$c = preg_replace('/[^a-f0-9]/', '', $_GET['c'] ?? '');
$mapa = json_decode(@file_get_contents(__DIR__ . '/mapa.json'), true) ?: [];
$destino = $mapa[$c] ?? 'https://aurzane.com/';
if (!preg_match('#^https://([a-z]+\.)?aurzane\.com/#', $destino)) $destino = 'https://aurzane.com/';
$ua = strtolower($_SERVER['HTTP_USER_AGENT'] ?? '');
$tipo = preg_match('/bot|crawl|spider|preview|facebookexternalhit|whatsapp|telegram|slack|discord|curl|python|wget|headless|bsky|mastodon|embed/', $ua) || $ua === '' ? 'b' : 'h';
if ($c !== '') @file_put_contents(dirname(__DIR__, 2) . '/ir-clics.log', gmdate('Y-m-d H:i') . "\t$c\t$tipo\n", FILE_APPEND | LOCK_EX);
header('Location: ' . $destino, true, 302);

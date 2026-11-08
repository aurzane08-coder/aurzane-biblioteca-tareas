#!/bin/bash
# Descarga robots.txt y páginas de ejemplo de las webs de frases para ver su estructura (solo lectura).
mkdir -p /tmp/sf; cd /tmp/sf
UA="Mozilla/5.0 (compatible; AurzaneBot/1.0; +https://aurzane.com)"
for u in https://www.proverbia.net/robots.txt https://www.proverbia.net/ https://www.proverbia.net/frase-del-dia https://www.proverbia.net/autores https://www.proverbia.net/temas \
         https://www.mundifrases.com/robots.txt https://www.mundifrases.com/ https://www.frasesypensamientos.com.ar/robots.txt https://www.frasesypensamientos.com.ar/; do
  f=$(echo "$u" | sed 's#https://##; s#[/:]#_#g'); curl -sSL -A "$UA" -m 30 -o "$f.html" -w "%{http_code} %{url_effective}\n" "$u" >> codigos.txt 2>&1; sleep 3
done

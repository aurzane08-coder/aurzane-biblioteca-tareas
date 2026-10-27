#!/bin/bash
# Sondeo 2: RUCT consulta de grados de una universidad, ficha de universidad y de título
set -x
O=univ/sondeo; mkdir -p $O
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
B="https://www.educacion.gob.es/ruct"
C=(-sSL -A "$UA" -c /tmp/ck -b /tmp/ck)
curl "${C[@]}" "$B/consultaestudios?actual=estudios" -o /dev/null
curl "${C[@]}" -X POST "$B/consultaestudios.action?actual=estudios" --data "consulta=1&codigoEstudio=&codigoUniversidad=014&descripcionEstudio=&codigoTipo=G&codigoSubTipo=&codigoRama=&ambito=&codigoEstado=&situacion=" -o $O/r2_lista014.html
curl "${C[@]}" "$B/universidad.action?codigoUniversidad=014&actual=universidades" -o $O/r2_univ014.html
COD=$(grep -o 'estudio.action?codigoCiclo=[^"&]*&amp;codigoTipo=[^"&]*&amp;CodigoEstudio=[0-9]*' $O/r2_lista014.html | head -1 | sed 's/&amp;/\&/g')
echo "COD=$COD"
[ -n "$COD" ] && curl "${C[@]}" "$B/$COD&actual=estudios" -o $O/r2_estudio.html
grep -o 'href="[^"]*estudio[^"]*"' $O/r2_lista014.html | head -20 > $O/r2_links.txt
grep -o 'href="[^"]*d-[0-9]*-[pe]=[^"]*"' $O/r2_lista014.html | head -20 >> $O/r2_links.txt
ls -la $O

# sondeo 2b

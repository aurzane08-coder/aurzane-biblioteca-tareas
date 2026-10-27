#!/bin/bash
# Sondeo 3: lista de grados (con action:listaestudios), detalle de un título
set -x
O=univ/sondeo; mkdir -p $O
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
B="https://www.educacion.gob.es/ruct"
C=(-sSL -A "$UA" -c /tmp/ck -b /tmp/ck)
curl "${C[@]}" "$B/consultaestudios?actual=estudios" -o /dev/null
curl "${C[@]}" -X POST "$B/consultaestudios.action?actual=estudios" --data-urlencode "consulta=1" --data "codigoEstudio=&codigoUniversidad=014&descripcionEstudio=&codigoTipo=G&codigoSubTipo=&codigoRama=&ambito=&codigoEstado=P&situacion=A&buscarHistorico=N" --data-urlencode "action:listaestudios=Consultar" -o $O/r3_lista014.html
grep -o 'href="[^"]*"' $O/r3_lista014.html | sort -u > $O/r3_links.txt
COD=$(grep -o 'href="[^"]*estudio\.action[^"]*"' $O/r3_lista014.html | head -1 | sed 's/href="//;s/"$//;s/&amp;/\&/g')
echo "COD=$COD" >> $O/r3_links.txt
[ -n "$COD" ] && curl "${C[@]}" "https://www.educacion.gob.es$COD" -o $O/r3_estudio.html
EXP=$(grep -o 'href="[^"]*6578706f7274=1[^"]*"' $O/r3_lista014.html | head -1 | sed 's/href="//;s/"$//;s/&amp;/\&/g')
echo "EXP=$EXP" >> $O/r3_links.txt
[ -n "$EXP" ] && curl "${C[@]}" "$B/$EXP" -o $O/r3_export.bin
ls -la $O

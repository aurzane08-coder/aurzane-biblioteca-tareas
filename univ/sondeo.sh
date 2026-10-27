#!/bin/bash
# Sondeo: RUCT y Supabase (solo lectura)
set -x
O=univ/sondeo; mkdir -p $O
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
curl -sSL -A "$UA" -c /tmp/ck -b /tmp/ck "https://www.educacion.gob.es/ruct/home" -o $O/ruct_home.html
curl -sSL -A "$UA" -c /tmp/ck -b /tmp/ck "https://www.educacion.gob.es/ruct/listauniversidades" -o $O/ruct_univ.html
curl -sSL -A "$UA" -c /tmp/ck -b /tmp/ck "https://www.educacion.gob.es/ruct/listaestudios" -o $O/ruct_estudios.html
curl -sSL -A "$UA" -c /tmp/ck -b /tmp/ck "https://www.educacion.gob.es/ruct/listacentros" -o $O/ruct_centros.html
U=https://chtfpqwrrarfdjcivlad.supabase.co; K=sb_publishable___1v6VjDew0l8uGfMyb9Nw_YyCLTPPw
curl -sS "$U/rest/v1/universidades?select=*&limit=3" -H "apikey: $K" -H "Authorization: Bearer $K" -o $O/sb_univ.json
curl -sS "$U/rest/v1/carreras?select=*&limit=3" -H "apikey: $K" -H "Authorization: Bearer $K" -o $O/sb_carr.json
curl -sS -X POST "$U/rest/v1/rpc/buscar_universidades" -H "apikey: $K" -H "Authorization: Bearer $K" -H "Content-Type: application/json" -d '{"p_q":"madrid"}' -o $O/sb_buscar.json
curl -sS -X POST "$U/rest/v1/rpc/facetas_universidades" -H "apikey: $K" -H "Authorization: Bearer $K" -H "Content-Type: application/json" -d '{}' -o $O/sb_facetas.json
curl -sS "$U/rest/v1/" -H "apikey: $K" -H "Authorization: Bearer $K" -o $O/sb_openapi.json
ls -la $O

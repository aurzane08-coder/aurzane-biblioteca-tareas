-- Sustituye las 5 universidades españolas antiguas por el RUCT completo
delete from public.carreras where universidad_id in (select id from public.universidades where pais = 'España' and coalesce(fuente,'') <> 'admin');
delete from public.universidades where pais = 'España' and coalesce(fuente,'') <> 'admin';

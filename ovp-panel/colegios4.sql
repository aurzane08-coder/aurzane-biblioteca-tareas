-- Colegios, cuarta parte (16/11/2026). Re-ejecutable.
-- El código de acceso de cada colegio deja de poder leerse sin ser administrador:
--  * anon y authenticated leen membretes sin la columna codigo (permiso por columna);
--  * el portal busca el colegio de un enlace ?inst= con membrete_por_codigo(), que solo devuelve nombre e institución;
--  * el admin trabaja con la vista membretes_admin, que solo muestra filas a quien es administrador.
create or replace function public.membrete_por_codigo(p_codigo text)
returns table(nombre_marca text, subtitulo text, institucion text)
language sql stable security definer set search_path = public as $$
  select m.nombre_marca, m.subtitulo, m.institucion from membretes m
   where m.activo and coalesce(m.codigo, '') <> '' and lower(m.codigo) = lower(trim(p_codigo)) limit 1
$$;
revoke execute on function public.membrete_por_codigo(text) from public;
grant execute on function public.membrete_por_codigo(text) to anon, authenticated;

create or replace view public.membretes_admin with (security_barrier = true) as
  select * from public.membretes where public.es_admin()
  with local check option;
revoke all on public.membretes_admin from public, anon;
grant select, insert, update, delete on public.membretes_admin to authenticated;

do $$
declare cols text;
begin
  select string_agg(quote_ident(column_name), ', ') into cols from information_schema.columns
   where table_schema = 'public' and table_name = 'membretes' and column_name <> 'codigo';
  execute 'revoke select on public.membretes from anon, authenticated';
  execute 'grant select (' || cols || ') on public.membretes to anon, authenticated';
end $$;

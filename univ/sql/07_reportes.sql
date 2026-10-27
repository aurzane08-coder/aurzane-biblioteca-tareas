-- Buzón de reportes: cualquier visitante de cualquier mundo AURZANE puede avisar de un problema
-- (enlace roto, dato incorrecto, página que no funciona, sugerencia). También lo usa el revisor
-- automático de enlaces. Solo el equipo (es_admin) los lee y gestiona.

create table if not exists public.reportes (
  id          uuid primary key default gen_random_uuid(),
  creado      timestamptz not null default now(),
  tipo        text not null check (tipo in ('enlace','dato','pagina','sugerencia','otro')),
  mensaje     text not null check (char_length(mensaje) between 3 and 2000),
  url         text check (url is null or char_length(url) <= 600),
  referencia  text check (referencia is null or char_length(referencia) <= 300),
  email       text check (email is null or (char_length(email) <= 200 and email ~ '^[^@\s]+@[^@\s]+\.[^@\s]+$')),
  navegador   text check (navegador is null or char_length(navegador) <= 300),
  origen      text not null default 'visitante' check (origen in ('visitante','robot')),
  estado      text not null default 'nuevo' check (estado in ('nuevo','revisando','resuelto','descartado')),
  nota        text,
  resuelto    timestamptz,
  user_id     uuid default auth.uid(),
  ip_hash     text
);
create index if not exists reportes_estado_idx on public.reportes (estado, creado desc);
create index if not exists reportes_ip_idx on public.reportes (ip_hash, creado desc);
create unique index if not exists reportes_robot_unico on public.reportes (url, referencia) where origen = 'robot' and estado in ('nuevo','revisando');

alter table public.reportes enable row level security;
revoke all on public.reportes from anon, authenticated;
grant select, update, delete on public.reportes to authenticated;

drop policy if exists reportes_admin_select on public.reportes;
create policy reportes_admin_select on public.reportes for select to authenticated using ((select public.es_admin()));
drop policy if exists reportes_admin_update on public.reportes;
create policy reportes_admin_update on public.reportes for update to authenticated using ((select public.es_admin())) with check ((select public.es_admin()));
drop policy if exists reportes_admin_delete on public.reportes;
create policy reportes_admin_delete on public.reportes for delete to authenticated using ((select public.es_admin()));

-- Entrada pública con límite: 6 reportes por hora y conexión.
create or replace function public.reportar_problema(p_tipo text, p_mensaje text, p_url text default null, p_referencia text default null, p_email text default null, p_navegador text default null)
returns uuid
language plpgsql security definer set search_path = public as $$
declare
  v_ip text := coalesce(split_part(current_setting('request.headers', true)::json ->> 'x-forwarded-for', ',', 1), 'sin-ip');
  v_hash text := md5('aurzane-reportes:' || v_ip);
  v_id uuid;
begin
  if (select count(*) from public.reportes where ip_hash = v_hash and creado > now() - interval '1 hour') >= 6 then
    raise exception 'Demasiados reportes seguidos. Inténtalo más tarde.';
  end if;
  insert into public.reportes (tipo, mensaje, url, referencia, email, navegador, ip_hash)
  values (coalesce(nullif(p_tipo, ''), 'otro'), trim(p_mensaje), left(p_url, 600), left(p_referencia, 300), nullif(trim(p_email), ''), left(p_navegador, 300), v_hash)
  returning id into v_id;
  return v_id;
end $$;
revoke all on function public.reportar_problema(text, text, text, text, text, text) from public;
grant execute on function public.reportar_problema(text, text, text, text, text, text) to anon, authenticated;

-- Entrada del revisor automático de enlaces (GitHub Actions): solo URL de aurzane.com, sin duplicados abiertos,
-- y cierra solo los avisos de enlaces que ya vuelven a funcionar.
create or replace function public.reportes_robot(p_rotos jsonb)
returns int
language plpgsql security definer set search_path = public as $$
declare n int := 0; r jsonb;
begin
  if jsonb_typeof(p_rotos) <> 'array' or jsonb_array_length(p_rotos) > 400 then
    raise exception 'Formato no válido';
  end if;
  update public.reportes set estado = 'resuelto', resuelto = now(), nota = coalesce(nota || ' · ', '') || 'Cerrado solo: el enlace vuelve a funcionar'
   where origen = 'robot' and estado in ('nuevo','revisando')
     and url not in (select x ->> 'url' from jsonb_array_elements(p_rotos) x);
  for r in select * from jsonb_array_elements(p_rotos) loop
    continue when coalesce(r ->> 'url', '') !~ '^https://([a-z]+\.)?aurzane\.com/';
    insert into public.reportes (tipo, mensaje, url, referencia, origen)
    values ('enlace', 'Enlace roto (' || coalesce(r ->> 'estado', '?') || ') detectado por el revisor automático', left(r ->> 'url', 600), left(r ->> 'desde', 300), 'robot')
    on conflict do nothing;
    n := n + 1;
  end loop;
  return n;
end $$;
revoke all on function public.reportes_robot(jsonb) from public;
grant execute on function public.reportes_robot(jsonb) to anon;

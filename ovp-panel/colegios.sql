-- Acceso de colegios a OVP (15/11/2026). Re-ejecutable.
-- Cada colegio = un membrete con código (enlace ovp.aurzane.com/?inst=CODIGO).
-- El personal del colegio entra con su AURZANE ID; queda vinculado por su correo en colegio_miembros (lo da de alta el admin).
-- El colegio ve el avance de sus estudiantes; el informe solo si el estudiante decide compartirlo.

create table if not exists public.colegio_miembros (
  email text not null check (email = lower(email)),
  membrete_id uuid not null references public.membretes(id) on delete cascade,
  nombre text,
  rol text not null default 'orientador' check (rol in ('orientador','direccion')),
  creado timestamptz not null default now(),
  primary key (email, membrete_id)
);
alter table public.colegio_miembros enable row level security;
drop policy if exists cm_admin on public.colegio_miembros;
create policy cm_admin on public.colegio_miembros for all to authenticated using (public.es_admin()) with check (public.es_admin());
drop policy if exists cm_propio on public.colegio_miembros;
create policy cm_propio on public.colegio_miembros for select to authenticated using (email = lower(auth.email()));
revoke all on public.colegio_miembros from anon;
grant select, insert, update, delete on public.colegio_miembros to authenticated;

alter table public.clientes add column if not exists comparte_informe_colegio boolean not null default false;

create or replace function public.es_miembro_colegio(p uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from colegio_miembros where membrete_id = p and email = lower(auth.email()))
$$;

create or replace function public.colegio_mis_colegios()
returns table(id uuid, nombre text, subtitulo text, institucion text, codigo text, escudo_url text, color_acento text, rol text)
language sql stable security definer set search_path = public as $$
  select m.id, m.nombre_marca, m.subtitulo, m.institucion, m.codigo, m.escudo_url, m.color_acento, cm.rol
    from colegio_miembros cm join membretes m on m.id = cm.membrete_id
   where cm.email = lower(auth.email())
  union
  select m.id, m.nombre_marca, m.subtitulo, m.institucion, m.codigo, m.escudo_url, m.color_acento, 'admin'
    from membretes m where public.es_admin() and coalesce(m.codigo, '') <> ''
$$;

create or replace function public.colegio_estudiantes(p_membrete uuid)
returns table(cliente_id uuid, nombre text, curso text, creado timestamptz, elegidas int, completadas int, ultima timestamptz, terminado timestamptz, comparte boolean)
language sql stable security definer set search_path = public as $$
  select c.id, c.nombre, c.curso, c.created_at,
         (select count(*) from activaciones a where a.cliente_id = c.id and (a.activo or a.completado))::int,
         (select count(*) from activaciones a where a.cliente_id = c.id and a.completado)::int,
         (select max(greatest(a.completado_at, a.activado_at)) from activaciones a where a.cliente_id = c.id),
         c.proceso_completado_at, c.comparte_informe_colegio
    from clientes c
   where c.membrete_id = p_membrete and c.eliminado_at is null
     and (public.es_miembro_colegio(p_membrete) or public.es_admin())
   order by c.created_at desc
$$;

create or replace function public.colegio_informe(p_cliente uuid) returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare c clientes%rowtype;
begin
  select * into c from clientes where id = p_cliente and eliminado_at is null;
  if not found then return null; end if;
  if not (public.es_admin() or (c.comparte_informe_colegio and public.es_miembro_colegio(c.membrete_id))) then
    raise exception 'sin permiso';
  end if;
  return jsonb_build_object(
    'cliente', jsonb_build_object('id', c.id, 'nombre', c.nombre, 'edad', c.edad, 'sexo', c.sexo, 'curso', c.curso, 'institucion', c.institucion,
       'grupo_normativo', c.grupo_normativo, 'membrete_id', c.membrete_id, 'profesional_id', c.profesional_id, 'plan', c.plan,
       'activaciones', (select coalesce(jsonb_agg(to_jsonb(a)), '[]'::jsonb) from activaciones a where a.cliente_id = c.id)),
    'chaside', (select coalesce(jsonb_agg(to_jsonb(x)), '[]'::jsonb) from respuestas_chaside x where x.cliente_id = c.id),
    'holland', (select coalesce(jsonb_agg(to_jsonb(x)), '[]'::jsonb) from respuestas_holland x where x.cliente_id = c.id),
    'af5', (select coalesce(jsonb_agg(to_jsonb(x)), '[]'::jsonb) from respuestas_af5 x where x.cliente_id = c.id),
    'chte', (select coalesce(jsonb_agg(to_jsonb(x)), '[]'::jsonb) from respuestas_chte x where x.cliente_id = c.id),
    'apt_b', (select coalesce(jsonb_agg(to_jsonb(x)), '[]'::jsonb) from respuestas_apt_b x where x.cliente_id = c.id),
    'apt_a', (select coalesce(jsonb_agg(to_jsonb(x)), '[]'::jsonb) from respuestas_apt_a x where x.cliente_id = c.id));
end $$;

create or replace function public.ovp_mi_colegio()
returns table(nombre text, subtitulo text, comparte boolean)
language sql stable security definer set search_path = public as $$
  select m.nombre_marca, m.subtitulo, c.comparte_informe_colegio
    from clientes c join membretes m on m.id = c.membrete_id
   where c.user_id = auth.uid() and c.eliminado_at is null limit 1
$$;

create or replace function public.ovp_compartir_colegio(p boolean) returns boolean
language sql security definer set search_path = public as $$
  update clientes set comparte_informe_colegio = p
   where user_id = auth.uid() and membrete_id is not null and eliminado_at is null
  returning comparte_informe_colegio
$$;

revoke execute on function public.es_miembro_colegio(uuid), public.colegio_mis_colegios(), public.colegio_estudiantes(uuid),
  public.colegio_informe(uuid), public.ovp_mi_colegio(), public.ovp_compartir_colegio(boolean) from public, anon;
grant execute on function public.es_miembro_colegio(uuid), public.colegio_mis_colegios(), public.colegio_estudiantes(uuid),
  public.colegio_informe(uuid), public.ovp_mi_colegio(), public.ovp_compartir_colegio(boolean) to authenticated;

-- Colegios en OVP, segunda parte (16/11/2026). Re-ejecutable.
-- 1) Cada colegio es un membrete con código (enlace ovp.aurzane.com/portal.html?inst=CODIGO) y un enfoque:
--    'general' (informe normal) o 'militar' (añade la sección de carrera militar). Lo elige la administración.
-- 2) Nadie puede ponerse a sí mismo el membrete de un colegio: solo se entra por su enlace.
-- 3) El colegio (o la administración) puede quitar a un estudiante que no es suyo: vuelve al proceso general
--    de AURZANE, su informe deja de llevar el membrete y la sección del colegio, y no puede volver a entrar por ese enlace.

alter table public.membretes add column if not exists enfoque text not null default 'general';
alter table public.membretes drop constraint if exists membretes_enfoque_chk;
alter table public.membretes add constraint membretes_enfoque_chk check (enfoque in ('general', 'militar'));
update public.membretes set enfoque = 'militar'
 where enfoque = 'general' and (lower(coalesce(codigo, '')) like 'comil%' or (coalesce(nombre_marca, '') || ' ' || coalesce(subtitulo, '') || ' ' || coalesce(institucion, '')) ~* 'colegio militar|\mCOMIL\M');

create table if not exists public.colegio_bloqueos (
  membrete_id uuid not null references public.membretes(id) on delete cascade,
  user_id uuid not null,
  motivo text,
  por text default lower(auth.email()),
  creado timestamptz not null default now(),
  primary key (membrete_id, user_id)
);
alter table public.colegio_bloqueos enable row level security;
drop policy if exists cb_admin on public.colegio_bloqueos;
create policy cb_admin on public.colegio_bloqueos for all to authenticated using (public.es_admin()) with check (public.es_admin());
revoke all on public.colegio_bloqueos from anon;
grant select, insert, update, delete on public.colegio_bloqueos to authenticated;

-- Enlace del colegio: solo vincula si el colegio está activo y la persona no fue retirada de él
create or replace function public.ovp_elegir_tests(p_tests text[], p_codigo text default null::text)
returns json language plpgsql security definer set search_path to 'public', 'pg_temp' as $function$
declare v_id uuid; v_validos constant text[] := array['chaside','holland','af5','apt_b','apt_a','chte']; v_tests text[]; v_membrete record; v_activadas int;
begin
  if auth.uid() is null then raise exception 'Necesitas iniciar sesión.'; end if;
  select array_agg(distinct t) into v_tests from unnest(coalesce(p_tests, '{}')) t where t = any (v_validos);
  if v_tests is null or array_length(v_tests, 1) is null then raise exception 'Elige al menos una evaluación.'; end if;
  select id into v_id from clientes where user_id = auth.uid() limit 1;
  if v_id is null then raise exception 'No encontramos tu proceso OVP.'; end if;
  perform set_config('aurzane.ovp_gratis', '1', true);
  update clientes set plan = 'premium', metodo_pago = 'gratis', pago_confirmado = true, plan_solicitado_at = coalesce(plan_solicitado_at, now())
   where id = v_id and (plan is distinct from 'premium' or metodo_pago is distinct from 'gratis' or not coalesce(pago_confirmado, false) or plan_solicitado_at is null);
  insert into activaciones (cliente_id, test_key, activo, activado_at) select v_id, t, true, now() from unnest(v_tests) t
    on conflict (cliente_id, test_key) do update set activo = true, activado_at = coalesce(activaciones.activado_at, now()) where not activaciones.activo;
  update activaciones set activo = false where cliente_id = v_id and activo and not coalesce(completado, false) and not (test_key = any (v_tests));
  if p_codigo is not null and length(trim(p_codigo)) > 0 then
    select id, institucion into v_membrete from membretes where lower(codigo) = lower(trim(p_codigo)) and activo limit 1;
    if found and not exists (select 1 from colegio_bloqueos b where b.membrete_id = v_membrete.id and b.user_id = auth.uid()) then
      update clientes set membrete_id = coalesce(membrete_id, v_membrete.id), institucion = coalesce(nullif(trim(institucion), ''), v_membrete.institucion) where id = v_id;
    end if;
  end if;
  perform set_config('aurzane.ovp_gratis', '', true);
  select count(*) into v_activadas from activaciones where cliente_id = v_id and activo;
  return json_build_object('activas', v_activadas);
end; $function$;

-- Membrete y firma desde el informe: el de un colegio no se puede elegir ni quitar desde aquí
create or replace function public.ovp_elegir_membrete(p_membrete uuid, p_profesional uuid default null::uuid)
returns void language plpgsql security definer set search_path to 'public', 'pg_temp' as $function$
declare v_cliente uuid; v_actual uuid; v_actual_cole boolean; v_nuevo_cole boolean;
begin
  select id, membrete_id into v_cliente, v_actual from clientes where user_id = auth.uid();
  if v_cliente is null then raise exception 'No encontramos tu ficha.'; end if;
  if p_membrete is not null and not exists (select 1 from membretes where id = p_membrete and activo) then raise exception 'Ese membrete no está disponible.'; end if;
  if p_profesional is not null and not exists (select 1 from profesionales where id = p_profesional and activo) then raise exception 'Ese profesional no está disponible.'; end if;
  select coalesce(codigo, '') <> '' into v_actual_cole from membretes where id = v_actual;
  select coalesce(codigo, '') <> '' into v_nuevo_cole from membretes where id = p_membrete;
  if coalesce(v_actual_cole, false) and p_membrete is distinct from v_actual then
    raise exception 'Tu informe lleva el membrete de tu colegio.';
  end if;
  if coalesce(v_nuevo_cole, false) and p_membrete is distinct from v_actual then
    raise exception 'El membrete de un colegio solo se obtiene con el enlace del colegio.';
  end if;
  update clientes set membrete_id = p_membrete, profesional_id = p_profesional where id = v_cliente;
end; $function$;

-- Quitar a un estudiante del colegio (orientación, dirección o administración)
create or replace function public.colegio_quitar_estudiante(p_cliente uuid, p_motivo text default null)
returns boolean language plpgsql security definer set search_path = public as $$
declare c clientes%rowtype;
begin
  select * into c from clientes where id = p_cliente and eliminado_at is null;
  if not found or c.membrete_id is null then return false; end if;
  if not (public.es_admin() or public.es_miembro_colegio(c.membrete_id)) then raise exception 'sin permiso'; end if;
  if c.user_id is not null then
    insert into colegio_bloqueos (membrete_id, user_id, motivo) values (c.membrete_id, c.user_id, left(p_motivo, 300))
      on conflict (membrete_id, user_id) do update set motivo = excluded.motivo, creado = now();
  end if;
  update clientes set membrete_id = null, comparte_informe_colegio = false where id = p_cliente;
  return true;
end $$;

-- Volver a admitir a alguien retirado por error (solo administración)
create or replace function public.colegio_readmitir(p_membrete uuid, p_user uuid)
returns boolean language plpgsql security definer set search_path = public as $$
begin
  if not public.es_admin() then raise exception 'sin permiso'; end if;
  delete from colegio_bloqueos where membrete_id = p_membrete and user_id = p_user;
  return true;
end $$;

-- Lista de colegios con su enfoque (para el panel)
drop function if exists public.colegio_mis_colegios();
create or replace function public.colegio_mis_colegios()
returns table(id uuid, nombre text, subtitulo text, institucion text, codigo text, escudo_url text, color_acento text, rol text, enfoque text, activo boolean)
language sql stable security definer set search_path = public as $$
  select m.id, m.nombre_marca, m.subtitulo, m.institucion, m.codigo, m.escudo_url, m.color_acento, cm.rol, m.enfoque, m.activo
    from colegio_miembros cm join membretes m on m.id = cm.membrete_id
   where cm.email = lower(auth.email()) and m.activo
  union
  select m.id, m.nombre_marca, m.subtitulo, m.institucion, m.codigo, m.escudo_url, m.color_acento, 'admin', m.enfoque, m.activo
    from membretes m where public.es_admin() and coalesce(m.codigo, '') <> ''
$$;

-- Alta y cambios de colegios (solo administración)
create or replace function public.colegio_guardar(p_id uuid, p_nombre text, p_subtitulo text, p_institucion text, p_codigo text,
  p_enfoque text, p_color text default '#C9A24B', p_escudo text default null, p_activo boolean default true)
returns uuid language plpgsql security definer set search_path = public as $$
declare v uuid; c text := lower(trim(p_codigo));
begin
  if not public.es_admin() then raise exception 'sin permiso'; end if;
  if c !~ '^[a-z0-9-]{2,40}$' then raise exception 'El código solo puede tener letras minúsculas, números y guiones (2 a 40).'; end if;
  if p_enfoque not in ('general', 'militar') then raise exception 'Enfoque no válido.'; end if;
  if exists (select 1 from membretes where lower(codigo) = c and id is distinct from p_id) then raise exception 'Ya hay un colegio con ese código.'; end if;
  if p_id is null then
    insert into membretes (nombre_marca, subtitulo, institucion, codigo, enfoque, color_acento, escudo_url, activo)
    values (trim(p_nombre), nullif(trim(p_subtitulo), ''), nullif(trim(p_institucion), ''), c, p_enfoque, coalesce(nullif(p_color, ''), '#C9A24B'), nullif(trim(p_escudo), ''), coalesce(p_activo, true))
    returning id into v;
  else
    update membretes set nombre_marca = trim(p_nombre), subtitulo = nullif(trim(p_subtitulo), ''), institucion = nullif(trim(p_institucion), ''), codigo = c,
      enfoque = p_enfoque, color_acento = coalesce(nullif(p_color, ''), color_acento), escudo_url = nullif(trim(p_escudo), ''), activo = coalesce(p_activo, activo)
     where id = p_id returning id into v;
  end if;
  return v;
end $$;

revoke execute on function public.colegio_quitar_estudiante(uuid, text), public.colegio_readmitir(uuid, uuid), public.colegio_mis_colegios(),
  public.colegio_guardar(uuid, text, text, text, text, text, text, text, boolean) from public, anon;
grant execute on function public.colegio_quitar_estudiante(uuid, text), public.colegio_readmitir(uuid, uuid), public.colegio_mis_colegios(),
  public.colegio_guardar(uuid, text, text, text, text, text, text, text, boolean) to authenticated;

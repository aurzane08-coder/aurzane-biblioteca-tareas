-- Modo aula de AURZANE LEARN (16/11/2026). Re-ejecutable.
-- Un docente crea un aula para un curso y comparte su código. Cada estudiante entra con su cuenta AURZANE ID y el código;
-- al unirse acepta que su docente vea su avance en ese curso (lecciones, mejor nota y certificado), y nada más.
create table if not exists public.learn_aulas (
  id uuid primary key default gen_random_uuid(),
  codigo text unique not null,
  nombre text not null,
  course_slug text not null,
  docente_id uuid not null,
  docente_email text,
  activa boolean not null default true,
  creado timestamptz not null default now()
);
create table if not exists public.learn_aula_miembros (
  aula_id uuid not null references public.learn_aulas(id) on delete cascade,
  user_id uuid not null,
  nombre text,
  unido timestamptz not null default now(),
  primary key (aula_id, user_id)
);
alter table public.learn_aulas enable row level security;
alter table public.learn_aula_miembros enable row level security;
revoke all on public.learn_aulas, public.learn_aula_miembros from anon, authenticated;

-- crear un aula (cualquier cuenta: el docente)
create or replace function public.aula_crear(p_nombre text, p_curso text)
returns text language plpgsql security definer set search_path = public as $$
declare c text; i int := 0;
begin
  if auth.uid() is null then raise exception 'Necesitas iniciar sesión.'; end if;
  if length(trim(coalesce(p_nombre, ''))) < 2 then raise exception 'Escribe un nombre para el aula.'; end if;
  if not exists (select 1 from course_courses where slug = p_curso and estado = 'publicado') then raise exception 'Ese curso no está disponible.'; end if;
  if (select count(*) from learn_aulas where docente_id = auth.uid() and activa) >= 50 then raise exception 'Has llegado al máximo de 50 aulas activas.'; end if;
  loop
    c := upper(substr(translate(md5(random()::text || clock_timestamp()::text), '01', 'kp'), 1, 6));
    exit when length(c) = 6 and not exists (select 1 from learn_aulas where codigo = c);
    i := i + 1; if i > 20 then raise exception 'Inténtalo de nuevo.'; end if;
  end loop;
  insert into learn_aulas (codigo, nombre, course_slug, docente_id, docente_email) values (c, left(trim(p_nombre), 80), p_curso, auth.uid(), lower(auth.email()));
  return c;
end $$;

-- unirse con el código (el estudiante)
create or replace function public.aula_unirse(p_codigo text, p_nombre text)
returns json language plpgsql security definer set search_path = public as $$
declare a learn_aulas%rowtype;
begin
  if auth.uid() is null then raise exception 'Necesitas iniciar sesión.'; end if;
  select * into a from learn_aulas where codigo = upper(trim(p_codigo)) and activa;
  if not found then raise exception 'No hay ningún aula activa con ese código.'; end if;
  if length(trim(coalesce(p_nombre, ''))) < 2 then raise exception 'Escribe tu nombre para que tu docente te reconozca.'; end if;
  insert into learn_aula_miembros (aula_id, user_id, nombre) values (a.id, auth.uid(), left(trim(p_nombre), 80))
    on conflict (aula_id, user_id) do update set nombre = excluded.nombre;
  return json_build_object('aula', a.nombre, 'curso', a.course_slug);
end $$;

-- aulas del docente, con número de estudiantes
create or replace function public.aula_mis_aulas()
returns table(id uuid, codigo text, nombre text, course_slug text, curso_titulo text, activa boolean, creado timestamptz, estudiantes int)
language sql stable security definer set search_path = public as $$
  select a.id, a.codigo, a.nombre, a.course_slug, c.titulo, a.activa, a.creado, (select count(*) from learn_aula_miembros m where m.aula_id = a.id)::int
    from learn_aulas a left join course_courses c on c.slug = a.course_slug
   where a.docente_id = auth.uid()
   order by a.creado desc
$$;

-- aulas a las que pertenece el estudiante
create or replace function public.aula_mis_clases()
returns table(nombre text, course_slug text, curso_titulo text, docente_email text, unido timestamptz)
language sql stable security definer set search_path = public as $$
  select a.nombre, a.course_slug, c.titulo, a.docente_email, m.unido
    from learn_aula_miembros m join learn_aulas a on a.id = m.aula_id left join course_courses c on c.slug = a.course_slug
   where m.user_id = auth.uid() and a.activa
   order by m.unido desc
$$;

-- avance de cada estudiante en el curso del aula (solo el docente o la administración)
create or replace function public.aula_avance(p_aula uuid)
returns table(user_id uuid, nombre text, unido timestamptz, lecciones int, total int, mejor_nota numeric, ultima timestamptz, certificado boolean)
language plpgsql stable security definer set search_path = public as $$
declare a learn_aulas%rowtype; cid uuid; tot int;
begin
  select * into a from learn_aulas where id = p_aula;
  if not found or not (a.docente_id = auth.uid() or public.es_admin()) then raise exception 'sin permiso'; end if;
  select id into cid from course_courses where slug = a.course_slug;
  select count(*) into tot from course_lessons l join course_modules mo on mo.id = l.module_id where mo.course_id = cid and l.estado = 'publicado' and mo.estado = 'publicado';
  return query
  select m.user_id, m.nombre, m.unido,
         (select count(*) from course_progress p join course_lessons l on l.id = p.lesson_id join course_modules mo on mo.id = l.module_id
           where p.user_id = m.user_id and mo.course_id = cid and p.completado_at is not null)::int,
         tot,
         (select max(t.nota) from course_attempts t where t.user_id = m.user_id and t.course_id = cid and t.finished_at is not null),
         greatest((select max(coalesce(p.completado_at, p.visitado_at)) from course_progress p join course_lessons l on l.id = p.lesson_id join course_modules mo on mo.id = l.module_id where p.user_id = m.user_id and mo.course_id = cid),
                  (select max(t.started_at) from course_attempts t where t.user_id = m.user_id and t.course_id = cid)),
         exists (select 1 from course_certificates ce where ce.user_id = m.user_id and ce.course_id = cid and not coalesce(ce.revocado, false))
    from learn_aula_miembros m where m.aula_id = p_aula
   order by m.nombre;
end $$;

-- el docente puede cerrar un aula o quitar a alguien; el estudiante puede salir
create or replace function public.aula_cerrar(p_aula uuid, p_activa boolean)
returns boolean language sql security definer set search_path = public as $$
  update learn_aulas set activa = p_activa where id = p_aula and (docente_id = auth.uid() or public.es_admin()) returning activa
$$;
create or replace function public.aula_quitar(p_aula uuid, p_user uuid)
returns boolean language plpgsql security definer set search_path = public as $$
begin
  if not exists (select 1 from learn_aulas where id = p_aula and (docente_id = auth.uid() or public.es_admin())) and p_user is distinct from auth.uid() then raise exception 'sin permiso'; end if;
  delete from learn_aula_miembros where aula_id = p_aula and user_id = p_user;
  return true;
end $$;

revoke execute on function public.aula_crear(text, text), public.aula_unirse(text, text), public.aula_mis_aulas(), public.aula_mis_clases(),
  public.aula_avance(uuid), public.aula_cerrar(uuid, boolean), public.aula_quitar(uuid, uuid) from public, anon;
grant execute on function public.aula_crear(text, text), public.aula_unirse(text, text), public.aula_mis_aulas(), public.aula_mis_clases(),
  public.aula_avance(uuid), public.aula_cerrar(uuid, boolean), public.aula_quitar(uuid, uuid) to authenticated;

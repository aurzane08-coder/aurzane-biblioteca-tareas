-- Mi aula de AURZANE LEARN (16/11/2026). Re-ejecutable. Panel personal: cada persona ve solo lo suyo.
create or replace function public.mi_aprendizaje()
returns table(slug text, titulo text, horas numeric, certificable boolean, total int, completadas int, minutos int,
              mejor_nota numeric, nota_minima numeric, certificado text, ultima timestamptz)
language sql stable security definer set search_path = public as $$
  with yo as (select auth.uid() as uid),
  lec as (
    select c.id cid, l.id lid, coalesce(l.minutos, 0) minutos
      from course_courses c join course_modules m on m.course_id = c.id join course_lessons l on l.module_id = m.id
     where c.estado = 'publicado' and m.estado = 'publicado' and l.estado = 'publicado')
  select c.slug, c.titulo, c.horas_estimadas, coalesce(c.certificable, false),
         (select count(*) from lec where lec.cid = c.id)::int,
         (select count(*) from lec join course_progress p on p.lesson_id = lec.lid, yo where lec.cid = c.id and p.user_id = yo.uid and p.completado_at is not null)::int,
         (select coalesce(sum(lec.minutos), 0) from lec join course_progress p on p.lesson_id = lec.lid, yo where lec.cid = c.id and p.user_id = yo.uid and p.completado_at is not null)::int,
         (select max(t.nota) from course_attempts t, yo where t.user_id = yo.uid and t.course_id = c.id and t.finished_at is not null),
         c.nota_minima,
         (select ce.codigo from course_certificates ce, yo where ce.user_id = yo.uid and ce.course_id = c.id and not coalesce(ce.revocado, false) order by ce.emitido_at desc limit 1),
         greatest((select max(coalesce(p.completado_at, p.visitado_at)) from lec join course_progress p on p.lesson_id = lec.lid, yo where lec.cid = c.id and p.user_id = yo.uid),
                  (select max(t.started_at) from course_attempts t, yo where t.user_id = yo.uid and t.course_id = c.id))
    from course_courses c
   where c.estado = 'publicado' and auth.uid() is not null
   order by 11 desc nulls last, c.titulo
$$;
revoke execute on function public.mi_aprendizaje() from public, anon;
grant execute on function public.mi_aprendizaje() to authenticated;

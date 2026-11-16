-- Colegios en OVP, tercera parte (16/11/2026). Re-ejecutable.
-- Estadísticas de intereses del colegio: respuestas de CHASIDE y Holland de sus estudiantes, sin nombres,
-- para que el panel muestre cuántos estudiantes tienen cada área como principal. Solo lo ven el equipo del colegio
-- y la administración (los colegios cuentan con el consentimiento informado de las familias).
create or replace function public.colegio_intereses(p_membrete uuid)
returns table(curso text, chaside jsonb, holland jsonb)
language sql stable security definer set search_path = public as $$
  select c.curso,
         (select coalesce(jsonb_agg(jsonb_build_object('n', x.pregunta_num, 'r', x.respuesta)), '[]'::jsonb) from respuestas_chaside x where x.cliente_id = c.id),
         (select coalesce(jsonb_agg(jsonb_build_object('item_num', y.item_num, 'valor', y.valor)), '[]'::jsonb) from respuestas_holland y where y.cliente_id = c.id)
    from clientes c
   where c.membrete_id = p_membrete and c.eliminado_at is null
     and (public.es_miembro_colegio(p_membrete) or public.es_admin())
     and exists (select 1 from activaciones a where a.cliente_id = c.id and a.completado and a.test_key in ('chaside', 'holland'))
$$;
revoke execute on function public.colegio_intereses(uuid) from public, anon;
grant execute on function public.colegio_intereses(uuid) to authenticated;

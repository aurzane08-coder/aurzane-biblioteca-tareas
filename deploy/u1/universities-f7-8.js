import { getAurzaneConfig } from '../config/defaults.js?v=f7.4-fix2';
import { createSupabaseDataAdapter } from '../data/supabase.js?v=f7.5-cache2';
import { createService } from './service-contract.js';
import { fail, ok } from './result.js';

const CONFIG = getAurzaneConfig();
const DEFAULT_PAGE_SIZE = CONFIG.services.universities.defaultPageSize;
const MAX_PAGE_SIZE = CONFIG.services.universities.maxPageSize;
const RESOURCES = Object.freeze({
  [CONFIG.services.universities.resource]: { table: CONFIG.services.universities.table },
  carreras: { table: 'carreras' },
});
const SEARCH_RPC = CONFIG.services.universities.searchRpc;
const FACETS_RPC = CONFIG.services.universities.facetsRpc;

function resolveDataAccess(source) {
  if (
    source &&
    typeof source.rpc === 'function' &&
    typeof source.get === 'function'
  ) return source;

  if (source && typeof source.from === 'function' && typeof source.rpc === 'function') {
    return createSupabaseDataAdapter(source, { resources: RESOURCES });
  }

  throw new Error('createUniversitiesService requires a Data Access adapter or Supabase client');
}

function normalizeSearchFilters(filters) {
  const pageSize = Math.min(
    Math.max(Math.trunc(Number(filters.pageSize) || DEFAULT_PAGE_SIZE), 1),
    MAX_PAGE_SIZE
  );
  const page = Math.max(Math.trunc(Number(filters.page) || 1), 1);

  return {
    p_q: filters.search ?? null,
    p_pais: filters.country ?? null,
    p_tipo_ies: filters.iesType ?? null,
    p_fin: filters.funding ?? null,
    p_nivel: filters.level ?? null,
    p_modalidad: filters.modality ?? null,
    p_campo_amplio: filters.field ?? null,
    p_provincia: filters.province ?? null,
    p_canton: filters.city ?? null,
    p_solo_verificadas: filters.verified === true,
    p_solo_logo: filters.withLogo === true,
    p_orden: filters.order ?? null,
    p_pagina: page,
    p_page_size: pageSize,
  };
}

export function createUniversitiesService(source) {
  const dataAccess = resolveDataAccess(source);

  const search = async (filters = {}) => {
    try {
      const result = await dataAccess.rpc({
        name: SEARCH_RPC,
        args: normalizeSearchFilters(filters),
      });
      return result.ok ? ok(result.data ?? { total: 0, rows: [] }) : result;
    } catch (error) {
      return fail(error);
    }
  };

  const facets = async () => {
    try {
      const result = await dataAccess.rpc({ name: FACETS_RPC, args: {} });
      return result.ok ? ok(result.data ?? {}) : result;
    } catch (error) {
      return fail(error);
    }
  };

  const ADMIN_COLUMNS = 'id,nombre,pais,tipo,tipo_ies,sitio_web,logo_url,ciudad,region,acronimo,anio_creacion,en_linea,descripcion,visible,destacada,fuente';
  const listAdmin = async ({ search = '', country = '', funding = '', status = '', limit = DEFAULT_PAGE_SIZE, offset = 0 } = {}) => {
    try {
      const normalizedLimit = Math.min(Math.max(Math.trunc(Number(limit) || DEFAULT_PAGE_SIZE), 1), MAX_PAGE_SIZE);
      const normalizedOffset = Math.max(Math.trunc(Number(offset) || 0), 0);
      const term = String(search || '').trim().replace(/[%,()]/g, ' ');
      const filters = {};
      if (term) filters.or = ['nombre', 'ciudad', 'acronimo'].map(column => ({ column, operator: 'ilike', value: '%' + term + '%' }));
      if (country) filters.pais = country;
      if (funding === 'pública') filters.tipo = 'pública';
      else if (funding === 'privada') filters.tipo = { neq: 'pública' };
      if (status === 'visible') filters.visible = true;
      else if (status === 'oculta') filters.visible = false;
      else if (status === 'destacada') filters.destacada = true;
      else if (status === 'sinweb') filters.sitio_web = { is: null };
      return dataAccess.list({
        resource: CONFIG.services.universities.resource,
        select: ADMIN_COLUMNS,
        filters,
        limit: normalizedLimit,
        offset: normalizedOffset,
        orderBy: 'nombre',
        ascending: true,
      });
    } catch (error) {
      return fail(error);
    }
  };

  const summary = async () => {
    try {
      const result = await dataAccess.rpc({ name: 'universidades_resumen_admin', args: {} });
      return result.ok ? ok(result.data ?? []) : result;
    } catch (error) { return fail(error); }
  };

  const listCareers = async ({ universityId } = {}) => {
    try {
      if (!universityId) return fail(new Error('universityId is required'));
      return dataAccess.list({ resource: 'carreras', select: '*', filters: { universidad_id: universityId }, limit: 2000, offset: 0, orderBy: 'nombre', ascending: true });
    } catch (error) { return fail(error); }
  };

  const createCareer = async ({ values } = {}) => {
    try {
      if (!values || !values.universidad_id || !values.nombre) return fail(new TypeError('universidad_id and nombre are required'));
      return dataAccess.create({ resource: 'carreras', values });
    } catch (error) { return fail(error); }
  };

  const removeCareer = async ({ id } = {}) => {
    try {
      if (!id) return fail(new Error('id is required'));
      return dataAccess.remove({ resource: 'carreras', id });
    } catch (error) { return fail(error); }
  };

  const create = async ({ values } = {}) => {
    try {
      if (!values || typeof values !== 'object' || Array.isArray(values)) return fail(new TypeError('values is required'));
      return dataAccess.create({ resource: CONFIG.services.universities.resource, values });
    } catch (error) { return fail(error); }
  };

  const update = async ({ id, values } = {}) => {
    try {
      if (!id) return fail(new Error('id is required'));
      if (!values || typeof values !== 'object' || Array.isArray(values)) return fail(new TypeError('values is required'));
      return dataAccess.update({ resource: CONFIG.services.universities.resource, id, values });
    } catch (error) { return fail(error); }
  };

  const remove = async ({ id } = {}) => {
    try {
      if (!id) return fail(new Error('id is required'));
      return dataAccess.remove({ resource: CONFIG.services.universities.resource, id });
    } catch (error) { return fail(error); }
  };

  const careerCounts = async ({ ids = [] } = {}) => {
    try {
      if (!Array.isArray(ids)) return fail(new TypeError('ids must be an array'));
      if (ids.length === 0) return ok({});
      const counts = await Promise.all(ids.map(async id => {
        const result = await dataAccess.count({ resource: 'carreras', filters: { universidad_id: id } });
        return [id, result.ok ? result.data : null];
      }));
      const output = {};
      for (const [id, count] of counts) output[id] = count;
      return ok(output);
    } catch (error) { return fail(error); }
  };

  const get = async ({ id } = {}) => {
    try {
      if (!id) return fail(new Error('id is required'));
      return dataAccess.get({ resource: CONFIG.services.universities.resource, id });
    } catch (error) {
      return fail(error);
    }
  };

  return Object.freeze({ ...createService({ get }), search, facets, listAdmin, create, update, remove, careerCounts, summary, listCareers, createCareer, removeCareer });
}

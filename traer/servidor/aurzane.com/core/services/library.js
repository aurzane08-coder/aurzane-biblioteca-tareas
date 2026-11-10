import { getAurzaneConfig } from '../config/defaults.js?v=f7.4-fix2';
import { createSupabaseDataAdapter } from '../data/supabase.js';
import { createService } from './service-contract.js';
import { fail, ok } from './result.js';

const CONFIG = getAurzaneConfig();
const WORLDS = new Set(CONFIG.worlds);
const RESOURCE = Object.freeze({
  [CONFIG.services.library.resource]: {
    table: CONFIG.services.library.table,
    select: CONFIG.services.library.select,
  },
});

function resolveDataAccess(source) {
  if (
    source &&
    typeof source.list === 'function' &&
    typeof source.get === 'function' &&
    typeof source.textSearch === 'function'
  ) return source;

  if (source && typeof source.from === 'function') {
    return createSupabaseDataAdapter(source, { resources: RESOURCE });
  }

  throw new Error('createLibraryService requires a Data Access adapter or Supabase client');
}

export function createLibraryService(source) {
  const dataAccess = resolveDataAccess(source);

  const list = async ({ world, query, openAccess, limit = CONFIG.services.library.defaultPageSize, offset = 0 } = {}) => {
    try {
      if (world && !WORLDS.has(world)) return fail(new Error(`Unsupported world: ${world}`));

      const size = Math.min(Math.max(Number(limit) || CONFIG.services.library.defaultPageSize, 1), CONFIG.services.library.maxPageSize);
      const from = Math.max(Number(offset) || 0, 0);
      const filters = {};
      if (world) filters.mundo = world;
      if (openAccess === true) filters.es_acceso_abierto = true;

      const common = {
        resource: CONFIG.services.library.resource,
        select: RESOURCE[CONFIG.services.library.resource].select,
        filters,
        limit: size,
        offset: from,
        orderBy: 'anio',
        ascending: false,
      };

      const result = query?.trim()
        ? await dataAccess.textSearch({
            ...common,
            column: CONFIG.services.library.searchColumn,
            query: query.trim(),
            type: CONFIG.services.library.searchType,
          })
        : await dataAccess.list(common);

      return result.ok
        ? ok({
            rows: result.data?.rows ?? [],
            total: result.data?.total ?? 0,
            limit: result.data?.limit ?? size,
            offset: result.data?.offset ?? from,
          })
        : result;
    } catch (error) {
      return fail(error);
    }
  };

  const get = async ({ id } = {}) => {
    try {
      if (!id) return fail(new Error('id is required'));
      return dataAccess.get({ resource: CONFIG.services.library.resource, id });
    } catch (error) {
      return fail(error);
    }
  };

  return createService({ list, get });
}

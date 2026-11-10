import { getAurzaneConfig } from '../config/defaults.js?v=f7.4-fix2';
import { fail, ok } from '../services/result.js';

const CONFIG = getAurzaneConfig();

function assertClient(supabase) {
  if (!supabase || (typeof supabase.from !== 'function' && typeof supabase.rpc !== 'function')) {
    throw new TypeError('createSupabaseDataAdapter requires a Supabase client.');
  }
}

function assertResource(resources, name) {
  if (
    !resources ||
    typeof resources !== 'object' ||
    Array.isArray(resources) ||
    typeof name !== 'string' ||
    !Object.prototype.hasOwnProperty.call(resources, name)
  ) {
    throw new Error('Unknown data resource: ' + name);
  }

  const resource = resources[name];
  if (!resource || typeof resource.table !== 'string' || !resource.table) {
    throw new Error('Unknown data resource: ' + name);
  }

  return resource;
}

function normalizeFilters(filters = {}) {
  if (!filters || typeof filters !== 'object' || Array.isArray(filters)) {
    throw new TypeError('filters must be an object.');
  }
  return Object.entries(filters).filter(([, value]) => value !== undefined && value !== null);
}

function applyFilters(query, filters) {
  let current = query;
  for (const [column, value] of normalizeFilters(filters)) {
    if (column === 'or') {
      if (!Array.isArray(value) || value.length === 0) continue;
      const expressions = value.map(item => {
        if (!item || typeof item.column !== 'string' || typeof item.operator !== 'string') throw new TypeError('Invalid OR filter.');
        const safeValue = String(item.value ?? '').replace(/,/g, '%2C');
        return item.column + '.' + item.operator + '.' + safeValue;
      });
      current = current.or(expressions.join(','));
      continue;
    }
    if (typeof column !== 'string' || !column) {
      throw new TypeError('Filter column must be a non-empty string.');
    }
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      if (Array.isArray(value.in)) current = current.in(column, value.in);
      else if (typeof value.ilike === 'string') current = current.ilike(column, value.ilike);
      else if (Object.prototype.hasOwnProperty.call(value, 'is')) current = current.is(column, value.is);
      else if (value.not && typeof value.not.operator === 'string') current = current.not(column, value.not.operator, value.not.value);
      else if (Object.prototype.hasOwnProperty.call(value, 'neq')) current = current.neq(column, value.neq);
      else if (Object.prototype.hasOwnProperty.call(value, 'gt')) current = current.gt(column, value.gt);
      else if (Object.prototype.hasOwnProperty.call(value, 'gte')) current = current.gte(column, value.gte);
      else if (Object.prototype.hasOwnProperty.call(value, 'lt')) current = current.lt(column, value.lt);
      else if (Object.prototype.hasOwnProperty.call(value, 'lte')) current = current.lte(column, value.lte);
      else current = current.eq(column, value);
    } else {
      current = current.eq(column, value);
    }
  }
  return current;
}

function wrapResult(result) {
  return result?.error ? fail(result.error, result.data ?? null) : ok(result?.data ?? null);
}

function normalizePagination(limit, offset) {
  const size = Math.min(Math.max(Math.trunc(Number(limit) || CONFIG.pagination.defaultPageSize), 1), CONFIG.pagination.maxPageSize);
  const from = Math.max(Math.trunc(Number(offset) || 0), 0);
  return { size, from };
}

function normalizeSearchType(type) {
  return type ?? CONFIG.services.library.searchType;
}

export function createSupabaseDataAdapter(supabase, options = {}) {
  assertClient(supabase);

  if (!options || typeof options !== 'object' || Array.isArray(options)) {
    throw new TypeError('options must be an object.');
  }

  const resources = options.resources ?? options;
  if (!resources || typeof resources !== 'object' || Array.isArray(resources)) {
    throw new TypeError('resources must be an object.');
  }

  const resourceRegistry = Object.freeze({ ...resources });

  const list = async ({
    resource: resourceName,
    select,
    filters = {},
    limit = CONFIG.pagination.defaultPageSize,
    offset = 0,
    orderBy,
    ascending = false,
  } = {}) => {
    try {
      const resource = assertResource(resourceRegistry, resourceName);
      const { size, from } = normalizePagination(limit, offset);
      let query = supabase.from(resource.table).select(select ?? resource.select ?? '*', { count: 'exact' });

      query = applyFilters(query, filters);

      if (orderBy) {
        query = query.order(orderBy, { ascending, nullsFirst: false });
      }

      const result = await query.range(from, from + size - 1);
      if (result?.error) return fail(result.error);

      return ok({
        rows: result?.data ?? [],
        total: result?.count ?? 0,
        limit: size,
        offset: from,
      });
    } catch (error) {
      return fail(error);
    }
  };

  const textSearch = async ({
    resource: resourceName,
    select,
    column,
    query: searchQuery,
    type = CONFIG.services.library.searchType,
    filters = {},
    limit = CONFIG.pagination.defaultPageSize,
    offset = 0,
    orderBy,
    ascending = false,
  } = {}) => {
    try {
      const resource = assertResource(resourceRegistry, resourceName);

      if (typeof column !== 'string' || !column) {
        return fail(new TypeError('textSearch column must be a non-empty string.'));
      }
      if (typeof searchQuery !== 'string' || !searchQuery.trim()) {
        return fail(new TypeError('textSearch query must be a non-empty string.'));
      }

      const { size, from } = normalizePagination(limit, offset);
      let request = supabase
        .from(resource.table)
        .select(select ?? resource.select ?? '*', { count: 'exact' });

      request = applyFilters(request, filters);
      request = request.textSearch(column, searchQuery.trim(), { type: normalizeSearchType(type) });

      if (orderBy) {
        request = request.order(orderBy, { ascending, nullsFirst: false });
      }

      const result = await request.range(from, from + size - 1);
      if (result?.error) return fail(result.error);

      return ok({
        rows: result?.data ?? [],
        total: result?.count ?? 0,
        limit: size,
        offset: from,
      });
    } catch (error) {
      return fail(error);
    }
  };

  const get = async (params = {}) => {
    try {
      if (!params || typeof params !== 'object' || Array.isArray(params)) {
        return fail(new TypeError('get params must be an object.'));
      }

      const resourceName = params.resource;
      const id = params.id;

      if (id === undefined || id === null || id === '') {
        return fail(new Error('id is required'));
      }

      const resource = assertResource(resourceRegistry, resourceName);
      const primaryKey = resource.primaryKey ?? 'id';
      const selection = params.select ?? resource.select ?? '*';

      const result = await supabase
        .from(resource.table)
        .select(selection)
        .eq(primaryKey, id)
        .maybeSingle();

      return wrapResult(result);
    } catch (error) {
      return fail(error);
    }
  };

  const create = async (params = {}) => {
    try {
      if (!params || typeof params !== 'object' || Array.isArray(params)) return fail(new TypeError('create params must be an object.'));
      const resource = assertResource(resourceRegistry, params.resource);
      if (!params.values || typeof params.values !== 'object' || Array.isArray(params.values)) return fail(new TypeError('create values must be an object.'));
      let request = supabase.from(resource.table).insert(params.values);
      if (typeof request.select === 'function') request = request.select(params.select ?? resource.select ?? '*');
      if (typeof request.maybeSingle === 'function') request = request.maybeSingle();
      return wrapResult(await request);
    } catch (error) { return fail(error); }
  };

  const update = async (params = {}) => {
    try {
      if (!params || typeof params !== 'object' || Array.isArray(params)) return fail(new TypeError('update params must be an object.'));
      const resource = assertResource(resourceRegistry, params.resource);
      if (params.id === undefined || params.id === null || params.id === '') return fail(new Error('id is required'));
      if (!params.values || typeof params.values !== 'object' || Array.isArray(params.values)) return fail(new TypeError('update values must be an object.'));
      const primaryKey = resource.primaryKey ?? 'id';
      let request = supabase.from(resource.table).update(params.values).eq(primaryKey, params.id);
      if (typeof request.select === 'function') request = request.select(params.select ?? resource.select ?? '*');
      if (typeof request.maybeSingle === 'function') request = request.maybeSingle();
      return wrapResult(await request);
    } catch (error) { return fail(error); }
  };

  const upsert = async (params = {}) => {
    try {
      if (!params || typeof params !== 'object' || Array.isArray(params)) return fail(new TypeError('upsert params must be an object.'));
      const resource = assertResource(resourceRegistry, params.resource);
      if (!params.values || (typeof params.values !== 'object')) return fail(new TypeError('upsert values must be an object or array.'));
      const options = {};
      if (params.onConflict) options.onConflict = Array.isArray(params.onConflict) ? params.onConflict.join(',') : params.onConflict;
      if (params.ignoreDuplicates !== undefined) options.ignoreDuplicates = Boolean(params.ignoreDuplicates);
      let request = supabase.from(resource.table).upsert(params.values, options);
      if (typeof request.select === 'function') request = request.select(params.select ?? resource.select ?? '*');
      return wrapResult(await request);
    } catch (error) { return fail(error); }
  };

  const remove = async (params = {}) => {
    try {
      if (!params || typeof params !== 'object' || Array.isArray(params)) return fail(new TypeError('remove params must be an object.'));
      const resource = assertResource(resourceRegistry, params.resource);
      if (params.id === undefined || params.id === null || params.id === '') return fail(new Error('id is required'));
      const primaryKey = resource.primaryKey ?? 'id';
      let request = supabase.from(resource.table).delete().eq(primaryKey, params.id);
      if (typeof request.select === 'function') request = request.select(params.select ?? resource.select ?? '*');
      if (typeof request.maybeSingle === 'function') request = request.maybeSingle();
      return wrapResult(await request);
    } catch (error) { return fail(error); }
  };

  const count = async (params = {}) => {
    try {
      if (!params || typeof params !== 'object' || Array.isArray(params)) return fail(new TypeError('count params must be an object.'));
      const resource = assertResource(resourceRegistry, params.resource);
      let query = supabase.from(resource.table).select('id', { count: 'exact', head: true });
      query = applyFilters(query, params.filters ?? {});
      const result = await query;
      if (result?.error) return fail(result.error);
      return ok(result?.count ?? 0);
    } catch (error) { return fail(error); }
  };

  const rpc = async (params = {}) => {
    try {
      if (!params || typeof params !== 'object' || Array.isArray(params)) {
        return fail(new TypeError('rpc params must be an object.'));
      }
      if (!params.name || typeof params.name !== 'string') {
        return fail(new Error('rpc name is required'));
      }
      if (typeof supabase.rpc !== 'function') {
        return fail(new Error('Supabase client does not support rpc'));
      }
      const result = await supabase.rpc(params.name, params.args ?? {});
      return wrapResult(result);
    } catch (error) {
      return fail(error);
    }
  };

  return Object.freeze({ list, get, create, update, remove, upsert, count, rpc, textSearch });
}

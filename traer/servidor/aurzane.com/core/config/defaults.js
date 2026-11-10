const WORLD_KEYS = Object.freeze(['mind', 'nexus', 'live', 'learn', 'build']);
const CONFIG_TYPES = new Set(['string', 'number', 'boolean', 'json']);

export const AURZANE_CONFIG = Object.freeze({
  app: Object.freeze({
    name: 'AURZANE',
    version: 'core-v1',
    environment: 'production',
  }),
  endpoints: Object.freeze({
    publicHost: 'aurzane.com',
  }),
  worlds: WORLD_KEYS,
  identity: Object.freeze({
    storageKey: 'aurzane-id-auth',
    cookieDomain: '.aurzane.com',
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  }),
  admin: Object.freeze({
    authorityRpc: 'es_admin',
  }),
  pagination: Object.freeze({
    defaultPageSize: 20,
    maxPageSize: 100,
  }),
  services: Object.freeze({
    content: Object.freeze({
      defaultPageSize: 20,
      maxPageSize: 100,
      preferUnified: true,
      unifiedResource: 'articulos',
      legacyResources: Object.freeze({
        mind: 'mind',
        nexus: 'nexus',
        live: 'live',
        learn: 'learn',
        build: 'build',
      }),
    }),
    configuration: Object.freeze({
      resource: 'configuration',
      auditResource: 'configuration_audit',
    }),
    library: Object.freeze({
      defaultPageSize: 20,
      maxPageSize: 100,
      resource: 'biblioteca',
      table: 'biblioteca_unificada',
      searchColumn: 'search_vector',
      searchType: 'websearch',
      select: 'id,mundo,titulo,abstract,autores,anio,licencia,es_acceso_abierto,url_articulo,doi',
    }),
    universities: Object.freeze({
      defaultPageSize: 24,
      maxPageSize: 100,
      resource: 'universidades',
      table: 'universidades',
      searchRpc: 'buscar_universidades',
      facetsRpc: 'facetas_universidades',
    }),
  }),
  observability: Object.freeze({
    frontendErrorTable: 'frontend_error_log',
  }),
});

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function deepFreeze(value) {
  if (!isPlainObject(value) && !Array.isArray(value)) return value;
  for (const child of Object.values(value)) deepFreeze(child);
  return Object.freeze(value);
}

function clone(value) {
  if (Array.isArray(value)) return value.map(clone);
  if (isPlainObject(value)) return Object.fromEntries(Object.entries(value).map(([key, child]) => [key, clone(child)]));
  return value;
}

function merge(base, overrides) {
  if (!isPlainObject(overrides)) return overrides;
  const result = { ...base };
  for (const [key, value] of Object.entries(overrides)) {
    result[key] = isPlainObject(value) && isPlainObject(base[key])
      ? merge(base[key], value)
      : clone(value);
  }
  return result;
}

function assertPositiveInteger(value, name) {
  if (!Number.isInteger(value) || value < 1) throw new TypeError(`${name} must be a positive integer.`);
}

function validateConfig(config) {
  if (!isPlainObject(config)) throw new TypeError('AURZANE configuration must be an object.');
  if (!isPlainObject(config.app) || typeof config.app.name !== 'string' || !config.app.name.trim()) {
    throw new TypeError('AURZANE configuration app.name is required.');
  }
  if (!isPlainObject(config.endpoints) || typeof config.endpoints.publicHost !== 'string' || !config.endpoints.publicHost.trim()) {
    throw new TypeError('AURZANE configuration endpoints.publicHost is required.');
  }
  if (!Array.isArray(config.worlds) || config.worlds.length === 0 || config.worlds.some(world => typeof world !== 'string' || !world.trim())) {
    throw new TypeError('AURZANE configuration worlds must be a non-empty string array.');
  }
  if (!isPlainObject(config.pagination)) throw new TypeError('AURZANE pagination configuration is required.');
  assertPositiveInteger(config.pagination.defaultPageSize, 'pagination.defaultPageSize');
  assertPositiveInteger(config.pagination.maxPageSize, 'pagination.maxPageSize');
  if (config.pagination.defaultPageSize > config.pagination.maxPageSize) {
    throw new RangeError('pagination.defaultPageSize cannot exceed pagination.maxPageSize.');
  }
  for (const [serviceName, service] of Object.entries(config.services ?? {})) {
    if (!isPlainObject(service)) throw new TypeError(`Configuration service ${serviceName} must be an object.`);
    if ('defaultPageSize' in service) assertPositiveInteger(service.defaultPageSize, `services.${serviceName}.defaultPageSize`);
    if ('maxPageSize' in service) assertPositiveInteger(service.maxPageSize, `services.${serviceName}.maxPageSize`);
    if ('defaultPageSize' in service && 'maxPageSize' in service && service.defaultPageSize > service.maxPageSize) {
      throw new RangeError(`services.${serviceName}.defaultPageSize cannot exceed maxPageSize.`);
    }
  }
  return config;
}

export function getAurzaneConfig(overrides = {}) {
  if (!isPlainObject(overrides)) throw new TypeError('AURZANE configuration overrides must be an object.');
  return deepFreeze(validateConfig(merge(AURZANE_CONFIG, overrides)));
}

export function assertAurzaneConfig(config) {
  return validateConfig(config);
}

export const AURZANE_CONFIG_TYPES = CONFIG_TYPES;

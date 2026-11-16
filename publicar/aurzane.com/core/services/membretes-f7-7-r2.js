import { createService } from './service-contract.js';
import { fail, ok } from './result.js';

// el admin lee y escribe por la vista membretes_admin, la única que muestra el código del colegio (16/11/2026)
export const MEMBRETES_DATA_RESOURCES = Object.freeze({ membretes: { table: 'membretes_admin' } });
const FIELDS = Object.freeze(['id','nombre_marca','subtitulo','color_acento','nota_legal','codigo','institucion','color_banda','color_texto_banda','escudo_url','activo','created_at']);
const DEFAULT_COLOR = '#C9A24B';
const HEX_COLOR = /^#[0-9a-f]{3}(?:[0-9a-f]{1}|[0-9a-f]{3}|[0-9a-f]{5})?$/i;
const PROTECTED_NAME = 'AURZANE';

function resolveDataAccess(source) {
  if (source && typeof source.list === 'function' && typeof source.get === 'function') return source;
  throw new TypeError('createMembretesService requires a Data Access adapter.');
}
function pick(values) {
  return Object.fromEntries(Object.entries(values || {}).filter(([key]) => FIELDS.includes(key) && !['id','created_at'].includes(key)));
}
function normalizeColor(value) {
  const color = String(value ?? DEFAULT_COLOR).trim();
  return HEX_COLOR.test(color) ? color : DEFAULT_COLOR;
}
function normalizeOptionalColor(value) {
  if (value === null || value === undefined || String(value).trim() === '') return null;
  const color = String(value).trim();
  return HEX_COLOR.test(color) ? color : null;
}
function normalizeOptional(values) {
  const out = { ...values };
  if ('color_banda' in out) out.color_banda = normalizeOptionalColor(out.color_banda);
  if ('color_texto_banda' in out) out.color_texto_banda = normalizeOptionalColor(out.color_texto_banda);
  if ('codigo' in out) out.codigo = out.codigo ? String(out.codigo).trim().toLowerCase().replace(/[^a-z0-9-]/g, '') || null : null;
  if ('activo' in out) out.activo = out.activo !== false;
  return out;
}
function normalizeName(value) {
  return String(value ?? '').trim();
}

export function createMembretesService(source) {
  const dataAccess = resolveDataAccess(source);
  const listAdmin = async ({ limit = 100, offset = 0 } = {}) => {
    try {
      const size = Math.min(Math.max(Math.trunc(Number(limit) || 100), 1), 100);
      const from = Math.max(Math.trunc(Number(offset) || 0), 0);
      return dataAccess.list({ resource: 'membretes', select: FIELDS.join(','), limit: size, offset: from, orderBy: 'created_at', ascending: true });
    } catch (error) { return fail(error); }
  };
  const get = async ({ id } = {}) => {
    try {
      if (!id) return fail(new Error('id is required'));
      return dataAccess.get({ resource: 'membretes', id, select: FIELDS.join(',') });
    } catch (error) { return fail(error); }
  };
  const create = async ({ values } = {}) => {
    try {
      if (!values || typeof values !== 'object' || Array.isArray(values)) return fail(new TypeError('values is required'));
      const nombre_marca = normalizeName(values.nombre_marca);
      if (!nombre_marca) return fail(new Error('nombre_marca is required'));
      return dataAccess.create({
        resource: 'membretes',
        values: pick(normalizeOptional({ ...values, nombre_marca, color_acento: normalizeColor(values.color_acento) })),
        select: FIELDS.join(','),
      });
    } catch (error) { return fail(error); }
  };
  const update = async ({ id, values } = {}) => {
    try {
      if (!id) return fail(new Error('id is required'));
      if (!values || typeof values !== 'object' || Array.isArray(values)) return fail(new TypeError('values is required'));
      const current = await get({ id });
      if (!current.ok) return current;
      const nombre_marca = 'nombre_marca' in values ? normalizeName(values.nombre_marca) : undefined;
      if ('nombre_marca' in values && !nombre_marca) return fail(new Error('nombre_marca is required'));
      if (current.data?.nombre_marca === PROTECTED_NAME && nombre_marca && nombre_marca !== PROTECTED_NAME) {
        return fail(new Error('The default AURZANE letterhead cannot be renamed.'));
      }
      const normalized = {
        ...values,
        ...(nombre_marca !== undefined ? { nombre_marca } : {}),
        ...(values.color_acento !== undefined ? { color_acento: normalizeColor(values.color_acento) } : {}),
      };
      if (current.data?.nombre_marca === PROTECTED_NAME && values.activo === false) {
        return fail(new Error('El membrete AURZANE es el predeterminado y no se puede ocultar.'));
      }
      return dataAccess.update({ resource: 'membretes', id, values: pick(normalizeOptional(normalized)), select: FIELDS.join(',') });
    } catch (error) { return fail(error); }
  };
  const remove = async ({ id } = {}) => {
    try {
      if (!id) return fail(new Error('id is required'));
      const current = await get({ id });
      if (!current.ok) return current;
      if (current.data?.nombre_marca === PROTECTED_NAME) return fail(new Error('The default AURZANE letterhead cannot be deleted.'));
      return dataAccess.remove({ resource: 'membretes', id, select: FIELDS.join(',') });
    } catch (error) { return fail(error); }
  };
  return Object.freeze({ ...createService({ list: listAdmin, get, create, update, remove }), listAdmin });
}

export const MEMBRETES_SERVICE_CONTRACT = Object.freeze({
  directDatabaseAccess: false,
  directInfrastructureAccess: false,
  resources: Object.freeze(['membretes']),
});

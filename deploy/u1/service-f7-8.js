import { fail, ok } from '../services/result.js';

const CAPABILITY_METHODS = Object.freeze({
  'configuration.read': Object.freeze(['listConfiguration', 'getConfiguration']),
  'configuration.write': Object.freeze(['createConfiguration', 'updateConfiguration']),
  'configuration.audit': Object.freeze(['historyConfiguration', 'restoreConfiguration']),
  'feature_flags.read': Object.freeze(['listFeatureFlags', 'getFeatureFlag']),
  'universities.read': Object.freeze(['listUniversities', 'getUniversity', 'careerCountsUniversities', 'summaryUniversities', 'listUniversityCareers']),
  'universities.write': Object.freeze(['createUniversity', 'updateUniversity', 'removeUniversity', 'createUniversityCareer', 'removeUniversityCareer']),
  'content.read': Object.freeze(['listContent', 'getContent']),
  'content.write': Object.freeze(['createContent', 'updateContent', 'removeContent']),
  'clients.read': Object.freeze(['listClients', 'getClient', 'findClientByEmail', 'listClientTrash']),
  'clients.write': Object.freeze(['createClient', 'updateClient', 'removeClient', 'restoreClient', 'setClientActivation']),
  'membretes.read': Object.freeze(['listMembretes', 'getMembrete']),
  'membretes.write': Object.freeze(['createMembrete', 'updateMembrete', 'removeMembrete']),
});

function requireContext(context) {
  if (!context || typeof context.authorize !== 'function') throw new TypeError('createAdminCapabilityService requires an Admin Context.');
  return context;
}
function requireService(service, name) {
  if (!service || typeof service[name] !== 'function') throw new TypeError('Admin capability service requires ' + name + '.');
  return service;
}

export function createAdminCapabilityService({ context, configuration, featureFlags, universities, content, clients, membretes } = {}) {
  const adminContext = requireContext(context);
  const configurationService = requireService(configuration, 'list');
  const featureFlagsService = requireService(featureFlags, 'list');
  const universitiesService = requireService(universities, 'listAdmin');
  const contentService = requireService(content, 'listAdmin');
  const clientsService = requireService(clients, 'listAdmin');
  const membretesService = requireService(membretes, 'listAdmin');

  const guard = async capability => {
    const result = await adminContext.authorize(capability);
    if (!result.ok) return result;
    return result.data === true ? null : fail(new Error('Admin capability denied: ' + capability + '.'));
  };
  const invoke = async (capability, target, method, args) => {
    try {
      const denied = await guard(capability);
      if (denied) return denied;
      const result = await target[method](args);
      return result?.ok === true || result?.ok === false ? result : ok(result);
    } catch (error) { return fail(error); }
  };

  const listConfiguration = args => invoke('configuration.read', configurationService, 'list', args);
  const getConfiguration = args => invoke('configuration.read', configurationService, 'get', args);
  const createConfiguration = args => invoke('configuration.write', configurationService, 'create', args);
  const updateConfiguration = args => invoke('configuration.write', configurationService, 'update', args);
  const historyConfiguration = args => invoke('configuration.audit', configurationService, 'history', args);
  const restoreConfiguration = args => invoke('configuration.audit', configurationService, 'restore', args);
  const listFeatureFlags = args => invoke('feature_flags.read', featureFlagsService, 'list', args);
  const getFeatureFlag = args => invoke('feature_flags.read', featureFlagsService, 'get', args);
  const listUniversities = args => invoke('universities.read', universitiesService, 'listAdmin', args);
  const getUniversity = args => invoke('universities.read', universitiesService, 'get', args);
  const careerCountsUniversities = args => invoke('universities.read', universitiesService, 'careerCounts', args);
  const createUniversity = args => invoke('universities.write', universitiesService, 'create', args);
  const updateUniversity = args => invoke('universities.write', universitiesService, 'update', args);
  const removeUniversity = args => invoke('universities.write', universitiesService, 'remove', args);
  const summaryUniversities = args => invoke('universities.read', universitiesService, 'summary', args);
  const listUniversityCareers = args => invoke('universities.read', universitiesService, 'listCareers', args);
  const createUniversityCareer = args => invoke('universities.write', universitiesService, 'createCareer', args);
  const removeUniversityCareer = args => invoke('universities.write', universitiesService, 'removeCareer', args);
  const listContent = args => invoke('content.read', contentService, 'listAdmin', args);
  const getContent = args => invoke('content.read', contentService, 'get', args);
  const createContent = args => invoke('content.write', contentService, 'create', args);
  const updateContent = args => invoke('content.write', contentService, 'update', args);
  const removeContent = args => invoke('content.write', contentService, 'remove', args);
  const listClients = args => invoke('clients.read', clientsService, 'listAdmin', args);
  const getClient = args => invoke('clients.read', clientsService, 'get', args);
  const findClientByEmail = args => invoke('clients.read', clientsService, 'findByEmail', args);
  const listClientTrash = args => invoke('clients.read', clientsService, 'listTrash', args);
  const createClient = args => invoke('clients.write', clientsService, 'create', args);
  const updateClient = args => invoke('clients.write', clientsService, 'update', args);
  const removeClient = args => invoke('clients.write', clientsService, 'remove', args);
  const restoreClient = args => invoke('clients.write', clientsService, 'restore', args);
  const setClientActivation = args => invoke('clients.write', clientsService, 'setActivation', args);
  const listMembretes = args => invoke('membretes.read', membretesService, 'listAdmin', args);
  const getMembrete = args => invoke('membretes.read', membretesService, 'get', args);
  const createMembrete = args => invoke('membretes.write', membretesService, 'create', args);
  const updateMembrete = args => invoke('membretes.write', membretesService, 'update', args);
  const removeMembrete = args => invoke('membretes.write', membretesService, 'remove', args);

  return Object.freeze({
    capabilities: CAPABILITY_METHODS,
    listConfiguration,getConfiguration,createConfiguration,updateConfiguration,historyConfiguration,restoreConfiguration,
    listFeatureFlags,getFeatureFlag,listUniversities,getUniversity,careerCountsUniversities,createUniversity,updateUniversity,removeUniversity,
    summaryUniversities,listUniversityCareers,createUniversityCareer,removeUniversityCareer,
    listContent,getContent,createContent,updateContent,removeContent,
    listClients,getClient,findClientByEmail,listClientTrash,createClient,updateClient,removeClient,restoreClient,setClientActivation,
    listMembretes,getMembrete,createMembrete,updateMembrete,removeMembrete,
  });
}

export const ADMIN_CAPABILITY_SERVICE_CONTRACT = Object.freeze({
  operations: Object.freeze(Object.values(CAPABILITY_METHODS).flat()),
  directDatabaseAccess: false,
  directInfrastructureAccess: false,
  sources: Object.freeze(['Admin Context','Configuration Service','Feature Flags Service','Universities Service','Content Service','Clients Service','Membretes Service']),
});

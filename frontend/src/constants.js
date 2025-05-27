export const baseUrl = 'http://aisearch-coe.payoda.net/api';

export const getApiRoute = (endpoint) => {
  
  return `${baseUrl}${endpoint}`
};
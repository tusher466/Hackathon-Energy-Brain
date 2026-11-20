export const formatCurrency = (value: number, regionCode: string, regions: any[]) => {
  const reg = regions?.find((r:any)=>r.code===regionCode) || { currency: 'BDT', currency_symbol: '৳' };
  const sym = reg.currency_symbol || reg.currency || '$';
  return `${sym}${value.toFixed(1)}`;
};

export const formatNumber = (n: number, decimals=1) => n.toFixed(decimals);

export const fmtKWh = (n: number) => `${n.toFixed(0)} kWh`;
export const fmtKW = (n: number) => `${n.toFixed(0)} kW`;
export const fmtCO2 = (kg: number) => {
  if (kg > 1000) return `${(kg/1000).toFixed(2)} t`;
  return `${kg.toFixed(0)} kg`;
};

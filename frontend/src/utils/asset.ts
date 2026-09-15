// Asset file path depends on the Vite base URL - /static/ in a build, / in dev
export const asset = (file: string) => `${import.meta.env.BASE_URL}${file}`;

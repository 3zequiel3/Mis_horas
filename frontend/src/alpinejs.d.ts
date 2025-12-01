declare module 'alpinejs' {
  interface Alpine {
    start(): void;
    data(name: string, callback: () => any): void;
    store(name: string, value: any): void;
  }
  
  const Alpine: Alpine;
  export default Alpine;
}

declare global {
  interface Window {
    Alpine: import('alpinejs').default;
  }
}

export {};

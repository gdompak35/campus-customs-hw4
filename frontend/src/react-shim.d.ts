declare module 'react' {
  export type FormEvent<T = any> = any
  export const useEffect: (effect: () => any, deps?: any[]) => any
  export function useState<T>(initial: T | (() => T)): [T, (value: T | ((previous: T) => T)) => void]
  export const StrictMode: any
  export const createElement: any
}

declare module 'react-dom/client' {
  export const createRoot: any
}

declare module 'react/jsx-runtime' {
  export const jsx: any
  export const jsxs: any
  export const Fragment: any
}

declare module '*.css'

declare namespace JSX {
  interface IntrinsicAttributes {
    key?: any
  }
  interface IntrinsicElements {
    [elementName: string]: any
  }
}

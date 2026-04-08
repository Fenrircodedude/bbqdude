import { useState, useEffect } from 'react';
import { type Product, type InventorySession } from './types';

const PRODUCTS_KEY = 'bbqdude_products';
const SESSIONS_KEY = 'bbqdude_sessions';

function load<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function save<T>(key: string, value: T) {
  localStorage.setItem(key, JSON.stringify(value));
}

const defaultProducts: Product[] = [
  { id: '1', name: 'Grillkol', sku: 'GK-001', category: 'Bränsle', expectedQty: 50, unit: 'kg' },
  { id: '2', name: 'Grillkrydda Original', sku: 'GK-002', category: 'Kryddor', expectedQty: 30, unit: 'st' },
  { id: '3', name: 'BBQ Sås', sku: 'BS-001', category: 'Såser', expectedQty: 24, unit: 'st' },
  { id: '4', name: 'Engångsgrill', sku: 'EG-001', category: 'Grillar', expectedQty: 20, unit: 'st' },
];

export function useProducts() {
  const [products, setProducts] = useState<Product[]>(() =>
    load(PRODUCTS_KEY, defaultProducts)
  );

  useEffect(() => save(PRODUCTS_KEY, products), [products]);

  function addProduct(p: Omit<Product, 'id'>) {
    setProducts(prev => [...prev, { ...p, id: crypto.randomUUID() }]);
  }

  function updateProduct(updated: Product) {
    setProducts(prev => prev.map(p => (p.id === updated.id ? updated : p)));
  }

  function deleteProduct(id: string) {
    setProducts(prev => prev.filter(p => p.id !== id));
  }

  return { products, addProduct, updateProduct, deleteProduct };
}

export function useSessions() {
  const [sessions, setSessions] = useState<InventorySession[]>(() =>
    load(SESSIONS_KEY, [])
  );

  useEffect(() => save(SESSIONS_KEY, sessions), [sessions]);

  function createSession(name: string, products: Product[]): InventorySession {
    const session: InventorySession = {
      id: crypto.randomUUID(),
      name,
      date: new Date().toISOString(),
      counts: Object.fromEntries(
        products.map(p => [p.id, { productId: p.id, actualQty: 0, counted: false, note: '' }])
      ),
      completed: false,
    };
    setSessions(prev => [session, ...prev]);
    return session;
  }

  function updateSession(updated: InventorySession) {
    setSessions(prev => prev.map(s => (s.id === updated.id ? updated : s)));
  }

  function deleteSession(id: string) {
    setSessions(prev => prev.filter(s => s.id !== id));
  }

  return { sessions, createSession, updateSession, deleteSession };
}

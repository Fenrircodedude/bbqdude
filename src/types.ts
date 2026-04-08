export interface Product {
  id: string;
  name: string;
  sku: string;
  category: string;
  expectedQty: number;
  unit: string;
}

export interface InventoryCount {
  productId: string;
  actualQty: number;
  counted: boolean;
  note: string;
}

export interface InventorySession {
  id: string;
  name: string;
  date: string;
  counts: Record<string, InventoryCount>;
  completed: boolean;
}

import { useState } from 'react';
import { type Product } from '../types';

interface Props {
  products: Product[];
  onAdd: (p: Omit<Product, 'id'>) => void;
  onUpdate: (p: Product) => void;
  onDelete: (id: string) => void;
}

const empty: Omit<Product, 'id'> = { name: '', sku: '', category: '', expectedQty: 0, unit: 'st' };

export default function ProductManager({ products, onAdd, onUpdate, onDelete }: Props) {
  const [form, setForm] = useState<Omit<Product, 'id'>>(empty);
  const [editId, setEditId] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [filterCat, setFilterCat] = useState('');

  const categories = [...new Set(products.map(p => p.category))].filter(Boolean);

  const visible = products.filter(p => {
    const matchSearch = p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.sku.toLowerCase().includes(search.toLowerCase());
    const matchCat = !filterCat || p.category === filterCat;
    return matchSearch && matchCat;
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) return;
    if (editId) {
      onUpdate({ ...form, id: editId });
      setEditId(null);
    } else {
      onAdd(form);
    }
    setForm(empty);
  }

  function startEdit(p: Product) {
    setEditId(p.id);
    setForm({ name: p.name, sku: p.sku, category: p.category, expectedQty: p.expectedQty, unit: p.unit });
  }

  function cancelEdit() {
    setEditId(null);
    setForm(empty);
  }

  return (
    <div className="section">
      <h2>Produkter</h2>

      <form className="product-form" onSubmit={handleSubmit}>
        <input
          placeholder="Namn *"
          value={form.name}
          onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
          required
        />
        <input
          placeholder="Art.nr / SKU"
          value={form.sku}
          onChange={e => setForm(f => ({ ...f, sku: e.target.value }))}
        />
        <input
          placeholder="Kategori"
          value={form.category}
          onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
        />
        <input
          type="number"
          placeholder="Förv. antal"
          min="0"
          value={form.expectedQty}
          onChange={e => setForm(f => ({ ...f, expectedQty: Number(e.target.value) }))}
        />
        <input
          placeholder="Enhet (st, kg…)"
          value={form.unit}
          onChange={e => setForm(f => ({ ...f, unit: e.target.value }))}
        />
        <button type="submit" className="btn-primary">
          {editId ? 'Spara' : 'Lägg till'}
        </button>
        {editId && (
          <button type="button" className="btn-secondary" onClick={cancelEdit}>
            Avbryt
          </button>
        )}
      </form>

      <div className="filters">
        <input
          placeholder="Sök produkt..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select value={filterCat} onChange={e => setFilterCat(e.target.value)}>
          <option value="">Alla kategorier</option>
          {categories.map(c => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      <div className="product-count">{visible.length} produkter</div>

      <div className="product-table-wrapper">
        <table className="product-table">
          <thead>
            <tr>
              <th>Namn</th>
              <th>Art.nr</th>
              <th>Kategori</th>
              <th>Förv. antal</th>
              <th>Enhet</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {visible.map(p => (
              <tr key={p.id} className={editId === p.id ? 'row-editing' : ''}>
                <td>{p.name}</td>
                <td className="muted">{p.sku}</td>
                <td>
                  <span className="badge">{p.category || '—'}</span>
                </td>
                <td className="num">{p.expectedQty}</td>
                <td className="muted">{p.unit}</td>
                <td className="actions">
                  <button onClick={() => startEdit(p)} title="Redigera">✏️</button>
                  <button onClick={() => onDelete(p.id)} title="Ta bort" className="btn-danger">✕</button>
                </td>
              </tr>
            ))}
            {visible.length === 0 && (
              <tr>
                <td colSpan={6} className="empty">Inga produkter hittades</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

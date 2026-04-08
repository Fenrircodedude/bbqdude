import { useState } from 'react';
import { type InventorySession as ISession, type Product } from '../types';

interface Props {
  session: ISession;
  products: Product[];
  onUpdate: (s: ISession) => void;
  onClose: () => void;
}

export default function InventorySession({ session, products, onUpdate, onClose }: Props) {
  const [search, setSearch] = useState('');
  const [filterCat, setFilterCat] = useState('');
  const [showUncounted, setShowUncounted] = useState(false);

  const categories = [...new Set(products.map(p => p.category))].filter(Boolean);

  const visible = products.filter(p => {
    const matchSearch = p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.sku.toLowerCase().includes(search.toLowerCase());
    const matchCat = !filterCat || p.category === filterCat;
    const matchUncounted = !showUncounted || !session.counts[p.id]?.counted;
    return matchSearch && matchCat && matchUncounted;
  });

  function setQty(productId: string, qty: number) {
    const updated: ISession = {
      ...session,
      counts: {
        ...session.counts,
        [productId]: { ...session.counts[productId], actualQty: qty, productId },
      },
    };
    onUpdate(updated);
  }

  function toggleCounted(productId: string) {
    const current = session.counts[productId];
    const updated: ISession = {
      ...session,
      counts: {
        ...session.counts,
        [productId]: { ...current, counted: !current?.counted, productId },
      },
    };
    onUpdate(updated);
  }

  function setNote(productId: string, note: string) {
    const updated: ISession = {
      ...session,
      counts: {
        ...session.counts,
        [productId]: { ...session.counts[productId], note, productId },
      },
    };
    onUpdate(updated);
  }

  function completeSession() {
    onUpdate({ ...session, completed: true });
    onClose();
  }

  const totalCounted = products.filter(p => session.counts[p.id]?.counted).length;
  const progress = products.length > 0 ? Math.round((totalCounted / products.length) * 100) : 0;

  const diff = (p: Product) => {
    const c = session.counts[p.id];
    if (!c?.counted) return null;
    return c.actualQty - p.expectedQty;
  };

  return (
    <div className="section">
      <div className="session-header">
        <div>
          <h2>{session.name}</h2>
          <div className="muted">{new Date(session.date).toLocaleString('sv-SE')}</div>
        </div>
        <button className="btn-secondary" onClick={onClose}>← Tillbaka</button>
      </div>

      <div className="progress-bar-wrapper">
        <div className="progress-label">
          {totalCounted} / {products.length} räknade &nbsp;({progress}%)
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
      </div>

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
        <label className="toggle-label">
          <input
            type="checkbox"
            checked={showUncounted}
            onChange={e => setShowUncounted(e.target.checked)}
          />
          Visa ej räknade
        </label>
      </div>

      <div className="count-list">
        {visible.map(p => {
          const count = session.counts[p.id] ?? { actualQty: 0, counted: false, note: '' };
          const d = diff(p);
          return (
            <div key={p.id} className={`count-row ${count.counted ? 'counted' : ''}`}>
              <div className="count-info">
                <div className="count-name">{p.name}</div>
                <div className="count-meta">
                  {p.sku && <span className="muted">{p.sku}</span>}
                  {p.category && <span className="badge">{p.category}</span>}
                  <span className="muted">Förv: {p.expectedQty} {p.unit}</span>
                </div>
              </div>

              <div className="count-controls">
                <div className="qty-control">
                  <button onClick={() => setQty(p.id, Math.max(0, count.actualQty - 1))}>−</button>
                  <input
                    type="number"
                    min="0"
                    value={count.actualQty}
                    onChange={e => setQty(p.id, Number(e.target.value))}
                  />
                  <button onClick={() => setQty(p.id, count.actualQty + 1)}>+</button>
                  <span className="unit">{p.unit}</span>
                </div>

                {count.counted && d !== null && (
                  <span className={`diff ${d > 0 ? 'diff-plus' : d < 0 ? 'diff-minus' : 'diff-zero'}`}>
                    {d > 0 ? `+${d}` : d === 0 ? '✓' : d}
                  </span>
                )}

                <input
                  className="note-input"
                  placeholder="Anteckning..."
                  value={count.note}
                  onChange={e => setNote(p.id, e.target.value)}
                />

                <button
                  className={`btn-count ${count.counted ? 'btn-counted' : ''}`}
                  onClick={() => toggleCounted(p.id)}
                >
                  {count.counted ? '✓ Räknad' : 'Markera räknad'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {!session.completed && progress === 100 && (
        <div className="complete-banner">
          <span>Alla produkter räknade!</span>
          <button className="btn-primary" onClick={completeSession}>
            Slutför inventering
          </button>
        </div>
      )}
    </div>
  );
}

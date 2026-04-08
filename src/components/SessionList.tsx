import { type InventorySession, type Product } from '../types';

interface Props {
  sessions: InventorySession[];
  products: Product[];
  onCreate: (name: string) => void;
  onOpen: (id: string) => void;
  onDelete: (id: string) => void;
}

export default function SessionList({ sessions, products, onCreate, onOpen, onDelete }: Props) {
  function handleCreate() {
    const name = prompt('Namn på inventeringen:', `Inventering ${new Date().toLocaleDateString('sv-SE')}`);
    if (name?.trim()) onCreate(name.trim());
  }

  function summary(s: InventorySession) {
    const counted = Object.values(s.counts).filter(c => c.counted).length;
    const total = products.length;
    const diffs = products.filter(p => {
      const c = s.counts[p.id];
      return c?.counted && c.actualQty !== p.expectedQty;
    }).length;
    return { counted, total, diffs };
  }

  return (
    <div className="section">
      <div className="section-header">
        <h2>Inventeringar</h2>
        <button className="btn-primary" onClick={handleCreate}>+ Ny inventering</button>
      </div>

      {sessions.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <div>Inga inventeringar ännu</div>
          <div className="muted">Starta en ny inventering för att börja räkna</div>
        </div>
      ) : (
        <div className="session-list">
          {sessions.map(s => {
            const { counted, total, diffs } = summary(s);
            const pct = total > 0 ? Math.round((counted / total) * 100) : 0;
            return (
              <div key={s.id} className={`session-card ${s.completed ? 'completed' : ''}`}>
                <div className="session-card-header">
                  <div>
                    <div className="session-card-name">{s.name}</div>
                    <div className="muted">{new Date(s.date).toLocaleString('sv-SE')}</div>
                  </div>
                  <div className="session-card-status">
                    {s.completed ? (
                      <span className="badge badge-green">Klar</span>
                    ) : (
                      <span className="badge badge-yellow">Pågående</span>
                    )}
                  </div>
                </div>

                <div className="session-card-stats">
                  <span>{counted}/{total} räknade</span>
                  {diffs > 0 && <span className="diff-minus">{diffs} avvikelse{diffs !== 1 ? 'r' : ''}</span>}
                </div>

                <div className="progress-bar mini">
                  <div className="progress-fill" style={{ width: `${pct}%` }} />
                </div>

                <div className="session-card-actions">
                  {!s.completed && (
                    <button className="btn-primary" onClick={() => onOpen(s.id)}>
                      Fortsätt
                    </button>
                  )}
                  {s.completed && (
                    <button className="btn-secondary" onClick={() => onOpen(s.id)}>
                      Visa rapport
                    </button>
                  )}
                  <button
                    className="btn-danger-outline"
                    onClick={() => {
                      if (confirm('Ta bort inventeringen?')) onDelete(s.id);
                    }}
                  >
                    Ta bort
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

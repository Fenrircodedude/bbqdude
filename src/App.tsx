import { useState } from 'react';
import { useProducts, useSessions } from './store';
import ProductManager from './components/ProductManager';
import SessionList from './components/SessionList';
import InventorySessionView from './components/InventorySession';
import './App.css';

type Tab = 'sessions' | 'products';

export default function App() {
  const { products, addProduct, updateProduct, deleteProduct } = useProducts();
  const { sessions, createSession, updateSession, deleteSession } = useSessions();
  const [tab, setTab] = useState<Tab>('sessions');
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  const activeSession = sessions.find(s => s.id === activeSessionId) ?? null;

  function handleCreateSession(name: string) {
    const session = createSession(name, products);
    setActiveSessionId(session.id);
  }

  if (activeSession) {
    return (
      <div className="app">
        <header className="app-header">
          <div className="logo">🔥 BBQ Dude Inventering</div>
        </header>
        <main className="app-main">
          <InventorySessionView
            session={activeSession}
            products={products}
            onUpdate={updateSession}
            onClose={() => setActiveSessionId(null)}
          />
        </main>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo">🔥 BBQ Dude Inventering</div>
        <nav className="app-nav">
          <button
            className={tab === 'sessions' ? 'nav-btn active' : 'nav-btn'}
            onClick={() => setTab('sessions')}
          >
            📋 Inventeringar
          </button>
          <button
            className={tab === 'products' ? 'nav-btn active' : 'nav-btn'}
            onClick={() => setTab('products')}
          >
            📦 Produkter
          </button>
        </nav>
      </header>
      <main className="app-main">
        {tab === 'sessions' ? (
          <SessionList
            sessions={sessions}
            products={products}
            onCreate={handleCreateSession}
            onOpen={setActiveSessionId}
            onDelete={deleteSession}
          />
        ) : (
          <ProductManager
            products={products}
            onAdd={addProduct}
            onUpdate={updateProduct}
            onDelete={deleteProduct}
          />
        )}
      </main>
    </div>
  );
}

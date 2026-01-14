// src/App.jsx
import { useState, useEffect } from 'react';
import { Toaster } from 'react-hot-toast'; // ← додаємо
import LoginForm from './components/LoginForm';
import TabNavigation from './components/TabNavigation';
import ExpenseForm from './components/ExpenseForm';
import ExpenseList from './components/ExpenseList';
import ExpenseStats from './components/ExpenseStats';
import { ExpenseProvider } from './context/ExpenseContext';

export default function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [activeTab, setActiveTab] = useState('add');

    useEffect(() => {
        const auth = localStorage.getItem('isAuthenticated');
        if (auth === 'true') setIsAuthenticated(true);
    }, []);

    const handleLogin = () => {
        setIsAuthenticated(true);
        // Уведомлення при вході
        import('react-hot-toast').then(({ toast }) => {
            toast.success('Успішний вхід!', { duration: 3000 });
        });
    };

    const handleLogout = () => {
        localStorage.removeItem('isAuthenticated');
        localStorage.removeItem('username');
        setIsAuthenticated(false);
        setActiveTab('add');
        // Уведомлення при виході
        import('react-hot-toast').then(({ toast }) => {
            toast('Ви вийшли з системи', { icon: '👋', duration: 3000 });
        });
    };

    if (!isAuthenticated) {
        return <LoginForm onLogin={handleLogin} />;
    }

    return (
        <ExpenseProvider>
            <div className="min-h-screen bg-gray-50 flex flex-col">
                <header className="bg-indigo-700 text-white shadow">
                    <div className="max-w-5xl mx-auto px-6 py-4 flex justify-between items-center">
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 bg-white rounded-full flex items-center justify-center text-indigo-700 font-bold text-xl">
                                ₴
                            </div>
                            <h1 className="text-2xl font-bold">Трекер витрат</h1>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="px-4 py-1.5 bg-white/20 hover:bg-white/30 rounded text-sm transition"
                        >
                            Вийти
                        </button>
                    </div>
                </header>

                <TabNavigation activeTab={activeTab} setActiveTab={setActiveTab} />

                <main className="flex-1 max-w-5xl mx-auto px-6 py-8 w-full">
                    <div className="bg-white rounded-xl shadow border border-gray-100 p-7 md:p-9 min-h-[400px]">
                        {activeTab === 'add' && (
                            <>
                                <h2 className="text-2xl font-semibold mb-6 text-gray-800">Додати витрату</h2>
                                <ExpenseForm />
                            </>
                        )}

                        {activeTab === 'list' && (
                            <>
                                <h2 className="text-2xl font-semibold mb-6 text-gray-800">Список витрат</h2>
                                <ExpenseList />
                            </>
                        )}

                        {activeTab === 'stats' && (
                            <>
                                <h2 className="text-2xl font-semibold mb-6 text-gray-800">Статистика</h2>
                                <ExpenseStats />
                            </>
                        )}
                    </div>
                </main>

                <footer className="bg-gray-800 text-gray-300 py-4 text-center text-sm mt-auto">
                    Frontend розробка • КПІ • 2025
                </footer>
            </div>

            {/* Тут додаємо контейнер для тостів */}
            <Toaster
                position="top-right"
                toastOptions={{
                    duration: 4000,
                    style: {
                        borderRadius: '10px',
                        background: '#333',
                        color: '#fff',
                    },
                }}
            />
        </ExpenseProvider>
    );
}
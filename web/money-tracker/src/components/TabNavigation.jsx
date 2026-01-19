// src/components/TabNavigation.jsx
export default function TabNavigation({ activeTab, setActiveTab }) {
    const tabs = [
        { id: 'add', label: 'Додати операцію' },
        { id: 'list', label: 'Список' },
        { id: 'stats', label: 'Статистика' },
        { id: 'balance', label: 'Баланс' },
    ];

    return (
        <nav className="bg-white border-b border-gray-200 shadow-sm">
            <div className="max-w-5xl mx-auto px-6">
                <div className="flex space-x-1 py-3 overflow-x-auto">
                    {tabs.map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex-1 py-3 px-4 text-center font-medium rounded-lg transition min-w-[120px] ${
                                activeTab === tab.id
                                    ? 'bg-indigo-100 text-indigo-700 shadow-sm'
                                    : 'text-gray-600 hover:bg-gray-100'
                            }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>
            </div>
        </nav>
    );
}
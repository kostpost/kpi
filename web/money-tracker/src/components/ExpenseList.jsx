// src/components/ExpenseList.jsx
import { useState } from 'react';
import { useExpenses } from '../context/ExpenseContext';
import toast from 'react-hot-toast';

export default function ExpenseList() {
    const { expenses, deleteExpense, categories, deleteCategory } = useExpenses();

    const [sortBy, setSortBy] = useState('date-desc');
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 7;

    // Фільтри
    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('');
    const [minAmount, setMinAmount] = useState('');
    const [maxAmount, setMaxAmount] = useState('');
    const [searchText, setSearchText] = useState('');

    // Сортування
    const sortedExpenses = [...expenses].sort((a, b) => {
        const dateA = new Date(a.date);
        const dateB = new Date(b.date);

        if (isNaN(dateA) || isNaN(dateB)) return 0;

        switch (sortBy) {
            case 'date-desc':
                return dateB - dateA;   // новіші зверху
            case 'date-asc':
                return dateA - dateB;   // старіші зверху
            case 'category':
                return a.category.localeCompare(b.category);
            case 'amount-desc':
                return b.amount - a.amount;
            case 'amount-asc':
                return a.amount - b.amount;
            default:
                return 0;
        }
    });

    // Фільтрація
    const filteredExpenses = sortedExpenses.filter(exp => {
        // Фільтр по даті
        if (dateFrom && new Date(exp.date) < new Date(dateFrom)) return false;
        if (dateTo && new Date(exp.date) > new Date(dateTo)) return false;

        // Фільтр по категорії
        if (selectedCategory && exp.category !== selectedCategory) return false;

        // Фільтр по сумі
        if (minAmount && exp.amount < Number(minAmount)) return false;
        if (maxAmount && exp.amount > Number(maxAmount)) return false;

        // Пошук за описом
        if (searchText) {
            const searchLower = searchText.toLowerCase();
            return exp.description.toLowerCase().includes(searchLower);
        }

        return true;
    });

    // Пагінація після фільтрації
    const totalPages = Math.ceil(filteredExpenses.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const currentExpenses = filteredExpenses.slice(startIndex, endIndex);

    const goToPage = (page) => {
        if (page >= 1 && page <= totalPages) {
            setCurrentPage(page);
        }
    };

    // При зміні фільтрів повертаємось на першу сторінку
    const resetPage = () => setCurrentPage(1);

    const handleDeleteExpense = (id) => {
        deleteExpense(id);
        toast.success('Витрату успішно видалено', { icon: '🗑️', duration: 3000 });
        if (currentExpenses.length === 1 && currentPage > 1) {
            setCurrentPage(currentPage - 1);
        }
    };

    const handleDeleteCategory = (cat) => {
        if (cat === 'Інше') {
            toast.error('Категорію "Інше" видалити не можна — це резервна категорія', { duration: 5000 });
            return;
        }

        deleteCategory(cat);
        toast.success(`Категорію «${cat}» видалено. Витрати переведено в "Інше"`, {
            icon: '✅',
            duration: 4000,
        });
    };

    if (expenses.length === 0) {
        return (
            <div className="py-12 text-center text-gray-500 italic">
                Ще немає жодної витрати. Додайте першу!
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Заголовок + сортування */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <h2 className="text-2xl font-bold text-gray-800">
                    Список витрат ({filteredExpenses.length})
                </h2>

                <select
                    value={sortBy}
                    onChange={e => {
                        setSortBy(e.target.value);
                        resetPage();
                    }}
                    className="px-4 py-2.5 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-indigo-500 outline-none text-sm font-medium shadow-sm"
                >
                    <option value="date-desc">За датою (новіші перші)</option>
                    <option value="date-asc">За датою (старіші перші)</option>
                    <option value="category">За категорією (А-Я)</option>
                    <option value="amount-desc">За сумою (від більшої)</option>
                    <option value="amount-asc">За сумою (від меншої)</option>
                </select>
            </div>

            {/* Фільтри */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 bg-gray-50 p-5 rounded-xl border border-gray-200">
                {/* По даті від */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Від дати</label>
                    <input
                        type="date"
                        value={dateFrom}
                        onChange={e => {
                            setDateFrom(e.target.value);
                            resetPage();
                        }}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                    />
                </div>

                {/* По даті до */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">До дати</label>
                    <input
                        type="date"
                        value={dateTo}
                        onChange={e => {
                            setDateTo(e.target.value);
                            resetPage();
                        }}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                    />
                </div>

                {/* По категорії */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Категорія</label>
                    <select
                        value={selectedCategory}
                        onChange={e => {
                            setSelectedCategory(e.target.value);
                            resetPage();
                        }}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-indigo-500 outline-none"
                    >
                        <option value="">Всі категорії</option>
                        {categories.map(cat => (
                            <option key={cat} value={cat}>{cat}</option>
                        ))}
                    </select>
                </div>

                {/* По сумі */}
                <div className="grid grid-cols-2 gap-2">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Від</label>
                        <input
                            type="number"
                            min="0"
                            value={minAmount}
                            onChange={e => {
                                setMinAmount(e.target.value);
                                resetPage();
                            }}
                            placeholder="0"
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">До</label>
                        <input
                            type="number"
                            min="0"
                            value={maxAmount}
                            onChange={e => {
                                setMaxAmount(e.target.value);
                                resetPage();
                            }}
                            placeholder="∞"
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                        />
                    </div>
                </div>

                {/* Пошук за описом */}
                <div className="md:col-span-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Пошук за описом</label>
                    <input
                        type="text"
                        value={searchText}
                        onChange={e => {
                            setSearchText(e.target.value);
                            resetPage();
                        }}
                        placeholder="Наприклад: кава, обід..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                    />
                </div>
            </div>

            {/* Список поточної сторінки */}
            <div className="space-y-4">
                {currentExpenses.length === 0 ? (
                    <div className="py-12 text-center text-gray-600 italic">
                        За вашими фільтрами нічого не знайдено
                    </div>
                ) : (
                    currentExpenses.map(exp => (
                        <div
                            key={exp.id}
                            className="p-5 bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4"
                        >
                            <div className="flex-1">
                                <div className="flex items-center gap-3 mb-1">
                  <span className="font-semibold text-lg text-gray-900">
                    {exp.category}
                  </span>
                                    <span className="text-xl font-bold text-indigo-700">
                    {exp.amount.toFixed(2)} грн
                  </span>
                                </div>

                                <div className="text-sm text-gray-600">
                                    {new Date(exp.date).toLocaleDateString('uk-UA', {
                                        weekday: 'short',
                                        day: 'numeric',
                                        month: 'long',
                                        year: 'numeric',
                                    })}
                                </div>

                                {exp.description !== '—' && (
                                    <div className="text-sm text-gray-500 mt-1 italic">
                                        «{exp.description}»
                                    </div>
                                )}
                            </div>

                            <button
                                onClick={() => handleDeleteExpense(exp.id)}
                                className="px-6 py-2.5 bg-red-50 hover:bg-red-100 text-red-700 font-medium rounded-lg transition-colors border border-red-200 whitespace-nowrap"
                            >
                                Видалити
                            </button>
                        </div>
                    ))
                )}
            </div>

            {/* Пагінація */}
            {totalPages > 1 && (
                <div className="flex justify-center items-center gap-3 mt-8">
                    <button
                        onClick={() => goToPage(currentPage - 1)}
                        disabled={currentPage === 1}
                        className={`px-4 py-2 rounded-lg transition ${
                            currentPage === 1 ? 'bg-gray-200 text-gray-500 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                        }`}
                    >
                        Попередня
                    </button>

                    {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                        <button
                            key={page}
                            onClick={() => goToPage(page)}
                            className={`w-10 h-10 rounded-lg transition font-medium ${
                                currentPage === page
                                    ? 'bg-indigo-600 text-white shadow-md'
                                    : 'bg-gray-100 hover:bg-indigo-100 text-gray-700'
                            }`}
                        >
                            {page}
                        </button>
                    ))}

                    <button
                        onClick={() => goToPage(currentPage + 1)}
                        disabled={currentPage === totalPages}
                        className={`px-4 py-2 rounded-lg transition ${
                            currentPage === totalPages ? 'bg-gray-200 text-gray-500 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                        }`}
                    >
                        Наступна
                    </button>
                </div>
            )}

            {/* Керування категоріями */}
            <div className="mt-12 pt-8 border-t border-gray-200">
                <h3 className="text-xl font-semibold text-gray-800 mb-5">
                    Керування категоріями
                </h3>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {categories.map(cat => (
                        <div
                            key={cat}
                            className="flex justify-between items-center p-4 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition"
                        >
                            <span className="font-medium text-gray-900">{cat}</span>

                            <button
                                onClick={() => handleDeleteCategory(cat)}
                                disabled={cat === 'Інше'}
                                className={`px-4 py-1.5 rounded text-sm font-medium transition ${
                                    cat === 'Інше'
                                        ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                                        : 'bg-red-50 hover:bg-red-100 text-red-700 border border-red-200'
                                }`}
                            >
                                Видалити
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
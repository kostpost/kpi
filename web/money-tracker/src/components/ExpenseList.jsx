// src/components/ExpenseList.jsx
import { useState } from 'react';
import { useExpenses } from '../context/ExpenseContext';
import toast from 'react-hot-toast';

export default function ExpenseList() {
    const {
        expenses,
        deleteOperation,
        expenseCategories,
        incomeCategories,
        deleteExpenseCategory,
        deleteIncomeCategory,
        balance
    } = useExpenses();

    const [sortBy, setSortBy] = useState('date-desc');
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 7;

    // Фільтри
    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');
    const [typeFilter, setTypeFilter] = useState('all'); // 'all', 'expense', 'income'
    const [selectedCategory, setSelectedCategory] = useState('');
    const [minAmount, setMinAmount] = useState('');
    const [maxAmount, setMaxAmount] = useState('');
    const [searchText, setSearchText] = useState('');

    // Сортування
    const sortedExpenses = [...expenses].sort((a, b) => {
        switch (sortBy) {
            case 'date-desc':
                return b.id - a.id;
            case 'date-asc':
                return a.id - b.id;
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
        if (typeFilter !== 'all' && exp.type !== typeFilter) return false;
        if (dateFrom && new Date(exp.date) < new Date(dateFrom)) return false;
        if (dateTo && new Date(exp.date) > new Date(dateTo)) return false;
        if (selectedCategory && exp.category !== selectedCategory) return false;
        if (minAmount && exp.amount < Number(minAmount)) return false;
        if (maxAmount && exp.amount > Number(maxAmount)) return false;
        if (searchText) {
            const searchLower = searchText.toLowerCase();
            return exp.description.toLowerCase().includes(searchLower);
        }
        return true;
    });

    // Пагінація
    const totalPages = Math.ceil(filteredExpenses.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const currentExpenses = filteredExpenses.slice(startIndex, endIndex);

    const goToPage = (page) => {
        if (page >= 1 && page <= totalPages) setCurrentPage(page);
    };

    const resetPage = () => setCurrentPage(1);

    const handleDeleteOperation = (id) => {
        deleteOperation(id);
        toast.success('Операцію видалено', { icon: '🗑️', duration: 3000 });
        if (currentExpenses.length === 1 && currentPage > 1) {
            setCurrentPage(currentPage - 1);
        }
    };

    // Визначаємо, які категорії показувати в залежності від typeFilter
    const displayedCategories = typeFilter === 'income'
        ? incomeCategories
        : typeFilter === 'expense'
            ? expenseCategories
            : [...expenseCategories, ...incomeCategories].filter((v, i, a) => a.indexOf(v) === i); // унікальні

    const handleDeleteCategory = (cat) => {
        if (cat === 'Інше') {
            toast.error('Категорію "Інше" видалити не можна', { duration: 5000 });
            return;
        }

        if (typeFilter === 'income') {
            deleteIncomeCategory(cat);
        } else if (typeFilter === 'expense') {
            deleteExpenseCategory(cat);
        } else {
            // Якщо "Всі", видаляємо з обох списків, якщо є
            deleteExpenseCategory(cat);
            deleteIncomeCategory(cat);
        }

        toast.success(`Категорію «${cat}» видалено`, { icon: '✅', duration: 3000 });
    };

    if (expenses.length === 0) {
        return (
            <div className="py-12 text-center text-gray-500 italic">
                Ще немає жодних операцій. Додайте першу!
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Поточний баланс */}
            <div className="bg-indigo-50 p-6 rounded-xl border border-indigo-200 text-center">
                <p className="text-lg font-medium text-gray-700">Поточний баланс</p>
                <p className="text-4xl font-bold text-indigo-700 mt-2">
                    {balance.toFixed(2)} грн
                </p>
            </div>

            {/* Заголовок + сортування */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <h2 className="text-2xl font-bold text-gray-800">
                    Операції ({filteredExpenses.length})
                </h2>

                <select
                    value={sortBy}
                    onChange={(e) => { setSortBy(e.target.value); resetPage(); }}
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
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 bg-gray-50 p-5 rounded-xl border border-gray-200">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Тип</label>
                    <select
                        value={typeFilter}
                        onChange={(e) => { setTypeFilter(e.target.value); resetPage(); setSelectedCategory(''); }}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-indigo-500"
                    >
                        <option value="all">Всі</option>
                        <option value="expense">Витрати</option>
                        <option value="income">Доходи</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Від дати</label>
                    <input
                        type="date"
                        value={dateFrom}
                        onChange={(e) => { setDateFrom(e.target.value); resetPage(); }}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">До дати</label>
                    <input
                        type="date"
                        value={dateTo}
                        onChange={(e) => { setDateTo(e.target.value); resetPage(); }}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Категорія</label>
                    <select
                        value={selectedCategory}
                        onChange={(e) => { setSelectedCategory(e.target.value); resetPage(); }}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-indigo-500"
                    >
                        <option value="">Всі</option>
                        {displayedCategories.map(cat => (
                            <option key={cat} value={cat}>{cat}</option>
                        ))}
                    </select>
                </div>

                <div className="grid grid-cols-2 gap-2">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Сума від</label>
                        <input
                            type="number"
                            value={minAmount}
                            onChange={(e) => { setMinAmount(e.target.value); resetPage(); }}
                            placeholder="0"
                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Сума до</label>
                        <input
                            type="number"
                            value={maxAmount}
                            onChange={(e) => { setMaxAmount(e.target.value); resetPage(); }}
                            placeholder="∞"
                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                        />
                    </div>
                </div>

                <div className="md:col-span-5">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Пошук за описом</label>
                    <input
                        type="text"
                        value={searchText}
                        onChange={(e) => { setSearchText(e.target.value); resetPage(); }}
                        placeholder="Наприклад: кава, зарплата..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                </div>
            </div>

            {/* Список операцій */}
            <div className="space-y-4">
                {currentExpenses.length === 0 ? (
                    <div className="py-12 text-center text-gray-600 italic">
                        За вашими фільтрами нічого не знайдено
                    </div>
                ) : (
                    currentExpenses.map(exp => (
                        <div
                            key={exp.id}
                            className={`p-5 border rounded-xl shadow-sm hover:shadow-md transition-all duration-200 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 ${
                                exp.type === 'expense' ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'
                            }`}
                        >
                            <div className="flex-1">
                                <div className="flex items-center gap-3 mb-1">
                                    <span className="font-semibold text-lg text-gray-900">
                                        {exp.category}
                                    </span>
                                    <span className={`text-xl font-bold ${exp.type === 'expense' ? 'text-red-700' : 'text-green-700'}`}>
                                        {exp.type === 'expense' ? '-' : '+'}{exp.amount.toFixed(2)} грн
                                    </span>
                                </div>

                                <div className="text-sm text-gray-600">
                                    {new Date(exp.date).toLocaleDateString('uk-UA')}
                                </div>

                                {exp.description !== '—' && (
                                    <div className="text-sm text-gray-500 mt-1 italic">
                                        «{exp.description}»
                                    </div>
                                )}
                            </div>

                            <button
                                onClick={() => handleDeleteOperation(exp.id)}
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
                                currentPage === page ? 'bg-indigo-600 text-white shadow-md' : 'bg-gray-100 hover:bg-indigo-100 text-gray-700'
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
                    Керування категоріями {typeFilter === 'income' ? '(доходи)' : typeFilter === 'expense' ? '(витрати)' : ''}
                </h3>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {displayedCategories.map(cat => (
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
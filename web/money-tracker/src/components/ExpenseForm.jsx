import { useState, useEffect } from 'react';
import { useExpenses } from '../context/ExpenseContext';
import toast from "react-hot-toast";

export default function ExpenseForm() {
    const {
        addOperation,
        expenseCategories,
        incomeCategories,
        addExpenseCategory,
        addIncomeCategory
    } = useExpenses();

    const [amount, setAmount] = useState('');
    const [category, setCategory] = useState('');
    const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
    const [description, setDescription] = useState('');
    const [error, setError] = useState('');
    const [newCategory, setNewCategory] = useState('');
    const [type, setType] = useState('expense');

    const categories = type === 'expense' ? expenseCategories : incomeCategories;
    const addNewCategory = type === 'expense' ? addExpenseCategory : addIncomeCategory;

    useEffect(() => {
        if (categories.length > 0) {
            if (!category || !categories.includes(category)) {
                setCategory(categories[0]);
            }
        }
    }, [categories, category, type]);

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!amount || Number(amount) <= 0) {
            setError('Сума повинна бути більше 0');
            return;
        }
        if (!category) {
            setError('Оберіть категорію');
            return;
        }

        addOperation({
            amount: Number(amount),
            category,
            date,
            description: description.trim() || '—',
            type,
        });

        setAmount('');
        setDescription('');
        setError('');
        toast.success(`${type === 'expense' ? 'Витрату' : 'Дохід'} додано: ${amount} грн (${category})`);
    };

    const handleAddCategory = (e) => {
        e.preventDefault();
        const trimmed = newCategory.trim();
        if (!trimmed) return;

        addNewCategory(trimmed);
        setCategory(trimmed);
        setNewCategory('');
        toast.success(`Категорію додано: ${trimmed}`);
    };

    return (
        <div className="space-y-8">
            <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                    <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
                        {error}
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Тип операції</label>
                        <div className="flex gap-8">
                            <label className="flex items-center gap-2">
                                <input
                                    type="radio"
                                    value="expense"
                                    checked={type === 'expense'}
                                    onChange={(e) => setType(e.target.value)}
                                    className="form-radio"
                                />
                                Витрата
                            </label>
                            <label className="flex items-center gap-2">
                                <input
                                    type="radio"
                                    value="income"
                                    checked={type === 'income'}
                                    onChange={(e) => setType(e.target.value)}
                                    className="form-radio"
                                />
                                Дохід
                            </label>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Сума (грн)</label>
                        <input
                            type="number"
                            step="0.01"
                            min="0.01"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                            placeholder="1250.00"
                            className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Категорія</label>
                        <select
                            value={category}
                            onChange={(e) => setCategory(e.target.value)}
                            className="w-full px-4 py-3 border rounded-lg bg-white focus:ring-2 focus:ring-indigo-500"
                        >
                            {categories.map(cat => (
                                <option key={cat} value={cat}>{cat}</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Дата</label>
                        <input
                            type="date"
                            value={date}
                            onChange={(e) => setDate(e.target.value)}
                            className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                            required
                        />
                    </div>

                    <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Опис (необов’язково)</label>
                        <input
                            type="text"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="Наприклад: Зарплата за січень"
                            className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                        />
                    </div>
                </div>

                <button
                    type="submit"
                    className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-lg transition"
                >
                    Додати {type === 'expense' ? 'витрату' : 'дохід'}
                </button>
            </form>

            <div className="pt-8 border-t border-gray-200">
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                    Додати нову категорію для {type === 'expense' ? 'витрат' : 'доходів'}
                </h3>
                <form onSubmit={handleAddCategory} className="flex flex-col sm:flex-row gap-3">
                    <input
                        type="text"
                        value={newCategory}
                        onChange={(e) => setNewCategory(e.target.value)}
                        placeholder={type === 'expense' ? "Наприклад: Подорожі, Кафе..." : "Наприклад: Премія, Депозит..."}
                        className="flex-1 px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500"
                    />
                    <button
                        type="submit"
                        className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white font-bold rounded-lg"
                    >
                        Додати
                    </button>
                </form>
            </div>
        </div>
    );
}
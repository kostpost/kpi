// src/components/ExpenseForm.jsx
import { useState, useEffect } from 'react';
import { useExpenses } from '../context/ExpenseContext';
import toast from "react-hot-toast";

export default function ExpenseForm() {
    const { addExpense, categories, addCategory } = useExpenses();

    const [amount, setAmount] = useState('');
    const [category, setCategory] = useState('');
    const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
    const [description, setDescription] = useState('');
    const [error, setError] = useState('');
    const [newCategory, setNewCategory] = useState('');

    // Критичний фікс: завжди тримаємо category в актуальному стані
    useEffect(() => {
        if (categories.length > 0) {
            // Якщо поточна категорія видалена або ще не встановлена — беремо першу
            if (!category || !categories.includes(category)) {
                setCategory(categories[0]);
            }
        }
    }, [categories, category]);

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

        addExpense({
            amount: Number(amount),
            category,
            date,
            description: description.trim() || '—',
        });

        // Скидаємо форму
        setAmount('');
        setDescription('');
        setDate(new Date().toISOString().slice(0, 10));
        setError('');

        toast.success(`Витрату додано: ${amount} грн (${category})`, { duration: 3500 });

    };

    const handleAddCategory = (e) => {
        e.preventDefault();
        const trimmed = newCategory.trim();

        if (trimmed && !categories.includes(trimmed)) {
            addCategory(trimmed);
            setNewCategory('');
            toast.success(`Категорію додано: ${trimmed}`, { icon: '✨' });
        } else if (categories.includes(trimmed)) {
            setCategory(trimmed);   // якщо вже існує — просто вибираємо
            setNewCategory('');
        }


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
                    {/* Сума */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Сума (грн)
                        </label>
                        <input
                            type="number"
                            step="0.01"
                            min="0.01"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                            placeholder="125.50"
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none transition"
                            required
                        />
                    </div>

                    {/* Категорія */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Категорія
                        </label>
                        <select
                            value={category}
                            onChange={(e) => setCategory(e.target.value)}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-indigo-500 outline-none transition"
                        >
                            {categories.map((cat) => (
                                <option key={cat} value={cat}>
                                    {cat}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Дата */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Дата
                        </label>
                        <input
                            type="date"
                            value={date}
                            onChange={(e) => setDate(e.target.value)}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none transition"
                            required
                        />
                    </div>

                    {/* Опис */}
                    <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Опис (необов'язково)
                        </label>
                        <input
                            type="text"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="Наприклад: Кава з друзями"
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none transition"
                        />
                    </div>
                </div>

                <button
                    type="submit"
                    className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-lg transition shadow-lg transform hover:-translate-y-0.5"
                >
                    Додати витрату
                </button>
            </form>

            {/* Додати нову категорію */}
            <div className="pt-8 border-t border-gray-200">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">
                    Додати нову категорію
                </h3>
                <form onSubmit={handleAddCategory} className="flex flex-col sm:flex-row gap-3">
                    <input
                        type="text"
                        value={newCategory}
                        onChange={(e) => setNewCategory(e.target.value)}
                        placeholder="Наприклад: Подорожі, Книги, Спорт..."
                        className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition"
                    />
                    <button
                        type="submit"
                        className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white font-bold rounded-lg transition shadow-md"
                    >
                        Додати категорію
                    </button>
                </form>
            </div>
        </div>
    );
}
// src/components/BalanceControl.jsx
import { useState } from 'react';
import { useExpenses } from '../context/ExpenseContext';
import toast from 'react-hot-toast';

export default function BalanceControl() {
    const { balance, setManualBalance } = useExpenses();
    const [newBalance, setNewBalance] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        const parsed = Number(newBalance);
        if (isNaN(parsed) || newBalance === '') {
            toast.error('Введіть коректну суму');
            return;
        }

        setManualBalance(parsed);
        setNewBalance('');
    };

    return (
        <div className="bg-white p-6 rounded-xl shadow border border-gray-200">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
                Поточний баланс: <span className="text-3xl font-bold text-indigo-700">{balance.toFixed(2)} грн</span>
            </h3>

            <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-4">
                <input
                    type="number"
                    step="0.01"
                    value={newBalance}
                    onChange={(e) => setNewBalance(e.target.value)}
                    placeholder="Введіть новий баланс"
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                />
                <button
                    type="submit"
                    className="px-8 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition"
                >
                    Встановити
                </button>
            </form>

        </div>
    );
}
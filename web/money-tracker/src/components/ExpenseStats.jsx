import { useState, useMemo } from 'react';
import { useExpenses } from '../context/ExpenseContext';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function ExpenseStats() {
    const { expenses, expenseCategories, incomeCategories } = useExpenses();

    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');

    // ──────────────────────────────────────────────
    // Функції для швидкого вибору періоду
    // ──────────────────────────────────────────────
    const setPeriod = (preset) => {
        const today = new Date();
        today.setHours(23, 59, 59, 999); // кінець дня

        let from = null;
        let to = today.toISOString().slice(0, 10);

        if (preset === 'day') {
            from = today.toISOString().slice(0, 10);
        } else if (preset === 'week') {
            const dayOfWeek = today.getDay(); // 0=неділя, 1=понеділок...
            const diff = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
            from = new Date(today);
            from.setDate(today.getDate() - diff);
            from = from.toISOString().slice(0, 10);
        } else if (preset === 'month') {
            from = new Date(today.getFullYear(), today.getMonth(), 1);
            from = from.toISOString().slice(0, 10);
        } else if (preset === 'year') {
            from = new Date(today.getFullYear(), 0, 1);
            from = from.toISOString().slice(0, 10);
        } else if (preset === 'all') {
            from = null;
            to = null;
        }

        setDateFrom(from);
        setDateTo(to);
    };

    // ──────────────────────────────────────────────
    // Фільтрація операцій
    // ──────────────────────────────────────────────
    const filtered = useMemo(() => {
        return expenses.filter(e => {
            const d = new Date(e.date);
            if (dateFrom && d < new Date(dateFrom + 'T00:00:00')) return false;
            if (dateTo && d > new Date(dateTo + 'T23:59:59.999')) return false;
            return true;
        });
    }, [expenses, dateFrom, dateTo]);

    const incomes = filtered.filter(e => e.type === 'income');
    const expensesOnly = filtered.filter(e => e.type === 'expense');

    const totalIncome = incomes.reduce((sum, op) => sum + op.amount, 0);
    const totalExpense = expensesOnly.reduce((sum, op) => sum + op.amount, 0);
    const net = totalIncome - totalExpense;

    // ──────────────────────────────────────────────
    // Дані по категоріях + відсотки
    // ──────────────────────────────────────────────
    const incomeByCat = useMemo(() => {
        const map = {};
        incomeCategories.forEach(cat => {
            const sum = incomes
                .filter(i => i.category === cat)
                .reduce((s, i) => s + i.amount, 0);
            if (sum > 0) map[cat] = { sum, percent: totalIncome > 0 ? (sum / totalIncome * 100) : 0 };
        });
        return map;
    }, [incomes, incomeCategories, totalIncome]);

    const expenseByCat = useMemo(() => {
        const map = {};
        expenseCategories.forEach(cat => {
            const sum = expensesOnly
                .filter(e => e.category === cat)
                .reduce((s, e) => s + e.amount, 0);
            if (sum > 0) map[cat] = { sum, percent: totalExpense > 0 ? (sum / totalExpense * 100) : 0 };
        });
        return map;
    }, [expensesOnly, expenseCategories, totalExpense]);

    // ──────────────────────────────────────────────
    // Діаграми
    // ──────────────────────────────────────────────
    const incomeChartData = {
        labels: Object.keys(incomeByCat),
        datasets: [{
            data: Object.values(incomeByCat).map(v => v.sum),
            backgroundColor: ['#10B981', '#34D399', '#059669', '#065F46', '#047857', '#6EE7B7', '#A7F3D0'],
        }]
    };

    const expenseChartData = {
        labels: Object.keys(expenseByCat),
        datasets: [{
            data: Object.values(expenseByCat).map(v => v.sum),
            backgroundColor: ['#EF4444', '#F97316', '#F59E0B', '#DC2626', '#B91C1C', '#991B1B', '#FCA5A5'],
        }]
    };

    const chartOptions = {
        responsive: true,
        plugins: {
            legend: { position: 'bottom' },
            tooltip: {
                callbacks: {
                    label: function (ctx) {
                        const value = ctx.parsed.toFixed(2);
                        const total = ctx.dataset.label === 'Доходи' ? totalIncome : totalExpense;
                        const percent = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : 0;
                        return `${ctx.label}: ${value} грн (${percent}%)`;
                    }
                }
            }
        }
    };

    // ──────────────────────────────────────────────
    // JSX
    // ──────────────────────────────────────────────
    return (
        <div className="space-y-8">

            {/* Швидкі кнопки періоду */}
            <div className="flex flex-wrap gap-3 justify-center">
                <button
                    onClick={() => setPeriod('day')}
                    className={`px-5 py-2.5 rounded-lg font-medium transition ${
                        dateFrom === new Date().toISOString().slice(0,10) && dateTo === dateFrom
                            ? 'bg-indigo-600 text-white shadow'
                            : 'bg-gray-200 hover:bg-gray-300'
                    }`}
                >
                    День
                </button>
                <button
                    onClick={() => setPeriod('week')}
                    className={`px-5 py-2.5 rounded-lg font-medium transition ${
                        dateFrom && dateTo && dateFrom.includes('-01-') === false && dateTo.includes('-31-') === false
                            ? 'bg-indigo-600 text-white shadow'
                            : 'bg-gray-200 hover:bg-gray-300'
                    }`}
                >
                    Тиждень
                </button>
                <button
                    onClick={() => setPeriod('month')}
                    className={`px-5 py-2.5 rounded-lg font-medium transition ${
                        dateFrom?.endsWith('-01') && dateTo?.match(/-3[01]$|-28|-29|-30/)
                            ? 'bg-indigo-600 text-white shadow'
                            : 'bg-gray-200 hover:bg-gray-300'
                    }`}
                >
                    Місяць
                </button>
                <button
                    onClick={() => setPeriod('year')}
                    className={`px-5 py-2.5 rounded-lg font-medium transition ${
                        dateFrom?.endsWith('-01-01') ? 'bg-indigo-600 text-white shadow' : 'bg-gray-200 hover:bg-gray-300'
                    }`}
                >
                    Рік
                </button>
                <button
                    onClick={() => setPeriod('all')}
                    className={`px-5 py-2.5 rounded-lg font-medium transition ${
                        !dateFrom && !dateTo ? 'bg-indigo-600 text-white shadow' : 'bg-gray-200 hover:bg-gray-300'
                    }`}
                >
                    Увесь час
                </button>
            </div>

            {/* Ручний вибір дат */}
            <div className="flex flex-col sm:flex-row gap-5 justify-center items-center bg-gray-50 p-5 rounded-xl border">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Від</label>
                    <input
                        type="date"
                        value={dateFrom}
                        onChange={e => setDateFrom(e.target.value)}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">До</label>
                    <input
                        type="date"
                        value={dateTo}
                        onChange={e => setDateTo(e.target.value)}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500"
                    />
                </div>
            </div>

            {filtered.length === 0 ? (
                <div className="text-center py-16 text-gray-500 italic">
                    Немає операцій за вибраний період
                </div>
            ) : (
                <>
                    {/* Підсумки */}
                    <div className="grid sm:grid-cols-3 gap-6">
                        <div className="bg-gradient-to-br from-green-500 to-green-700 text-white p-6 rounded-xl text-center shadow-lg">
                            <p className="text-lg font-medium">Дохід</p>
                            <p className="text-4xl font-bold mt-1">{totalIncome.toFixed(2)} грн</p>
                        </div>
                        <div className="bg-gradient-to-br from-red-500 to-red-700 text-white p-6 rounded-xl text-center shadow-lg">
                            <p className="text-lg font-medium">Витрати</p>
                            <p className="text-4xl font-bold mt-1">{totalExpense.toFixed(2)} грн</p>
                        </div>
                        <div className={`p-6 rounded-xl text-center text-white shadow-lg ${net >= 0 ? 'bg-indigo-600' : 'bg-amber-600'}`}>
                            <p className="text-lg font-medium">Результат</p>
                            <p className="text-4xl font-bold mt-1">{net.toFixed(2)} грн</p>
                        </div>
                    </div>

                    <div className="grid lg:grid-cols-2 gap-8">

                        {/* Доходи */}
                        {totalIncome > 0 && (
                            <div className="bg-white p-6 rounded-xl shadow border">
                                <h3 className="text-xl font-semibold text-green-800 mb-5 text-center">
                                    Доходи за категоріями
                                </h3>

                                <div className="max-w-md mx-auto mb-8">
                                    <Pie
                                        data={incomeChartData}
                                        options={{
                                            ...chartOptions,
                                            plugins: { ...chartOptions.plugins, title: { display: true, text: 'Структура доходів', font: { size: 16 } } }
                                        }}
                                    />
                                </div>

                                <div className="overflow-x-auto">
                                    <table className="min-w-full">
                                        <thead className="bg-gray-100">
                                        <tr>
                                            <th className="px-5 py-3 text-left text-sm font-medium text-gray-700">Категорія</th>
                                            <th className="px-5 py-3 text-right text-sm font-medium text-gray-700">Сума</th>
                                            <th className="px-5 py-3 text-right text-sm font-medium text-gray-700">%</th>
                                        </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-200">
                                        {Object.entries(incomeByCat)
                                            .sort((a, b) => b[1].sum - a[1].sum)
                                            .map(([cat, { sum, percent }]) => (
                                                <tr key={cat}>
                                                    <td className="px-5 py-3 text-gray-900">{cat}</td>
                                                    <td className="px-5 py-3 text-right font-medium text-green-700">
                                                        {sum.toFixed(2)} грн
                                                    </td>
                                                    <td className="px-5 py-3 text-right text-gray-600">
                                                        {percent.toFixed(1)}%
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}

                        {/* Витрати */}
                        {totalExpense > 0 && (
                            <div className="bg-white p-6 rounded-xl shadow border">
                                <h3 className="text-xl font-semibold text-red-800 mb-5 text-center">
                                    Витрати за категоріями
                                </h3>

                                <div className="max-w-md mx-auto mb-8">
                                    <Pie
                                        data={expenseChartData}
                                        options={{
                                            ...chartOptions,
                                            plugins: { ...chartOptions.plugins, title: { display: true, text: 'Структура витрат', font: { size: 16 } } }
                                        }}
                                    />
                                </div>

                                <div className="overflow-x-auto">
                                    <table className="min-w-full">
                                        <thead className="bg-gray-100">
                                        <tr>
                                            <th className="px-5 py-3 text-left text-sm font-medium text-gray-700">Категорія</th>
                                            <th className="px-5 py-3 text-right text-sm font-medium text-gray-700">Сума</th>
                                            <th className="px-5 py-3 text-right text-sm font-medium text-gray-700">%</th>
                                        </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-200">
                                        {Object.entries(expenseByCat)
                                            .sort((a, b) => b[1].sum - a[1].sum)
                                            .map(([cat, { sum, percent }]) => (
                                                <tr key={cat}>
                                                    <td className="px-5 py-3 text-gray-900">{cat}</td>
                                                    <td className="px-5 py-3 text-right font-medium text-red-700">
                                                        {sum.toFixed(2)} грн
                                                    </td>
                                                    <td className="px-5 py-3 text-right text-gray-600">
                                                        {percent.toFixed(1)}%
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}
                    </div>
                </>
            )}
        </div>
    );
}
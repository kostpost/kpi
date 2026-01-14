// src/components/ExpenseStats.jsx
import { useExpenses } from '../context/ExpenseContext';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function ExpenseStats() {
    const { expenses, categories } = useExpenses();

    const categorySums = categories.reduce((acc, cat) => {
        acc[cat] = expenses.filter(exp => exp.category === cat).reduce((sum, exp) => sum + exp.amount, 0);
        return acc;
    }, {});

    const data = {
        labels: categories.filter(cat => categorySums[cat] > 0),
        datasets: [{
            data: categories.filter(cat => categorySums[cat] > 0).map(cat => categorySums[cat]),
            backgroundColor: ['#6366F1', '#10B981', '#EF4444', '#F59E0B', '#3B82F6', '#EC4899'],
            hoverBackgroundColor: ['#4F46E5', '#059669', '#DC2626', '#D97706', '#2563EB', '#DB2777'],
        }],
    };

    const options = {
        responsive: true,
        plugins: {
            legend: { position: 'top' },
            tooltip: { callbacks: { label: (context) => `${context.label}: ${context.parsed.toFixed(2)} грн` } },
        },
    };

    const totalSum = expenses.reduce((sum, exp) => sum + exp.amount, 0);

    return (
        <div>
            <h2 className="text-2xl font-semibold mb-6 text-gray-800">Статистика витрат</h2>

            {expenses.length === 0 ? (
                <div className="py-12 text-center text-gray-500 italic">Ще немає даних для статистики</div>
            ) : (
                <div className="space-y-8">
                    <div className="text-center">
                        <p className="text-xl font-medium text-gray-700 mb-2">Загальна сума витрат</p>
                        <p className="text-3xl font-bold text-indigo-600">{totalSum.toFixed(2)} грн</p>
                    </div>

                    <div className="max-w-md mx-auto">
                        <p className="text-xl font-medium text-gray-700 mb-4 text-center">Розподіл за категоріями</p>
                        <Pie data={data} options={options} />
                    </div>
                </div>
            )}
        </div>
    );
}
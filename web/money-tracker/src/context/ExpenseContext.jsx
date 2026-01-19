import { createContext, useContext, useState, useEffect } from 'react';
import toast from "react-hot-toast";

const ExpenseContext = createContext();

export function ExpenseProvider({ children }) {
    const [expenses, setExpenses] = useState(() => {
        const saved = localStorage.getItem('expenses');
        return saved ? JSON.parse(saved) : [];
    });

    const [expenseCategories, setExpenseCategories] = useState(() => {
        const saved = localStorage.getItem('expenseCategories');
        return saved ? JSON.parse(saved) : ['Їжа', 'Транспорт', 'Розваги', 'Комуналка', 'Здоров’я', 'Одяг', 'Інше'];
    });

    const [incomeCategories, setIncomeCategories] = useState(() => {
        const saved = localStorage.getItem('incomeCategories');
        return saved ? JSON.parse(saved) : ['Зарплата', 'Фріланс', 'Подарунки', 'Продаж', 'Інвестиції', 'Повернення боргу', 'Інше'];
    });

    const [balance, setBalance] = useState(() => {
        const saved = localStorage.getItem('balance');
        return saved ? Number(saved) : 0;
    });

    useEffect(() => {
        localStorage.setItem('expenses', JSON.stringify(expenses));
    }, [expenses]);

    useEffect(() => {
        localStorage.setItem('expenseCategories', JSON.stringify(expenseCategories));
    }, [expenseCategories]);

    useEffect(() => {
        localStorage.setItem('incomeCategories', JSON.stringify(incomeCategories));
    }, [incomeCategories]);

    useEffect(() => {
        localStorage.setItem('balance', balance.toString());
    }, [balance]);

    const addOperation = (newOperation) => {
        setExpenses(prev => [...prev, { ...newOperation, id: Date.now() }]);

        if (newOperation.type === 'expense') {
            setBalance(prev => prev - newOperation.amount);
        } else if (newOperation.type === 'income') {
            setBalance(prev => prev + newOperation.amount);
        }
    };

    const deleteOperation = (id) => {
        const op = expenses.find(o => o.id === id);
        if (op) {
            if (op.type === 'expense') {
                setBalance(prev => prev + op.amount);
            } else if (op.type === 'income') {
                setBalance(prev => prev - op.amount);
            }
        }
        setExpenses(prev => prev.filter(o => o.id !== id));
    };

    const addExpenseCategory = (newCat) => {
        const trimmed = newCat.trim();
        if (trimmed && !expenseCategories.includes(trimmed)) {
            setExpenseCategories(prev => [...prev, trimmed]);
        }
    };

    const addIncomeCategory = (newCat) => {
        const trimmed = newCat.trim();
        if (trimmed && !incomeCategories.includes(trimmed)) {
            setIncomeCategories(prev => [...prev, trimmed]);
        }
    };

    const deleteExpenseCategory = (cat) => {
        if (cat === 'Інше') {
            toast.error('Категорію "Інше" не можна видалити');
            return;
        }
        setExpenseCategories(prev => prev.filter(c => c !== cat));
        setExpenses(prev => prev.filter(e => !(e.type === 'expense' && e.category === cat)));
    };

    const deleteIncomeCategory = (cat) => {
        if (cat === 'Інше') {
            toast.error('Категорію "Інше" не можна видалити');
            return;
        }
        setIncomeCategories(prev => prev.filter(c => c !== cat));
        setExpenses(prev => prev.filter(e => !(e.type === 'income' && e.category === cat)));
    };

    const setManualBalance = (newBalance) => {
        const val = Number(newBalance);
        if (!isNaN(val)) {
            setBalance(val);
            toast.success(`Баланс встановлено: ${val.toFixed(2)} грн`);
        } else {
            toast.error('Некоректне значення');
        }
    };

    return (
        <ExpenseContext.Provider value={{
            expenses,
            expenseCategories,
            incomeCategories,
            balance,
            addOperation,
            deleteOperation,
            addExpenseCategory,
            addIncomeCategory,
            deleteExpenseCategory,
            deleteIncomeCategory,
            setManualBalance
        }}>
            {children}
        </ExpenseContext.Provider>
    );
}

export const useExpenses = () => useContext(ExpenseContext);
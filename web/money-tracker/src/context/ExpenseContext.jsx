// src/context/ExpenseContext.jsx
import { createContext, useContext, useState, useEffect } from 'react';

const ExpenseContext = createContext();

export function ExpenseProvider({ children }) {
    const [expenses, setExpenses] = useState(() => {
        const saved = localStorage.getItem('expenses');
        return saved ? JSON.parse(saved) : [];
    });

    const [categories, setCategories] = useState(() => {
        const saved = localStorage.getItem('categories');
        return saved ? JSON.parse(saved) : ['Їжа', 'Транспорт', 'Розваги', 'Комуналка', 'Інше'];
    });

    useEffect(() => {
        localStorage.setItem('expenses', JSON.stringify(expenses));
    }, [expenses]);

    useEffect(() => {
        localStorage.setItem('categories', JSON.stringify(categories));
    }, [categories]);

    const addExpense = (newExpense) => {
        setExpenses(prev => [...prev, { ...newExpense, id: Date.now() }]);
    };

    const deleteExpense = (id) => {
        setExpenses(prev => prev.filter(exp => exp.id !== id));
    };

    const addCategory = (newCategory) => {
        if (newCategory.trim() && !categories.includes(newCategory.trim())) {
            setCategories(prev => [...prev, newCategory.trim()]);
        }
    };

    const deleteCategory = (categoryToDelete) => {
        // Якщо видаляємо "Інше" — забороняємо (бо це резервна)
        if (categoryToDelete === 'Інше') {
            return;
        }

        // Переводимо всі витрати з видаленої категорії в "Інше"
        setExpenses(prev =>
            prev.map(exp =>
                exp.category === categoryToDelete
                    ? { ...exp, category: 'Інше' }
                    : exp
            )
        );

        // Видаляємо категорію зі списку
        setCategories(prev => prev.filter(cat => cat !== categoryToDelete));
    };

    return (
        <ExpenseContext.Provider value={{ expenses, categories, addExpense, deleteExpense, addCategory, deleteCategory }}>
            {children}
        </ExpenseContext.Provider>
    );
}

export const useExpenses = () => useContext(ExpenseContext);
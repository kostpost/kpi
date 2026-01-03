// app/page.tsx
import React from "react";
import Image from "next/image";
// Компонент одного рядка гри — оновлений
// Компонент одного рядка гри — оновлений (онлайн горизонтально)
const GameRow = ({ index }: { index: number }) => (
    <div className="flex items-center gap-4 py-3 px-5 hover:bg-accent/50 transition-colors border-b border-border last:border-b-0">
        {/* Менша горизонтальна аватарка */}
        <div className="relative w-32 h-16 shrink-0 rounded overflow-hidden bg-gray-800">
            <div className="w-full h-full bg-gray-600 border-2 border-dashed border-gray-500 flex items-center justify-center text-xs text-gray-400">
                460×215
            </div>
        </div>
        {/* Назва гри + розробник */}
        <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-base truncate text-foreground">
                Game Title {index}
            </h4>
            <p className="text-sm text-muted-foreground">Valve / EA DICE / etc</p>
        </div>
        {/* Онлайн горизонтально: текущий (зелений) лівіше + пік правіше */}
        <div className="flex items-center gap-6 text-right">
            <div>
                <p className="font-bold text-green-500 text-base">106,888</p>
                <p className="text-xs text-muted-foreground">Players Now</p>
            </div>
            <div>
                <p className="font-medium text-base">133,686</p>
                <p className="text-xs text-muted-foreground">24h Peak</p>
            </div>
        </div>
    </div>
);
// Компонент однієї таблиці
const GameTable = ({ title }: { title: string }) => (
    <div className="bg-card rounded-lg shadow-lg overflow-hidden w-full max-w-4xl">
        <div className="bg-muted px-5 py-3 border-b border-border">
            <h2 className="text-xl font-bold text-foreground">{title} →</h2>
        </div>
        <div>
            {Array.from({ length: 10 }, (_, i) => (
                <GameRow key={i} index={i + 1} />
            ))}
        </div>
    </div>
);
// Головна сторінка
export default function HomePage() {
    return (
        <div className="min-h-screen bg-background">
            <div className="container mx-auto px-4 py-12">
                {/* Перший рядок */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-12 justify-items-center mb-16">
                    <GameTable title="Most Played Games" />
                    <GameTable title="Trending Games" />
                </div>
                {/* Другий рядок */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-12 justify-items-center">
                    <GameTable title="Popular Releases" />
                    <GameTable title="Hot Releases" />
                </div>
            </div>
        </div>
    );
}
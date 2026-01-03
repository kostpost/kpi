// app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Image from "next/image"; // якщо захочеш іконку пошуку

const inter = Inter({ subsets: ["latin", "cyrillic"] });

export const metadata: Metadata = {
    title: "GamingLibrary",
    description: "Ігрова бібліотека",
};

export default function RootLayout({
                                       children,
                                   }: {
    children: React.ReactNode;
}) {
    return (
        <html lang="uk">
        <body className={`${inter.className} min-h-screen flex flex-col`}>
        {/* Navbar — буде на всіх сторінках */}
        <header className="bg-card border-b border-border sticky top-0 z-50">
            <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                {/* Логотип */}
                <div className="flex items-center">
                    <h1 className="text-2xl font-bold text-foreground">GamingLibrary</h1>
                </div>

                {/* Поле пошуку (по центру) */}
                <div className="flex-1 max-w-xl mx-8">
                    <div className="relative">
                        <input
                            type="text"
                            placeholder="Пошук ігор..."
                            className="w-full px-4 py-2 bg-muted border border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent"
                            disabled // візуал, без функціоналу поки
                        />
                        {/* Іконка пошуку (опціонально) */}
                        <div className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                            🔍
                        </div>
                    </div>
                </div>

                {/* Кнопка входу */}
                <div>
                    <button className="px-6 py-2 bg-accent text-foreground font-medium rounded-lg hover:bg-accent/80 transition-colors">
                        Увійти
                    </button>
                </div>
            </div>
        </header>

        {/* Основний контент сторінки */}
        <main className="flex-1 bg-background">
            {children}
        </main>

        {/* Опціональний футер (можна прибрати) */}
        <footer className="bg-card border-t border-border py-4 text-center text-sm text-muted-foreground">
            © 2025 GamingLibrary • Ткаченко Костянтин, КПІ ІП-з31
        </footer>
        </body>
        </html>
    );
}
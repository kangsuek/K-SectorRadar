import { Link } from 'react-router-dom'
import { useTheme } from '../../hooks/useTheme'

export default function Header() {
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="sticky top-0 z-50 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 transition-colors">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="text-xl font-bold text-gray-900 dark:text-white">
            K-SectorRadar
          </Link>
          <nav className="flex items-center gap-6">
            <Link to="/" className="text-gray-700 dark:text-gray-300 hover:text-primary">
              Dashboard
            </Link>
            <Link to="/compare" className="text-gray-700 dark:text-gray-300 hover:text-primary">
              Comparison
            </Link>
            <Link to="/settings" className="text-gray-700 dark:text-gray-300 hover:text-primary">
              Settings
            </Link>
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-700 dark:text-gray-300 hover:text-primary"
            >
              GitHub
            </a>
          </nav>
        </div>
      </div>
    </header>
  )
}


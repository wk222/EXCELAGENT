import { Sun, Moon, Settings } from 'lucide-react'
import { useAppStore } from '../../stores/appStore'
import { Button } from '../ui/Button'
import { Link } from 'react-router-dom'

export function Header() {
  const { theme, setTheme, isProcessing } = useAppStore()

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light')
    // 更新HTML类名以应用主题
    document.documentElement.classList.toggle('dark', theme === 'light')
  }

  return (
    <header className="h-16 border-b border-border bg-card/50 backdrop-blur-sm flex items-center justify-between px-6">
      <div className="flex items-center space-x-4">
        <h1 className="text-xl font-semibold">Excel智能体</h1>
        {isProcessing && (
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
            <span>AI正在处理中<span className="loading-dots"></span></span>
          </div>
        )}
      </div>

      <div className="flex items-center space-x-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleTheme}
          className="h-9 w-9 p-0"
        >
          {theme === 'light' ? (
            <Moon className="h-4 w-4" />
          ) : (
            <Sun className="h-4 w-4" />
          )}
        </Button>
        
        <Link to="/settings">
          <Button variant="ghost" size="sm" className="h-9 w-9 p-0">
            <Settings className="h-4 w-4" />
          </Button>
        </Link>
      </div>
    </header>
  )
}
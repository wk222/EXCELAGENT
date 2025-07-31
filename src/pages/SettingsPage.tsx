import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { useAppStore } from '../stores/appStore'
import { LLMService } from '../utils/llmService'
import { Save, TestTube, RefreshCw, Moon, Sun, Monitor } from 'lucide-react'
import toast from 'react-hot-toast'

export function SettingsPage() {
  const { llmSettings, updateLLMSettings, theme, setTheme } = useAppStore()
  const [localSettings, setLocalSettings] = useState(llmSettings)
  const [isValidating, setIsValidating] = useState(false)
  const [apiValid, setApiValid] = useState<boolean | null>(null)

  useEffect(() => {
    setLocalSettings(llmSettings)
  }, [llmSettings])

  const handleSave = () => {
    updateLLMSettings(localSettings)
    toast.success('设置已保存')
  }

  const handleValidateApi = async () => {
    if (!localSettings.apiKey) {
      toast.error('请先输入API密钥')
      return
    }

    setIsValidating(true)
    const loadingToast = toast.loading('正在验证API设置...')

    try {
      const llmService = new LLMService(localSettings)
      const isValid = await llmService.validateApiKey()
      
      setApiValid(isValid)
      
      if (isValid) {
        toast.success('API设置验证成功！', { id: loadingToast })
      } else {
        toast.error('API设置验证失败，请检查密钥和地址', { id: loadingToast })
      }
    } catch (error) {
      setApiValid(false)
      toast.error(
        error instanceof Error ? error.message : 'API验证失败', 
        { id: loadingToast }
      )
    } finally {
      setIsValidating(false)
    }
  }

  const handleReset = () => {
    const defaultSettings = {
      model: 'gpt-3.5-turbo',
      temperature: 0.7,
      maxTokens: 2000,
      apiKey: '',
      baseUrl: 'https://api.openai.com/v1',
    }
    setLocalSettings(defaultSettings)
    updateLLMSettings(defaultSettings)
    setApiValid(null)
    toast.success('设置已重置为默认值')
  }

  const handleThemeChange = (newTheme: 'light' | 'dark') => {
    setTheme(newTheme)
    document.documentElement.classList.toggle('dark', newTheme === 'dark')
    toast.success(`已切换到${newTheme === 'light' ? '浅色' : '深色'}主题`)
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold">设置</h1>
        <p className="text-muted-foreground mt-2">
          配置AI模型参数和应用偏好设置
        </p>
      </div>

      {/* LLM设置 */}
      <Card>
        <CardHeader>
          <CardTitle>AI模型设置</CardTitle>
          <CardDescription>
            配置大语言模型的API连接和参数
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* API基础设置 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                模型名称
              </label>
              <select
                className="w-full p-3 border border-input rounded-md bg-background"
                value={localSettings.model}
                onChange={(e) => setLocalSettings(prev => ({ ...prev, model: e.target.value }))}
              >
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4-turbo-preview">GPT-4 Turbo</option>
                <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                <option value="claude-3-opus">Claude 3 Opus</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                API基础URL
              </label>
              <input
                type="text"
                className="w-full p-3 border border-input rounded-md bg-background"
                placeholder="https://api.openai.com/v1"
                value={localSettings.baseUrl}
                onChange={(e) => setLocalSettings(prev => ({ ...prev, baseUrl: e.target.value }))}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              API密钥
            </label>
            <div className="flex space-x-2">
              <input
                type="password"
                className="flex-1 p-3 border border-input rounded-md bg-background"
                placeholder="输入您的API密钥"
                value={localSettings.apiKey}
                onChange={(e) => setLocalSettings(prev => ({ ...prev, apiKey: e.target.value }))}
              />
              <Button
                variant="outline"
                onClick={handleValidateApi}
                disabled={isValidating || !localSettings.apiKey}
              >
                {isValidating ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                ) : (
                  <TestTube className="h-4 w-4 mr-2" />
                )}
                验证
              </Button>
            </div>
            {apiValid !== null && (
              <div className={`mt-2 text-sm ${apiValid ? 'text-green-600' : 'text-red-600'}`}>
                {apiValid ? '✅ API设置有效' : '❌ API设置无效'}
              </div>
            )}
          </div>

          {/* 模型参数 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                温度系数: {localSettings.temperature}
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                className="w-full"
                value={localSettings.temperature}
                onChange={(e) => setLocalSettings(prev => ({ ...prev, temperature: Number(e.target.value) }))}
              />
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>确定性</span>
                <span>创造性</span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                最大令牌数
              </label>
              <input
                type="number"
                min="100"
                max="8000"
                step="100"
                className="w-full p-3 border border-input rounded-md bg-background"
                value={localSettings.maxTokens}
                onChange={(e) => setLocalSettings(prev => ({ ...prev, maxTokens: Number(e.target.value) }))}
              />
            </div>
          </div>

          {/* 操作按钮 */}
          <div className="flex items-center space-x-3">
            <Button onClick={handleSave}>
              <Save className="h-4 w-4 mr-2" />
              保存设置
            </Button>
            <Button variant="outline" onClick={handleReset}>
              <RefreshCw className="h-4 w-4 mr-2" />
              重置默认
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 界面设置 */}
      <Card>
        <CardHeader>
          <CardTitle>界面设置</CardTitle>
          <CardDescription>
            自定义应用的外观和行为
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-3">主题模式</label>
              <div className="flex space-x-3">
                <Button
                  variant={theme === 'light' ? 'default' : 'outline'}
                  onClick={() => handleThemeChange('light')}
                  className="flex items-center space-x-2"
                >
                  <Sun className="h-4 w-4" />
                  <span>浅色</span>
                </Button>
                <Button
                  variant={theme === 'dark' ? 'default' : 'outline'}
                  onClick={() => handleThemeChange('dark')}
                  className="flex items-center space-x-2"
                >
                  <Moon className="h-4 w-4" />
                  <span>深色</span>
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 关于信息 */}
      <Card>
        <CardHeader>
          <CardTitle>关于</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm">
            <div>
              <span className="font-medium">Excel智能体</span> v2.0 - JavaScript版本
            </div>
            <div className="text-muted-foreground">
              基于AI的Excel数据分析工具，支持智能分析、自动可视化和深度洞察生成
            </div>
            <div className="text-muted-foreground">
              技术栈：React + TypeScript + Vite + Plotly.js + SheetJS
            </div>
            <div className="text-muted-foreground">
              © 2025 Excel智能体团队
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
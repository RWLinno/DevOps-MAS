import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Switch } from './ui/switch'
import { Badge } from './ui/badge'
import { Slider } from './ui/slider'
import { Textarea } from './ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog'
import { useTheme } from './ThemeProvider'
import { 
  Settings, 
  Moon, 
  Sun, 
  Monitor, 
  Cpu, 
  MemoryStick, 
  Zap, 
  Brain, 
  Eye, 
  Search, 
  FileText, 
  BarChart3, 
  Activity,
  Save,
  RotateCcw,
  Download,
  Upload,
  AlertTriangle,

  Info
} from 'lucide-react'

interface SettingsPanelProps {
  isOpen?: boolean
  onClose?: () => void
}

interface SystemConfig {
  theme: 'light' | 'dark' | 'system'
  enableNotifications: boolean
  enableSounds: boolean
  autoRefresh: boolean
  refreshInterval: number
  maxConcurrentModels: number
  memoryThreshold: number
  enableVRAMAwareness: boolean
  enableSymbolDetection: boolean
  enableDynamicWeights: boolean
  responseTimeout: number
  maxRetries: number
}

interface AgentConfig {
  id: string
  name: string
  enabled: boolean
  confidence: number
  priority: 'low' | 'medium' | 'high'
  maxTokens: number
  temperature: number
}

export function SettingsPanel({ isOpen = false, onClose }: SettingsPanelProps) {
  const { setTheme } = useTheme()
  const [activeTab, setActiveTab] = useState<'system' | 'agents' | 'performance' | 'advanced'>('system')
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  
  const [systemConfig, setSystemConfig] = useState<SystemConfig>({
    theme: 'system',
    enableNotifications: true,
    enableSounds: false,
    autoRefresh: true,
    refreshInterval: 30,
    maxConcurrentModels: 2,
    memoryThreshold: 85,
    enableVRAMAwareness: true,
    enableSymbolDetection: true,
    enableDynamicWeights: true,
    responseTimeout: 300,
    maxRetries: 3
  })

  const [agentConfigs, setAgentConfigs] = useState<AgentConfig[]>([
    {
      id: 'route_agent',
      name: '路由智能体',
      enabled: true,
      confidence: 0.85,
      priority: 'high',
      maxTokens: 512,
      temperature: 0.7
    },
    {
      id: 'knowledge_agent',
      name: '知识库智能体',
      enabled: true,
      confidence: 0.8,
      priority: 'high',
      maxTokens: 1024,
      temperature: 0.7
    },
    {
      id: 'visual_analysis_agent',
      name: '视觉分析智能体',
      enabled: true,
      confidence: 0.8,
      priority: 'medium',
      maxTokens: 512,
      temperature: 0.7
    },
    {
      id: 'search_agent',
      name: '搜索智能体',
      enabled: true,
      confidence: 0.8,
      priority: 'medium',
      maxTokens: 1024,
      temperature: 0.3
    },
    {
      id: 'comprehensive_agent',
      name: '综合分析智能体',
      enabled: true,
      confidence: 0.8,
      priority: 'high',
      maxTokens: 2048,
      temperature: 0.7
    },
    {
      id: 'metrics_analysis_agent',
      name: '指标分析智能体',
      enabled: true,
      confidence: 0.8,
      priority: 'medium',
      maxTokens: 1024,
      temperature: 0.5
    }
  ])

  const updateSystemConfig = (key: keyof SystemConfig, value: any) => {
    setSystemConfig(prev => ({ ...prev, [key]: value }))
    setHasUnsavedChanges(true)
  }

  const updateAgentConfig = (id: string, key: keyof AgentConfig, value: any) => {
    setAgentConfigs(prev => prev.map(agent => 
      agent.id === id ? { ...agent, [key]: value } : agent
    ))
    setHasUnsavedChanges(true)
  }

  const saveSettings = () => {
    // 模拟保存设置
    console.log('保存设置:', { systemConfig, agentConfigs })
    setHasUnsavedChanges(false)
    
    // 应用主题设置
    if (systemConfig.theme !== 'system') {
      setTheme(systemConfig.theme)
    }
  }

  const resetSettings = () => {
    // 重置到默认设置
    setSystemConfig({
      theme: 'system',
      enableNotifications: true,
      enableSounds: false,
      autoRefresh: true,
      refreshInterval: 30,
      maxConcurrentModels: 2,
      memoryThreshold: 85,
      enableVRAMAwareness: true,
      enableSymbolDetection: true,
      enableDynamicWeights: true,
      responseTimeout: 300,
      maxRetries: 3
    })
    setHasUnsavedChanges(true)
  }

  const exportSettings = () => {
    const settings = { systemConfig, agentConfigs }
    const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'devops-mas-settings.json'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const importSettings = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const settings = JSON.parse(e.target?.result as string)
          if (settings.systemConfig) setSystemConfig(settings.systemConfig)
          if (settings.agentConfigs) setAgentConfigs(settings.agentConfigs)
          setHasUnsavedChanges(true)
        } catch (error) {
          console.error('导入设置失败:', error)
        }
      }
      reader.readAsText(file)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      default: return 'bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-200'
    }
  }

  const getAgentIcon = (id: string) => {
    switch (id) {
      case 'route_agent': return Brain
      case 'visual_analysis_agent': return Eye
      case 'search_agent': return Search
      case 'knowledge_agent': return FileText
      case 'metrics_analysis_agent': return BarChart3
      case 'comprehensive_agent': return Activity
      default: return Settings
    }
  }

  if (!isOpen) return null

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Settings className="w-5 h-5" />
            <span>系统设置</span>
            {hasUnsavedChanges && (
              <Badge variant="outline" className="bg-yellow-100 text-yellow-800">
                未保存
              </Badge>
            )}
          </DialogTitle>
        </DialogHeader>

        <div className="flex space-x-6">
          {/* 侧边栏导航 */}
          <div className="w-48 space-y-2">
            {[
              { id: 'system', label: '系统设置', icon: Monitor },
              { id: 'agents', label: '智能体配置', icon: Brain },
              { id: 'performance', label: '性能优化', icon: Zap },
              { id: 'advanced', label: '高级设置', icon: Settings }
            ].map(({ id, label, icon: Icon }) => (
              <Button
                key={id}
                variant={activeTab === id ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => setActiveTab(id as any)}
              >
                <Icon className="w-4 h-4 mr-2" />
                {label}
              </Button>
            ))}
          </div>

          {/* 主要内容区域 */}
          <div className="flex-1 space-y-6">
            {activeTab === 'system' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Monitor className="w-5 h-5" />
                      <span>界面设置</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label>主题</Label>
                      <div className="flex space-x-2">
                        {[
                          { value: 'light', label: '浅色', icon: Sun },
                          { value: 'dark', label: '深色', icon: Moon },
                          { value: 'system', label: '跟随系统', icon: Monitor }
                        ].map(({ value, label, icon: Icon }) => (
                          <Button
                            key={value}
                            variant={systemConfig.theme === value ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => updateSystemConfig('theme', value)}
                          >
                            <Icon className="w-4 h-4 mr-1" />
                            {label}
                          </Button>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <Label htmlFor="notifications">启用通知</Label>
                      <Switch
                        id="notifications"
                        checked={systemConfig.enableNotifications}
                        onCheckedChange={(checked) => updateSystemConfig('enableNotifications', checked)}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <Label htmlFor="sounds">启用声音</Label>
                      <Switch
                        id="sounds"
                        checked={systemConfig.enableSounds}
                        onCheckedChange={(checked) => updateSystemConfig('enableSounds', checked)}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <Label htmlFor="autoRefresh">自动刷新</Label>
                      <Switch
                        id="autoRefresh"
                        checked={systemConfig.autoRefresh}
                        onCheckedChange={(checked) => updateSystemConfig('autoRefresh', checked)}
                      />
                    </div>

                    {systemConfig.autoRefresh && (
                      <div className="space-y-2">
                        <Label>刷新间隔 (秒): {systemConfig.refreshInterval}</Label>
                        <Slider
                          value={[systemConfig.refreshInterval]}
                          onValueChange={([value]) => updateSystemConfig('refreshInterval', value)}
                          min={5}
                          max={300}
                          step={5}
                          className="w-full"
                        />
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Zap className="w-5 h-5" />
                      <span>VRAM感知设置</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>启用VRAM感知</Label>
                        <p className="text-xs text-slate-500">自动根据可用VRAM选择合适的模型</p>
                      </div>
                      <Switch
                        checked={systemConfig.enableVRAMAwareness}
                        onCheckedChange={(checked) => updateSystemConfig('enableVRAMAwareness', checked)}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>最大并发模型数: {systemConfig.maxConcurrentModels}</Label>
                      <Slider
                        value={[systemConfig.maxConcurrentModels]}
                        onValueChange={([value]) => updateSystemConfig('maxConcurrentModels', value)}
                        min={1}
                        max={6}
                        step={1}
                        className="w-full"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>内存阈值 (%): {systemConfig.memoryThreshold}</Label>
                      <Slider
                        value={[systemConfig.memoryThreshold]}
                        onValueChange={([value]) => updateSystemConfig('memoryThreshold', value)}
                        min={50}
                        max={95}
                        step={5}
                        className="w-full"
                      />
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {activeTab === 'agents' && (
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Brain className="w-5 h-5" />
                      <span>智能体配置</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {agentConfigs.map((agent) => {
                        const Icon = getAgentIcon(agent.id)
                        return (
                          <div key={agent.id} className="p-4 border border-slate-200 dark:border-slate-700 rounded-lg">
                            <div className="flex items-center justify-between mb-4">
                              <div className="flex items-center space-x-3">
                                <Icon className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                                <div>
                                  <h4 className="font-medium">{agent.name}</h4>
                                  <p className="text-xs text-slate-500">{agent.id}</p>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                <Badge className={getPriorityColor(agent.priority)}>
                                  {agent.priority}
                                </Badge>
                                <Switch
                                  checked={agent.enabled}
                                  onCheckedChange={(checked) => updateAgentConfig(agent.id, 'enabled', checked)}
                                />
                              </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                              <div className="space-y-2">
                                <Label>置信度阈值: {agent.confidence.toFixed(2)}</Label>
                                <Slider
                                  value={[agent.confidence]}
                                  onValueChange={([value]) => updateAgentConfig(agent.id, 'confidence', value)}
                                  min={0.5}
                                  max={1.0}
                                  step={0.05}
                                  className="w-full"
                                />
                              </div>

                              <div className="space-y-2">
                                <Label>温度: {agent.temperature.toFixed(1)}</Label>
                                <Slider
                                  value={[agent.temperature]}
                                  onValueChange={([value]) => updateAgentConfig(agent.id, 'temperature', value)}
                                  min={0.0}
                                  max={1.0}
                                  step={0.1}
                                  className="w-full"
                                />
                              </div>

                              <div className="space-y-2">
                                <Label htmlFor={`${agent.id}-tokens`}>最大Token数</Label>
                                <Input
                                  id={`${agent.id}-tokens`}
                                  type="number"
                                  value={agent.maxTokens}
                                  onChange={(e) => updateAgentConfig(agent.id, 'maxTokens', parseInt(e.target.value))}
                                  min={256}
                                  max={8192}
                                />
                              </div>

                              <div className="space-y-2">
                                <Label htmlFor={`${agent.id}-priority`}>优先级</Label>
                                <select
                                  id={`${agent.id}-priority`}
                                  value={agent.priority}
                                  onChange={(e) => updateAgentConfig(agent.id, 'priority', e.target.value)}
                                  className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-md bg-white dark:bg-slate-800"
                                >
                                  <option value="low">低</option>
                                  <option value="medium">中</option>
                                  <option value="high">高</option>
                                </select>
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {activeTab === 'performance' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Cpu className="w-5 h-5" />
                      <span>性能优化</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>启用符号检测</Label>
                        <p className="text-xs text-slate-500">检测查询中的特殊符号以优化路由</p>
                      </div>
                      <Switch
                        checked={systemConfig.enableSymbolDetection}
                        onCheckedChange={(checked) => updateSystemConfig('enableSymbolDetection', checked)}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label>启用动态权重</Label>
                        <p className="text-xs text-slate-500">根据上下文动态调整智能体权重</p>
                      </div>
                      <Switch
                        checked={systemConfig.enableDynamicWeights}
                        onCheckedChange={(checked) => updateSystemConfig('enableDynamicWeights', checked)}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>响应超时 (秒): {systemConfig.responseTimeout}</Label>
                      <Slider
                        value={[systemConfig.responseTimeout]}
                        onValueChange={([value]) => updateSystemConfig('responseTimeout', value)}
                        min={30}
                        max={600}
                        step={30}
                        className="w-full"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>最大重试次数: {systemConfig.maxRetries}</Label>
                      <Slider
                        value={[systemConfig.maxRetries]}
                        onValueChange={([value]) => updateSystemConfig('maxRetries', value)}
                        min={1}
                        max={5}
                        step={1}
                        className="w-full"
                      />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <MemoryStick className="w-5 h-5" />
                      <span>内存管理</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <div className="flex items-start space-x-2">
                        <Info className="w-5 h-5 text-blue-500 mt-0.5" />
                        <div>
                          <h4 className="font-medium text-blue-900 dark:text-blue-100">VRAM感知系统状态</h4>
                          <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                            当前检测到24GB VRAM环境，系统已自动优化为Mid-High配置。
                            推荐使用Qwen2.5-32B-Instruct文本模型和Qwen2.5-VL-7B-Instruct视觉模型。
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="p-3 border border-slate-200 dark:border-slate-700 rounded">
                        <div className="font-medium mb-1">硬件层级</div>
                        <div className="text-slate-600 dark:text-slate-400">Mid-High (24GB)</div>
                      </div>
                      <div className="p-3 border border-slate-200 dark:border-slate-700 rounded">
                        <div className="font-medium mb-1">推荐并发模型</div>
                        <div className="text-slate-600 dark:text-slate-400">2-3个</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {activeTab === 'advanced' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Settings className="w-5 h-5" />
                      <span>高级设置</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="api-endpoint">API端点</Label>
                      <Input
                        id="api-endpoint"
                        placeholder="http://localhost:8080"
                        defaultValue="http://localhost:8080"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="api-key">API密钥</Label>
                      <Input
                        id="api-key"
                        type="password"
                        placeholder="输入API密钥"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="custom-prompt">自定义系统提示</Label>
                      <Textarea
                        id="custom-prompt"
                        placeholder="输入自定义系统提示..."
                        rows={4}
                      />
                    </div>

                    <div className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
                      <div className="flex items-start space-x-2">
                        <AlertTriangle className="w-5 h-5 text-amber-500 mt-0.5" />
                        <div>
                          <h4 className="font-medium text-amber-900 dark:text-amber-100">注意</h4>
                          <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
                            修改高级设置可能会影响系统稳定性。请确保您了解这些设置的作用。
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>配置管理</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex space-x-2">
                      <Button onClick={exportSettings} variant="outline">
                        <Download className="w-4 h-4 mr-2" />
                        导出配置
                      </Button>
                      <Button onClick={() => document.getElementById('import-settings')?.click()} variant="outline">
                        <Upload className="w-4 h-4 mr-2" />
                        导入配置
                      </Button>
                      <input
                        id="import-settings"
                        type="file"
                        accept=".json"
                        onChange={importSettings}
                        className="hidden"
                      />
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* 底部操作按钮 */}
            <div className="flex items-center justify-between pt-6 border-t border-slate-200 dark:border-slate-700">
              <div className="flex space-x-2">
                <Button onClick={resetSettings} variant="outline">
                  <RotateCcw className="w-4 h-4 mr-2" />
                  重置
                </Button>
              </div>
              <div className="flex space-x-2">
                <Button onClick={onClose} variant="outline">
                  取消
                </Button>
                <Button onClick={saveSettings} disabled={!hasUnsavedChanges}>
                  <Save className="w-4 h-4 mr-2" />
                  保存设置
                </Button>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
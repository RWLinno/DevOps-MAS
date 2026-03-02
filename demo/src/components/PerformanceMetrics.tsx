
import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'

import { Button } from './ui/button'
import { Progress } from './ui/progress'
import { 
  TrendingUp, 
  TrendingDown, 
  Clock, 
  CheckCircle, 

  Target,
  Zap,
  BarChart3,
  PieChart,
  Activity,

  Download,


  MessageSquare,
  Brain
} from 'lucide-react'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area,


  PieChart as RechartsPieChart,
  Pie,
  Cell
} from 'recharts'

interface MetricData {
  timestamp: string
  responseTime: number
  successRate: number
  agentAccuracy: number
  systemLoad: number
  queryCount: number
  errorCount: number
}

interface AgentPerformance {
  name: string
  displayName: string
  accuracy: number
  avgResponseTime: number
  usageCount: number
  successRate: number
  trend: 'up' | 'down' | 'stable'
}

interface SystemMetrics {
  totalQueries: number
  avgResponseTime: number
  successRate: number
  agentAccuracy: number
  systemUptime: number
  peakLoad: number
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

export function PerformanceMetrics() {
  const [timeRange, setTimeRange] = useState<'1h' | '24h' | '7d' | '30d'>('24h')
  const [metricsData, setMetricsData] = useState<MetricData[]>([])
  const [agentPerformance] = useState<AgentPerformance[]>([
    {
      name: 'route_agent',
      displayName: '路由智能体',
      accuracy: 0.95,
      avgResponseTime: 0.12,
      usageCount: 1250,
      successRate: 0.98,
      trend: 'up'
    },
    {
      name: 'knowledge_agent',
      displayName: '知识库智能体',
      accuracy: 0.89,
      avgResponseTime: 0.85,
      usageCount: 856,
      successRate: 0.92,
      trend: 'stable'
    },
    {
      name: 'search_agent',
      displayName: '搜索智能体',
      accuracy: 0.92,
      avgResponseTime: 2.3,
      usageCount: 642,
      successRate: 0.88,
      trend: 'up'
    },
    {
      name: 'visual_analysis_agent',
      displayName: '视觉分析智能体',
      accuracy: 0.88,
      avgResponseTime: 1.2,
      usageCount: 324,
      successRate: 0.85,
      trend: 'down'
    },
    {
      name: 'comprehensive_agent',
      displayName: '综合分析智能体',
      accuracy: 0.93,
      avgResponseTime: 2.8,
      usageCount: 478,
      successRate: 0.94,
      trend: 'up'
    },
    {
      name: 'metrics_analysis_agent',
      displayName: '指标分析智能体',
      accuracy: 0.85,
      avgResponseTime: 1.5,
      usageCount: 198,
      successRate: 0.87,
      trend: 'stable'
    }
  ])

  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>({
    totalQueries: 3748,
    avgResponseTime: 1.45,
    successRate: 0.91,
    agentAccuracy: 0.90,
    systemUptime: 99.8,
    peakLoad: 85
  })

  // 生成模拟数据
  useEffect(() => {
    const generateData = () => {
      const data: MetricData[] = []
      const now = new Date()
      const intervals = timeRange === '1h' ? 60 : timeRange === '24h' ? 24 : timeRange === '7d' ? 7 : 30
      const intervalMs = timeRange === '1h' ? 60000 : timeRange === '24h' ? 3600000 : timeRange === '7d' ? 86400000 : 86400000
      
      for (let i = intervals - 1; i >= 0; i--) {
        const timestamp = new Date(now.getTime() - i * intervalMs)
        const timeStr = timeRange === '1h' 
          ? timestamp.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
          : timeRange === '24h'
          ? timestamp.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
          : timestamp.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
        
        data.push({
          timestamp: timeStr,
          responseTime: Math.max(0.5, Math.min(3.0, 1.45 + (Math.random() - 0.5) * 1.0)),
          successRate: Math.max(0.8, Math.min(1.0, 0.91 + (Math.random() - 0.5) * 0.1)),
          agentAccuracy: Math.max(0.8, Math.min(1.0, 0.90 + (Math.random() - 0.5) * 0.1)),
          systemLoad: Math.max(20, Math.min(100, 65 + (Math.random() - 0.5) * 30)),
          queryCount: Math.floor(Math.random() * 50 + 10),
          errorCount: Math.floor(Math.random() * 5)
        })
      }
      
      setMetricsData(data)
    }

    generateData()
    const interval = setInterval(generateData, 30000)
    return () => clearInterval(interval)
  }, [timeRange])

  // 更新系统指标
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemMetrics(prev => ({
        ...prev,
        totalQueries: prev.totalQueries + Math.floor(Math.random() * 10),
        avgResponseTime: Math.max(0.5, Math.min(3.0, prev.avgResponseTime + (Math.random() - 0.5) * 0.1)),
        successRate: Math.max(0.85, Math.min(0.98, prev.successRate + (Math.random() - 0.5) * 0.02)),
        agentAccuracy: Math.max(0.85, Math.min(0.98, prev.agentAccuracy + (Math.random() - 0.5) * 0.02)),
        peakLoad: Math.max(50, Math.min(100, prev.peakLoad + (Math.random() - 0.5) * 5))
      }))
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp className="w-4 h-4 text-green-500" />
      case 'down': return <TrendingDown className="w-4 h-4 text-red-500" />
      default: return <Activity className="w-4 h-4 text-slate-500" />
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up': return 'text-green-600'
      case 'down': return 'text-red-600'
      default: return 'text-slate-600'
    }
  }

  const exportMetrics = () => {
    const data = {
      systemMetrics,
      agentPerformance,
      metricsData,
      exportTime: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `devops-mas-metrics-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const pieData = agentPerformance.map((agent, index) => ({
    name: agent.displayName,
    value: agent.usageCount,
    color: COLORS[index % COLORS.length]
  }))

  return (
    <div className="space-y-6">
      {/* 控制面板 */}
      <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5 text-blue-500" />
              <span>性能指标概览</span>
            </span>
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1 bg-slate-100 dark:bg-slate-700 rounded-lg p-1">
                {(['1h', '24h', '7d', '30d'] as const).map((range) => (
                  <Button
                    key={range}
                    variant={timeRange === range ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setTimeRange(range)}
                    className="text-xs"
                  >
                    {range}
                  </Button>
                ))}
              </div>
              <Button variant="outline" size="sm" onClick={exportMetrics}>
                <Download className="w-4 h-4 mr-1" />
                导出
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
      </Card>

      {/* 关键指标卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600 dark:text-slate-400">总查询数</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {systemMetrics.totalQueries.toLocaleString()}
                </p>
                <div className="flex items-center space-x-1 mt-1">
                  <TrendingUp className="w-3 h-3 text-green-500" />
                  <span className="text-xs text-green-600">+12.5%</span>
                </div>
              </div>
              <MessageSquare className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600 dark:text-slate-400">平均响应时间</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {systemMetrics.avgResponseTime.toFixed(2)}s
                </p>
                <div className="flex items-center space-x-1 mt-1">
                  <TrendingDown className="w-3 h-3 text-green-500" />
                  <span className="text-xs text-green-600">-8.3%</span>
                </div>
              </div>
              <Clock className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600 dark:text-slate-400">查询成功率</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {(systemMetrics.successRate * 100).toFixed(1)}%
                </p>
                <Progress value={systemMetrics.successRate * 100} className="mt-2 h-2" />
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600 dark:text-slate-400">智能体准确率</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {(systemMetrics.agentAccuracy * 100).toFixed(1)}%
                </p>
                <div className="flex items-center space-x-1 mt-1">
                  <TrendingUp className="w-3 h-3 text-green-500" />
                  <span className="text-xs text-green-600">+3.2%</span>
                </div>
              </div>
              <Target className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 性能趋势图表 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-blue-500" />
              <span>响应时间 & 成功率趋势</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={metricsData}>
                  <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                  <XAxis dataKey="timestamp" className="text-xs" />
                  <YAxis yAxisId="left" className="text-xs" />
                  <YAxis yAxisId="right" orientation="right" className="text-xs" />
                  <Tooltip />
                  <Line 
                    yAxisId="left"
                    type="monotone" 
                    dataKey="responseTime" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    name="响应时间(s)"
                  />
                  <Line 
                    yAxisId="right"
                    type="monotone" 
                    dataKey="successRate" 
                    stroke="#10b981" 
                    strokeWidth={2}
                    name="成功率"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="w-5 h-5 text-yellow-500" />
              <span>系统负载 & 查询量</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={metricsData}>
                  <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                  <XAxis dataKey="timestamp" className="text-xs" />
                  <YAxis yAxisId="left" className="text-xs" />
                  <YAxis yAxisId="right" orientation="right" className="text-xs" />
                  <Tooltip />
                  <Area 
                    yAxisId="left"
                    type="monotone" 
                    dataKey="systemLoad" 
                    stroke="#f59e0b" 
                    fill="#f59e0b" 
                    fillOpacity={0.3}
                    name="系统负载(%)"
                  />
                  <Area 
                    yAxisId="right"
                    type="monotone" 
                    dataKey="queryCount" 
                    stroke="#8b5cf6" 
                    fill="#8b5cf6" 
                    fillOpacity={0.3}
                    name="查询量"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 智能体性能对比 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Brain className="w-5 h-5 text-purple-500" />
              <span>智能体性能对比</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {agentPerformance.map((agent, index) => (
                <div key={agent.name} className="p-4 border border-slate-200 dark:border-slate-700 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      />
                      <h4 className="font-medium">{agent.displayName}</h4>
                      {getTrendIcon(agent.trend)}
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-slate-600 dark:text-slate-400">
                      <span>使用次数: {agent.usageCount}</span>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-xs text-slate-500 mb-1">准确率</p>
                      <div className="flex items-center space-x-2">
                        <Progress value={agent.accuracy * 100} className="flex-1 h-2" />
                        <span className="text-sm font-medium">{(agent.accuracy * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                    
                    <div>
                      <p className="text-xs text-slate-500 mb-1">成功率</p>
                      <div className="flex items-center space-x-2">
                        <Progress value={agent.successRate * 100} className="flex-1 h-2" />
                        <span className="text-sm font-medium">{(agent.successRate * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                    
                    <div>
                      <p className="text-xs text-slate-500 mb-1">响应时间</p>
                      <div className="flex items-center space-x-2">
                        <span className={`text-sm font-medium ${getTrendColor(agent.trend)}`}>
                          {agent.avgResponseTime.toFixed(2)}s
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <PieChart className="w-5 h-5 text-green-500" />
              <span>智能体使用分布</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </RechartsPieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 space-y-2">
              {pieData.map((entry, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: entry.color }}
                    />
                    <span className="truncate">{entry.name}</span>
                  </div>
                  <span className="font-medium">{entry.value}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 系统健康状态 */}
      <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-green-500" />
            <span>系统健康状态</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-4">
              <h4 className="font-medium text-slate-700 dark:text-slate-300">系统运行时间</h4>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full" />
                <span className="text-2xl font-bold">{systemMetrics.systemUptime}%</span>
              </div>
              <Progress value={systemMetrics.systemUptime} className="h-2" />
              <p className="text-xs text-slate-500">过去30天平均运行时间</p>
            </div>
            
            <div className="space-y-4">
              <h4 className="font-medium text-slate-700 dark:text-slate-300">峰值负载</h4>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  systemMetrics.peakLoad > 90 ? 'bg-red-500' : 
                  systemMetrics.peakLoad > 70 ? 'bg-yellow-500' : 'bg-green-500'
                }`} />
                <span className="text-2xl font-bold">{systemMetrics.peakLoad}%</span>
              </div>
              <Progress value={systemMetrics.peakLoad} className="h-2" />
              <p className="text-xs text-slate-500">24小时内最高系统负载</p>
            </div>
            
            <div className="space-y-4">
              <h4 className="font-medium text-slate-700 dark:text-slate-300">错误率</h4>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full" />
                <span className="text-2xl font-bold">{((1 - systemMetrics.successRate) * 100).toFixed(1)}%</span>
              </div>
              <Progress value={(1 - systemMetrics.successRate) * 100} className="h-2" />
              <p className="text-xs text-slate-500">过去24小时错误率</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
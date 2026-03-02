import React, { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'

import { Textarea } from './ui/textarea'
import { Badge } from './ui/badge'
import { ScrollArea } from './ui/scroll-area'
import { 
  Send, 
  Image, 
  
  Mic, 
  Bot, 
  User, 
  Search, 
  AlertTriangle, 
  Eye,
  Activity,
  Bug,
  Zap,
  Clock
} from 'lucide-react'

interface Message {
  id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  symbols?: string[]
  agentUsed?: string
  confidence?: number
  processingTime?: number
}

interface SystemStatus {
  isOnline: boolean
  gpuUsage: number
  memoryUsage: number
  activeAgents: number
  responseTime: number
}

interface ChatInterfaceProps {
  systemStatus: SystemStatus
}

const SYMBOL_CONFIGS = {
  '@': { icon: Search, label: '文档检索', color: 'bg-blue-500', description: '激活文档检索功能' },
  '/search': { icon: Search, label: '搜索增强', color: 'bg-green-500', description: '提升搜索智能体置信度' },
  '/analyze': { icon: Activity, label: '综合分析', color: 'bg-purple-500', description: '启用综合分析模式' },
  '/debug': { icon: Bug, label: '调试模式', color: 'bg-orange-500', description: '激活日志分析智能体' },
  '/monitor': { icon: Activity, label: '监控模式', color: 'bg-cyan-500', description: '启用指标分析智能体' },
  '/visual': { icon: Eye, label: '视觉分析', color: 'bg-pink-500', description: '激活视觉分析智能体' },
  '!urgent': { icon: AlertTriangle, label: '紧急处理', color: 'bg-red-500', description: '优先级处理模式' }
}

const EXAMPLE_QUERIES = [
  { text: '@redis_troubleshooting.md 如何解决Redis连接超时问题？', symbols: ['@'] },
  { text: '/search 最新的Kubernetes版本特性', symbols: ['/search'] },
  { text: '!urgent 生产环境数据库连接失败', symbols: ['!urgent'] },
  { text: '/analyze 系统性能下降原因分析', symbols: ['/analyze'] },
  { text: '/debug 应用程序崩溃日志分析', symbols: ['/debug'] }
]

export function ChatInterface({ systemStatus }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: '欢迎使用 DevOps-MAS 智能运维问答系统！我可以帮助您解决技术问题、分析日志、监控系统性能等。您可以使用特殊符号来激活不同的功能模式。',
      timestamp: new Date(),
      symbols: []
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [detectedSymbols, setDetectedSymbols] = useState<string[]>([])
  const [isRecording, setIsRecording] = useState(false)
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // 检测输入中的符号
  useEffect(() => {
    const symbols = Object.keys(SYMBOL_CONFIGS).filter(symbol => 
      inputValue.includes(symbol)
    )
    setDetectedSymbols(symbols)
  }, [inputValue])

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 模拟发送消息
  const handleSendMessage = async () => {
    if (!inputValue.trim() && !selectedImage) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
      symbols: detectedSymbols
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setSelectedImage(null)
    setIsLoading(true)

    // 模拟AI响应
    setTimeout(() => {
      const agentUsed = getAgentForSymbols(detectedSymbols)
      const confidence = Math.random() * 0.3 + 0.7 // 0.7-1.0
      const processingTime = Math.random() * 2 + 0.5 // 0.5-2.5s

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: generateMockResponse(userMessage.content, detectedSymbols),
        timestamp: new Date(),
        symbols: detectedSymbols,
        agentUsed,
        confidence,
        processingTime
      }

      setMessages(prev => [...prev, assistantMessage])
      setIsLoading(false)
    }, Math.random() * 2000 + 1000)
  }

  const getAgentForSymbols = (symbols: string[]): string => {
    if (symbols.includes('@')) return 'retriever_agent'
    if (symbols.includes('/search')) return 'search_agent'
    if (symbols.includes('/analyze')) return 'comprehensive_agent'
    if (symbols.includes('/debug')) return 'log_analysis_agent'
    if (symbols.includes('/monitor')) return 'metrics_analysis_agent'
    if (symbols.includes('/visual')) return 'visual_analysis_agent'
    if (symbols.includes('!urgent')) return 'comprehensive_agent'
    return 'knowledge_agent'
  }

const generateMockResponse = (query: string, symbols: string[]): string => {
    const q = query.toLowerCase()
    if (symbols.includes('@')) {
      return `📚 **RAG 检索增强回答** — 基于 redis_troubleshooting.md\n\n## Redis 连接超时排查指南\n\n### 1. 检查 Redis 节点状态\n\`\`\`bash\nredis-cli -h 10.0.1.52 -p 6379 ping\nsystemctl status redis\n\`\`\`\n\n### 2. 检查系统资源\n\`\`\`bash\ndmesg | grep -i oom     # 检查是否被OOM Kill\nfree -h                 # 检查内存\nredis-cli info memory   # Redis内存使用\n\`\`\`\n\n### 3. 连接池分析\n- 确认 maxclients 配置（默认 10000）\n- 检查连接泄漏：\`redis-cli client list | wc -l\`\n- 配置连接超时：\`timeout 300\`\n\n### 4. 解决方案\n1. 重启异常节点：\`systemctl restart redis\`\n2. 增加 maxmemory 配置（建议 8GB）\n3. 使用 SCAN 替代 KEYS 命令\n4. 添加连接池监控告警\n\n---\n📄 **参考文档：** redis_troubleshooting.md (相关度: 0.95)`
    }
    if (symbols.includes('/search')) {
      return `🔍 **搜索增强回答** — SearchAgent\n\n## Kubernetes 1.28 版本核心特性\n\n### 新增功能\n- **Sidecar Containers (KEP-753)**：原生支持 sidecar 容器模式，优化服务网格场景\n- **Native Sidecar 支持 Job**：Job 中的 sidecar 容器可正常终止\n- **ValidatingAdmissionPolicy GA**：声明式准入策略正式可用\n\n### 安全增强\n- 改进的 KMS v2 API（稳定版）\n- Pod 安全标准更新\n- 减少了 CVE 攻击面\n\n### 性能优化\n- 调度器吞吐量提升 15%\n- etcd 读写延迟降低\n- 节点扩缩速度优化\n\n**信息来源：** kubernetes.io/blog, GitHub Release Notes`
    }
    if (symbols.includes('!urgent')) {
      return `🚨 **P0 紧急处理 — ComprehensiveAgent**\n\n## 数据库连接失败紧急响应\n\n### ⚡ 立即执行 (0-5分钟)\n1. **Kill 慢查询**：\n\`\`\`sql\nSHOW FULL PROCESSLIST;\nSELECT CONCAT('KILL ', id, ';') FROM information_schema.processlist WHERE time > 10;\n\`\`\`\n2. **临时扩容连接池**：\n\`\`\`sql\nSET GLOBAL max_connections = 800;\n\`\`\`\n3. **检查磁盘空间**：\`df -h /var/lib/mysql\`\n\n### 🔍 诊断 (5-15分钟)\n4. 检查慢查询日志：\`SHOW VARIABLES LIKE 'slow_query_log'\`\n5. 分析连接来源：\`SELECT user, host, COUNT(*) FROM information_schema.processlist GROUP BY user, host\`\n6. InnoDB 状态：\`SHOW ENGINE INNODB STATUS\`\n\n### 🛡️ 根因修复\n7. 添加缺失索引（如检测到全表扫描）\n8. 应用层添加 5s 查询超时\n9. 配置 Circuit Breaker\n\n**⏱ 预计恢复时间：15-30分钟**`
    }
    if (symbols.includes('/debug')) {
      return `🐛 **日志分析 — LogAnalysisAgent**\n\n## 日志扫描结果\n\n### 错误统计\n| 级别 | 数量 | 比例 |\n|------|------|------|\n| ERROR | 6 | 43% |\n| WARN | 3 | 21% |\n| INFO | 5 | 36% |\n\n### 关键错误\n1. \`[FATAL] redis.client - All connection attempts failed for node redis-cluster-03\`\n2. \`[ERROR] cache.service - CacheService unavailable, falling back to DB\`\n3. \`[ERROR] api.recommendation - Request timeout after 3000ms\`\n\n### 错误模式分析\n- **根因链：** Redis 节点 OOM → 连接池耗尽 → 缓存失效 → API 超时\n- **影响范围：** 推荐 API p99 延迟从 120ms 飙升到 2340ms\n- **触发时间：** 08:23:01 - 08:23:07（持续 6 秒）\n\n### 建议\n1. 设置 Redis maxmemory-policy 为 allkeys-lru\n2. 添加 Lua 脚本内存限制\n3. 配置连接池 eviction 策略`
    }
    if (symbols.includes('/monitor')) {
      return `📊 **指标分析 — MetricsAnalysisAgent**\n\n## 系统性能报告\n\n### 核心指标\n- **CPU 使用率：** 72% (⚠️ 警告阈值 80%)\n- **内存使用：** 14.2GB / 16GB (88% ⚠️)\n- **磁盘 IOPS：** 2,340 (正常)\n- **网络延迟：** 2.1ms (正常)\n\n### Redis 集群状态\n- 节点 01: ✅ 正常 (used_memory: 3.2GB)\n- 节点 02: ✅ 正常 (used_memory: 3.8GB)\n- 节点 03: ❌ 异常 (connection_refused)\n\n### 趋势分析\n- API p99 延迟：120ms → 2340ms (过去 5 分钟 ↑1850%)\n- 错误率：0.01% → 12.3% (过去 5 分钟 ↑)\n- QPS：15,000 → 8,200 (下降 45%)\n\n### 告警\n🔴 redis_connection_failure (P1)\n🟡 api_latency_high (P2)\n🟡 memory_usage_high (P2)`
    }
    if (symbols.includes('/visual')) {
      return `👁️ **视觉分析 — VisualAnalysisAgent (Qwen2.5-VL)**\n\n## 截图分析结果\n\n检测到这是一张 **Grafana 监控面板截图**，包含以下信息：\n\n### 识别到的面板\n1. **Redis Connections** - 连接数在 08:23 出现断崖式下降\n2. **API Response Time** - p99 延迟在同一时间点出现尖刺（2340ms）\n3. **Error Rate** - 错误率从 0.01% 飙升到 12.3%\n\n### 关联分析\n三个指标在 08:23:01 同时异常，指向 Redis 集群节点故障。连接数下降先于延迟上升，确认 Redis 是根因而非受害者。\n\n### 建议\n- 重点关注 redis-cluster-03 节点\n- 检查该时间点的系统 dmesg 日志\n- 确认是否有 OOM Kill 事件`
    }
    if (q.includes('redis') || q.includes('缓存') || q.includes('connection')) {
      return `## Redis 连接问题诊断\n\n### 问题分析\n根据您的描述，这是典型的 Redis 连接故障场景。\n\n### 诊断步骤\n1. **检查 Redis 进程状态**\n\`\`\`bash\nredis-cli ping\nsystemctl status redis\n\`\`\`\n\n2. **检查连接池**\n\`\`\`bash\nredis-cli info clients\nredis-cli client list | wc -l\n\`\`\`\n\n3. **检查内存**\n\`\`\`bash\nredis-cli info memory\n\`\`\`\n\n### 常见原因\n- OOM Kill（内存不足被系统杀死）\n- maxmemory 配置过低\n- 连接泄漏导致连接池耗尽\n- Lua 脚本执行占用过多内存\n\n### 解决方案\n1. 重启 Redis 节点\n2. 调整 maxmemory（建议物理内存的 75%）\n3. 配置 maxmemory-policy 为 allkeys-lru\n4. 添加连接池监控告警\n\n**路由智能体：** knowledge_agent (置信度: 0.88)`
    }
    if (q.includes('kafka') || q.includes('消费') || q.includes('lag')) {
      return `## Kafka Consumer Lag 诊断\n\n### 问题分析\nConsumer lag 过高通常表示消费者处理速度跟不上生产者速度。\n\n### 诊断步骤\n1. **检查 Consumer 状态**\n\`\`\`bash\nkafka-consumer-groups --bootstrap-server kafka:9092 \\\n  --describe --group data-pipeline-cg\n\`\`\`\n\n2. **检查错误日志**\n查看是否有 NullPointerException、序列化异常等\n\n3. **检查 DLQ**\n\`\`\`bash\nkafka-console-consumer --topic user-events-dlq --from-beginning | wc -l\n\`\`\`\n\n### 解决方案\n1. 修复消费者代码中的异常处理\n2. 增加消费者并行度（当前 3 → 建议 6）\n3. 重放 DLQ 中的消息\n4. 优化消息处理逻辑，减少单条处理时间\n\n**路由智能体：** log_analysis_agent (置信度: 0.91)`
    }
    if (q.includes('mysql') || q.includes('数据库') || q.includes('连接池')) {
      return `## MySQL 连接池耗尽诊断\n\n### 🚨 紧急处理\n1. **Kill 慢查询**\n\`\`\`sql\nSELECT * FROM information_schema.processlist \nWHERE time > 10 ORDER BY time DESC;\n\`\`\`\n\n2. **临时扩容**\n\`\`\`sql\nSET GLOBAL max_connections = 800;\n\`\`\`\n\n### 根因分析\n- 全表扫描：orders 表 280 万行无索引\n- 慢查询持续 12.5 秒，占用连接不释放\n- 建议添加索引：\n\`\`\`sql\nCREATE INDEX idx_orders_status_created \nON orders(status, created_at);\n\`\`\`\n\n### 长期方案\n1. 启用慢查询日志（阈值 1 秒）\n2. 应用层添加查询超时（5 秒）\n3. 连接池监控（>80% 告警）\n4. 定期索引优化审查\n\n**路由智能体：** comprehensive_agent (置信度: 0.93)`
    }
    return `## 问题分析\n\n感谢您的查询。根据 DevOps-MAS 多智能体系统的分析：\n\n### 诊断建议\n1. **检查相关服务状态** — 确认受影响组件是否正常运行\n2. **查看系统日志** — 使用 \`/debug\` 指令激活日志分析智能体\n3. **监控指标检查** — 使用 \`/monitor\` 查看性能指标\n4. **知识库检索** — 使用 \`@文档名.md\` 引用相关排查文档\n\n### 可用功能\n- \`@文档名.md\` — RAG 文档检索\n- \`/debug\` — 日志分析模式\n- \`/monitor\` — 系统监控\n- \`/visual\` — 图像分析\n- \`!urgent\` — 紧急处理\n\n请提供更多细节或使用上述指令获取更精确的分析。\n\n**路由智能体：** knowledge_agent (置信度: 0.75)`
  }

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedImage(file)
    }
  }

  const handleExampleQuery = (query: string) => {
    setInputValue(query)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-200px)]">
      {/* 主聊天区域 */}
      <div className="lg:col-span-3">
        <Card className="h-full flex flex-col bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm border-slate-200 dark:border-slate-700">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center space-x-2">
                <Bot className="w-5 h-5 text-blue-500" />
                <span>智能对话</span>
              </span>
              <div className="flex items-center space-x-2 text-sm text-slate-500">
                <Clock className="w-4 h-4" />
                <span>响应时间: {systemStatus.responseTime.toFixed(1)}s</span>
              </div>
            </CardTitle>
          </CardHeader>
          
          <CardContent className="flex-1 flex flex-col p-0">
            {/* 消息列表 */}
            <ScrollArea className="flex-1 px-6">
              <div className="space-y-4 py-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[80%] ${
                      message.type === 'user' 
                        ? 'bg-blue-500 text-white' 
                        : message.type === 'system'
                        ? 'bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-200'
                        : 'bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-slate-100'
                    } rounded-lg p-3`}>
                      <div className="flex items-start space-x-2">
                        {message.type === 'user' ? (
                          <User className="w-4 h-4 mt-0.5 flex-shrink-0" />
                        ) : (
                          <Bot className="w-4 h-4 mt-0.5 flex-shrink-0" />
                        )}
                        <div className="flex-1">
                          <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                          
                          {/* 符号指示器 */}
                          {message.symbols && message.symbols.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {message.symbols.map((symbol) => {
                                const config = SYMBOL_CONFIGS[symbol as keyof typeof SYMBOL_CONFIGS]
                                if (!config) return null
                                const Icon = config.icon
                                return (
                                  <Badge
                                    key={symbol}
                                    variant="secondary"
                                    className={`${config.color} text-white text-xs`}
                                  >
                                    <Icon className="w-3 h-3 mr-1" />
                                    {config.label}
                                  </Badge>
                                )
                              })}
                            </div>
                          )}
                          
                          {/* AI响应元数据 */}
                          {message.type === 'assistant' && (
                            <div className="flex items-center space-x-4 mt-2 text-xs text-slate-500 dark:text-slate-400">
                              {message.agentUsed && (
                                <span>智能体: {message.agentUsed}</span>
                              )}
                              {message.confidence && (
                                <span>置信度: {(message.confidence * 100).toFixed(1)}%</span>
                              )}
                              {message.processingTime && (
                                <span>处理时间: {message.processingTime.toFixed(2)}s</span>
                              )}
                            </div>
                          )}
                          
                          <div className="text-xs text-slate-400 mt-1">
                            {message.timestamp.toLocaleTimeString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-slate-100 dark:bg-slate-700 rounded-lg p-3">
                      <div className="flex items-center space-x-2">
                        <Bot className="w-4 h-4" />
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div ref={messagesEndRef} />
            </ScrollArea>
            
            {/* 符号检测提示 */}
            {detectedSymbols.length > 0 && (
              <div className="px-6 py-2 bg-blue-50 dark:bg-blue-900/20 border-t border-blue-200 dark:border-blue-800">
                <div className="flex items-center space-x-2 text-sm text-blue-700 dark:text-blue-300">
                  <Zap className="w-4 h-4" />
                  <span>检测到特殊符号:</span>
                  <div className="flex space-x-1">
                    {detectedSymbols.map((symbol) => {
                      const config = SYMBOL_CONFIGS[symbol as keyof typeof SYMBOL_CONFIGS]
                      if (!config) return null
                      return (
                        <Badge key={symbol} variant="outline" className="text-xs">
                          {config.label}
                        </Badge>
                      )
                    })}
                  </div>
                </div>
              </div>
            )}
            
            {/* 输入区域 */}
            <div className="p-6 border-t border-slate-200 dark:border-slate-700">
              <div className="flex space-x-2">
                <div className="flex-1">
                  <Textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="输入您的问题... 使用 @ 激活文档检索，/search 增强搜索，!urgent 紧急处理"
                    className="min-h-[60px] resize-none"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        handleSendMessage()
                      }
                    }}
                  />
                  {selectedImage && (
                    <div className="mt-2 p-2 bg-slate-100 dark:bg-slate-700 rounded text-sm">
                      已选择图片: {selectedImage.name}
                    </div>
                  )}
                </div>
                
                <div className="flex flex-col space-y-2">
                  <Button
                    onClick={handleSendMessage}
                    disabled={isLoading || (!inputValue.trim() && !selectedImage)}
                    className="bg-blue-500 hover:bg-blue-600"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={() => fileInputRef.current?.click()}
                    className="p-2"
                  >
                    <Image className="w-4 h-4" />
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={() => setIsRecording(!isRecording)}
                    className={`p-2 ${isRecording ? 'bg-red-100 text-red-600' : ''}`}
                  >
                    <Mic className="w-4 h-4" />
                  </Button>
                  
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* 侧边栏 */}
      <div className="space-y-4">
        {/* 符号指南 */}
        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">符号功能指南</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {Object.entries(SYMBOL_CONFIGS).map(([symbol, config]) => {
              const Icon = config.icon
              return (
                <div key={symbol} className="flex items-center space-x-2 text-xs">
                  <div className={`w-6 h-6 ${config.color} rounded flex items-center justify-center`}>
                    <Icon className="w-3 h-3 text-white" />
                  </div>
                  <div>
                    <div className="font-medium">{symbol}</div>
                    <div className="text-slate-500">{config.description}</div>
                  </div>
                </div>
              )
            })}
          </CardContent>
        </Card>
        
        {/* 示例查询 */}
        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">示例查询</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {EXAMPLE_QUERIES.map((example, index) => (
              <Button
                key={index}
                variant="ghost"
                className="w-full text-left text-xs h-auto p-2 whitespace-normal"
                onClick={() => handleExampleQuery(example.text)}
              >
                {example.text}
              </Button>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
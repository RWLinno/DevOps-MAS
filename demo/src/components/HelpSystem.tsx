import React, { useState } from 'react'
import { Card, CardContent } from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Badge } from './ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog'
import { ScrollArea } from './ui/scroll-area'
import { 
  HelpCircle, 
  Search, 
  Book, 
  MessageSquare, 
  Zap, 
  Brain, 



  Activity,
  AlertTriangle,

  ArrowRight,
  ExternalLink,
  Video,
  Download,
  Github,
  Mail
} from 'lucide-react'

interface HelpSystemProps {
  isOpen: boolean
  onClose: () => void
}

interface HelpTopic {
  id: string
  title: string
  description: string
  category: 'getting-started' | 'features' | 'troubleshooting' | 'advanced'
  icon: React.ComponentType<{ className?: string }>
  content: string
  tags: string[]
}

interface FAQ {
  question: string
  answer: string
  category: string
}

const HELP_TOPICS: HelpTopic[] = [
  {
    id: 'quick-start',
    title: '快速开始',
    description: '了解如何开始使用DevOps-MAS',
    category: 'getting-started',
    icon: Zap,
    content: `
# 快速开始指南

欢迎使用DevOps-MAS智能工程问答系统！本指南将帮助您快速上手。

## 基本使用

1. **发送普通查询**：直接在聊天框中输入您的问题
2. **使用特殊符号**：利用符号激活特定功能
3. **上传图片**：点击图片按钮上传截图或图表进行分析

## 特殊符号功能

- **@filename.md**：激活文档检索功能
- **/search**：增强搜索智能体置信度
- **/analyze**：启用综合分析模式
- **/debug**：激活调试和日志分析
- **!urgent**：紧急处理模式

## 示例查询

- \`@redis_troubleshooting.md 如何解决Redis连接超时问题？\`
- \`/search 最新的Kubernetes版本特性\`
- \`!urgent 生产环境数据库连接失败\`
    `,
    tags: ['入门', '基础', '符号']
  },
  {
    id: 'symbol-detection',
    title: '符号检测功能',
    description: '了解如何使用符号来优化AI响应',
    category: 'features',
    icon: Search,
    content: `
# 符号检测功能详解

DevOps-MAS支持多种特殊符号来激活不同的功能模式。

## 支持的符号

### @ 符号 - 文档检索
- **格式**：\`@filename.md\` 或 \`@document_name\`
- **功能**：激活文档检索功能，在知识库中搜索相关文档
- **示例**：\`@troubleshooting.md 如何解决网络问题？\`

### /search - 搜索增强
- **格式**：\`/search 查询内容\`
- **功能**：提升搜索智能体的置信度，进行网络搜索
- **示例**：\`/search Docker最新版本特性\`

### /analyze - 综合分析
- **格式**：\`/analyze 问题描述\`
- **功能**：启用综合分析智能体，进行深度分析
- **示例**：\`/analyze 系统性能下降原因\`

### /debug - 调试模式
- **格式**：\`/debug 错误信息\`
- **功能**：激活日志分析智能体，进行错误排查
- **示例**：\`/debug 应用程序崩溃日志分析\`

### !urgent - 紧急处理
- **格式**：\`!urgent 紧急问题\`
- **功能**：优先级处理模式，快速响应
- **示例**：\`!urgent 生产环境服务不可用\`

## 符号组合使用

您可以在一个查询中使用多个符号：
\`!urgent @incident_response.md /analyze 生产环境故障\`
    `,
    tags: ['符号', '检索', '搜索', '分析']
  },
  {
    id: 'agent-system',
    title: '多智能体系统',
    description: '了解DevOps-MAS的智能体协调机制',
    category: 'features',
    icon: Brain,
    content: `
# 多智能体系统架构

DevOps-MAS采用多智能体协作架构，每个智能体专门处理特定类型的任务。

## 智能体类型

### 路由智能体 (Route Agent)
- **职责**：分析查询并选择最适合的智能体
- **特点**：高置信度阈值(0.85)，语义自适应路由
- **优化**：支持符号检测和动态权重调整

### 知识库智能体 (Knowledge Agent)
- **职责**：查询知识库和技术文档
- **特点**：支持RAG增强，文档检索优化
- **模型**：Qwen2.5-VL-7B-Instruct

### 视觉分析智能体 (Visual Analysis Agent)
- **职责**：处理图像分析和视觉内容理解
- **支持格式**：jpg, jpeg, png, bmp, webp
- **最大文件**：10MB

### 搜索智能体 (Search Agent)
- **职责**：执行网络搜索和信息检索
- **搜索引擎**：DuckDuckGo, GitHub
- **信任域名**：包含主流技术网站

### 综合分析智能体 (Comprehensive Agent)
- **职责**：处理复杂问题和综合分析
- **特点**：高优先级，大token容量(2048)

### 指标分析智能体 (Metrics Analysis Agent)
- **职责**：分析系统指标和性能数据
- **特点**：专注于数值分析和趋势预测

## 协调机制

1. **查询接收**：路由智能体接收并分析查询
2. **符号检测**：识别特殊符号和关键词
3. **置信度评估**：计算各智能体的适配度
4. **权重调整**：根据上下文动态调整权重
5. **智能体选择**：选择置信度最高的智能体执行
    `,
    tags: ['智能体', '架构', '路由', '协调']
  },
  {
    id: 'vram-awareness',
    title: 'VRAM感知系统',
    description: '了解智能模型降级和资源管理',
    category: 'advanced',
    icon: Activity,
    content: `
# VRAM感知系统

DevOps-MAS具备智能的VRAM感知能力，能够根据硬件配置自动选择合适的模型。

## 硬件层级

### Minimal (<4GB)
- **推荐模型**：Qwen2.5-1.5B-Instruct
- **并发模型**：1个
- **优化策略**：Mock模式，极保守加载

### Low End (4-8GB)
- **推荐模型**：Qwen2.5-3B-Instruct
- **并发模型**：1个
- **优化策略**：启用量化，保守策略

### Mid Range (16-24GB)
- **推荐模型**：Qwen2.5-14B-Instruct
- **并发模型**：2个
- **优化策略**：平衡策略

### Mid High (24-32GB) - 当前环境
- **推荐文本模型**：Qwen2.5-32B-Instruct (20GB)
- **推荐VL模型**：Qwen2.5-VL-7B-Instruct (10GB)
- **并发模型**：2-3个
- **优化策略**：平衡策略，最佳性能

### High End (32GB+)
- **推荐模型**：Qwen2.5-72B-Instruct
- **并发模型**：4个
- **优化策略**：激进加载，最高性能

## 降级策略

1. **模型内降级**：同类型模型间的降级
2. **量化降级**：使用量化版本减少内存占用
3. **功能降级**：降低处理复杂度
4. **Mock模式**：最终保障，确保系统可用性

## 监控指标

- **VRAM使用率**：实时监控GPU内存使用
- **模型加载状态**：跟踪模型加载和卸载
- **降级事件**：记录和通知降级情况
- **性能指标**：响应时间和成功率统计
    `,
    tags: ['VRAM', '硬件', '优化', '降级']
  }
]

const FAQS: FAQ[] = [
  {
    question: '如何提高查询的准确性？',
    answer: '使用特殊符号来激活相应功能，如使用@符号进行文档检索，使用/search进行网络搜索。提供具体的上下文信息也有助于提高准确性。',
    category: '使用技巧'
  },
  {
    question: '为什么我的查询响应很慢？',
    answer: '响应时间可能受多种因素影响：1) 查询复杂度 2) 当前系统负载 3) 网络搜索需求 4) 图像处理任务。您可以在系统监控页面查看详细的性能指标。',
    category: '性能问题'
  },
  {
    question: '支持哪些图片格式？',
    answer: '支持常见的图片格式：JPG, JPEG, PNG, BMP, WEBP。单个文件大小限制为10MB。',
    category: '功能支持'
  },
  {
    question: '如何使用文档检索功能？',
    answer: '在查询前加上@符号和文档名，如"@troubleshooting.md 如何解决网络问题？"。系统会在知识库中搜索相关文档并结合内容回答。',
    category: '功能支持'
  },
  {
    question: 'VRAM不足时系统如何处理？',
    answer: '系统会自动检测VRAM使用情况，在内存不足时启用降级策略：1) 使用更小的模型 2) 启用量化优化 3) 限制并发模型数量 4) 必要时使用Mock模式确保可用性。',
    category: '系统管理'
  },
  {
    question: '如何查看智能体的选择过程？',
    answer: '在"智能体协调"页面可以查看完整的路由决策过程，包括符号检测、置信度评估、权重调整和最终选择的详细步骤。',
    category: '系统监控'
  }
]

export function HelpSystem({ isOpen, onClose }: HelpSystemProps) {
  const [activeCategory, setActiveCategory] = useState<string>('getting-started')
  const [selectedTopic, setSelectedTopic] = useState<HelpTopic | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [showFAQ, setShowFAQ] = useState(false)

  const categories = [
    { id: 'getting-started', label: '入门指南', icon: Book },
    { id: 'features', label: '功能特性', icon: Zap },
    { id: 'troubleshooting', label: '故障排除', icon: AlertTriangle },
    { id: 'advanced', label: '高级功能', icon: Brain }
  ]

  const filteredTopics = HELP_TOPICS.filter(topic => {
    const matchesCategory = activeCategory === 'all' || topic.category === activeCategory
    const matchesSearch = searchQuery === '' || 
      topic.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      topic.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      topic.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    return matchesCategory && matchesSearch
  })

  const filteredFAQs = FAQS.filter(faq => 
    searchQuery === '' || 
    faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
    faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <HelpCircle className="w-5 h-5" />
            <span>帮助中心</span>
          </DialogTitle>
        </DialogHeader>

        <div className="flex h-[70vh]">
          {/* 侧边栏 */}
          <div className="w-64 border-r border-slate-200 dark:border-slate-700 pr-4">
            <div className="space-y-4">
              {/* 搜索框 */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
                <Input
                  placeholder="搜索帮助内容..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>

              {/* 分类导航 */}
              <div className="space-y-1">
                <Button
                  variant={showFAQ ? 'default' : 'ghost'}
                  className="w-full justify-start"
                  onClick={() => {
                    setShowFAQ(true)
                    setSelectedTopic(null)
                  }}
                >
                  <MessageSquare className="w-4 h-4 mr-2" />
                  常见问题
                </Button>
                
                {categories.map(({ id, label, icon: Icon }) => (
                  <Button
                    key={id}
                    variant={activeCategory === id && !showFAQ ? 'default' : 'ghost'}
                    className="w-full justify-start"
                    onClick={() => {
                      setActiveCategory(id)
                      setShowFAQ(false)
                      setSelectedTopic(null)
                    }}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {label}
                  </Button>
                ))}
              </div>

              {/* 快速链接 */}
              <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
                <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">快速链接</h4>
                <div className="space-y-1">
                  <Button variant="ghost" size="sm" className="w-full justify-start text-xs">
                    <Video className="w-3 h-3 mr-2" />
                    视频教程
                  </Button>
                  <Button variant="ghost" size="sm" className="w-full justify-start text-xs">
                    <Download className="w-3 h-3 mr-2" />
                    用户手册
                  </Button>
                  <Button variant="ghost" size="sm" className="w-full justify-start text-xs">
                    <Github className="w-3 h-3 mr-2" />
                    GitHub仓库
                  </Button>
                  <Button variant="ghost" size="sm" className="w-full justify-start text-xs">
                    <Mail className="w-3 h-3 mr-2" />
                    联系支持
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* 主要内容区域 */}
          <div className="flex-1 pl-6">
            <ScrollArea className="h-full">
              {selectedTopic ? (
                /* 详细内容视图 */
                <div className="space-y-4">
                  <div className="flex items-center space-x-2 text-sm text-slate-500">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setSelectedTopic(null)}
                      className="p-0 h-auto"
                    >
                      {showFAQ ? '常见问题' : categories.find(c => c.id === activeCategory)?.label}
                    </Button>
                    <ArrowRight className="w-3 h-3" />
                    <span>{selectedTopic.title}</span>
                  </div>

                  <div className="flex items-start space-x-3">
                    <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                      <selectedTopic.icon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{selectedTopic.title}</h1>
                      <p className="text-slate-600 dark:text-slate-400 mt-1">{selectedTopic.description}</p>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {selectedTopic.tags.map((tag, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="prose prose-slate dark:prose-invert max-w-none">
                    <div className="whitespace-pre-wrap">{selectedTopic.content}</div>
                  </div>
                </div>
              ) : showFAQ ? (
                /* FAQ视图 */
                <div className="space-y-4">
                  <div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white">常见问题</h1>
                    <p className="text-slate-600 dark:text-slate-400 mt-1">
                      查找常见问题的快速解答
                    </p>
                  </div>

                  <div className="space-y-4">
                    {filteredFAQs.map((faq, index) => (
                      <Card key={index} className="bg-white/60 dark:bg-slate-800/60">
                        <CardContent className="p-4">
                          <div className="flex items-start space-x-3">
                            <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                              <span className="text-xs font-bold text-blue-600 dark:text-blue-400">Q</span>
                            </div>
                            <div className="flex-1">
                              <h3 className="font-medium text-slate-900 dark:text-white mb-2">
                                {faq.question}
                              </h3>
                              <p className="text-sm text-slate-600 dark:text-slate-400">
                                {faq.answer}
                              </p>
                              <Badge variant="outline" className="mt-2 text-xs">
                                {faq.category}
                              </Badge>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              ) : (
                /* 主题列表视图 */
                <div className="space-y-4">
                  <div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                      {categories.find(c => c.id === activeCategory)?.label || '帮助主题'}
                    </h1>
                    <p className="text-slate-600 dark:text-slate-400 mt-1">
                      选择一个主题了解详细信息
                    </p>
                  </div>

                  {searchQuery && (
                    <div className="text-sm text-slate-500">
                      找到 {filteredTopics.length} 个相关主题
                    </div>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {filteredTopics.map((topic) => {
                      const Icon = topic.icon
                      return (
                        <Card
                          key={topic.id}
                          className="cursor-pointer hover:shadow-md transition-shadow bg-white/60 dark:bg-slate-800/60"
                          onClick={() => setSelectedTopic(topic)}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-start space-x-3">
                              <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center flex-shrink-0">
                                <Icon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                              </div>
                              <div className="flex-1">
                                <h3 className="font-medium text-slate-900 dark:text-white mb-1">
                                  {topic.title}
                                </h3>
                                <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                                  {topic.description}
                                </p>
                                <div className="flex flex-wrap gap-1">
                                  {topic.tags.slice(0, 3).map((tag, index) => (
                                    <Badge key={index} variant="secondary" className="text-xs">
                                      {tag}
                                    </Badge>
                                  ))}
                                  {topic.tags.length > 3 && (
                                    <Badge variant="secondary" className="text-xs">
                                      +{topic.tags.length - 3}
                                    </Badge>
                                  )}
                                </div>
                              </div>
                              <ExternalLink className="w-4 h-4 text-slate-400" />
                            </div>
                          </CardContent>
                        </Card>
                      )
                    })}
                  </div>

                  {filteredTopics.length === 0 && (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Search className="w-6 h-6 text-slate-400" />
                      </div>
                      <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">
                        未找到相关内容
                      </h3>
                      <p className="text-slate-600 dark:text-slate-400">
                        尝试使用不同的关键词搜索或浏览其他分类
                      </p>
                    </div>
                  )}
                </div>
              )}
            </ScrollArea>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
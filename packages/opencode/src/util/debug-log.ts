import { EOL } from "os"

/**
 * OpenCode 调试日志工具
 * 
 * 使用方法:
 * 1. 设置环境变量: export OPENCODE_DEBUG=1
 * 2. 在代码中导入: import { DebugLog } from "@/util/debug-log"
 * 3. 添加日志: DebugLog.cli("Starting...")
 */

export namespace DebugLog {
  // 检查是否启用调试
  const enabled = process.env.OPENCODE_DEBUG === '1'
  const verbose = process.env.OPENCODE_VERBOSE === '1'
  
  // 颜色代码
  const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    dim: '\x1b[2m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
    white: '\x1b[37m',
  }
  
  // 格式化时间戳
  function timestamp(): string {
    const now = new Date()
    const hours = String(now.getHours()).padStart(2, '0')
    const minutes = String(now.getMinutes()).padStart(2, '0')
    const seconds = String(now.getSeconds()).padStart(2, '0')
    const ms = String(now.getMilliseconds()).padStart(3, '0')
    return `${hours}:${minutes}:${seconds}.${ms}`
  }
  
  // 内部日志函数
  function log(emoji: string, color: string, component: string, ...args: any[]) {
    if (!enabled) return
    
    const time = `${colors.dim}${timestamp()}${colors.reset}`
    const tag = `${emoji} ${color}[${component}]${colors.reset}`
    
    console.error(time, tag, ...args)
  }
  
  // CLI 相关
  export function cli(...args: any[]) {
    log('🚀', colors.blue, 'CLI', ...args)
  }
  
  // Server 相关
  export function server(...args: any[]) {
    log('🌐', colors.green, 'SERVER', ...args)
  }
  
  // Session 相关
  export function session(...args: any[]) {
    log('💬', colors.cyan, 'SESSION', ...args)
  }
  
  // Agent 相关
  export function agent(...args: any[]) {
    log('🤖', colors.magenta, 'AGENT', ...args)
  }
  
  // Tool 相关
  export function tool(toolName: string, ...args: any[]) {
    log('🔧', colors.yellow, `TOOL:${toolName}`, ...args)
  }
  
  // TUI 相关
  export function tui(...args: any[]) {
    log('🖥️ ', colors.blue, 'TUI', ...args)
  }
  
  // Provider 相关
  export function provider(providerName: string, ...args: any[]) {
    log('🔌', colors.magenta, `PROVIDER:${providerName}`, ...args)
  }
  
  // LSP 相关
  export function lsp(...args: any[]) {
    log('📝', colors.cyan, 'LSP', ...args)
  }
  
  // MCP 相关
  export function mcp(...args: any[]) {
    log('🔗', colors.yellow, 'MCP', ...args)
  }
  
  // Storage 相关
  export function storage(...args: any[]) {
    log('💾', colors.green, 'STORAGE', ...args)
  }
  
  // 性能追踪
  export function perf(component: string, operation: string, duration: number) {
    const durationStr = duration < 1 
      ? `${duration.toFixed(2)}ms`
      : duration < 1000
      ? `${Math.round(duration)}ms`
      : `${(duration / 1000).toFixed(2)}s`
    
    log('⏱️ ', colors.yellow, 'PERF', `${component}.${operation}:`, durationStr)
  }
  
  // 错误日志
  export function error(component: string, error: Error | string, ...args: any[]) {
    log('❌', colors.red, component, error, ...args)
  }
  
  // 成功日志
  export function success(component: string, ...args: any[]) {
    log('✅', colors.green, component, ...args)
  }
  
  // 警告日志
  export function warn(component: string, ...args: any[]) {
    log('⚠️ ', colors.yellow, component, ...args)
  }
  
  // 详细追踪（仅在 VERBOSE 模式）
  export function trace(component: string, fn: string, data?: any) {
    if (!verbose) return
    log('📍', colors.dim, `TRACE:${component}`, fn, data || '')
  }
  
  // 分隔线
  export function separator(title?: string) {
    if (!enabled) return
    const line = '═'.repeat(60)
    if (title) {
      console.error(`${colors.dim}${line}${colors.reset}`)
      console.error(`${colors.bright}${title}${colors.reset}`)
      console.error(`${colors.dim}${line}${colors.reset}`)
    } else {
      console.error(`${colors.dim}${line}${colors.reset}`)
    }
  }
  
  // 对象格式化输出
  export function object(component: string, label: string, obj: any) {
    if (!enabled) return
    log('📦', colors.cyan, component, label)
    console.error(JSON.stringify(obj, null, 2))
  }
  
  // 计时器
  export class Timer {
    private startTime: number
    private component: string
    private operation: string
    
    constructor(component: string, operation: string) {
      this.component = component
      this.operation = operation
      this.startTime = performance.now()
      
      if (enabled) {
        log('⏱️ ', colors.blue, component, `Starting: ${operation}`)
      }
    }
    
    stop(label?: string) {
      const duration = performance.now() - this.startTime
      perf(this.component, label || this.operation, duration)
      return duration
    }
  }
  
  // 流程追踪
  export class FlowTracker {
    private steps: Array<{ step: string; time: number; data?: any }> = []
    private startTime: number
    private flowName: string
    
    constructor(flowName: string) {
      this.flowName = flowName
      this.startTime = performance.now()
      
      if (enabled) {
        separator(`Flow: ${flowName}`)
      }
    }
    
    step(stepName: string, data?: any) {
      const elapsed = performance.now() - this.startTime
      this.steps.push({ step: stepName, time: elapsed, data })
      
      if (enabled) {
        log('📍', colors.cyan, 'FLOW', `[+${elapsed.toFixed(0)}ms] ${stepName}`, data || '')
      }
    }
    
    complete() {
      const totalTime = performance.now() - this.startTime
      
      if (enabled) {
        separator(`Flow Complete: ${this.flowName}`)
        console.error(`${colors.green}Total time: ${totalTime.toFixed(2)}ms${colors.reset}`)
        console.error(`${colors.dim}Steps:${colors.reset}`)
        
        this.steps.forEach((s, i) => {
          console.error(`  ${i + 1}. [+${s.time.toFixed(0)}ms] ${s.step}`)
        })
        
        separator()
      }
      
      return {
        flowName: this.flowName,
        totalTime,
        steps: this.steps
      }
    }
  }
}

// 导出便捷类型
export type { DebugLog }

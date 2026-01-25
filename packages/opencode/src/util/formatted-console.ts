import { Log } from "./log"

/**
 * 格式化的控制台输出
 * 
 * 提供更清晰、更易读的控制台日志输出
 */
export namespace FormattedConsole {
  const enabled = process.env.OPENCODE_TELEMETRY === '1' || process.env.OPENCODE_DEBUG === '1'
  
  // 颜色定义
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
    gray: '\x1b[90m',
  }

  /**
   * 格式化时间戳
   */
  function formatTime(): string {
    const now = new Date()
    return now.toTimeString().split(' ')[0] // HH:MM:SS
  }

  /**
   * 打印工具调用开始
   */
  export function toolCallStart(toolName: string, input: any) {
    if (!enabled) return

    console.error(
      `${colors.gray}[${formatTime()}]${colors.reset} ` +
      `${colors.cyan}🔧 Tool${colors.reset} ` +
      `${colors.bright}${toolName}${colors.reset} ` +
      `${colors.dim}started${colors.reset}`
    )
  }

  /**
   * 打印工具调用结束
   */
  export function toolCallEnd(toolName: string, success: boolean, duration: number) {
    if (!enabled) return

    const icon = success ? '✅' : '❌'
    const status = success ? colors.green : colors.red
    const statusText = success ? 'completed' : 'failed'

    console.error(
      `${colors.gray}[${formatTime()}]${colors.reset} ` +
      `${status}${icon} Tool${colors.reset} ` +
      `${colors.bright}${toolName}${colors.reset} ` +
      `${colors.dim}${statusText} in ${duration}ms${colors.reset}`
    )
  }

  /**
   * 打印 LLM 调用开始
   */
  export function llmCallStart(provider: string, model: string) {
    if (!enabled) return

    console.error(
      `${colors.gray}[${formatTime()}]${colors.reset} ` +
      `${colors.magenta}🤖 LLM${colors.reset} ` +
      `${colors.bright}${provider}/${model}${colors.reset} ` +
      `${colors.dim}started${colors.reset}`
    )
  }

  /**
   * 打印 LLM 调用结束
   */
  export function llmCallEnd(provider: string, model: string, success: boolean, tokens?: number, duration?: number) {
    if (!enabled) return

    const icon = success ? '✅' : '❌'
    const status = success ? colors.green : colors.red
    const statusText = success ? 'completed' : 'failed'

    let info = statusText
    if (duration) info += ` in ${duration}ms`
    if (tokens) info += `, ${formatTokens(tokens)} tokens`

    console.error(
      `${colors.gray}[${formatTime()}]${colors.reset} ` +
      `${status}${icon} LLM${colors.reset} ` +
      `${colors.bright}${provider}/${model}${colors.reset} ` +
      `${colors.dim}${info}${colors.reset}`
    )
  }

  /**
   * 打印成本估算
   */
  export function cost(provider: string, model: string, tokens: number, cost: number) {
    if (!enabled) return

    console.error(
      `${colors.gray}[${formatTime()}]${colors.reset} ` +
      `${colors.yellow}💰 Cost${colors.reset} ` +
      `${colors.bright}${provider}/${model}${colors.reset} ` +
      `${colors.dim}${formatTokens(tokens)} tokens ≈ $${cost.toFixed(4)}${colors.reset}`
    )
  }

  /**
   * 打印分隔线
   */
  export function separator(char: string = '─', width: number = 60) {
    if (!enabled) return
    console.error(colors.dim + char.repeat(width) + colors.reset)
  }

  /**
   * 打印消息组开始
   */
  export function groupStart(title: string) {
    if (!enabled) return
    console.error(`\n${colors.bright}${title}${colors.reset}`)
    separator()
  }

  /**
   * 打印消息组结束
   */
  export function groupEnd() {
    if (!enabled) return
    separator()
    console.error('')
  }

  /**
   * 格式化 token 数量
   */
  function formatTokens(tokens: number): string {
    if (tokens >= 1000000) {
      return `${(tokens / 1000000).toFixed(1)}M`
    } else if (tokens >= 1000) {
      return `${(tokens / 1000).toFixed(1)}K`
    }
    return tokens.toString()
  }

  /**
   * 检查是否启用
   */
  export function isEnabled(): boolean {
    return enabled
  }
}

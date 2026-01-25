import { Log } from "./log"
import type { MessageV2 } from "../session/message-v2"
import type { Provider } from "../provider/provider"

/**
 * OpenCode 遥测日志系统
 * 
 * 用于追踪和记录:
 * - 工具调用 (Tool Calls)
 * - MCP 调用 (MCP Calls)
 * - AI 模型调用 (LLM Calls)
 * - Token 消耗 (Token Usage)
 * - 上下文管理 (Context Management)
 * 
 * 使用方法:
 * 1. 设置环境变量: export OPENCODE_TELEMETRY=1
 * 2. 在代码中导入: import { TelemetryLog } from "@/util/telemetry-log"
 * 3. 记录事件: TelemetryLog.toolCall({ ... })
 */

export namespace TelemetryLog {
  // 检查是否启用遥测
  const enabled = process.env.OPENCODE_TELEMETRY === '1' || process.env.OPENCODE_DEBUG === '1'
  
  const log = Log.create({ service: "telemetry" })

  // ============================================================================
  // 工具调用追踪
  // ============================================================================

  export interface ToolCallEvent {
    sessionID: string
    messageID: string
    callID: string
    toolName: string
    agent: string
    input: any
    timestamp: number
  }

  export interface ToolResultEvent {
    sessionID: string
    messageID: string
    callID: string
    toolName: string
    success: boolean
    duration: number
    output?: string
    error?: string
    metadata?: any
    timestamp: number
  }

  /**
   * 记录工具调用开始
   */
  export function toolCallStart(event: ToolCallEvent) {
    if (!enabled) return

    log.info("tool_call_start", {
      sessionID: event.sessionID,
      messageID: event.messageID,
      callID: event.callID,
      tool: event.toolName,
      agent: event.agent,
      input: JSON.stringify(event.input),
      timestamp: event.timestamp,
    })
  }

  /**
   * 记录工具调用结果
   */
  export function toolCallEnd(event: ToolResultEvent) {
    if (!enabled) return

    log.info("tool_call_end", {
      sessionID: event.sessionID,
      messageID: event.messageID,
      callID: event.callID,
      tool: event.toolName,
      success: event.success,
      duration: event.duration,
      outputLength: event.output?.length || 0,
      error: event.error,
      metadata: event.metadata ? JSON.stringify(event.metadata) : undefined,
      timestamp: event.timestamp,
    })
  }

  // ============================================================================
  // MCP 调用追踪
  // ============================================================================

  export interface MCPCallEvent {
    sessionID: string
    messageID: string
    mcpName: string
    toolName: string
    input: any
    timestamp: number
  }

  export interface MCPResultEvent {
    sessionID: string
    messageID: string
    mcpName: string
    toolName: string
    success: boolean
    duration: number
    output?: any
    error?: string
    timestamp: number
  }

  /**
   * 记录 MCP 调用开始
   */
  export function mcpCallStart(event: MCPCallEvent) {
    if (!enabled) return

    log.info("mcp_call_start", {
      sessionID: event.sessionID,
      messageID: event.messageID,
      mcp: event.mcpName,
      tool: event.toolName,
      input: JSON.stringify(event.input),
      timestamp: event.timestamp,
    })
  }

  /**
   * 记录 MCP 调用结果
   */
  export function mcpCallEnd(event: MCPResultEvent) {
    if (!enabled) return

    log.info("mcp_call_end", {
      sessionID: event.sessionID,
      messageID: event.messageID,
      mcp: event.mcpName,
      tool: event.toolName,
      success: event.success,
      duration: event.duration,
      error: event.error,
      timestamp: event.timestamp,
    })
  }

  // ============================================================================
  // LLM 调用追踪
  // ============================================================================

  export interface LLMCallEvent {
    sessionID: string
    messageID: string
    providerID: string
    modelID: string
    agent: string
    inputTokens?: number
    inputMessages: number
    timestamp: number
  }

  export interface LLMResultEvent {
    sessionID: string
    messageID: string
    providerID: string
    modelID: string
    success: boolean
    duration: number
    inputTokens?: number
    outputTokens?: number
    totalTokens?: number
    reasoningTokens?: number
    finishReason?: string
    error?: string
    timestamp: number
  }

  /**
   * 记录 LLM 调用开始
   */
  export function llmCallStart(event: LLMCallEvent) {
    if (!enabled) return

    log.info("llm_call_start", {
      sessionID: event.sessionID,
      messageID: event.messageID,
      provider: event.providerID,
      model: event.modelID,
      agent: event.agent,
      inputTokens: event.inputTokens,
      inputMessages: event.inputMessages,
      timestamp: event.timestamp,
    })
  }

  /**
   * 记录 LLM 调用结果
   */
  export function llmCallEnd(event: LLMResultEvent) {
    if (!enabled) return

    log.info("llm_call_end", {
      sessionID: event.sessionID,
      messageID: event.messageID,
      provider: event.providerID,
      model: event.modelID,
      success: event.success,
      duration: event.duration,
      inputTokens: event.inputTokens,
      outputTokens: event.outputTokens,
      totalTokens: event.totalTokens,
      reasoningTokens: event.reasoningTokens,
      finishReason: event.finishReason,
      error: event.error,
      timestamp: event.timestamp,
    })
  }

  // ============================================================================
  // Token 使用统计
  // ============================================================================

  export interface TokenUsageEvent {
    sessionID: string
    messageID: string
    providerID: string
    modelID: string
    promptTokens: number
    completionTokens: number
    totalTokens: number
    reasoningTokens?: number
    cachedTokens?: number
    timestamp: number
  }

  /**
   * 记录 Token 使用情况
   */
  export function tokenUsage(event: TokenUsageEvent) {
    if (!enabled) return

    log.info("token_usage", {
      sessionID: event.sessionID,
      messageID: event.messageID,
      provider: event.providerID,
      model: event.modelID,
      promptTokens: event.promptTokens,
      completionTokens: event.completionTokens,
      totalTokens: event.totalTokens,
      reasoningTokens: event.reasoningTokens,
      cachedTokens: event.cachedTokens,
      timestamp: event.timestamp,
    })
  }

  // ============================================================================
  // 上下文管理追踪
  // ============================================================================

  export interface ContextEvent {
    sessionID: string
    messageID: string
    contextSize: number
    messageCount: number
    toolCallCount: number
    truncated: boolean
    timestamp: number
  }

  /**
   * 记录上下文管理信息
   */
  export function contextManagement(event: ContextEvent) {
    if (!enabled) return

    log.info("context_management", {
      sessionID: event.sessionID,
      messageID: event.messageID,
      contextSize: event.contextSize,
      messageCount: event.messageCount,
      toolCallCount: event.toolCallCount,
      truncated: event.truncated,
      timestamp: event.timestamp,
    })
  }

  // ============================================================================
  // Session 级别统计
  // ============================================================================

  export interface SessionStatsEvent {
    sessionID: string
    totalMessages: number
    totalToolCalls: number
    totalMCPCalls: number
    totalLLMCalls: number
    totalTokens: number
    totalDuration: number
    timestamp: number
  }

  /**
   * 记录 Session 统计信息
   */
  export function sessionStats(event: SessionStatsEvent) {
    if (!enabled) return

    log.info("session_stats", {
      sessionID: event.sessionID,
      totalMessages: event.totalMessages,
      totalToolCalls: event.totalToolCalls,
      totalMCPCalls: event.totalMCPCalls,
      totalLLMCalls: event.totalLLMCalls,
      totalTokens: event.totalTokens,
      totalDuration: event.totalDuration,
      timestamp: event.timestamp,
    })
  }

  // ============================================================================
  // 性能追踪
  // ============================================================================

  export interface PerformanceEvent {
    component: string
    operation: string
    duration: number
    metadata?: any
    timestamp: number
  }

  /**
   * 记录性能指标
   */
  export function performance(event: PerformanceEvent) {
    if (!enabled) return

    log.info("performance", {
      component: event.component,
      operation: event.operation,
      duration: event.duration,
      metadata: event.metadata ? JSON.stringify(event.metadata) : undefined,
      timestamp: event.timestamp,
    })
  }

  // ============================================================================
  // 工具类
  // ============================================================================

  /**
   * 创建一个追踪器,用于自动记录开始和结束事件
   */
  export class Tracker<TStart, TEnd> {
    private startTime: number
    private startEvent: TStart
    private onStart: (event: TStart) => void
    private onEnd: (event: TEnd) => void

    constructor(
      startEvent: TStart,
      onStart: (event: TStart) => void,
      onEnd: (event: TEnd) => void,
    ) {
      this.startTime = Date.now()
      this.startEvent = startEvent
      this.onStart = onStart
      this.onEnd = onEnd
      
      // 记录开始事件
      this.onStart(startEvent)
    }

    /**
     * 结束追踪并记录结果
     */
    end(result: Omit<TEnd, 'duration' | 'timestamp'>) {
      const duration = Date.now() - this.startTime
      this.onEnd({
        ...result,
        duration,
        timestamp: Date.now(),
      } as TEnd)
      return duration
    }
  }

  /**
   * 创建工具调用追踪器
   */
  export function trackToolCall(event: ToolCallEvent) {
    return new Tracker<ToolCallEvent, ToolResultEvent>(
      event,
      toolCallStart,
      toolCallEnd,
    )
  }

  /**
   * 创建 MCP 调用追踪器
   */
  export function trackMCPCall(event: MCPCallEvent) {
    return new Tracker<MCPCallEvent, MCPResultEvent>(
      event,
      mcpCallStart,
      mcpCallEnd,
    )
  }

  /**
   * 创建 LLM 调用追踪器
   */
  export function trackLLMCall(event: LLMCallEvent) {
    return new Tracker<LLMCallEvent, LLMResultEvent>(
      event,
      llmCallStart,
      llmCallEnd,
    )
  }

  // ============================================================================
  // 辅助函数
  // ============================================================================

  /**
   * 检查遥测是否启用
   */
  export function isEnabled(): boolean {
    return enabled
  }

  /**
   * 格式化 token 数量
   */
  export function formatTokens(tokens: number): string {
    if (tokens < 1000) return `${tokens}`
    if (tokens < 1000000) return `${(tokens / 1000).toFixed(1)}K`
    return `${(tokens / 1000000).toFixed(1)}M`
  }

  /**
   * 格式化持续时间
   */
  export function formatDuration(ms: number): string {
    if (ms < 1000) return `${Math.round(ms)}ms`
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
    return `${Math.floor(ms / 60000)}m ${Math.round((ms % 60000) / 1000)}s`
  }

  /**
   * 计算 token 成本 (示例,需要根据实际价格调整)
   */
  export function estimateCost(
    providerID: string,
    modelID: string,
    inputTokens: number,
    outputTokens: number,
  ): number {
    // 这里可以根据不同的 provider 和 model 计算实际成本
    // 示例价格 (需要更新为实际价格)
    const prices: Record<string, { input: number; output: number }> = {
      'openai/gpt-4': { input: 0.03 / 1000, output: 0.06 / 1000 },
      'openai/gpt-3.5-turbo': { input: 0.0015 / 1000, output: 0.002 / 1000 },
      'anthropic/claude-3-opus': { input: 0.015 / 1000, output: 0.075 / 1000 },
      'anthropic/claude-3-sonnet': { input: 0.003 / 1000, output: 0.015 / 1000 },
    }

    const key = `${providerID}/${modelID}`
    const price = prices[key] || { input: 0, output: 0 }
    
    return (inputTokens * price.input) + (outputTokens * price.output)
  }
}

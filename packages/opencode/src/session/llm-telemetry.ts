import { TelemetryLog } from "../util/telemetry-log"
import { HTTPLog } from "../util/http-log"
import type { LLM } from "../session/llm"
import type { StreamTextResult } from "ai"

/**
 * LLM 调用遥测包装器
 * 
 * 自动追踪 AI 模型调用和 token 消耗
 */
export namespace LLMTelemetry {
  /**
   * 包装 LLM stream 调用,添加遥测追踪
   */
  export async function wrapStream(
    input: LLM.StreamInput,
    streamFn: (input: LLM.StreamInput) => Promise<LLM.StreamOutput>,
  ): Promise<LLM.StreamOutput> {
    // 创建追踪器
    const tracker = TelemetryLog.trackLLMCall({
      sessionID: input.sessionID,
      messageID: input.user.id,
      providerID: input.model.providerID,
      modelID: input.model.id,
      agent: input.agent.name,
      inputMessages: input.messages.length,
      timestamp: Date.now(),
    })

    try {
      // 调用原始 stream 函数
      const result = await streamFn(input)

      // 监听 stream 完成事件
      monitorStreamCompletion(result, tracker, input)

      return result
    } catch (error) {
      // 记录失败
      tracker.end({
        sessionID: input.sessionID,
        messageID: input.user.id,
        providerID: input.model.providerID,
        modelID: input.model.id,
        success: false,
        error: error instanceof Error ? error.message : String(error),
      })

      throw error
    }
  }

  /**
   * 监听 stream 完成,记录 token 使用情况
   */
  function monitorStreamCompletion(
    result: StreamTextResult<any, any>,
    tracker: TelemetryLog.Tracker<TelemetryLog.LLMCallEvent, TelemetryLog.LLMResultEvent>,
    input: LLM.StreamInput,
  ) {
    // 使用 Promise 监听完成
    result.then(
      (finalResult) => {
        // 获取 token 使用情况
        const usage = finalResult.usage

        // 记录成功结果
        tracker.end({
          sessionID: input.sessionID,
          messageID: input.user.id,
          providerID: input.model.providerID,
          modelID: input.model.id,
          success: true,
          inputTokens: usage?.promptTokens,
          outputTokens: usage?.completionTokens,
          totalTokens: usage?.totalTokens,
          finishReason: finalResult.finishReason,
        })

        // 记录详细的 token 使用情况
        if (usage) {
          TelemetryLog.tokenUsage({
            sessionID: input.sessionID,
            messageID: input.user.id,
            providerID: input.model.providerID,
            modelID: input.model.id,
            promptTokens: usage.promptTokens,
            completionTokens: usage.completionTokens,
            totalTokens: usage.totalTokens,
            timestamp: Date.now(),
          })

          // 如果启用了遥测,打印成本估算
          if (TelemetryLog.isEnabled()) {
            const cost = TelemetryLog.estimateCost(
              input.model.providerID,
              input.model.id,
              usage.promptTokens,
              usage.completionTokens,
            )
            
            if (cost > 0) {
              console.error(
                `💰 [COST] ${input.model.providerID}/${input.model.id}: ` +
                `${TelemetryLog.formatTokens(usage.totalTokens)} tokens ≈ $${cost.toFixed(4)}`
              )
            }
          }
        }
      },
      (error) => {
        // 记录失败
        tracker.end({
          sessionID: input.sessionID,
          messageID: input.user.id,
          providerID: input.model.providerID,
          modelID: input.model.id,
          success: false,
          error: error instanceof Error ? error.message : String(error),
        })
      },
    )
  }

  /**
   * 记录上下文管理信息
   */
  export function logContextManagement(
    sessionID: string,
    messageID: string,
    messages: any[],
    truncated: boolean,
  ) {
    // 计算工具调用数量
    let toolCallCount = 0
    for (const msg of messages) {
      if (Array.isArray(msg.content)) {
        for (const part of msg.content) {
          if (part.type === 'tool-call') {
            toolCallCount++
          }
        }
      }
    }

    // 估算上下文大小 (简单估算)
    const contextSize = JSON.stringify(messages).length

    TelemetryLog.contextManagement({
      sessionID,
      messageID,
      contextSize,
      messageCount: messages.length,
      toolCallCount,
      truncated,
      timestamp: Date.now(),
    })
  }
}

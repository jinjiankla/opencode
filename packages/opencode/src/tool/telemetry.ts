import { Tool } from "../tool/tool"
import { TelemetryLog } from "../util/telemetry-log"
import { ulid } from "ulid"

/**
 * 工具调用包装器
 * 
 * 自动为所有工具调用添加遥测日志
 */
export namespace ToolTelemetry {
  /**
   * 包装工具的 execute 函数,添加遥测追踪
   */
  export function wrapToolExecute<P extends any, M extends any>(
    toolInfo: Awaited<ReturnType<Tool.Info<any, M>["init"]>>,
    toolId: string,
  ): typeof toolInfo {
    const originalExecute = toolInfo.execute

    toolInfo.execute = async (args, ctx) => {
      const callID = ctx.callID || ulid()
      
      // 创建追踪器
      const tracker = TelemetryLog.trackToolCall({
        sessionID: ctx.sessionID,
        messageID: ctx.messageID,
        callID,
        toolName: toolId,
        agent: ctx.agent,
        input: args,
        timestamp: Date.now(),
      })

      try {
        // 执行原始工具
        const result = await originalExecute(args, ctx)

        // 记录成功结果
        tracker.end({
          sessionID: ctx.sessionID,
          messageID: ctx.messageID,
          callID,
          toolName: toolId,
          success: true,
          output: result.output,
          metadata: result.metadata,
        })

        return result
      } catch (error) {
        // 记录失败结果
        tracker.end({
          sessionID: ctx.sessionID,
          messageID: ctx.messageID,
          callID,
          toolName: toolId,
          success: false,
          error: error instanceof Error ? error.message : String(error),
        })

        throw error
      }
    }

    return toolInfo
  }

  /**
   * 包装工具定义,自动添加遥测
   */
  export function wrapTool<Parameters extends any, Result extends any>(
    tool: Tool.Info<Parameters, Result>,
  ): Tool.Info<Parameters, Result> {
    const originalInit = tool.init

    return {
      ...tool,
      init: async (ctx) => {
        const toolInfo = await originalInit(ctx)
        return wrapToolExecute(toolInfo, tool.id)
      },
    }
  }
}

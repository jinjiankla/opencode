import path from "path"
import fs from "fs/promises"
import { Global } from "../global"
import z from "zod"

export namespace Log {
  export const Level = z.enum(["DEBUG", "INFO", "WARN", "ERROR"]).meta({ ref: "LogLevel", description: "Log level" })
  export type Level = z.infer<typeof Level>

  const levelPriority: Record<Level, number> = {
    DEBUG: 0,
    INFO: 1,
    WARN: 2,
    ERROR: 3,
  }

  let level: Level = "INFO"

  function shouldLog(input: Level): boolean {
    return levelPriority[input] >= levelPriority[level]
  }

  export type Logger = {
    debug(message?: any, extra?: Record<string, any>): void
    info(message?: any, extra?: Record<string, any>): void
    error(message?: any, extra?: Record<string, any>): void
    warn(message?: any, extra?: Record<string, any>): void
    tag(key: string, value: string): Logger
    clone(): Logger
    time(
      message: string,
      extra?: Record<string, any>,
    ): {
      stop(): void
      [Symbol.dispose](): void
    }
  }

  const loggers = new Map<string, Logger>()

  export const Default = create({ service: "default" })

  export interface Options {
    print: boolean
    dev?: boolean
    level?: Level
  }

  let logpath = ""
  export function file() {
    return logpath
  }
  let write = (msg: any) => {
    process.stderr.write(msg)
    return msg.length
  }

  export async function init(options: Options) {
    if (options.level) level = options.level
    cleanup(Global.Path.log)
    if (options.print) return
    logpath = path.join(
      Global.Path.log,
      options.dev ? "dev.log" : new Date().toISOString().split(".")[0].replace(/:/g, "") + ".log",
    )
    const logfile = Bun.file(logpath)
    await fs.truncate(logpath).catch(() => {})
    const writer = logfile.writer()
    write = async (msg: any) => {
      const num = writer.write(msg)
      writer.flush()
      return num
    }
  }

  async function cleanup(dir: string) {
    const glob = new Bun.Glob("????-??-??T??????.log")
    const files = await Array.fromAsync(
      glob.scan({
        cwd: dir,
        absolute: true,
      }),
    )
    if (files.length <= 5) return

    const filesToDelete = files.slice(0, -10)
    await Promise.all(filesToDelete.map((file) => fs.unlink(file).catch(() => {})))
  }

  function formatError(error: Error, depth = 0): string {
    const result = error.message
    return error.cause instanceof Error && depth < 10
      ? result + " Caused by: " + formatError(error.cause, depth + 1)
      : result
  }

  let last = Date.now()
  export function create(tags?: Record<string, any>) {
    tags = tags || {}

    const service = tags["service"]
    if (service && typeof service === "string") {
      const cached = loggers.get(service)
      if (cached) {
        return cached
      }
    }

    function build(level: string, message: any, extra?: Record<string, any>) {
      const colors = {
        DEBUG: "\x1b[90m",
        INFO: "\x1b[34m",
        WARN: "\x1b[33m",
        ERROR: "\x1b[31m",
        RESET: "\x1b[0m",
        GRAY: "\x1b[90m",
        CYAN: "\x1b[36m",
      }

      const levelColor = colors[level as keyof typeof colors] || colors.RESET
      const formattedLevel = `${levelColor}${level.padEnd(5)}${colors.RESET}`

      const allTags = { ...tags, ...extra }
      const tagString = Object.entries(allTags)
        .filter(([_, value]) => value !== undefined && value !== null)
        .map(([key, value]) => {
          let val = value
          if (value instanceof Error) val = formatError(value)
          else if (typeof value === "object") val = JSON.stringify(value)
          return `${colors.CYAN}${key}${colors.RESET}=${val}`
        })
        .join(" ")

      const next = new Date()
      const diff = next.getTime() - last
      last = next.getTime()
      
      const timeStr = `${colors.GRAY}${next.toISOString().split("T")[1].split(".")[0]}${colors.RESET}`
      const diffStr = `${colors.GRAY}+${diff.toString().padStart(3)}ms${colors.RESET}`

      const prefix = [timeStr, diffStr, formattedLevel].filter(Boolean).join(" ")
      
      let msg = message
      if (message instanceof Error) msg = formatError(message)
      else if (typeof message === "object") msg = JSON.stringify(message)

      const suffix = tagString ? `  ${colors.GRAY}# ${tagString}${colors.RESET}` : ""

      return `${prefix} ${colors.GRAY}│${colors.RESET} ${msg}${suffix}\n`
    }

    const result: Logger = {
      debug(message?: any, extra?: Record<string, any>) {
        if (shouldLog("DEBUG")) {
          write(build("DEBUG", message, extra))
        }
      },
      info(message?: any, extra?: Record<string, any>) {
        if (shouldLog("INFO")) {
          write(build("INFO", message, extra))
        }
      },
      error(message?: any, extra?: Record<string, any>) {
        if (shouldLog("ERROR")) {
          write(build("ERROR", message, extra))
        }
      },
      warn(message?: any, extra?: Record<string, any>) {
        if (shouldLog("WARN")) {
          write(build("WARN", message, extra))
        }
      },
      tag(key: string, value: string) {
        if (tags) tags[key] = value
        return result
      },
      clone() {
        return Log.create({ ...tags })
      },
      time(message: string, extra?: Record<string, any>) {
        const now = Date.now()
        result.info(message, { status: "started", ...extra })
        function stop() {
          result.info(message, {
            status: "completed",
            duration: Date.now() - now,
            ...extra,
          })
        }
        return {
          stop,
          [Symbol.dispose]() {
            stop()
          },
        }
      },
    }

    if (service && typeof service === "string") {
      loggers.set(service, result)
    }

    return result
  }
}

"use client"

import * as React from "react"
import { cn } from "cn"
import {
  Streamdown,
  useIsCodeFenceIncomplete,
  type ExtraProps,
} from "streamdown"

import {
  CodeBlock,
  CodeBlockActions,
  CodeBlockContent,
  CodeBlockCopyButton,
  CodeBlockHeader,
  CodeBlockLine,
  CodeBlockTitle,
} from "@workspace/ui/components/code-block"

function MarkdownCodeBlock({
  code,
  language,
}: {
  code: string
  language: string
}) {
  const incomplete = useIsCodeFenceIncomplete()

  return (
    <CodeBlock>
      <CodeBlockHeader>
        <CodeBlockTitle>{language || "text"}</CodeBlockTitle>
        <CodeBlockActions>
          <CodeBlockCopyButton value={code} disabled={incomplete} />
        </CodeBlockActions>
      </CodeBlockHeader>
      <CodeBlockContent>
        <CodeBlockLine>{code}</CodeBlockLine>
      </CodeBlockContent>
    </CodeBlock>
  )
}

function MarkdownCode({
  node,
  className,
  children,
  ...props
}: React.ComponentProps<"code"> & ExtraProps) {
  if (!("data-block" in props)) {
    return (
      <code
        className={cn(
          "rounded-sm bg-muted px-1 py-0.5 font-mono text-[0.9em]",
          className
        )}
        {...props}
      >
        {children}
      </code>
    )
  }

  return (
    <MarkdownCodeBlock
      code={typeof children === "string" ? children : ""}
      language={/language-(\S+)/.exec(className ?? "")?.[1] ?? ""}
    />
  )
}

const DEFAULT_COMPONENTS = { code: MarkdownCode }

function Markdown({
  className,
  components = DEFAULT_COMPONENTS,
  controls = false,
  ...props
}: React.ComponentProps<typeof Streamdown>) {
  return (
    <Streamdown
      data-slot="markdown"
      components={components}
      controls={controls}
      className={cn("w-full min-w-0 overflow-hidden", className)}
      {...props}
    />
  )
}

export { Markdown }

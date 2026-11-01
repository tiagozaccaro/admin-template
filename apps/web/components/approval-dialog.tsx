"use client"

import * as React from "react"
import { AlertTriangle } from "lucide-react"

import { Button } from "@workspace/ui/components/button"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@workspace/ui/components/sheet"

export type ApprovalRequest = {
  id: string
  toolName: string
  args: Record<string, unknown>
  summary: string
}

type ApprovalDialogProps = {
  request: ApprovalRequest | null
  onApprove: (request: ApprovalRequest) => void
  onDeny: (request: ApprovalRequest) => void
}

export function ApprovalDialog({
  request,
  onApprove,
  onDeny,
}: ApprovalDialogProps) {
  const open = request !== null

  if (!request) {
    return null
  }

  return (
    <Sheet open={open} onOpenChange={() => {}}>
      <SheetContent
        side="bottom"
        className="sm:max-w-lg"
        showCloseButton={false}
      >
        <SheetHeader>
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-500" />
            <SheetTitle>Approval required</SheetTitle>
          </div>
          <SheetDescription>
            The agent wants to run a destructive action. Review and approve or
            deny it.
          </SheetDescription>
        </SheetHeader>
        <div className="grid gap-3 py-4">
          <div className="rounded-md border border-border bg-muted/40 p-3">
            <p className="text-sm font-medium">Tool</p>
            <p className="font-mono text-sm text-muted-foreground">
              {request.toolName}
            </p>
          </div>
          <div className="rounded-md border border-border bg-muted/40 p-3">
            <p className="text-sm font-medium">Summary</p>
            <p className="text-sm text-muted-foreground">{request.summary}</p>
          </div>
          <div className="rounded-md border border-border bg-muted/40 p-3">
            <p className="text-sm font-medium">Arguments</p>
            <pre className="mt-1 overflow-x-auto text-xs text-muted-foreground">
              {JSON.stringify(request.args, null, 2)}
            </pre>
          </div>
        </div>
        <SheetFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => onDeny(request)}
          >
            Deny
          </Button>
          <Button onClick={() => onApprove(request)}>Approve</Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}

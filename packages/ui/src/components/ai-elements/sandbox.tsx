import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@workspace/ui/components/tabs"
export function Sandbox({ code, output }: { code: string; output?: string }) {
  return (
    <Tabs defaultValue="code">
      <TabsList>
        <TabsTrigger value="code">Code</TabsTrigger>
        <TabsTrigger value="output">Output</TabsTrigger>
      </TabsList>
      <TabsContent value="code">
        <pre className="overflow-auto rounded-md bg-muted p-3 text-xs">
          {code}
        </pre>
      </TabsContent>
      <TabsContent value="output">
        <pre className="overflow-auto rounded-md bg-muted p-3 text-xs">
          {output}
        </pre>
      </TabsContent>
    </Tabs>
  )
}

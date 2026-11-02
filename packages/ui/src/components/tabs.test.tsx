import { render, screen, fireEvent } from "@testing-library/react"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./tabs.js"
import { describe, it, expect } from "vitest"
/// <reference types="@testing-library/jest-dom" />

describe("Tabs", () => {
  it("renders triggers and content", () => {
    render(
      <Tabs defaultValue="a">
        <TabsList>
          <TabsTrigger value="a">Tab A</TabsTrigger>
          <TabsTrigger value="b">Tab B</TabsTrigger>
        </TabsList>
        <TabsContent value="a">Content A</TabsContent>
        <TabsContent value="b">Content B</TabsContent>
      </Tabs>
    )
    expect(screen.getByText("Tab A")).toBeInTheDocument()
    expect(screen.getByText("Content A")).toBeInTheDocument()
  })
})

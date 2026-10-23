import { render, screen } from "@testing-library/react"
import { Card, CardHeader, CardTitle, CardContent } from "./card.js"
import { describe, it, expect } from "vitest"
/// <reference types="@testing-library/jest-dom" />

describe("Card", () => {
  it("renders title and content", () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Title</CardTitle>
        </CardHeader>
        <CardContent>Body</CardContent>
      </Card>
    )
    expect(screen.getByText("Title")).toBeInTheDocument()
    expect(screen.getByText("Body")).toBeInTheDocument()
  })
})

import { render, screen } from "@testing-library/react"
import { Badge } from "./badge.js"
import { describe, it, expect } from "vitest"
/// <reference types="@testing-library/jest-dom" />

describe("Badge", () => {
  it("renders children", () => {
    render(<Badge>New</Badge>)
    expect(screen.getByText("New")).toBeInTheDocument()
  })
})

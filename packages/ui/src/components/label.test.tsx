import { render, screen } from "@testing-library/react"
import { Label } from "./label.js"
import { describe, it, expect } from "vitest"
/// <reference types="@testing-library/jest-dom" />

describe("Label", () => {
  it("renders children", () => {
    render(<Label>Name</Label>)
    expect(screen.getByText("Name")).toBeInTheDocument()
  })
})

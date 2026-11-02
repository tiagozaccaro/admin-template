import { render, screen } from "@testing-library/react"
import { Separator } from "./separator.js"
import { describe, it, expect } from "vitest"
/// <reference types="@testing-library/jest-dom" />

describe("Separator", () => {
  it("renders", () => {
    render(<Separator />)
    expect(screen.getByRole("separator")).toBeInTheDocument()
  })
})

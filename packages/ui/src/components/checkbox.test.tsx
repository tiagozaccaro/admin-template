import { render, screen, fireEvent } from "@testing-library/react"
import { Checkbox } from "./checkbox.js"
import { describe, it, expect, vi } from "vitest"
/// <reference types="@testing-library/jest-dom" />

describe("Checkbox", () => {
  it("renders", () => {
    render(<Checkbox aria-label="agree" />)
    expect(screen.getByRole("checkbox", { name: "agree" })).toBeInTheDocument()
  })

  it("toggles on click", () => {
    const onCheckedChange = vi.fn()
    render(<Checkbox aria-label="agree" onCheckedChange={onCheckedChange} />)
    fireEvent.click(screen.getByRole("checkbox", { name: "agree" }))
    expect(onCheckedChange).toHaveBeenCalled()
  })
})

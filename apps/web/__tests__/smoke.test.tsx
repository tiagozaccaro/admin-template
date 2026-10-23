import { render, screen } from "@testing-library/react"
import { describe, it, expect } from "vitest"

function Hello() {
  return <div>Hello</div>
}

describe("smoke", () => {
  it("renders", () => {
    render(<Hello />)
    expect(screen.getByText("Hello")).toBeTruthy()
  })
})

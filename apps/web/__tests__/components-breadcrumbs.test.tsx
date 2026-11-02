import { render, screen } from "@testing-library/react"
import { describe, it, expect } from "vitest"
import { Breadcrumbs } from "@/components/breadcrumbs"

describe("breadcrumbs", () => {
  it("renders items", () => {
    render(
      <Breadcrumbs items={[{ label: "Home", href: "/" }, { label: "Items" }]} />
    )
    expect(screen.getByText("Home")).toBeTruthy()
    expect(screen.getByText("Items")).toBeTruthy()
  })
})
